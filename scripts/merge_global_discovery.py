#!/usr/bin/env python3
"""Merge and validate all 24 global GLO-90 shards into a traceable release."""
from __future__ import annotations

import argparse
import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_SHARDS = 24
TARGETS = ("moon", "mars")


def validate_candidate_rows(rows: list[dict[str, Any]], target: str) -> None:
    """Reject duplicate, malformed or non-finite shortlist inputs before ranking."""
    seen: set[str] = set()
    for index, row in enumerate(rows):
        prefix = f"{target} candidate[{index}]"
        if not isinstance(row, dict):
            raise ValueError(f"{prefix}: candidate must be an object")
        candidate_id = row.get("id")
        if not isinstance(candidate_id, str) or not candidate_id:
            raise ValueError(f"{prefix}: non-empty id required")
        if candidate_id in seen:
            raise ValueError(f"{target}: duplicate candidate id {candidate_id}")
        seen.add(candidate_id)
        if not isinstance(row.get("tile_id"), str) or not row["tile_id"]:
            raise ValueError(f"{prefix}: tile_id required")
        for key in ("core_terrain_index", "secondary_diagnostic_index", "latitude", "longitude"):
            value = row.get(key)
            if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
                raise ValueError(f"{prefix}: {key} must be finite numeric data")
        if not 0 <= row["core_terrain_index"] <= 100:
            raise ValueError(f"{prefix}: core_terrain_index outside [0, 100]")
        if not 0 <= row["secondary_diagnostic_index"] <= 100:
            raise ValueError(f"{prefix}: secondary_diagnostic_index outside [0, 100]")
        if not -90 <= row["latitude"] <= 90 or not -180 <= row["longitude"] <= 180:
            raise ValueError(f"{prefix}: coordinates outside WGS84 bounds")


def select(rows: list[dict[str, Any]], limit: int = 1200, max_per_tile: int = 3) -> list[dict[str, Any]]:
    """Rank by the declared core family only; keep secondary rank diagnostic."""
    ordered = sorted(rows, key=lambda row: (-row["core_terrain_index"], row["id"]))
    chosen: list[dict[str, Any]] = []
    counts: dict[str, int] = {}
    for row in ordered:
        tile_id = row["tile_id"]
        if counts.get(tile_id, 0) >= max_per_tile:
            continue
        counts[tile_id] = counts.get(tile_id, 0) + 1
        chosen.append(dict(row))
        if len(chosen) >= limit:
            break
    secondary_order = {
        row["id"]: rank
        for rank, row in enumerate(
            sorted(chosen, key=lambda row: (-row["secondary_diagnostic_index"], row["id"])), 1
        )
    }
    for rank, row in enumerate(chosen, 1):
        row["shortlist_rank"] = rank
        row["secondary_rank_within_primary_shortlist"] = secondary_order[row["id"]]
        row["ranking_role"] = "primary_core_only; secondary index is diagnostic only"
    return chosen


def load_shards(source: Path) -> dict[int, dict[str, Any]]:
    files = sorted(source.rglob("global-shard-*.json"))
    if len(files) != EXPECTED_SHARDS:
        raise ValueError(f"Expected exactly {EXPECTED_SHARDS} shard files; found {len(files)}")
    shards: dict[int, dict[str, Any]] = {}
    for path in files:
        payload = json.loads(path.read_text(encoding="utf-8"))
        shard_id = payload.get("shard")
        if not isinstance(shard_id, int) or not 0 <= shard_id < EXPECTED_SHARDS:
            raise ValueError(f"{path}: invalid shard identifier {shard_id!r}")
        if shard_id in shards:
            raise ValueError(f"Duplicate shard identifier {shard_id}")
        if payload.get("shard_count") != EXPECTED_SHARDS:
            raise ValueError(f"Shard {shard_id}: unexpected shard_count")
        if payload.get("is_smoke_test") is True:
            raise ValueError(f"Shard {shard_id}: smoke-test output cannot enter a release")
        for key in ("tile_inventory_total", "tiles_assigned", "tiles_processed", "candidate_windows_evaluated"):
            if not isinstance(payload.get(key), int) or payload[key] < 0:
                raise ValueError(f"Shard {shard_id}: {key} must be a non-negative integer")
        failures = payload.get("tile_failures")
        if not isinstance(failures, list):
            raise ValueError(f"Shard {shard_id}: tile_failures must be a list")
        if payload["tiles_processed"] + len(failures) != payload["tiles_assigned"]:
            raise ValueError(f"Shard {shard_id}: processed + failed tiles does not equal assigned tiles")
        if not isinstance(payload.get("targets"), dict):
            raise ValueError(f"Shard {shard_id}: targets object missing")
        for target in TARGETS:
            if not isinstance(payload["targets"].get(target, {}).get("candidate_windows"), list):
                raise ValueError(f"Shard {shard_id}: {target} candidate_windows missing")
        if not isinstance(payload.get("target_reference_profiles"), dict):
            raise ValueError(f"Shard {shard_id}: reference profiles missing")
        shards[shard_id] = payload
    if sorted(shards) != list(range(EXPECTED_SHARDS)):
        raise ValueError("Shard set is incomplete")
    inventory_counts = {payload["tile_inventory_total"] for payload in shards.values()}
    if len(inventory_counts) != 1:
        raise ValueError("Shard tile inventories disagree; refusing to merge inconsistent runs")
    assigned_sum = sum(payload["tiles_assigned"] for payload in shards.values())
    inventory_total = inventory_counts.pop()
    if assigned_sum != inventory_total:
        raise ValueError(f"Shard assignments ({assigned_sum}) do not equal provider inventory ({inventory_total})")
    return shards


def build_release(shards: dict[int, dict[str, Any]]) -> dict[str, Any]:
    ref = shards[0]["target_reference_profiles"]
    for shard_id, payload in shards.items():
        if payload["target_reference_profiles"] != ref:
            raise ValueError(f"Shard {shard_id}: reference profiles differ from shard 0")
    inventory_total = shards[0]["tile_inventory_total"]
    assigned = sum(payload["tiles_assigned"] for payload in shards.values())
    processed = sum(payload["tiles_processed"] for payload in shards.values())
    failed = [item for payload in shards.values() for item in payload["tile_failures"]]
    inventory_total = shards[0]["tile_inventory_total"]
    if assigned != inventory_total:
        raise ValueError(f"Shard assignments ({assigned}) do not equal provider inventory ({inventory_total})")
    for shard_id, payload in shards.items():
        if payload["tiles_processed"] + len(payload["tile_failures"]) != payload["tiles_assigned"]:
            raise ValueError(f"Shard {shard_id}: processed + failed tiles does not equal assigned tiles")
    windows = sum(payload["candidate_windows_evaluated"] for payload in shards.values())
    candidate_rows = {
        target: [row for payload in shards.values() for row in payload["targets"][target]["candidate_windows"]]
        for target in TARGETS
    }
    for target, rows in candidate_rows.items():
        validate_candidate_rows(rows, target)
    shortlists = {target: select(candidate_rows[target]) for target in TARGETS}
    full = assigned == inventory_total and processed == assigned and not failed
    return {
        "schema_version": "1.1.0",
        "project": "ANALOG-X Global Discovery & Intelligence Engine",
        "generated_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "status": "complete" if full else "partial",
        "ranking_contract": {
            "schema_version": "1.1.0",
            "ranking_ready": True,
            "primary_feature_family": "core",
            "primary_sort": ["core_terrain_index descending", "id ascending"],
            "secondary_role": "diagnostic_only",
            "consensus_score": False,
            "candidate_rows_validated": True,
            "note": "A ranking-ready terrain-screening release is not an independently validated planetary analog model."
        },
        "completion_contract": {
            "global_land_tile_inventory_total": inventory_total,
            "tiles_assigned_to_shards": assigned,
            "tiles_processed": processed,
            "tile_failures": len(failed),
            "tile_processing_coverage_pct": round(100 * processed / max(inventory_total, 1), 4),
            "candidate_windows_evaluated": windows,
            "shards_expected": EXPECTED_SHARDS,
            "shards_received": len(shards),
            "complete_global_land_inventory_scan": full,
            "coverage_definition": "Fraction of Copernicus GLO-90 tileList land tiles whose elevation COG was opened and processed. Ocean has no DEM tile; this is not a claim of ocean coverage."
        },
        "source": {
            "provider": "Copernicus DEM / AWS Open Data",
            "product": "COP-DEM_GLO-90-DGED",
            "resolution": "90 m nominal (30 arc seconds)",
            "data_type": "DSM",
            "tile_inventory": "https://copernicus-dem-90m.s3.amazonaws.com/tileList.txt",
            "asset_base": "https://copernicus-dem-90m.s3.eu-central-1.amazonaws.com/",
            "documentation": "https://copernicus-dem-90m.s3.amazonaws.com/readme.html",
            "registry": "https://registry.opendata.aws/copernicus-dem/",
            "license": "Copernicus DEM GLO-90 general-public licence; see provider terms"
        },
        "method": {
            "unit_of_analysis": "Non-overlapping 6x6-cell windows, nominally ~5.55 km x ~5.55 km at ~925 m support, in each one-degree land tile",
            "resampling": "GLO-90 COG resampled by area averaging to a local metric CRS at 925 m nominal cell size",
            "core_features": ref["feature_families"]["core"],
            "primary_ranking_feature_family": "core",
            "secondary_features": ref["feature_families"]["secondary"],
            "secondary_ranking_role": "Diagnostic only; not averaged into the primary score or used to order the global shortlist.",
            "secondary_features_role": "Alternative terrain diagnostics from the same DEM source; not independent-source validation.",
            "score": "Separate core and secondary terrain-distance indices use IQR-normalized feature gaps. The global shortlist is ordered by core_terrain_index only; no blended consensus score is produced.",
            "target_reference_profiles": ref,
            "target_reference_sources": {
                "moon": "NASA LRO LOLA GDR LDEM_80S_80M, regional Shackleton Rim grid",
                "mars": "NASA MGS MOLA MEGDR 64 ppd, regional Nili Patera grid"
            },
            "validity": "At least 70% of 36 elevation cells and at least 15 valid slope and relief derivatives",
            "window_sampling": "Non-overlapping stride equal to six cells; windows are not statistically independent at broader spatial scales.",
            "interpretation": "A terrain-screening lead only. Score is not a probability, calibrated accuracy, geological equivalence, resource estimate, operational suitability, or landing/rover safety."
        },
        "targets": {
            target: {
                "reference": ref[target],
                "shortlist_method": "Top 1,200 by primary core terrain index, capped at three candidates per 1-degree source tile; secondary index is diagnostic only",
                "candidate_windows": shortlists[target]
            } for target in TARGETS
        },
        "failed_tiles": failed,
        "shard_summaries": [
            {
                "shard": i,
                "tiles_assigned": shards[i]["tiles_assigned"],
                "tiles_processed": shards[i]["tiles_processed"],
                "tiles_without_valid_windows": shards[i]["tiles_without_valid_windows"],
                "candidate_windows_evaluated": shards[i]["candidate_windows_evaluated"],
                "tile_failures": len(shards[i]["tile_failures"])
            } for i in range(EXPECTED_SHARDS)
        ],
        "limits": [
            "Worldwide coverage applies only to the enumerated public GLO-90 land-tile inventory; ocean is excluded.",
            "GLO-90 is a DSM and contains surface objects such as vegetation, buildings, snow and ice.",
            "Global data are coarser than selected GLO-30 local study windows; do not merge their scores without a scale-aware method.",
            "Terrain descriptors do not measure lithology, mineralogy, regolith strength, dust, illumination, radiation, water/ice, subsurface resources or trafficability.",
            "The secondary feature family is an alternative diagnostic from the same DEM, not independent validation.",
            "The candidate shortlists are bounded to 1,200 ranked windows per target, not a complete export of all evaluated windows."
        ]
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-dir", default="global-shards")
    parser.add_argument("--output", default="data/global_discovery/global_discovery.json")
    args = parser.parse_args()
    shards = load_shards(Path(args.input_dir))
    result = build_release(shards)
    output = ROOT / args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": result["status"],
        "ranking_ready": result["ranking_contract"]["ranking_ready"],
        "tile_inventory_total": result["completion_contract"]["global_land_tile_inventory_total"],
        "tiles_processed": result["completion_contract"]["tiles_processed"],
        "tile_failures": result["completion_contract"]["tile_failures"],
        "windows": result["completion_contract"]["candidate_windows_evaluated"],
        "moon_shortlist": len(result["targets"]["moon"]["candidate_windows"]),
        "mars_shortlist": len(result["targets"]["mars"]["candidate_windows"]),
        "output": str(output)
    }, indent=2))


if __name__ == "__main__":
    main()

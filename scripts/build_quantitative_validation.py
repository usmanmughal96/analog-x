#!/usr/bin/env python3
"""Build transparent global, robustness, second-source, geology and field evidence diagnostics."""
from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
GLOBAL = ROOT / "data/global_discovery/global_discovery.json"
NASADEM = ROOT / "data/validation/nasadem_crosscheck.json"
LANDCOVER = ROOT / "data/global_discovery/global_landcover_enrichment.json"
POWER = ROOT / "data/global_discovery/global_power_enrichment.json"
LITHOLOGY = ROOT / "data/global_discovery/global_lithology_enrichment.json"
FIELD = ROOT / "data/field_validation/observations.json"
LABEL_VALIDATION = ROOT / "data/validation/independent_analog_label_validation.json"
REGISTRY = ROOT / "data/source_registry.json"
MANIFEST = ROOT / "data/provenance/reproducibility_manifest.json"
OUT = ROOT / "data/validation/quantitative_validation.json"


def read(path: Path) -> dict[str, Any] | None:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else None


def sha256(path: Path) -> str | None:
    if not path.exists():
        return None
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def average_rank(values: list[float]) -> np.ndarray:
    """One-based average ranks, including deterministic handling of ties."""
    order = np.argsort(np.asarray(values), kind="mergesort")
    ranks = np.empty(len(values), dtype=float)
    start = 0
    while start < len(order):
        end = start + 1
        while end < len(order) and values[order[end]] == values[order[start]]:
            end += 1
        ranks[order[start:end]] = (start + 1 + end) / 2.0
        start = end
    return ranks


def spearman(a: list[float], b: list[float]) -> float | None:
    if len(a) < 3:
        return None
    ra, rb = average_rank(a), average_rank(b)
    if np.std(ra) == 0 or np.std(rb) == 0:
        return None
    return round(float(np.corrcoef(ra, rb)[0, 1]), 4)


def ranking_integrity(global_data: dict[str, Any]) -> dict[str, Any]:
    """Verify the published shortlist really follows the declared core-only contract."""
    checks: dict[str, Any] = {}
    all_valid = global_data.get("schema_version") == "1.1.0"
    for target in ("moon", "mars"):
        rows = global_data.get("targets", {}).get(target, {}).get("candidate_windows", [])
        ids = [row.get("id") for row in rows]
        expected = sorted(rows, key=lambda row: (-float(row["core_terrain_index"]), row["id"]))
        order_ok = ids == [row.get("id") for row in expected]
        primary_ranks = [row.get("shortlist_rank") for row in rows]
        secondary_ranks = [row.get("secondary_rank_within_primary_shortlist") for row in rows]
        rank_ok = primary_ranks == list(range(1, len(rows) + 1))
        secondary_ok = (
            len(secondary_ranks) == len(rows)
            and all(isinstance(rank, int) and not isinstance(rank, bool) for rank in secondary_ranks)
            and sorted(secondary_ranks) == list(range(1, len(rows) + 1))
        )
        unique_ok = len(ids) == len(set(ids))
        target_ok = bool(rows) and order_ok and rank_ok and secondary_ok and unique_ok
        checks[target] = {
            "candidate_count": len(rows),
            "primary_core_order_valid": order_ok,
            "primary_ranks_sequential": rank_ok,
            "secondary_diagnostic_ranks_permutation": secondary_ok,
            "candidate_ids_unique": unique_ok,
            "ranking_valid": target_ok,
        }
        all_valid = all_valid and target_ok
    contract = global_data.get("ranking_contract", {})
    contract_ok = (
        contract.get("ranking_ready") is True
        and contract.get("primary_feature_family") == "core"
        and contract.get("consensus_score") is False
    )
    completion = global_data.get("completion_contract", {})
    inventory_complete = (
        global_data.get("status") == "complete"
        and completion.get("complete_global_land_inventory_scan") is True
        and completion.get("shards_received") == completion.get("shards_expected") == 24
        and completion.get("tiles_assigned_to_shards") == completion.get("global_land_tile_inventory_total")
        and completion.get("tiles_processed") == completion.get("global_land_tile_inventory_total")
        and completion.get("tile_failures") == 0
    )
    ready = bool(all_valid and contract_ok and inventory_complete)
    return {
        "status": "ready" if ready else "stale_or_invalid",
        "ranking_ready": ready,
        "dataset_schema_version": global_data.get("schema_version"),
        "required_schema_version": "1.1.0",
        "ranking_contract_present": contract_ok,
        "complete_failure_free_inventory": inventory_complete,
        "targets": checks,
        "note": "Ranking readiness verifies data schema, ordering and rank integrity only. It does not establish independent scientific accuracy or planetary analog validity.",
    }


def target_report(rows: list[dict[str, Any]]) -> dict[str, Any]:
    if not rows:
        return {"status": "no_global_candidates"}
    core = [float(row["core_terrain_index"]) for row in rows]
    secondary = [float(row["secondary_diagnostic_index"]) for row in rows]
    core_order = np.argsort(np.asarray(core))[::-1]
    secondary_order = np.argsort(np.asarray(secondary))[::-1]
    id_to_secondary_rank = {
        rows[idx]["id"]: rank for rank, idx in enumerate(secondary_order, 1)
    }
    report: dict[str, Any] = {
        "candidate_pool_size": len(rows),
        "primary_ranking": "core_terrain_index descending",
        "secondary_ranking": "secondary_diagnostic_index descending, diagnostic only",
        "core_vs_secondary_spearman": spearman(core, secondary),
        "top_25_overlap": len(set(core_order[:25]) & set(secondary_order[:25])),
        "top_100_overlap": len(set(core_order[:100]) & set(secondary_order[:100])),
        "median_score_family_gap_points": round(float(np.median([
            abs(a - b) for a, b in zip(core, secondary)
        ])), 4),
        "top_25_secondary_rank_range": [
            int(min(id_to_secondary_rank[rows[idx]["id"]] for idx in core_order[:min(25, len(rows))])),
            int(max(id_to_secondary_rank[rows[idx]["id"]] for idx in core_order[:min(25, len(rows))])),
        ],
        "interpretation": (
            "This diagnostic compares two different feature families derived from the same "
            "Copernicus GLO-90 source within the retained primary shortlist. It tests rank "
            "sensitivity to feature choice; it is not independent-source validation, model "
            "accuracy, field truth or a calibrated probability."
        ),
    }
    for n in (25, 100, 500):
        selected = [rows[i] for i in core_order[:min(n, len(rows))]]
        report[f"top_{n}_unique_source_tiles"] = len({row["tile_id"] for row in selected})
        report[f"top_{n}_occupied_10deg_cells"] = len({
            (int((row["latitude"] + 90) // 10), int((row["longitude"] + 180) // 10))
            for row in selected
        })
    return report


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--require-ranking-ready", action="store_true")
    args = parser.parse_args()
    global_data = read(GLOBAL)
    if not global_data:
        payload: dict[str, Any] = {
            "schema_version": "2.0.0",
            "generated_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
            "status": "awaiting_global_scan",
        }
    else:
        contract = global_data.get("completion_contract", {})
        targets: dict[str, Any] = {}
        for target in ("moon", "mars"):
            rows = global_data.get("targets", {}).get(target, {}).get("candidate_windows", [])
            targets[target] = target_report(rows)
        complete = (
            global_data.get("status") == "complete"
            and contract.get("complete_global_land_inventory_scan") is True
            and contract.get("tiles_processed") == contract.get("global_land_tile_inventory_total")
            and contract.get("tile_failures") == 0
        )
        payload = {
            "schema_version": "2.1.0",
            "generated_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
            "status": "diagnostic_only",
            "ranking_release": ranking_integrity(global_data),
            "global_scan": {
                "status": global_data.get("status"),
                "global_land_tile_inventory_total": contract.get("global_land_tile_inventory_total"),
                "tiles_assigned_to_shards": contract.get("tiles_assigned_to_shards"),
                "tiles_processed": contract.get("tiles_processed"),
                "tile_failures": contract.get("tile_failures"),
                "tile_processing_coverage_pct": contract.get("tile_processing_coverage_pct"),
                "candidate_windows_evaluated": contract.get("candidate_windows_evaluated"),
                "shards_expected": contract.get("shards_expected"),
                "shards_received": contract.get("shards_received"),
                "complete_global_land_inventory_scan": complete,
                "coverage_definition": contract.get("coverage_definition"),
            },
            "targets": targets,
            "interpretation": (
                "Global terrain screening is complete only for the enumerated Copernicus GLO-90 "
                "land-tile inventory. The stored list is a bounded shortlist, not all evaluated "
                "windows. Primary rank uses the core terrain family only; the alternative family "
                "is diagnostic. Neither score is a probability, calibrated accuracy or analog verdict."
            ),
        }

    if not global_data:
        payload["ranking_release"] = {
            "status": "awaiting_global_scan",
            "ranking_ready": False,
            "required_schema_version": "1.1.0",
            "targets": {},
        }

    label_validation = read(LABEL_VALIDATION)
    payload["independent_analog_label_validation"] = label_validation or {
        "status": "awaiting_reference_labels",
        "note": "No independently sourced, reviewed positive/negative analog label file is present. No AUC or accuracy is inferred.",
    }

    landcover = read(LANDCOVER)
    if landcover:
        payload["global_land_cover_enrichment"] = {
            "state": landcover.get("state"),
            "shortlist_candidate_windows_unique": landcover.get("shortlist_candidate_windows_unique", 0),
            "processed_candidate_windows": landcover.get("processed_candidate_windows", 0),
            "coverage_percent_of_shortlist": landcover.get("coverage_percent_of_shortlist", 0),
            "source_collection": landcover.get("source", {}).get("collection"),
            "year": landcover.get("source", {}).get("year"),
            "interpretation": "2023 Sentinel-2-derived land-cover context for retained shortlist windows only; not geology or field truth.",
        }
    else:
        payload["global_land_cover_enrichment"] = {"state": "awaiting_enrichment"}

    power = read(POWER)
    if power:
        payload["global_nasa_power_climatology"] = {
            "state": power.get("state"),
            "scope": power.get("scope", {}),
            "parameters": power.get("source", {}).get("parameters", []),
            "interpretation": "NASA POWER gridded climatology at retained candidate coordinates, not in-situ observations or a full global climate raster.",
        }
    else:
        payload["global_nasa_power_climatology"] = {"state": "awaiting_enrichment"}

    lithology = read(LITHOLOGY)
    if lithology:
        payload["global_lithology_context"] = {
            "state": lithology.get("state"),
            "scope": lithology.get("scope", {}),
            "source": lithology.get("source", {}),
            "method": lithology.get("method", {}),
            "limitations": lithology.get("limitations", []),
            "interpretation": "Generalized GLiM centre-point context for retained candidates only. Not area-weighted, field-verified geology; excluded from candidate scoring.",
        }
    else:
        payload["global_lithology_context"] = {"state": "awaiting_enrichment"}

    nasadem = read(NASADEM)
    if nasadem:
        payload["independent_dem_crosscheck"] = {
            "state": nasadem.get("status"),
            "sites_attempted": nasadem.get("sites_attempted"),
            "sites_crosschecked": nasadem.get("sites_crosschecked", 0),
            "rank_concordance": nasadem.get("rank_concordance", {}),
            "source": nasadem.get("source"),
            "limits": nasadem.get("limitations", []),
            "interpretation": "Independent elevation-source check on a small selected overlap set; not field validation or a global accuracy estimate.",
        }
    else:
        payload["independent_dem_crosscheck"] = {"state": "awaiting_validation_run"}

    field = read(FIELD) or {"status": "not_started", "observations": []}
    observations = field.get("observations", [])
    reviewed = [row for row in observations if row.get("review_status") == "independently_reviewed"]
    payload["ground_truth_validation"] = {
        "state": "independently_reviewed_observations_present" if reviewed else (
            "field_observations_unreviewed" if observations else "not_available"
        ),
        "observations_total": len(observations),
        "independently_reviewed_observations": len(reviewed),
        "note": (
            "Physical field validation can only be claimed for properties and locations covered by "
            "documented measurements and independent review. Protocols, proposed stations and desk data do not count."
        ),
    }

    manifest = read(MANIFEST)
    payload["reproducibility"] = {
        "manifest_state": "present" if manifest else "not_built",
        "manifest_sha256": sha256(MANIFEST),
        "hashed_repository_file_count": manifest.get("file_count") if manifest else 0,
        "source_registry_records": len(manifest.get("source_registry_records", [])) if manifest else 0,
        "manifest_generated_at_utc": manifest.get("generated_at_utc") if manifest else None,
        "limitations": [
            "SHA-256 establishes byte-level identity, not scientific validity or source authenticity.",
            "The manifest records the repository commit before its own final commit; it cannot hash its final committed bytes.",
            "Historical external retrieval metadata may be incomplete and must be traced through source registry and product-specific records.",
        ],
    }

    registry = read(REGISTRY) or {"sources": []}
    state_counts = Counter(row.get("state", "missing") for row in registry.get("sources", []))
    payload["evidence_registry"] = {
        "source_records": len(registry.get("sources", [])),
        "state_counts": dict(sorted(state_counts.items())),
        "rule": "browse_only, metadata_only and reference_only records are not represented as fully processed quantitative science inputs.",
    }

    payload["release_gate"] = {
        "ranking_release": "ready only when schema 1.1.0 core-only ordering and rank-integrity checks pass",
        "independent_analog_validation": "awaiting independently sourced, reviewed labels and spatially blocked held-out evaluation",
        "global_scan": "complete only when every enumerated land tile is processed and tile_failures=0",
        "quantitative_validation": "diagnostic-only until independent labels, spatially blocked tests and defensible held-out validation are available",
        "field_validation": "requires georeferenced observations, instrument/calibration provenance, permissions and independent review",
        "data_depth": "each source retains a state; browse images and catalogue metadata are not decoded science arrays",
        "reproducibility": "manifest and per-product source/method/parameter/provenance records required; hashes alone do not prove validity",
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {OUT.relative_to(ROOT)} ({payload['status']})")
    ranking = payload.get("ranking_release", {})
    print(f"Ranking release: {ranking.get('status', 'unknown')}")
    if args.require_ranking_ready and ranking.get("ranking_ready") is not True:
        raise SystemExit("Ranking release gate failed: regenerate and verify the schema 1.1.0 core-only shortlist.")


if __name__ == "__main__":
    main()

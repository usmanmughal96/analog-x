#!/usr/bin/env python3
"""Merge the 24 global terrain-discovery shards into a traceable release dataset."""
from __future__ import annotations
import argparse, json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def select(rows, limit=1200, max_per_tile=3):
    rows = sorted(rows, key=lambda x: (-x["consensus_index"], -x["metric_family_score_agreement"], x["id"]))
    chosen, counts = [], {}
    for row in rows:
        tid = row["tile_id"]
        if counts.get(tid, 0) >= max_per_tile:
            continue
        counts[tid] = counts.get(tid, 0) + 1
        chosen.append(row)
        if len(chosen) >= limit:
            break
    for i, row in enumerate(chosen, 1):
        row["shortlist_rank"] = i
    return chosen


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-dir", default="global-shards")
    parser.add_argument("--output", default="data/global_discovery/global_discovery.json")
    args = parser.parse_args()
    source = Path(args.input_dir)
    files = sorted(source.rglob("global-shard-*.json"))
    shards = {json.loads(p.read_text(encoding="utf-8"))["shard"]: json.loads(p.read_text(encoding="utf-8")) for p in files}
    if len(shards) != 24 or sorted(shards) != list(range(24)):
        raise SystemExit(f"Expected all 24 global scan shards; found {len(shards)}: {sorted(shards)}")
    inventory_counts = {x["tile_inventory_total"] for x in shards.values()}
    if len(inventory_counts) != 1:
        raise SystemExit("Shard tile inventories disagree; refusing to merge inconsistent runs")
    inventory_total = inventory_counts.pop()
    assigned = sum(x["tiles_assigned"] for x in shards.values())
    processed = sum(x["tiles_processed"] for x in shards.values())
    failed = [item for shard in shards.values() for item in shard["tile_failures"]]
    windows = sum(x["candidate_windows_evaluated"] for x in shards.values())
    rows = {
        target: [candidate for shard in shards.values() for candidate in shard["targets"][target]["candidate_windows"]]
        for target in ("moon", "mars")
    }
    ref = shards[0]["target_reference_profiles"]
    full = assigned == inventory_total and processed == assigned and not failed
    result = {
        "schema_version": "1.0.0",
        "project": "ANALOG-X Global Discovery & Intelligence Engine",
        "generated_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "status": "complete" if full else "partial",
        "completion_contract": {
            "global_land_tile_inventory_total": inventory_total,
            "tiles_assigned_to_shards": assigned,
            "tiles_processed": processed,
            "tile_failures": len(failed),
            "tile_processing_coverage_pct": round(100 * processed / max(inventory_total, 1), 4),
            "candidate_windows_evaluated": windows,
            "shards_expected": 24,
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
            "secondary_features": ref["feature_families"]["secondary"],
            "secondary_features_role": "Alternative terrain diagnostics used to assess metric-family rank robustness; derived from the same DEM source and not independent-source validation.",
            "score": "Each feature family's normalized mean absolute gap to the selected planetary reference median, scaled by the IQR of windows in the ten-site Earth reference pack; transformed as 100*exp(-mean_gap). Consensus is the arithmetic mean of core and secondary indexes.",
            "target_reference_profiles": ref,
            "target_reference_sources": {
                "moon": "NASA LRO LOLA GDR LDEM_80S_80M, regional Shackleton Rim grid",
                "mars": "NASA MGS MOLA MEGDR 64 ppd, regional Nili Patera grid"
            },
            "validity": "At least 70% of 36 elevation cells and at least 15 valid slope and relief derivatives",
            "window_sampling": "Non-overlapping stride equal to six cells to reduce compute and avoid duplicate adjacent windows; windows are not statistically independent at broader spatial scales.",
            "interpretation": "A terrain-screening lead only. Score is not a probability, calibrated accuracy, geological equivalence, resource estimate, operational suitability, or landing/rover safety."
        },
        "targets": {
            target: {"reference": ref[target], "shortlist_method": "Top 1,200 consensus candidates, capped at three candidates per 1-degree source tile", "candidate_windows": select(rows[target])}
            for target in ("moon", "mars")
        },
        "failed_tiles": failed,
        "shard_summaries": [
            {
                "shard": i, "tiles_assigned": shards[i]["tiles_assigned"],
                "tiles_processed": shards[i]["tiles_processed"],
                "tiles_without_valid_windows": shards[i]["tiles_without_valid_windows"],
                "candidate_windows_evaluated": shards[i]["candidate_windows_evaluated"],
                "tile_failures": len(shards[i]["tile_failures"])
            } for i in range(24)
        ],
        "limits": [
            "The worldwide search is only complete when all 24 shards are present and every tile in the public GLO-90 tile inventory has been processed; otherwise status remains partial.",
            "GLO-90 is a DSM and contains surface objects such as vegetation, buildings, snow and ice.",
            "The global data are coarser than the existing selected GLO-30 local study windows; do not merge the two resolutions into an unqualified score.",
            "Copernicus GLO-90 terrain descriptors do not measure lithology, mineralogy, regolith strength, dust, illumination, radiation, water/ice, subsurface resources or trafficability.",
            "The secondary feature family is a robustness check within the same DEM, not independent-source validation.",
            "The candidate shortlists are bounded to 1,200 ranked windows per target; they are not a complete export of every evaluated window."
        ]
    }
    out = ROOT / args.output
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": result["status"], "tile_inventory_total": inventory_total, "tiles_processed": processed, "tile_failures": len(failed), "windows": windows, "moon_shortlist": len(result["targets"]["moon"]["candidate_windows"]), "mars_shortlist": len(result["targets"]["mars"]["candidate_windows"]), "output": str(out)}, indent=2))


if __name__ == "__main__":
    main()

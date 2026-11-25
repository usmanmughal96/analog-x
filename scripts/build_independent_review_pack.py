#!/usr/bin/env python3
"""Create a blind, spatially stratified independent-review packet.

The public packet intentionally excludes candidate IDs, ranks, scores and terrain
metrics. A separate case-key file restores those fields after review; never
commit or share that key with reviewers.
"""
from __future__ import annotations
import argparse, hashlib, json, secrets
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
GLOBAL = ROOT / "data/global_discovery/global_discovery.json"
RANKED_OUT = ROOT / "data/global_discovery/top_ranked_candidates.json"
PACKET_OUT = ROOT / "data/validation/independent_analog_review_packet.json"
TARGETS = ("moon", "mars")
SAMPLE_BINS = (
    (1, 25, "top_25"),
    (26, 100, "ranks_26_100"),
    (101, 300, "ranks_101_300"),
    (301, 600, "ranks_301_600"),
    (601, 900, "ranks_601_900"),
    (901, 1200, "ranks_901_1200"),
)
SAMPLE_PER_BIN = 8
REVIEW_VERSION = "terrain_morphology_transfer_v1"


def spatial_group(row: dict[str, Any]) -> str:
    lat, lon = float(row["latitude"]), float(row["longitude"])
    lat_cell = min(17, max(0, int((lat + 90.0) // 10.0)))
    lon_cell = min(35, max(0, int((lon + 180.0) // 10.0)))
    return f"g10_{lat_cell:02d}_{lon_cell:02d}"


def case_id(target: str, candidate_id: str, blind_salt: str) -> str:
    # Keyed IDs prevent dictionary matching against the public candidate list.
    digest = hashlib.sha256(f"{blind_salt}|{target}|{candidate_id}".encode()).hexdigest()
    return f"AX-{target[:1].upper()}-{digest[:16].upper()}"


def _rank_rows(target: str, target_data: dict[str, Any]) -> list[dict[str, Any]]:
    rows = target_data.get("candidate_windows", [])
    if not isinstance(rows, list) or not rows:
        raise ValueError(f"{target}: no candidate_windows")
    normalized = []
    for index, row in enumerate(rows, 1):
        rank = row.get("shortlist_rank", index)
        if not isinstance(rank, int) or isinstance(rank, bool) or rank != index:
            raise ValueError(f"{target}: shortlist rank mismatch at row {index}")
        for field in ("id", "tile_id", "latitude", "longitude", "core_terrain_index", "secondary_diagnostic_index"):
            if field not in row:
                raise ValueError(f"{target} rank {rank}: missing {field}")
        normalized.append(row)
    return normalized


def _sample_bin(target: str, rows: list[dict[str, Any]], start: int, end: int) -> list[dict[str, Any]]:
    candidates = [row for row in rows if start <= int(row["shortlist_rank"]) <= end]
    # Deterministic selection independent of Python's randomized hash seed.
    candidates.sort(key=lambda row: hashlib.sha256(
        f"ANALOG-X-review-v1|{target}|{start}|{row['id']}".encode()
    ).hexdigest())
    chosen: list[dict[str, Any]] = []
    used_groups: set[str] = set()
    used_tiles: set[str] = set()
    for row in candidates:
        group = spatial_group(row)
        if group in used_groups or row["tile_id"] in used_tiles:
            continue
        chosen.append(row)
        used_groups.add(group)
        used_tiles.add(row["tile_id"])
        if len(chosen) == SAMPLE_PER_BIN:
            break
    if len(chosen) < SAMPLE_PER_BIN:
        for row in candidates:
            if row in chosen or row["tile_id"] in used_tiles:
                continue
            chosen.append(row)
            used_tiles.add(row["tile_id"])
            if len(chosen) == SAMPLE_PER_BIN:
                break
    if len(chosen) != SAMPLE_PER_BIN:
        raise ValueError(
            f"{target} ranks {start}-{end}: only {len(chosen)} spatially diversified candidates; "
            f"need {SAMPLE_PER_BIN}"
        )
    return chosen


def build_outputs(global_data: dict[str, Any], blind_salt: str | None = None) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    blind_salt = blind_salt or secrets.token_hex(32)
    if global_data.get("schema_version") != "1.1.0":
        raise ValueError("A schema 1.1.0 released global shortlist is required")
    contract = global_data.get("ranking_contract", {})
    if contract.get("ranking_ready") is not True or contract.get("primary_feature_family") != "core":
        raise ValueError("Global core-only ranking contract is not ready")
    if contract.get("consensus_score") is not False:
        raise ValueError("Unexpected consensus score contract")
    completion = global_data.get("completion_contract", {})
    if global_data.get("status") != "complete" or completion.get("tile_failures") != 0:
        raise ValueError("A complete, failure-free global inventory is required")

    ranked: dict[str, Any] = {}
    packet_cases: list[dict[str, Any]] = []
    private_cases: dict[str, Any] = {}
    counts: dict[str, Any] = {}
    for target in TARGETS:
        rows = _rank_rows(target, global_data.get("targets", {}).get(target, {}))
        ranked[target] = {
            "reference_profile": "Shackleton Rim" if target == "moon" else "Nili Patera",
            "candidate_count": len(rows),
            "ranking": "core_terrain_index descending; ID ascending tie-break",
            "score_interpretation": "Terrain-distance screening index, not a probability or validated analog score.",
            "top_25": [
                {
                    "rank": row["shortlist_rank"], "candidate_id": row["id"], "tile_id": row["tile_id"],
                    "latitude": row["latitude"], "longitude": row["longitude"],
                    "core_terrain_index": row["core_terrain_index"],
                    "secondary_diagnostic_index": row["secondary_diagnostic_index"],
                    "secondary_rank": row.get("secondary_rank_within_primary_shortlist"),
                    "window_footprint_km": row.get("window_footprint_km"),
                    "analysis_support_m": row.get("analysis_support_m"),
                    "terrain": row.get("terrain", {}),
                }
                for row in rows[:25]
            ],
        }
        strata_counts = []
        for start, end, name in SAMPLE_BINS:
            selected = _sample_bin(target, rows, start, end)
            strata_counts.append({"stratum": name, "rank_range": [start, end], "n": len(selected)})
            for row in selected:
                cid = case_id(target, row["id"], blind_salt)
                group = spatial_group(row)
                packet_cases.append({
                    "review_case_id": cid,
                    "target": target,
                    "reference_profile": "Shackleton Rim" if target == "moon" else "Nili Patera",
                    "location": {
                        "latitude_wgs84_deg": round(float(row["latitude"]), 1),
                        "longitude_wgs84_deg": round(float(row["longitude"]), 1),
                        "precision_note": "Approximate area locator rounded to the nearest 0.1 degree; not the exact candidate-window centre.",
                    },
                    "analysis_window_km": row.get("window_footprint_km", 5.55),
                    "analysis_support_m": row.get("analysis_support_m", 925),
                    "source_product": "Copernicus DEM GLO-90 (COP-DEM_GLO-90-DGED)",
                    "independent_review": {
                        "label": None,
                        "criterion_version": REVIEW_VERSION,
                        "evidence_refs": [],
                        "reviewer_name": None,
                        "reviewer_affiliation": None,
                        "reviewer_qualification": None,
                        "review_date_utc": None,
                        "confidence_1_to_5": None,
                        "independent_of_analogx_score": None,
                        "rationale": None,
                        "limitations": [],
                    },
                })
                private_cases[cid] = {
                    "target": target,
                    "candidate_id": row["id"],
                    "latitude_wgs84_deg": row["latitude"],
                    "longitude_wgs84_deg": row["longitude"],
                    "shortlist_rank": row["shortlist_rank"],
                    "tile_id": row["tile_id"],
                    "spatial_group": group,
                    "core_terrain_index": row["core_terrain_index"],
                    "secondary_diagnostic_index": row["secondary_diagnostic_index"],
                }
        counts[target] = {"candidate_count": len(rows), "strata": strata_counts}
    packet_cases.sort(key=lambda row: (row["target"], row["review_case_id"]))
    ranking_snapshot = {
        "schema_version": "1.0.0",
        "generated_at_utc": global_data.get("generated_at_utc"),
        "global_scan": {
            "status": global_data.get("status"),
            "tiles_processed": completion.get("tiles_processed"),
            "tile_inventory_total": completion.get("global_land_tile_inventory_total"),
            "tile_failures": completion.get("tile_failures"),
            "candidate_windows_evaluated": completion.get("candidate_windows_evaluated"),
        },
        "ranking_contract": contract,
        "targets": ranked,
        "limits": [
            "Moon and Mars are separate target-specific ranked lists, not one combined leaderboard.",
            "Ranks are within each retained 1,200-candidate shortlist, not ranks across all 5.85 million evaluated windows.",
            "Scores are terrain-screening indices, not probabilities, accuracy estimates or analog verdicts.",
            "No independent labels or field observations are implied by this export.",
        ],
    }
    reviewer_packet = {
        "schema_version": "1.0.0",
        "project": "ANALOG-X",
        "review_version": REVIEW_VERSION,
        "status": "ready_for_external_review",
        "purpose": "Blind, spatially stratified review of terrain-morphology transferability for the current global candidate shortlist.",
        "sampling": {
            "design": "Six predeclared shortlist-rank strata per target; eight candidates per stratum; spatial diversity preferred within each stratum.",
            "public_location_precision_degrees": 0.1,
            "location_policy": "Public case coordinates are rounded to the nearest 0.1 degree. Exact candidate coordinates are retained only in the private case key.",
            "selection_seed": "SHA256(ANALOG-X-review-v1 | target | rank-bin | candidate-id)",
            "spatial_group": "Predeclared 10-degree geographic grid cell; an expert may coalesce adjacent cells into a single geologic block before evaluation, but must not split neighbouring geology across train/test.",
            "cases_per_target": SAMPLE_PER_BIN * len(SAMPLE_BINS),
            "rank_and_score_withheld": True,
        },
        "review_instructions": [
            "Do not request or use ANALOG-X scores or ranks before recording a review.",
            "Assess only the stated terrain-morphology criterion against independent maps, papers, datasets or first-hand expertise.",
            "Positive means the external evidence supports the stated target-relevant morphology/process match; negative means a plausible lookalike fails the criterion; inconclusive or insufficient_evidence must remain unlabelled.",
            "Cite at least one independent evidence reference for positive or negative labels.",
            "Record reviewer qualifications, affiliation, date, confidence and limitations.",
            "Do not treat this terrain-only screen as evidence of volatile access, illumination, radiation, mission safety or overall planetary equivalence.",
        ],
        "cases": packet_cases,
        "quality_gate": {
            "required_evidence_refs_for_binary_label": True,
            "required_reviewer_provenance": True,
            "required_confidence": True,
            "required_independence_declaration": True,
            "inconclusive_labels_excluded_from_auc": True,
        },
        "private_key_policy": "The case key contains candidate IDs, ranks and scores. Generate it locally and keep it outside the public repository. Never send it to reviewers.",
    }
    private_key = {
        "schema_version": "1.0.0",
        "review_version": REVIEW_VERSION,
        "blind_case_id_salt": blind_salt,
        "warning": "PRIVATE: contains candidate IDs, shortlist ranks and model scores. Do not commit or share with reviewers.",
        "cases": private_cases,
    }
    return ranking_snapshot, reviewer_packet, private_key


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--global", dest="global_path", type=Path, default=GLOBAL)
    parser.add_argument("--ranked-output", type=Path, default=RANKED_OUT)
    parser.add_argument("--packet-output", type=Path, default=PACKET_OUT)
    parser.add_argument("--key-output", type=Path, help="Private, untracked case-key file. Never commit this file.")
    parser.add_argument("--skip-review-packet", action="store_true", help="Refresh the public ranking snapshot without regenerating the owner-private blind review packet.")
    args = parser.parse_args()
    data = json.loads(args.global_path.read_text(encoding="utf-8"))
    if args.skip_review_packet:
        ranked, _, _ = build_outputs(data, blind_salt="ranking-snapshot-only")
        packet = None
        key = None
    else:
        if not args.key_output:
            parser.error("--key-output is required unless --skip-review-packet is used")
        blind_salt = None
        if args.key_output.exists():
            try:
                previous_key = json.loads(args.key_output.read_text(encoding="utf-8"))
                blind_salt = previous_key.get("blind_case_id_salt")
            except (OSError, json.JSONDecodeError):
                blind_salt = None
        ranked, packet, key = build_outputs(data, blind_salt=blind_salt or secrets.token_hex(32))
    args.ranked_output.parent.mkdir(parents=True, exist_ok=True)
    args.packet_output.parent.mkdir(parents=True, exist_ok=True)
    args.ranked_output.write_text(json.dumps(ranked, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    packet_written = packet is not None
    if packet_written:
        args.packet_output.write_text(json.dumps(packet, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    if args.key_output and key is not None:
        args.key_output.parent.mkdir(parents=True, exist_ok=True)
        args.key_output.write_text(json.dumps(key, indent=2, allow_nan=False) + "\n", encoding="utf-8")
        try:
            args.key_output.chmod(0o600)
        except OSError:
            pass
    print(json.dumps({
        "ranking_snapshot": str(args.ranked_output.relative_to(ROOT)) if args.ranked_output.is_relative_to(ROOT) else str(args.ranked_output),
        "review_packet": str(args.packet_output.relative_to(ROOT)) if packet_written else "unchanged (private review packet is owner-managed)",
        "cases": {target: sum(1 for row in packet["cases"] if row["target"] == target) for target in TARGETS} if packet_written else "unchanged",
        "private_key_written": bool(args.key_output and key is not None),
    }, indent=2))


if __name__ == "__main__":
    main()

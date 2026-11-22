#!/usr/bin/env python3
"""Import expert responses using the uncommitted private review-case key."""
from __future__ import annotations
import argparse, json
from datetime import datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "data/validation/independent_analog_review_packet.json"
LABELS = ROOT / "data/validation/independent_analog_labels.json"
BINARY = {"positive", "negative"}


def convert_responses(packet: dict[str, Any], key: dict[str, Any], existing: dict[str, Any]) -> tuple[dict[str, Any], dict[str, int]]:
    if packet.get("review_version") != key.get("review_version"):
        raise ValueError("Review packet and private key versions do not match")
    private_cases = key.get("cases", {})
    labels = list(existing.get("labels", []))
    existing_ids = {(row.get("target"), row.get("candidate_id")) for row in labels}
    added = {"positive": 0, "negative": 0, "inconclusive_or_blank": 0}
    for case in packet.get("cases", []):
        review = case.get("independent_review") or {}
        label = review.get("label")
        if label not in BINARY:
            added["inconclusive_or_blank"] += 1
            continue
        cid = case.get("review_case_id")
        private = private_cases.get(cid)
        if not private:
            raise ValueError(f"Unknown review_case_id: {cid}")
        if private["target"] != case.get("target"):
            raise ValueError(f"{cid}: target does not match private key")
        required = (
            "criterion_version", "evidence_refs", "reviewer_name", "reviewer_affiliation",
            "reviewer_qualification", "review_date_utc", "confidence_1_to_5",
            "independent_of_analogx_score", "rationale",
        )
        missing = [name for name in required if review.get(name) in (None, "", [])]
        if missing:
            raise ValueError(f"{cid}: missing review fields: {', '.join(missing)}")
        if review["independent_of_analogx_score"] is not True:
            raise ValueError(f"{cid}: reviewer must attest independence from ANALOG-X score")
        if not isinstance(review["confidence_1_to_5"], int) or not 1 <= review["confidence_1_to_5"] <= 5:
            raise ValueError(f"{cid}: confidence_1_to_5 must be an integer from 1 to 5")
        try:
            datetime.fromisoformat(review["review_date_utc"].replace("Z", "+00:00"))
        except ValueError as exc:
            raise ValueError(f"{cid}: review_date_utc must be ISO-8601") from exc
        if not isinstance(review["evidence_refs"], list) or not review["evidence_refs"]:
            raise ValueError(f"{cid}: at least one evidence reference is required")
        identity = (private["target"], private["candidate_id"])
        if identity in existing_ids:
            raise ValueError(f"{cid}: candidate already has a label; adjudicate outside this importer")
        row = {
            "target": private["target"],
            "candidate_id": private["candidate_id"],
            "label": label,
            "spatial_group": private["spatial_group"],
            "evidence_ref": "; ".join(str(x) for x in review["evidence_refs"]),
            "reviewer": f"{review['reviewer_name']} ({review['reviewer_qualification']}; {review['reviewer_affiliation']})",
            "review_date_utc": review["review_date_utc"],
            "core_terrain_index": private["core_terrain_index"],
            "review_scope": review["criterion_version"] + ": " + review["rationale"],
            "reviewer_confidence_1_to_5": review["confidence_1_to_5"],
            "reviewer_independence_attested": True,
            "review_case_id": cid,
            "review_limitations": review.get("limitations", []),
        }
        labels.append(row)
        existing_ids.add(identity)
        added[label] += 1
    result = dict(existing)
    result["schema_version"] = "1.0.0"
    result["project"] = "ANALOG-X"
    result["labels"] = labels
    result["import_summary"] = added
    return result, added


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--packet", type=Path, default=PACKET)
    parser.add_argument("--key", type=Path, required=True)
    parser.add_argument("--labels", type=Path, default=LABELS)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    if not args.key.exists():
        raise SystemExit("Private case key not found; generate it locally with build_independent_review_pack.py --key-output PATH")
    packet = json.loads(args.packet.read_text(encoding="utf-8"))
    key = json.loads(args.key.read_text(encoding="utf-8"))
    existing = json.loads(args.labels.read_text(encoding="utf-8")) if args.labels.exists() else {
        "schema_version": "1.0.0", "project": "ANALOG-X", "label_policy": {}, "labels": []
    }
    result, counts = convert_responses(packet, key, existing)
    print(json.dumps({"dry_run": args.dry_run, "added": counts, "total_labels": len(result["labels"])}))
    if not args.dry_run:
        args.labels.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()

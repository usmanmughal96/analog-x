#!/usr/bin/env python3
"""Import expert responses using the uncommitted private review-case key."""
from __future__ import annotations

import argparse
import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "data/validation/independent_analog_review_packet.json"
LABELS = ROOT / "data/validation/independent_analog_labels.json"
BINARY = {"positive", "negative"}
NON_BINARY = {"inconclusive", "insufficient_evidence"}
CRITERION_VERSION = "terrain_morphology_transfer_v1"


def valid_utc_datetime(value: Any) -> bool:
    """Require an explicit UTC offset; date-only and local-time values are invalid."""
    if not isinstance(value, str) or not value.strip():
        return False
    text = value.strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError:
        return False
    return (
        parsed.tzinfo is not None
        and parsed.utcoffset() == timezone.utc.utcoffset(parsed)
    )


def _required_text(review: dict[str, Any], name: str, case_id: str) -> str:
    value = review.get(name)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{case_id}: {name} must be a non-empty string")
    return value.strip()


def convert_responses(
    packet: dict[str, Any],
    key: dict[str, Any],
    existing: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, int]]:
    if packet.get("schema_version") != "1.0.0":
        raise ValueError("Unsupported reviewer packet schema_version")
    if packet.get("review_version") != key.get("review_version"):
        raise ValueError("Review packet and private key versions do not match")
    if packet.get("review_version") != CRITERION_VERSION:
        raise ValueError("Reviewer packet criterion version is not the supported criterion")
    if not isinstance(packet.get("cases"), list):
        raise ValueError("Reviewer packet must contain a cases array")
    private_cases = key.get("cases", {})
    if not isinstance(private_cases, dict):
        raise ValueError("Private case key must contain a cases object")

    labels = list(existing.get("labels", []))
    existing_ids = {(row.get("target"), row.get("candidate_id")) for row in labels}
    added = {"positive": 0, "negative": 0, "inconclusive_or_blank": 0}

    for case in packet["cases"]:
        review = case.get("independent_review") or {}
        if not isinstance(review, dict):
            raise ValueError(f"{case.get('review_case_id', 'unknown case')}: independent_review must be an object")
        label = review.get("label")
        if label in (None, "") or label in NON_BINARY:
            added["inconclusive_or_blank"] += 1
            continue
        if label not in BINARY:
            raise ValueError(f"{case.get('review_case_id', 'unknown case')}: unsupported review label {label!r}")

        cid = case.get("review_case_id")
        if not isinstance(cid, str) or not cid:
            raise ValueError("Binary assessment is missing review_case_id")
        private = private_cases.get(cid)
        if not isinstance(private, dict):
            raise ValueError(f"Unknown review_case_id: {cid}")
        if private.get("target") != case.get("target"):
            raise ValueError(f"{cid}: target does not match private key")

        criterion = _required_text(review, "criterion_version", cid)
        if criterion != CRITERION_VERSION:
            raise ValueError(f"{cid}: criterion_version must be {CRITERION_VERSION}")
        reviewer_name = _required_text(review, "reviewer_name", cid)
        reviewer_affiliation = _required_text(review, "reviewer_affiliation", cid)
        reviewer_qualification = _required_text(review, "reviewer_qualification", cid)
        rationale = _required_text(review, "rationale", cid)

        if review.get("independent_of_analogx_score") is not True:
            raise ValueError(f"{cid}: reviewer must attest independence from ANALOG-X score")

        confidence = review.get("confidence_1_to_5")
        if isinstance(confidence, bool) or not isinstance(confidence, int) or not 1 <= confidence <= 5:
            raise ValueError(f"{cid}: confidence_1_to_5 must be an integer from 1 to 5")

        review_date = review.get("review_date_utc")
        if not valid_utc_datetime(review_date):
            raise ValueError(f"{cid}: review_date_utc must be an explicit ISO-8601 UTC date-time")

        evidence_refs = review.get("evidence_refs")
        if (
            not isinstance(evidence_refs, list)
            or not evidence_refs
            or any(not isinstance(ref, str) or not ref.strip() for ref in evidence_refs)
        ):
            raise ValueError(f"{cid}: evidence_refs must be a non-empty list of non-empty strings")
        limitations = review.get("limitations", [])
        if not isinstance(limitations, list) or any(not isinstance(item, str) for item in limitations):
            raise ValueError(f"{cid}: limitations must be a list of strings")

        target = private.get("target")
        candidate_id = private.get("candidate_id")
        spatial_group = private.get("spatial_group")
        score = private.get("core_terrain_index")
        if target not in {"moon", "mars"}:
            raise ValueError(f"{cid}: private key target must be moon or mars")
        if not isinstance(candidate_id, str) or not candidate_id:
            raise ValueError(f"{cid}: private key candidate_id is missing")
        if not isinstance(spatial_group, str) or not spatial_group:
            raise ValueError(f"{cid}: private key spatial_group is missing")
        if (
            isinstance(score, bool)
            or not isinstance(score, (int, float))
            or not math.isfinite(float(score))
            or not 0 <= float(score) <= 100
        ):
            raise ValueError(f"{cid}: private key core_terrain_index must be finite numeric data in [0, 100]")

        identity = (target, candidate_id)
        if identity in existing_ids:
            raise ValueError(f"{cid}: candidate already has a label; adjudicate outside this importer")

        row = {
            "target": target,
            "candidate_id": candidate_id,
            "label": label,
            "criterion_version": criterion,
            "spatial_group": spatial_group,
            "evidence_ref": "; ".join(ref.strip() for ref in evidence_refs),
            "reviewer": f"{reviewer_name} ({reviewer_qualification}; {reviewer_affiliation})",
            "review_date_utc": review_date.strip(),
            "core_terrain_index": float(score),
            "review_scope": criterion + ": " + rationale,
            "reviewer_confidence_1_to_5": confidence,
            "reviewer_independence_attested": True,
            "review_case_id": cid,
            "review_limitations": limitations,
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

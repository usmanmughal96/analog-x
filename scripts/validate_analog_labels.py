#!/usr/bin/env python3
"""Evaluate independently reviewed analog labels with deterministic spatial-group holdout.

Expected input: data/validation/independent_analog_labels.json
Each row must include target (moon|mars), candidate_id, label (positive|negative),
spatial_group, evidence_ref, reviewer, review_date_utc and core_terrain_index.
No labels are synthesized. If the held-out spatial groups do not contain both
classes, the report remains awaiting_labels rather than emitting an AUC.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "data/validation/independent_analog_labels.json"
OUTPUT = ROOT / "data/validation/independent_analog_label_validation.json"


def auc(labels: list[int], scores: list[float]) -> float:
    positives = [score for label, score in zip(labels, scores) if label == 1]
    negatives = [score for label, score in zip(labels, scores) if label == 0]
    if not positives or not negatives:
        raise ValueError("AUC requires positive and negative examples in the evaluation split")
    wins = sum(1.0 if p > n else 0.5 if p == n else 0.0 for p in positives for n in negatives)
    return wins / (len(positives) * len(negatives))


def group_is_held_out(group: str) -> bool:
    """Stable 20% group holdout; neighbouring records in one group stay together."""
    import hashlib
    return int(hashlib.sha256(group.encode("utf-8")).hexdigest()[:8], 16) % 5 == 0


def validate_rows(rows: list[dict[str, Any]]) -> None:
    seen: set[tuple[str, str]] = set()
    for index, row in enumerate(rows):
        prefix = f"labels[{index}]"
        target = row.get("target")
        if target not in {"moon", "mars"}:
            raise ValueError(f"{prefix}: target must be moon or mars")
        if row.get("label") not in {"positive", "negative"}:
            raise ValueError(f"{prefix}: label must be positive or negative")
        for key in ("candidate_id", "spatial_group", "evidence_ref", "reviewer", "review_date_utc"):
            if not isinstance(row.get(key), str) or not row[key].strip():
                raise ValueError(f"{prefix}: {key} is required")
        score = row.get("core_terrain_index")
        if isinstance(score, bool) or not isinstance(score, (int, float)) or not 0 <= score <= 100:
            raise ValueError(f"{prefix}: core_terrain_index must be numeric in [0, 100]")
        identity = (target, row["candidate_id"])
        if identity in seen:
            raise ValueError(f"{prefix}: duplicate target/candidate_id")
        seen.add(identity)


def build_report(rows: list[dict[str, Any]]) -> dict[str, Any]:
    validate_rows(rows)
    targets: dict[str, Any] = {}
    for target in ("moon", "mars"):
        subset = [row for row in rows if row["target"] == target]
        groups = sorted({row["spatial_group"] for row in subset})
        test_groups = {group for group in groups if group_is_held_out(group)}
        test = [row for row in subset if row["spatial_group"] in test_groups]
        train = [row for row in subset if row["spatial_group"] not in test_groups]
        positives = sum(row["label"] == "positive" for row in test)
        negatives = sum(row["label"] == "negative" for row in test)
        status = "awaiting_spatially_blocked_labels"
        auc_value = None
        if len(groups) >= 5 and positives and negatives:
            auc_value = round(auc(
                [1 if row["label"] == "positive" else 0 for row in test],
                [float(row["core_terrain_index"]) for row in test]
            ), 4)
            status = "spatial_group_holdout_diagnostic"
        targets[target] = {
            "status": status,
            "n_total": len(subset),
            "n_spatial_groups": len(groups),
            "n_train": len(train),
            "n_test": len(test),
            "n_test_positive": positives,
            "n_test_negative": negatives,
            "held_out_groups": sorted(test_groups),
            "roc_auc": auc_value,
            "interpretation": "Exploratory spatial-group holdout on reviewer-labelled candidates. It is not a universal accuracy estimate; assess label quality, group design and uncertainty before drawing conclusions."
        }
    overall = "spatial_group_holdout_diagnostic" if any(
        item["roc_auc"] is not None for item in targets.values()
    ) else "awaiting_spatially_blocked_labels"
    return {
        "schema_version": "1.0.0",
        "generated_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "status": overall,
        "method": {
            "score": "core_terrain_index",
            "holdout": "deterministic 20% holdout by spatial_group; all records from one group remain in one split",
            "unit_of_independence": "spatial_group, not individual candidate window",
            "uncertainty": "No confidence interval is reported in this first diagnostic. A predeclared group bootstrap and external expert review are required before any accuracy claim."
        },
        "targets": targets,
        "limitations": [
            "Labels must be independently sourced and reviewed; the script does not create or infer labels.",
            "A held-out split must contain both positive and negative labels; otherwise AUC is withheld.",
            "Spatial groups must be defined before looking at scores and should separate neighbouring or geologically related candidates.",
            "This evaluates terrain-screening scores against supplied labels only; it does not prove planetary process equivalence or field truth."
        ]
    }


def main() -> None:
    if not INPUT.exists():
        report = {
            "schema_version": "1.0.0",
            "generated_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
            "status": "awaiting_reference_labels",
            "targets": {},
            "note": "No independently sourced and reviewed label file exists. No AUC, accuracy or analog validity is inferred."
        }
    else:
        payload = json.loads(INPUT.read_text(encoding="utf-8"))
        report = build_report(payload.get("labels", []))
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"Label validation: {report['status']}")


if __name__ == "__main__":
    main()

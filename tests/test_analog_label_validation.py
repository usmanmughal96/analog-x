import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import validate_analog_labels as labels


def make_label(target, candidate_id, label, spatial_group, score, evidence_ref="doi:example"):
    return {
        "target": target,
        "candidate_id": candidate_id,
        "label": label,
        "spatial_group": spatial_group,
        "evidence_ref": evidence_ref,
        "reviewer": "Independent reviewer (planetary geomorphology; External University)",
        "review_date_utc": "2026-11-22T12:00:00Z",
        "criterion_version": "terrain_morphology_transfer_v1",
        "review_scope": "terrain_morphology_transfer_v1: reviewed the stated morphology criterion",
        "reviewer_confidence_1_to_5": 4,
        "reviewer_independence_attested": True,
        "core_terrain_index": score,
    }


class AnalogLabelValidationTests(unittest.TestCase):
    def test_auc_orders_positive_scores(self):
        self.assertEqual(labels.auc([1, 1, 0, 0], [0.9, 0.8, 0.2, 0.1]), 1.0)

    def test_auc_counts_ties_as_half(self):
        self.assertEqual(labels.auc([1, 0], [0.5, 0.5]), 0.5)

    def test_missing_or_bad_evidence_is_rejected(self):
        row = make_label("moon", "a", "positive", "g1", 80, evidence_ref="")
        with self.assertRaisesRegex(ValueError, "evidence_ref is required"):
            labels.validate_rows([row])

    def test_duplicate_candidate_per_target_is_rejected(self):
        row = make_label("mars", "a", "negative", "g1", 20)
        with self.assertRaisesRegex(ValueError, "duplicate target/candidate_id"):
            labels.validate_rows([row, dict(row)])

    def test_spatial_group_assignment_is_deterministic(self):
        self.assertEqual(labels.group_is_held_out("region-alpha"), labels.group_is_held_out("region-alpha"))

    def test_nonfinite_score_rejected(self):
        row = make_label("moon", "a", "positive", "g1", float("nan"))
        with self.assertRaisesRegex(ValueError, "finite numeric"):
            labels.validate_rows([row])

    def test_current_candidate_score_must_match_release(self):
        row = make_label("moon", "a", "positive", "g1", 81)
        with self.assertRaisesRegex(ValueError, "does not match"):
            labels.validate_rows([row], {("moon", "a"): 80.0})

    def test_date_only_or_non_utc_review_timestamps_are_rejected(self):
        base = make_label("moon", "a", "positive", "g1", 80)
        for invalid in ("2026-11-22", "2026-11-22T12:00:00", "2026-11-22T17:00:00+05:00"):
            row = dict(base, review_date_utc=invalid)
            with self.subTest(value=invalid):
                with self.assertRaisesRegex(ValueError, "explicit ISO-8601 UTC"):
                    labels.validate_rows([row])

    def test_missing_reviewer_independence_attestation_is_rejected(self):
        row = make_label("moon", "a", "positive", "g1", 80)
        row["reviewer_independence_attested"] = False
        with self.assertRaisesRegex(ValueError, "reviewer_independence_attested"):
            labels.validate_rows([row])

    def test_boolean_confidence_is_rejected(self):
        row = make_label("moon", "a", "positive", "g1", 80)
        row["reviewer_confidence_1_to_5"] = True
        with self.assertRaisesRegex(ValueError, "reviewer_confidence_1_to_5"):
            labels.validate_rows([row])

    def test_auc_is_withheld_when_only_one_held_out_spatial_group_exists(self):
        rows = []
        for index in range(5):
            group = f"region-{index:03d}"
            rows.extend([
                make_label("moon", f"{group}-positive", "positive", group, 80, "doi:positive"),
                make_label("moon", f"{group}-negative", "negative", group, 20, "doi:negative"),
            ])
        report = labels.build_report(rows)
        moon = report["targets"]["moon"]
        self.assertEqual(moon["n_spatial_groups"], 5)
        self.assertEqual(moon["n_test_spatial_groups"], 1)
        self.assertFalse(moon["evaluation_gate_passed"])
        self.assertIsNone(moon["roc_auc"])
        self.assertEqual(moon["status"], "awaiting_spatially_blocked_labels")

    def test_auc_requires_multiple_held_out_groups_for_both_classes(self):
        rows = []
        for index in range(20):
            group = f"region-{index:03d}"
            rows.extend([
                make_label("moon", f"{group}-positive", "positive", group, 80, "doi:positive"),
                make_label("moon", f"{group}-negative", "negative", group, 20, "doi:negative"),
            ])
        report = labels.build_report(rows)
        moon = report["targets"]["moon"]
        self.assertEqual(moon["n_test_spatial_groups"], 5)
        self.assertEqual(moon["n_test_positive_spatial_groups"], 5)
        self.assertEqual(moon["n_test_negative_spatial_groups"], 5)
        self.assertTrue(moon["evaluation_gate_passed"])
        self.assertEqual(moon["roc_auc"], 1.0)
        self.assertEqual(moon["status"], "spatial_group_holdout_diagnostic")

    def test_auc_is_withheld_when_one_class_occurs_in_only_one_held_out_group(self):
        rows = []
        held_groups = [
            f"region-{index:03d}"
            for index in range(20)
            if labels.group_is_held_out(f"region-{index:03d}")
        ]
        self.assertEqual(len(held_groups), 5)
        for index in range(20):
            group = f"region-{index:03d}"
            rows.append(make_label("moon", f"{group}-negative", "negative", group, 20, "doi:negative"))
            if group == held_groups[0]:
                rows.append(make_label("moon", f"{group}-positive", "positive", group, 80, "doi:positive"))
        report = labels.build_report(rows)
        moon = report["targets"]["moon"]
        self.assertEqual(moon["n_test_spatial_groups"], 5)
        self.assertEqual(moon["n_test_positive_spatial_groups"], 1)
        self.assertEqual(moon["n_test_negative_spatial_groups"], 5)
        self.assertFalse(moon["evaluation_gate_passed"])
        self.assertIsNone(moon["roc_auc"])


if __name__ == "__main__":
    unittest.main()

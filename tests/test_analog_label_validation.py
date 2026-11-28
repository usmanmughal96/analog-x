import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import validate_analog_labels as labels


class AnalogLabelValidationTests(unittest.TestCase):
    def test_auc_orders_positive_scores(self):
        self.assertEqual(labels.auc([1, 1, 0, 0], [0.9, 0.8, 0.2, 0.1]), 1.0)

    def test_auc_counts_ties_as_half(self):
        self.assertEqual(labels.auc([1, 0], [0.5, 0.5]), 0.5)

    def test_missing_or_bad_evidence_is_rejected(self):
        row = {
            "target": "moon", "candidate_id": "a", "label": "positive",
            "spatial_group": "g1", "evidence_ref": "", "reviewer": "reviewer",
            "review_date_utc": "2026-11-22T12:00:00Z", "core_terrain_index": 80
        }
        with self.assertRaises(ValueError):
            labels.validate_rows([row])

    def test_duplicate_candidate_per_target_is_rejected(self):
        row = {
            "target": "mars", "candidate_id": "a", "label": "negative",
            "spatial_group": "g1", "evidence_ref": "doi:example", "reviewer": "reviewer",
            "review_date_utc": "2026-11-22T12:00:00Z", "core_terrain_index": 20
        }
        with self.assertRaises(ValueError):
            labels.validate_rows([row, dict(row)])

    def test_spatial_group_assignment_is_deterministic(self):
        self.assertEqual(labels.group_is_held_out("region-alpha"), labels.group_is_held_out("region-alpha"))

    def test_nonfinite_score_rejected(self):
        row = {
            "target":"moon","candidate_id":"a","label":"positive","spatial_group":"g1",
            "evidence_ref":"doi:example","reviewer":"independent reviewer",
            "review_date_utc":"2026-11-22T12:00:00Z","core_terrain_index":float("nan")
        }
        with self.assertRaisesRegex(ValueError, "finite numeric"):
            labels.validate_rows([row])

    def test_current_candidate_score_must_match_release(self):
        row = {
            "target":"moon","candidate_id":"a","label":"positive","spatial_group":"g1",
            "evidence_ref":"doi:example","reviewer":"independent reviewer",
            "review_date_utc":"2026-11-22T12:00:00Z","core_terrain_index":81
        }
        with self.assertRaisesRegex(ValueError, "does not match"):
            labels.validate_rows([row], {("moon","a"):80.0})


    def test_date_only_or_non_utc_review_timestamps_are_rejected(self):
        base = {
            "target": "moon", "candidate_id": "a", "label": "positive",
            "spatial_group": "g1", "evidence_ref": "doi:example",
            "reviewer": "independent reviewer",
            "core_terrain_index": 80
        }
        for invalid in ("2026-11-22", "2026-11-22T12:00:00", "2026-11-22T17:00:00+05:00"):
            row = dict(base, review_date_utc=invalid)
            with self.subTest(value=invalid):
                with self.assertRaisesRegex(ValueError, "explicit ISO-8601 UTC"):
                    labels.validate_rows([row])

    def test_auc_is_withheld_when_only_one_held_out_spatial_group_exists(self):
        rows = []
        for index in range(5):
            group = f"region-{index:03d}"
            rows.extend([
                {
                    "target": "moon", "candidate_id": f"{group}-positive",
                    "label": "positive", "spatial_group": group,
                    "evidence_ref": "doi:positive", "reviewer": "reviewer",
                    "review_date_utc": "2026-11-22T12:00:00Z",
                    "core_terrain_index": 80,
                },
                {
                    "target": "moon", "candidate_id": f"{group}-negative",
                    "label": "negative", "spatial_group": group,
                    "evidence_ref": "doi:negative", "reviewer": "reviewer",
                    "review_date_utc": "2026-11-22T12:00:00Z",
                    "core_terrain_index": 20,
                },
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
                {
                    "target": "moon", "candidate_id": f"{group}-positive",
                    "label": "positive", "spatial_group": group,
                    "evidence_ref": "doi:positive", "reviewer": "reviewer",
                    "review_date_utc": "2026-11-22T12:00:00Z",
                    "core_terrain_index": 80,
                },
                {
                    "target": "moon", "candidate_id": f"{group}-negative",
                    "label": "negative", "spatial_group": group,
                    "evidence_ref": "doi:negative", "reviewer": "reviewer",
                    "review_date_utc": "2026-11-22T12:00:00Z",
                    "core_terrain_index": 20,
                },
            ])
        report = labels.build_report(rows)
        moon = report["targets"]["moon"]
        self.assertEqual(moon["n_test_spatial_groups"], 5)
        self.assertEqual(moon["n_test_positive_spatial_groups"], 5)
        self.assertEqual(moon["n_test_negative_spatial_groups"], 5)
        self.assertTrue(moon["evaluation_gate_passed"])
        self.assertEqual(moon["roc_auc"], 1.0)
        self.assertEqual(moon["status"], "spatial_group_holdout_diagnostic")


if __name__ == "__main__":
    unittest.main()

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
            "review_date_utc": "2026-11-22", "core_terrain_index": 80
        }
        with self.assertRaises(ValueError):
            labels.validate_rows([row])

    def test_duplicate_candidate_per_target_is_rejected(self):
        row = {
            "target": "mars", "candidate_id": "a", "label": "negative",
            "spatial_group": "g1", "evidence_ref": "doi:example", "reviewer": "reviewer",
            "review_date_utc": "2026-11-22", "core_terrain_index": 20
        }
        with self.assertRaises(ValueError):
            labels.validate_rows([row, dict(row)])

    def test_spatial_group_assignment_is_deterministic(self):
        self.assertEqual(labels.group_is_held_out("region-alpha"), labels.group_is_held_out("region-alpha"))

    def test_nonfinite_score_rejected(self):
        row = {
            "target":"moon","candidate_id":"a","label":"positive","spatial_group":"g1",
            "evidence_ref":"doi:example","reviewer":"independent reviewer",
            "review_date_utc":"2026-11-22","core_terrain_index":float("nan")
        }
        with self.assertRaisesRegex(ValueError, "finite numeric"):
            labels.validate_rows([row])

    def test_current_candidate_score_must_match_release(self):
        row = {
            "target":"moon","candidate_id":"a","label":"positive","spatial_group":"g1",
            "evidence_ref":"doi:example","reviewer":"independent reviewer",
            "review_date_utc":"2026-11-22","core_terrain_index":81
        }
        with self.assertRaisesRegex(ValueError, "does not match"):
            labels.validate_rows([row], {("moon","a"):80.0})

if __name__ == "__main__":
    unittest.main()

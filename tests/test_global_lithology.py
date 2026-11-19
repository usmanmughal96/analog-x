import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import enrich_global_lithology as glim


class GlobalLithologyTests(unittest.TestCase):
    def test_parse_features_preserves_codes_and_labels(self):
        rows = glim.parse_features({"features": [{"attributes": {
            "OBJECTID": 7, "LithoL2": "V2", "Lithology": "Intermediate volcanics",
            "Litho16": "V", "ORIG_FID": 11
        }}]})
        self.assertEqual(rows[0]["lithology_level_2_code"], "V2")
        self.assertEqual(rows[0]["lithology_description"], "Intermediate volcanics")
        self.assertEqual(rows[0]["lithology_level_1_code"], "V")
        self.assertEqual(rows[0]["feature_id"], 7)

    def test_empty_feature_response_is_not_assigned_a_class(self):
        self.assertEqual(glim.parse_features({"features": []}), [])

    def test_arcgis_error_is_raised(self):
        with self.assertRaises(RuntimeError):
            glim.parse_features({"error": {"message": "bad geometry"}})

    def test_shortlist_is_deduplicated_and_retains_target_membership(self):
        data = {"targets": {
            "moon": {"candidate_windows": [{"id": "a", "latitude": 12.0, "longitude": 22.0, "core_terrain_index": 90.0}]},
            "mars": {"candidate_windows": [
                {"id": "a", "latitude": 12.0, "longitude": 22.0, "core_terrain_index": 80.0},
                {"id": "b", "latitude": -20.0, "longitude": 40.0, "core_terrain_index": 75.0}
            ]}
        }}
        rows = glim.shortlist_points(data, limit=100)
        self.assertEqual(len(rows), 2)
        first = next(x for x in rows if x["candidate_id"] == "a")
        self.assertEqual(set(first["target_membership"]), {"moon", "mars"})
        self.assertEqual(first["core_terrain_index_by_target"], {"moon": 90.0, "mars": 80.0})


if __name__ == "__main__":
    unittest.main()

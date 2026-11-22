import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import build_quantitative_validation as validation


class RankingReleaseGateTests(unittest.TestCase):
    def _dataset(self, complete=True):
        rows = [
            {"id": "a", "core_terrain_index": 90, "secondary_rank_within_primary_shortlist": 2, "shortlist_rank": 1},
            {"id": "b", "core_terrain_index": 80, "secondary_rank_within_primary_shortlist": 1, "shortlist_rank": 2},
        ]
        return {
            "schema_version": "1.1.0",
            "status": "complete" if complete else "partial",
            "ranking_contract": {"ranking_ready": complete, "primary_feature_family": "core", "consensus_score": False},
            "completion_contract": {
                "complete_global_land_inventory_scan": complete,
                "shards_received": 24, "shards_expected": 24,
                "tiles_assigned_to_shards": 24, "global_land_tile_inventory_total": 24,
                "tiles_processed": 24 if complete else 23, "tile_failures": 0 if complete else 1,
            },
            "targets": {"moon": {"candidate_windows": rows}, "mars": {"candidate_windows": rows}},
        }

    def test_complete_core_only_dataset_passes(self):
        self.assertTrue(validation.ranking_integrity(self._dataset(True))["ranking_ready"])

    def test_partial_inventory_cannot_be_ranking_ready(self):
        self.assertFalse(validation.ranking_integrity(self._dataset(False))["ranking_ready"])

    def test_wrong_schema_cannot_be_ranking_ready(self):
        dataset = self._dataset(True)
        dataset["schema_version"] = "1.0.0"
        self.assertFalse(validation.ranking_integrity(dataset)["ranking_ready"])

    def test_wrong_primary_order_fails(self):
        dataset = self._dataset(True)
        rows = dataset["targets"]["moon"]["candidate_windows"]
        rows.reverse()
        self.assertFalse(validation.ranking_integrity(dataset)["ranking_ready"])


if __name__ == "__main__":
    unittest.main()

import math
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import build_global_discovery as gd


class GlobalDiscoveryTests(unittest.TestCase):
    def test_parse_northern_eastern_tile(self):
        tile = gd.parse_tile_id("Copernicus_DSM_COG_30_N00_00_E000_00_DEM/")
        self.assertEqual(tile["south"], 0)
        self.assertEqual(tile["west"], 0)
        self.assertEqual(tile["north"], 1)
        self.assertEqual(tile["east"], 1)

    def test_parse_southern_western_tile(self):
        tile = gd.parse_tile_id("Copernicus_DSM_COG_30_S90_00_W178_00_DEM/")
        self.assertEqual(tile["south"], -90)
        self.assertEqual(tile["west"], -178)

    def test_reject_non_tile_line(self):
        self.assertIsNone(gd.parse_tile_id("readme.html"))

    def test_partition_is_exhaustive_and_bounded(self):
        ids = {gd.partition_for_lon(lon) for lon in range(-180, 180)}
        self.assertEqual(ids, set(range(gd.SHARDS)))
        self.assertEqual(gd.partition_for_lon(-180), 0)
        self.assertEqual(gd.partition_for_lon(179), gd.SHARDS - 1)

    def test_projection_uses_polar_crs_at_high_latitudes(self):
        self.assertEqual(gd.local_metric_crs(86, 20), "EPSG:3413")
        self.assertEqual(gd.local_metric_crs(-85, 20), "EPSG:3031")
        self.assertTrue(gd.local_metric_crs(30, 70).startswith("EPSG:326"))

    def test_planar_surface_metrics_are_finite(self):
        rows, cols = 6, 6
        rr, cc = __import__("numpy").mgrid[0:rows, 0:cols]
        z = (cc * gd.CELL_M * 0.1 + rr * gd.CELL_M * 0.05).astype("float32")
        slope, relief = gd.derive_metric_arrays(z)
        result = gd.window_metrics(z, slope, relief, 0, 0)
        self.assertIsNotNone(result)
        self.assertTrue(math.isfinite(result["median_slope_deg"]))
        expected = math.degrees(math.atan(math.hypot(0.1, 0.05)))
        self.assertAlmostEqual(result["median_slope_deg"], expected, places=2)
        self.assertGreaterEqual(result["valid_cell_pct"], 70)

    def test_diverse_selector_limits_tile_concentration(self):
        rows = []
        for i in range(6):
            rows.append({"id": f"a{i}", "tile_id": "tile-a", "core_terrain_index": 99-i, "secondary_diagnostic_index": i})
        rows.append({"id": "b", "tile_id": "tile-b", "core_terrain_index": 80, "secondary_diagnostic_index": 90})
        selected = gd.select_diverse(rows, limit=5, max_per_tile=2)
        self.assertEqual(sum(x["tile_id"] == "tile-a" for x in selected), 2)
        self.assertIn("tile-b", [x["tile_id"] for x in selected])

    def test_selector_uses_core_index_not_secondary_or_legacy_consensus(self):
        rows = [
            {"id": "core-best", "tile_id": "a", "core_terrain_index": 95, "secondary_diagnostic_index": 10, "consensus_index": 20},
            {"id": "secondary-best", "tile_id": "b", "core_terrain_index": 70, "secondary_diagnostic_index": 99, "consensus_index": 99},
        ]
        selected = gd.select_diverse(rows, limit=2, max_per_tile=4)
        self.assertEqual(selected[0]["id"], "core-best")
        self.assertEqual(selected[1]["id"], "secondary-best")


class GlobalMergeReleaseTests(unittest.TestCase):
    def _shard(self, shard_id, tile_id):
        return {
            "shard": shard_id, "shard_count": 24, "tile_inventory_total": 24,
            "tiles_assigned": 1, "tiles_processed": 1, "tiles_without_valid_windows": 0, "tile_failures": [],
            "candidate_windows_evaluated": 2, "is_smoke_test": False,
            "target_reference_profiles": {"moon": {"name": "Moon test", "profile": {}, "feature_families": {"core": ["a"], "secondary": ["b"]}}, "mars": {"name": "Mars test", "profile": {}, "feature_families": {"core": ["a"], "secondary": ["b"]}}, "earth_iqr": {}, "feature_families": {"core": ["a"], "secondary": ["b"]}},
            "targets": {
                target: {"candidate_windows": [{
                    "id": f"{target}-{shard_id}", "tile_id": tile_id,
                    "latitude": 0.0, "longitude": float(shard_id),
                    "core_terrain_index": float(100-shard_id),
                    "secondary_diagnostic_index": float(shard_id),
                }]} for target in ("moon", "mars")
            }
        }

    def test_merge_rejects_missing_shards(self):
        import merge_global_discovery as merge
        with self.assertRaises(ValueError):
            merge.load_shards(Path("/definitely/not/a/real/shard/directory"))

    def test_core_only_selector_and_secondary_rank(self):
        import merge_global_discovery as merge
        rows = [
            {"id": "core", "tile_id": "a", "core_terrain_index": 90, "secondary_diagnostic_index": 10},
            {"id": "secondary", "tile_id": "b", "core_terrain_index": 80, "secondary_diagnostic_index": 99},
        ]
        selected = merge.select(rows, limit=2, max_per_tile=2)
        self.assertEqual([x["id"] for x in selected], ["core", "secondary"])
        self.assertEqual(selected[0]["shortlist_rank"], 1)
        self.assertEqual(selected[0]["secondary_rank_within_primary_shortlist"], 2)

    def test_candidate_validation_rejects_duplicate_ids(self):
        import merge_global_discovery as merge
        row = {"id": "same", "tile_id": "a", "core_terrain_index": 90, "secondary_diagnostic_index": 10, "latitude": 0, "longitude": 0}
        with self.assertRaises(ValueError):
            merge.validate_candidate_rows([row, dict(row)], "moon")

    def test_candidate_validation_rejects_nan(self):
        import merge_global_discovery as merge
        row = {"id": "bad", "tile_id": "a", "core_terrain_index": float("nan"), "secondary_diagnostic_index": 10, "latitude": 0, "longitude": 0}
        with self.assertRaises(ValueError):
            merge.validate_candidate_rows([row], "mars")

    def test_merge_requires_complete_assignment_accounting(self):
        import merge_global_discovery as merge
        shards = {i: self._shard(i, f"tile-{i}") for i in range(24)}
        shards[0]["tiles_assigned"] = 2
        with self.assertRaises(ValueError):
            merge.build_release(shards)

    def test_complete_merge_emits_explicit_core_only_release_contract(self):
        import merge_global_discovery as merge
        shards = {i: self._shard(i, f"tile-{i}") for i in range(24)}
        release = merge.build_release(shards)
        self.assertEqual(release["schema_version"], "1.1.0")
        self.assertTrue(release["ranking_contract"]["ranking_ready"])
        self.assertEqual(release["ranking_contract"]["primary_feature_family"], "core")
        self.assertFalse(release["ranking_contract"]["consensus_score"])
        self.assertTrue(release["completion_contract"]["complete_global_land_inventory_scan"])
        for target in ("moon", "mars"):
            rows = release["targets"][target]["candidate_windows"]
            self.assertEqual(
                [row["shortlist_rank"] for row in rows],
                list(range(1, len(rows) + 1))
            )
            self.assertEqual(
                [row["id"] for row in rows],
                [row["id"] for row in sorted(rows, key=lambda row: (-row["core_terrain_index"], row["id"]))]
            )


if __name__ == "__main__":
    unittest.main()

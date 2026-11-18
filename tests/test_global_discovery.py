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
            rows.append({"id": f"a{i}", "tile_id": "tile-a", "consensus_index": 99-i, "metric_family_score_agreement": 90})
        rows.append({"id": "b", "tile_id": "tile-b", "consensus_index": 80, "metric_family_rank_concordance": 90})
        selected = gd.select_diverse(rows, limit=5, max_per_tile=2)
        self.assertEqual(sum(x["tile_id"] == "tile-a" for x in selected), 2)
        self.assertIn("tile-b", [x["tile_id"] for x in selected])


if __name__ == "__main__":
    unittest.main()

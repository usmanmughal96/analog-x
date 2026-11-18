import math
import unittest

from science.build_regional_window_scan import derive_windows, percentile


class RegionalWindowScanTests(unittest.TestCase):
    def test_percentile_uses_linear_interpolation(self):
        self.assertAlmostEqual(percentile([0.0, 10.0], 0.25), 2.5)
        self.assertAlmostEqual(percentile([1.0, 2.0, 3.0], 0.50), 2.0)

    def test_planar_grid_produces_expected_slope_and_relief(self):
        # A 0.1 rise/run east-facing plane on a 925 m square grid.
        grid = [
            [round(column * 92.5, 6) for column in range(8)]
            for _ in range(8)
        ]
        windows = derive_windows(
            {
                "values": grid,
                "pixel_size_m": {"x": 925.0, "y": 925.0},
            },
            site_id="synthetic",
            site={"name": "Synthetic test", "country": "Testland"},
        )
        self.assertEqual(len(windows), 9)
        expected_slope = math.degrees(math.atan(0.1))
        for window in windows:
            self.assertAlmostEqual(
                window["terrain"]["median_slope_deg"], expected_slope, places=5
            )
            self.assertAlmostEqual(
                window["terrain"]["p90_slope_deg"], expected_slope, places=5
            )
            self.assertAlmostEqual(
                window["terrain"]["p90_local_relief_m"], 185.0, places=5
            )
            self.assertEqual(window["valid_cell_percent"], 100.0)

    def test_invalid_grid_cells_are_not_imputed(self):
        grid = [[0.0 for _ in range(8)] for _ in range(8)]
        for row in range(8):
            for column in range(8):
                grid[row][column] = column * 92.5
        # Remove an entire column. Any retained windows must still pass the
        # explicit cell-count and valid-derivative thresholds.
        for row in range(8):
            grid[row][3] = None
        windows = derive_windows(
            {"values": grid, "pixel_size_m": {"x": 925.0, "y": 925.0}},
            site_id="masked",
            site={"name": "Masked test", "country": "Testland"},
        )
        self.assertTrue(all(window["valid_cell_percent"] >= 70.0 for window in windows))
        self.assertTrue(all(window["terrain"]["median_slope_deg"] is not None for window in windows))


if __name__ == "__main__":
    unittest.main()

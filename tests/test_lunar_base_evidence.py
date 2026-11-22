import sys
import unittest
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import process_lunar_base_evidence as lunar


class LunarBaseEvidenceRasterTests(unittest.TestCase):
    def test_integer_masked_raster_can_be_filled_with_nan(self):
        source = np.ma.array(
            np.array([[0, 25], [100, 255]], dtype=np.uint8),
            mask=np.array([[False, False], [False, True]]),
        )
        converted = lunar.masked_array_to_float(source)
        self.assertEqual(converted.dtype, np.float64)
        self.assertEqual(converted[0, 0], 0.0)
        self.assertTrue(np.isnan(converted[1, 1]))

    def test_illumination_summary_accepts_uint8_source_raster(self):
        source = np.ma.array(
            np.array([0, 20, 100, 255], dtype=np.uint8),
            mask=np.array([False, False, False, True]),
        )
        summary = lunar.summarize_illumination(
            "test", "https://example.test/wac.tif", source, {}, "https://example.test/wac.lbl"
        )
        self.assertEqual(summary["valid_pixel_count"], 3)
        self.assertEqual(summary["illumination_percent"]["median"], 20.0)


if __name__ == "__main__":
    unittest.main()

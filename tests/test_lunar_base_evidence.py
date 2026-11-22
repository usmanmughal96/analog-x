import sys
import unittest
from unittest.mock import patch
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


    def test_make_preview_writes_grayscale_browse_image(self):
        values = np.array(
            [[0.0, 10.0, 20.0], [30.0, 40.0, np.nan], [50.0, 60.0, 70.0]],
            dtype=np.float64,
        )
        from tempfile import TemporaryDirectory
        from PIL import Image
        with TemporaryDirectory() as directory:
            output = Path(directory) / "preview.png"
            with patch.object(lunar, "PREVIEW_PATH", output):
                lunar.make_preview(values)
            self.assertTrue(output.exists())
            with Image.open(output) as image:
                self.assertEqual(image.mode, "L")
                self.assertEqual(image.size, (3, 3))
                pixels = np.asarray(image)
                self.assertGreater(int(pixels[2, 1]), int(pixels[0, 1]))
                self.assertEqual(int(pixels[1, 2]), 0)

    def test_make_preview_rejects_insufficient_valid_cells(self):
        with self.assertRaises(RuntimeError):
            lunar.make_preview(np.array([[1.0, np.nan], [np.nan, 2.0]]))


if __name__ == "__main__":
    unittest.main()

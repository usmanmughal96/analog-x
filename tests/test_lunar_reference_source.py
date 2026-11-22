import json
import sys
import tempfile
import unittest

import numpy as np
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import build_lunar_south_pole_reference as source


class Lunar5mSourceValidationTests(unittest.TestCase):
    def write_file(self, directory, name, payload):
        path = Path(directory) / name
        path.write_bytes(payload)
        return path

    def test_accepts_classic_little_endian_tiff_signature(self):
        with tempfile.TemporaryDirectory() as directory:
            path = self.write_file(directory, "valid.tif", b"II*\x00" + b"data")
            self.assertEqual(source.validate_downloaded_tiff(path, expected_bytes=8, min_bytes=4), 8)

    def test_accepts_bigtiff_signature(self):
        with tempfile.TemporaryDirectory() as directory:
            path = self.write_file(directory, "valid.tif", b"II+\x00" + b"data")
            self.assertEqual(source.validate_downloaded_tiff(path, min_bytes=4), 8)

    def test_rejects_html_or_error_payload(self):
        with tempfile.TemporaryDirectory() as directory:
            path = self.write_file(directory, "bad.tif", b"<html>" + b"x" * 32)
            with self.assertRaisesRegex(RuntimeError, "not a TIFF"):
                source.validate_downloaded_tiff(path, min_bytes=4)

    def test_rejects_truncated_download(self):
        with tempfile.TemporaryDirectory() as directory:
            path = self.write_file(directory, "short.tif", b"II*\x00" + b"x" * 4)
            with self.assertRaisesRegex(RuntimeError, "suspiciously small"):
                source.validate_downloaded_tiff(path, min_bytes=32)

    def test_zero_return_count_does_not_invalidate_interpolated_elevation(self):
        elevation = np.array([[10.0, 11.0], [12.0, 13.0]])
        counts = np.array([[0.0, 2.0], [3.0, 0.0]])
        slope = np.array([[1.0, 1.5], [2.0, 2.5]])
        terrain, count_valid, positive = source.lola_support_masks(elevation, counts, slope)
        self.assertTrue(terrain.all())
        self.assertTrue(count_valid.all())
        self.assertEqual(int(positive.sum()), 2)

    def test_count_nodata_is_separate_from_dem_validity(self):
        elevation = np.array([[10.0, 11.0], [12.0, 13.0]])
        counts = np.array([[0.0, -9999.0], [3.0, 0.0]])
        slope = np.array([[1.0, 1.5], [2.0, 2.5]])
        terrain, count_valid, positive = source.lola_support_masks(
            elevation, counts, slope, nodata_counts=-9999.0
        )
        self.assertTrue(terrain.all())
        self.assertFalse(count_valid[0, 1])
        self.assertFalse(positive[0, 1])


    def test_json_safe_converts_non_finite_raster_metadata_to_null(self):
        payload = {
            "nodata": float("nan"),
            "positive_infinity": float("inf"),
            "negative_infinity": float("-inf"),
            "numpy_value": np.float32(np.nan),
            "nested": [1.25, None, {"finite": np.float64(2.5)}],
        }
        safe = source.json_safe(payload)
        self.assertIsNone(safe["nodata"])
        self.assertIsNone(safe["positive_infinity"])
        self.assertIsNone(safe["negative_infinity"])
        self.assertIsNone(safe["numpy_value"])
        self.assertEqual(safe["nested"], [1.25, None, {"finite": 2.5}])
        # The exact same strict encoder used by the build must accept the output.
        encoded = json.dumps(safe, allow_nan=False)
        self.assertIn('"nodata": null', encoded)

    def test_rejects_misaligned_lola_arrays(self):
        with self.assertRaisesRegex(ValueError, "share one grid"):
            source.lola_support_masks(np.ones((2, 2)), np.ones((2, 3)), np.ones((2, 2)))

    def test_rejects_content_length_mismatch(self):
        with tempfile.TemporaryDirectory() as directory:
            path = self.write_file(directory, "short.tif", b"II*\x00" + b"x" * 4)
            with self.assertRaisesRegex(RuntimeError, "Incomplete raster download"):
                source.validate_downloaded_tiff(path, expected_bytes=100, min_bytes=4)


    def test_uncertainty_mask_rejects_nodata_and_nonfinite(self):
        values = np.array([[0.2, 0.0], [np.nan, 0.5]], dtype=float)
        mask = source.valid_uncertainty_mask(values, nodata=0.0)
        self.assertTrue(mask[0, 0])
        self.assertFalse(mask[0, 1])
        self.assertFalse(mask[1, 0])
        self.assertTrue(mask[1, 1])

    def test_all_lola_uncertainty_products_must_share_grid(self):
        class Dataset:
            def __init__(self, width, height):
                self.width=width
                self.height=height
                self.crs="MOON_ME"
                self.transform=(5,0,0,0,-5,0)
        self.assertTrue(source.validate_lola_product_alignment({
            "dem":Dataset(10,10),"count":Dataset(10,10),
            "slope":Dataset(10,10),"zerr":Dataset(10,10),"serr":Dataset(10,10)
        }))
        with self.assertRaisesRegex(RuntimeError,"do not share identical grid geometry"):
            source.validate_lola_product_alignment({
                "dem":Dataset(10,10),"count":Dataset(10,10),
                "slope":Dataset(10,10),"zerr":Dataset(10,10),"serr":Dataset(9,10)
            })


if __name__ == "__main__":
    unittest.main()

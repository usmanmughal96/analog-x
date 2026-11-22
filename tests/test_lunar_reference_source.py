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

    def test_rejects_misaligned_lola_arrays(self):
        with self.assertRaisesRegex(ValueError, "share one grid"):
            source.lola_support_masks(np.ones((2, 2)), np.ones((2, 3)), np.ones((2, 2)))

    def test_rejects_content_length_mismatch(self):
        with tempfile.TemporaryDirectory() as directory:
            path = self.write_file(directory, "short.tif", b"II*\x00" + b"x" * 4)
            with self.assertRaisesRegex(RuntimeError, "Incomplete raster download"):
                source.validate_downloaded_tiff(path, expected_bytes=100, min_bytes=4)


if __name__ == "__main__":
    unittest.main()

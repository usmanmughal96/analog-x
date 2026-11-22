import sys
import tempfile
import unittest
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

    def test_rejects_content_length_mismatch(self):
        with tempfile.TemporaryDirectory() as directory:
            path = self.write_file(directory, "short.tif", b"II*\x00" + b"x" * 4)
            with self.assertRaisesRegex(RuntimeError, "Incomplete raster download"):
                source.validate_downloaded_tiff(path, expected_bytes=100, min_bytes=4)


if __name__ == "__main__":
    unittest.main()

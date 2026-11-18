import sys
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
import enrich_global_landcover as lc


class GlobalLandCoverTests(unittest.TestCase):
    def test_class_codes_are_explicit(self):
        self.assertEqual(lc.CLASSES[1],"water")
        self.assertEqual(lc.CLASSES[8],"bare_ground")
        self.assertEqual(lc.CLASSES[9],"snow_ice")
        self.assertEqual(lc.CLASSES[11],"rangeland")

    def test_bbox_is_wgs84_order(self):
        west,south,east,north=lc.candidate_bbox(28.5,62.6)
        self.assertLess(west,62.6)
        self.assertGreater(east,62.6)
        self.assertLess(south,28.5)
        self.assertGreater(north,28.5)
        self.assertTrue(-180<=west<east<=180)
        self.assertTrue(-90<=south<north<=90)

    def test_high_latitude_bbox_stays_bounded(self):
        west,south,east,north=lc.candidate_bbox(83.0,179.8)
        self.assertTrue(-180<=west<east<=180)
        self.assertTrue(-90<=south<north<=90)

    def test_landcover_cog_url_signing(self):
        token="?sig=abc"
        self.assertEqual(lc.sign_href("https://example.test/file.tif",token),"https://example.test/file.tif&sig=abc")
        self.assertEqual(lc.sign_href("https://example.test/file.tif?x=1",token),"https://example.test/file.tif?x=1&sig=abc")
        self.assertEqual(lc.sign_href("https://example.test/file.tif",""),"https://example.test/file.tif")

    def test_global_source_and_year_are_fixed(self):
        self.assertEqual(lc.COLLECTION,"io-lulc-annual-v02")
        self.assertIn("2023",lc.YEAR_START)
        self.assertIn("2024",lc.YEAR_END)


if __name__=="__main__":
    unittest.main()

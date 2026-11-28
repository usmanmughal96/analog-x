import unittest

from shapely.geometry import box

from scripts.process_lunar_psr_vectors import (
    SITE,
    analyze_psr_features,
    build_study_aoi,
    make_lunar_geographic_crs,
    parse_projection,
)


MOON_SOUTH_POLAR_WKT = """PROJCS["POLAR_STEREOGRAPHIC MOON",GEOGCS["GCS_MOON",DATUM["D_MOON",SPHEROID["Moon_polarRadius",1737400,0]],PRIMEM["Reference_Meridian",0],UNIT["degree",0.0174532925199433,AUTHORITY["EPSG","9122"]]],PROJECTION["Polar_Stereographic"],PARAMETER["latitude_of_origin",-90],PARAMETER["central_meridian",0],PARAMETER["false_easting",0],PARAMETER["false_northing",0],UNIT["metre",1],AXIS["Easting",NORTH],AXIS["Northing",NORTH]]"""


class LunarPsrIntersectionTests(unittest.TestCase):
    def setUp(self):
        from pyproj import CRS
        self.target_crs = CRS.from_wkt(MOON_SOUTH_POLAR_WKT)
        self.aoi, self.center, self.forward, self.inverse = build_study_aoi(self.target_crs)

    def test_projection_uses_lunar_reference_radius_and_polar_stereographic(self):
        parsed = parse_projection_from_wkt(MOON_SOUTH_POLAR_WKT)
        self.assertTrue(parsed.is_projected)
        self.assertAlmostEqual(parsed.ellipsoid.semi_major_metre, 1737400.0, places=3)
        self.assertIn("stereographic", parsed.coordinate_operation.method_name.lower())

    def test_aoi_is_exact_29_6_km_square_and_round_trips_site_coordinate(self):
        self.assertAlmostEqual(self.aoi.area / 1_000_000.0, 29.6 * 29.6, places=8)
        longitude, latitude = self.inverse.transform(*self.center)
        self.assertAlmostEqual(latitude, SITE["latitude_planetocentric_deg"], places=8)
        self.assertAlmostEqual(longitude % 360.0, SITE["longitude_east_deg"], places=8)

    def test_detects_psr_intersection_and_reports_clipped_geometry(self):
        cx, cy = self.center
        intersecting = box(cx + 1000, cy - 1000, cx + 4000, cy + 4000)
        features = [
            ({"PSR_ID": "inside-psr", "AREA": 18.0}, intersecting)
        ]
        result = analyze_psr_features(features, self.aoi, self.center, self.inverse)
        self.assertEqual(result["intersecting_polygon_count_within_source"], 1)
        self.assertEqual(result["positive_area_overlap_count_within_source"], 1)
        self.assertGreater(result["overlap_area_total_km2"], 0)
        row = result["intersecting_psrs"][0]
        self.assertEqual(row["psr_id"], "inside-psr")
        self.assertTrue(row["intersects_study_window"])
        self.assertIsNotNone(row["clipped_geometry_site_relative_km"])
        self.assertEqual(row["distance_from_aoi_boundary_km"], 0.0)

    def test_reports_nearest_nonintersecting_psr_and_excludes_distant_features(self):
        cx, cy = self.center
        outside = box(cx + 16_000, cy - 500, cx + 17_000, cy + 500)
        far = box(cx + 100_000, cy - 500, cx + 101_000, cy + 500)
        result = analyze_psr_features(
            [
                ({"PSR_ID": "near", "AREA": 2.0}, outside),
                ({"PSR_ID": "far", "AREA": 3.0}, far),
            ],
            self.aoi,
            self.center,
            self.inverse,
            nearby_radius_km=50,
        )
        self.assertEqual(result["intersecting_polygon_count_within_source"], 0)
        self.assertEqual(len(result["nearest_psrs_within_radius"]), 1)
        row = result["nearest_psrs_within_radius"][0]
        self.assertEqual(row["psr_id"], "near")
        self.assertFalse(row["intersects_study_window"])
        self.assertAlmostEqual(row["distance_from_aoi_boundary_km"], 1.2, places=6)
        self.assertAlmostEqual(result["nearest_boundary_distance_km"], 1.2, places=6)

    def test_empty_source_keeps_unknown_as_no_features_not_as_zero_distance(self):
        result = analyze_psr_features([], self.aoi, self.center, self.inverse)
        self.assertEqual(result["feature_count_in_source"], 0)
        self.assertEqual(result["intersecting_polygon_count_within_source"], 0)
        self.assertIsNone(result["nearest_boundary_distance_km"])
        self.assertEqual(result["nearest_psrs_within_radius"], [])


def parse_projection_from_wkt(wkt):
    from pyproj import CRS
    return CRS.from_wkt(wkt)


if __name__ == "__main__":
    unittest.main()

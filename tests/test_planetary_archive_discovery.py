import unittest
from unittest.mock import patch

from scripts.fetch_planetary_archive_discovery import (
    NILI,
    NILI_HIRISE_DTM_DISCOVERY_BBOX,
    KNOWN_NILI_HIRISE_DTM,
    ODE_TARGETS,
    _clean_iipt,
    _clean_product,
    _find_matching_iipt_sets,
    extract_iipt_sets,
    extract_products,
    unwrap_ode,
    xml_to_value,
    parse_pds_label_text,
    _core_aoi_intersection,
    inspect_known_hirise_dtm_label,
    inspect_hirise_dtm_product_label,
    inspect_hirise_dtm_products,
    build_hirise_dtm_img_url,
    build_known_dtm_reference,
)
import xml.etree.ElementTree as ET





class FakeRangeResponse:
    def __init__(self, body, status_code=206):
        self.body = body
        self.status_code = status_code
        self.url = "https://example.test/hiRISE-dtm.img"
        self.headers = {"Content-Range": f"bytes 0-{len(body)-1}/430063620"}
        self.closed = False

    def raise_for_status(self):
        if self.status_code >= 400:
            raise RuntimeError("HTTP error")

    def iter_content(self, chunk_size=32768):
        for offset in range(0, len(self.body), chunk_size):
            yield self.body[offset:offset + chunk_size]

    def close(self):
        self.closed = True


class PlanetaryArchiveDiscoveryTests(unittest.TestCase):
    def test_nili_patera_aoi_matches_existing_mola_window(self):
        west, south, east, north = NILI["bbox_wsen"]
        self.assertAlmostEqual(west, 66.7438569302, places=6)
        self.assertAlmostEqual(south, 8.6469409271, places=6)
        self.assertAlmostEqual(east, 67.2561430698, places=6)
        self.assertAlmostEqual(north, 9.1530590729, places=6)

    def test_nili_hirise_dtm_discovery_window_includes_published_center_without_changing_core_aoi(self):
        west, south, east, north = NILI_HIRISE_DTM_DISCOVERY_BBOX
        self.assertEqual(NILI["bbox_wsen"][2], 67.2561430698)
        self.assertGreater(east, 67.33)
        self.assertEqual([west, south, north], [
            NILI["bbox_wsen"][0], NILI["bbox_wsen"][1], NILI["bbox_wsen"][3]
        ])
        self.assertAlmostEqual(KNOWN_NILI_HIRISE_DTM["center_latitude_deg"], 8.781, places=3)
        self.assertAlmostEqual(KNOWN_NILI_HIRISE_DTM["center_longitude_east_deg"], 67.33, places=2)
        self.assertEqual(KNOWN_NILI_HIRISE_DTM["id"], "DTEEC_017762_1890_018039_1890_A01")
        self.assertEqual(KNOWN_NILI_HIRISE_DTM["stereo_pair"], ["ESP_017762_1890", "ESP_018039_1890"])
        self.assertEqual(KNOWN_NILI_HIRISE_DTM["core_mola_aoi_footprint_intersection"], "not_yet_verified_from_product_label")

    def test_hirise_dtm_query_uses_expanded_bbox_only_for_that_dataset(self):
        by_id = {row["id"]: row for row in ODE_TARGETS}
        self.assertEqual(by_id["mars_hirise_dtm_nili"]["spatial_bbox"], NILI_HIRISE_DTM_DISCOVERY_BBOX)
        self.assertNotIn("spatial_bbox", by_id["mars_mola_megdr_nili"])

    def test_archive_searches_are_exact_known_datasets(self):
        by_id = {row["id"]: row for row in ODE_TARGETS}
        self.assertEqual(by_id["mars_hirise_dtm_nili"]["dataset_id"], "MRO-M-HIRISE-5-DTM-V1.0")
        self.assertEqual(by_id["mars_hirise_dtm_nili"]["product_type_filter"], "DTM")
        self.assertEqual(by_id["mars_mola_megdr_nili"]["dataset_id"], "mgs_mola_topography_derived-data_meg064")
        self.assertEqual(by_id["mars_mola_megdr_nili"]["product_type_filter"], "MEGDR")
        self.assertEqual(by_id["moon_lola_reference"]["dataset_id"], "lro_lola_rdr-data_gridded")
        self.assertEqual(by_id["moon_lola_reference"]["product_type_filter"], "GDRDEM")
        self.assertEqual(by_id["moon_diviner_prp"]["dataset_id"], "lro_diviner_derived_prp")
        self.assertEqual(by_id["moon_diviner_prp"]["product_type_filter"], "PRP")

    def test_parses_embedded_pds_label_fields_and_geographic_bounds(self):
        label = """PDS_VERSION_ID = PDS3
PRODUCT_ID = "DTEEC_017762_1890_018039_1890_A01"
MAP_PROJECTION_TYPE = EQUIRECTANGULAR
MAP_SCALE = 1.01 <M/PIXEL>
CENTER_LATITUDE = 8.781
CENTER_LONGITUDE = 67.33
MINIMUM_LATITUDE = 8.70
MAXIMUM_LATITUDE = 8.86
WESTERNMOST_LONGITUDE = 67.20
EASTERNMOST_LONGITUDE = 67.30
LINE_SAMPLES = 2048
LINES = 4096
END
"""
        fields = parse_pds_label_text(label)
        self.assertTrue(fields["_LABEL_TERMINATED"])
        self.assertEqual(fields["PRODUCT_ID"], "DTEEC_017762_1890_018039_1890_A01")
        self.assertAlmostEqual(float(fields["MAP_SCALE"]), 1.01)
        bounds = {
            "min_lat": float(fields["MINIMUM_LATITUDE"]),
            "max_lat": float(fields["MAXIMUM_LATITUDE"]),
            "west_lon": float(fields["WESTERNMOST_LONGITUDE"]),
            "east_lon": float(fields["EASTERNMOST_LONGITUDE"]),
        }
        self.assertTrue(_core_aoi_intersection(bounds))

    def test_known_dtm_reference_promotes_verified_non_overlap_to_top_level(self):
        inspection = {
            "status": "label_verified_bounds_outside_core_aoi",
            "core_mola_aoi_footprint_intersection": False,
            "bounds": {
                "min_lat": 8.650757405385,
                "max_lat": 8.9115110029789,
                "west_lon": 67.26487883,
                "east_lon": 67.38538575,
            },
        }
        record = build_known_dtm_reference(inspection)
        self.assertIs(record["core_mola_aoi_footprint_intersection"], False)
        self.assertIn("does not intersect", record["metadata_boundary"])
        self.assertEqual(record["pds_label_inspection"], inspection)

    def test_known_dtm_reference_preserves_unknown_when_label_bounds_are_incomplete(self):
        inspection = {
            "status": "label_read_but_geographic_bounds_incomplete",
            "core_mola_aoi_footprint_intersection": None,
        }
        record = build_known_dtm_reference(inspection)
        self.assertEqual(
            record["core_mola_aoi_footprint_intersection"],
            "not_yet_verified_from_product_label",
        )
        self.assertIn("unknown", record["metadata_boundary"])

    def test_known_dtm_reference_handles_positive_intersection_explicitly(self):
        inspection = {
            "status": "label_verified_bounds_intersect_core_aoi",
            "core_mola_aoi_footprint_intersection": True,
        }
        record = build_known_dtm_reference(inspection)
        self.assertIs(record["core_mola_aoi_footprint_intersection"], True)
        self.assertIn("intersects", record["metadata_boundary"])

    def test_dtm_label_bounds_can_confirm_no_overlap_with_core_aoi(self):
        bounds = {
            "min_lat": 8.70, "max_lat": 8.86,
            "west_lon": 67.30, "east_lon": 67.40,
        }
        self.assertFalse(_core_aoi_intersection(bounds))
        self.assertIsNone(_core_aoi_intersection({"min_lat": 8.7, "max_lat": 8.8}))

    def test_verified_nili_dtm_label_bounds_do_not_intersect_original_mola_aoi(self):
        # Exact bounds parsed from the committed 256 KiB prefix of the public
        # HiRISE DTM PDS3 label. Keep this adjacent reference separate from
        # the original MOLA comparison AOI.
        bounds = {
            "min_lat": 8.650757405385,
            "max_lat": 8.9115110029789,
            "west_lon": 67.26487883,
            "east_lon": 67.38538575,
        }
        self.assertFalse(_core_aoi_intersection(bounds))
        self.assertGreater(bounds["west_lon"], NILI["bbox_wsen"][2])

    def test_builds_official_img_url_from_ode_relative_path(self):
        product = {
            "pdsid": "DTEEC_043779_1890_043423_1890_A01",
            "ihid": "MRO",
            "iid": "HiRISE",
            "pt": "DTM",
            "Data_Set_Id": "MRO-M-HIRISE-5-DTM-V1.0",
            "RelativePathToVol": (
                "dtm\\esp\\orb_043700_043799\\"
                "esp_043779_1890_esp_043423_1890\\"
            ),
        }
        self.assertEqual(
            build_hirise_dtm_img_url(product),
            "https://www.uahirise.org/PDS/DTM/ESP/ORB_043700_043799/"
            "ESP_043779_1890_ESP_043423_1890/"
            "DTEEC_043779_1890_043423_1890_A01.IMG",
        )

    def test_rejects_unsafe_or_non_hirise_ode_product_paths(self):
        product = {
            "pdsid": "DTEEC_043779_1890_043423_1890_A01",
            "ihid": "MRO",
            "iid": "HiRISE",
            "pt": "DTM",
            "Data_Set_Id": "MRO-M-HIRISE-5-DTM-V1.0",
            "RelativePathToVol": "dtm\\esp\\..\\outside\\",
        }
        with self.assertRaisesRegex(ValueError, "unsafe path components"):
            build_hirise_dtm_img_url(product)
        product["RelativePathToVol"] = "dtm\\esp\\orb_043700_043799\\folder\\"
        product["Data_Set_Id"] = "MRO-M-HIRISE-3-DTM-V1.1"
        with self.assertRaisesRegex(ValueError, "not in the MRO HiRISE DTM data set"):
            build_hirise_dtm_img_url(product)

    def test_generic_dtm_label_read_uses_product_specific_url_and_id(self):
        label = b"""PDS_VERSION_ID = PDS3
PRODUCT_ID = "DTEEC_043779_1890_043423_1890_A01"
DATA_SET_ID = "MRO-M-HIRISE-5-DTM-V1.0"
MAP_PROJECTION_TYPE = EQUIRECTANGULAR
MAP_SCALE = 1.01 <M/PIXEL>
MINIMUM_LATITUDE = 8.70
MAXIMUM_LATITUDE = 8.86
WESTERNMOST_LONGITUDE = 67.20
EASTERNMOST_LONGITUDE = 67.30
END
"""
        response = FakeRangeResponse(label)
        product = {
            "pdsid": "DTEEC_043779_1890_043423_1890_A01",
            "ode_id": 28520359,
            "ihid": "MRO",
            "iid": "HiRISE",
            "pt": "DTM",
            "Data_Set_Id": "MRO-M-HIRISE-5-DTM-V1.0",
            "RelativePathToVol": (
                "dtm\\esp\\orb_043700_043799\\"
                "esp_043779_1890_esp_043423_1890\\"
            ),
        }
        with patch(
            "scripts.fetch_planetary_archive_discovery.SESSION.get",
            return_value=response,
        ) as get:
            result = inspect_hirise_dtm_product_label(product)
        self.assertEqual(result["pdsid"], product["pdsid"])
        self.assertEqual(result["ode_id"], 28520359)
        self.assertEqual(result["status"], "label_verified_bounds_intersect_core_aoi")
        self.assertTrue(result["core_mola_aoi_footprint_intersection"])
        self.assertIn("DTEEC_043779_1890_043423_1890_A01.IMG", result["source_url"])
        self.assertEqual(get.call_args.args[0], result["source_url"])
        self.assertTrue(response.closed)

    def test_inspects_every_unique_ode_dtm_product_and_preserves_unknown_states(self):
        products = []
        labels = []
        for index in range(4):
            pdsid = f"DTEEC_04377{index}_1890_04342{index}_1890_A01"
            products.append({
                "pdsid": pdsid,
                "ode_id": 28000000 + index,
                "ihid": "MRO",
                "iid": "HiRISE",
                "pt": "DTM",
                "Data_Set_Id": "MRO-M-HIRISE-5-DTM-V1.0",
                "RelativePathToVol": (
                    f"dtm\\esp\\orb_043700_043799\\{pdsid.lower()}\\"
                ),
            })
            if index == 0:
                labels.append(b"""PDS_VERSION_ID = PDS3
PRODUCT_ID = "FIRST"
MINIMUM_LATITUDE = 8.70
MAXIMUM_LATITUDE = 8.80
WESTERNMOST_LONGITUDE = 67.20
EASTERNMOST_LONGITUDE = 67.30
END
""")
            elif index == 1:
                labels.append(b"""PDS_VERSION_ID = PDS3
PRODUCT_ID = "SECOND"
MINIMUM_LATITUDE = 8.70
MAXIMUM_LATITUDE = 8.80
WESTERNMOST_LONGITUDE = 67.30
EASTERNMOST_LONGITUDE = 67.40
END
""")
            elif index == 2:
                labels.append(b"""PDS_VERSION_ID = PDS3
PRODUCT_ID = "THIRD"
MINIMUM_LATITUDE = 8.70
MAXIMUM_LATITUDE = 8.80
END
""")
            else:
                labels.append(b"PDS_VERSION_ID = PDS3\\nPRODUCT_ID = \"FOURTH\"\\n")

        responses = [FakeRangeResponse(label) for label in labels]
        with patch(
            "scripts.fetch_planetary_archive_discovery.SESSION.get",
            side_effect=responses,
        ) as get:
            results = inspect_hirise_dtm_products(
                products + [products[0]],
                pause_seconds=0,
            )
        self.assertEqual(len(results), 4)
        self.assertEqual([row["pdsid"] for row in results], [row["pdsid"] for row in products])
        self.assertEqual(
            [row["status"] for row in results],
            [
                "label_verified_bounds_intersect_core_aoi",
                "label_verified_bounds_outside_core_aoi",
                "label_read_but_geographic_bounds_incomplete",
                "label_not_complete_within_range_cap",
            ],
        )
        self.assertEqual(get.call_count, 4)
        self.assertTrue(all(response.closed for response in responses))

    def test_bounded_label_read_verifies_core_aoi_footprint_when_bounds_present(self):
        label = b"""PDS_VERSION_ID = PDS3
PRODUCT_ID = "DTEEC_017762_1890_018039_1890_A01"
MAP_PROJECTION_TYPE = EQUIRECTANGULAR
MAP_SCALE = 1.01 <M/PIXEL>
MINIMUM_LATITUDE = 8.70
MAXIMUM_LATITUDE = 8.86
WESTERNMOST_LONGITUDE = 67.20
EASTERNMOST_LONGITUDE = 67.30
END
"""
        response = FakeRangeResponse(label)
        with patch("scripts.fetch_planetary_archive_discovery.SESSION.get", return_value=response) as get:
            result = inspect_known_hirise_dtm_label()
        self.assertEqual(result["status"], "label_verified_bounds_intersect_core_aoi")
        self.assertTrue(result["core_mola_aoi_footprint_intersection"])
        self.assertEqual(result["fields"]["PRODUCT_ID"], "DTEEC_017762_1890_018039_1890_A01")
        self.assertTrue(response.closed)
        headers = get.call_args.kwargs["headers"]
        self.assertTrue(headers["Range"].startswith("bytes=0-"))

    def test_bounded_label_read_stops_at_cap_without_claiming_footprint(self):
        response = FakeRangeResponse(b"A" * 4096)
        with patch("scripts.fetch_planetary_archive_discovery.SESSION.get", return_value=response) as get:
            result = inspect_known_hirise_dtm_label(max_bytes=128)
        self.assertEqual(result["status"], "label_not_complete_within_range_cap")
        self.assertEqual(result["bytes_read"], 128)
        self.assertIsNone(result["core_mola_aoi_footprint_intersection"])
        self.assertEqual(get.call_args.kwargs["headers"]["Range"], "bytes=0-127")
        self.assertTrue(response.closed)

    def test_extracts_dynamic_iipt_sets_from_json_response(self):
        payload = {
            "ODEResults": {
                "Status": "Success",
                "IIPTSets": {
                    "IIPTSet": [
                        {"IHID": "mro", "IID": "HiRISE", "PT": "RDRV11", "DataSetId": "MRO-M-HIRISE-5-DTM-V1.0"}
                    ]
                },
            }
        }
        rows = extract_iipt_sets(payload)
        self.assertEqual(len(rows), 1)
        self.assertEqual(_clean_iipt(rows[0])["PT"], "RDRV11")

    def test_extracts_iipt_sets_from_xml_shape(self):
        xml = ET.fromstring(
            "<ODEResults><Status>Success</Status><IIPTSets>"
            "<IIPTSet><IHID>mro</IHID><IID>HiRISE</IID><PT>RDRV11</PT>"
            "<DataSetId>MRO-M-HIRISE-5-DTM-V1.0</DataSetId></IIPTSet>"
            "</IIPTSets></ODEResults>"
        )
        payload = {xml.tag: xml_to_value(xml)}
        rows = extract_iipt_sets(payload)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["DataSetId"], "MRO-M-HIRISE-5-DTM-V1.0")

    def test_matching_requires_exact_host_instrument_and_dataset(self):
        spec = {
            "ihid": "mro",
            "instrument_tokens": ("hirise",),
            "dataset_id": "MRO-M-HIRISE-5-DTM-V1.0",
            "product_type_filter": "DTM",
        }
        rows = [
            {"IHID": "mro", "IID": "HiRISE", "IName": "High Resolution Imaging Science Experiment", "PT": "RDRV11", "DataSetId": "MRO-M-HIRISE-5-DTM-V1.0"},
            {"IHID": "mro", "IID": "HiRISE", "PT": "DTM", "DataSetId": "MRO-M-HIRISE-5-DTM-V1.0"},
            {"IHID": "mro", "IID": "HiRISE", "PT": "DTM", "DataSetId": "MRO-M-HIRISE-3-DTM-V1.1"},
            {"IHID": "mgs", "IID": "MOLA", "PT": "MEGDR", "DataSetId": "MRO-M-HIRISE-5-DTM-V1.0"},
        ]
        matches = _find_matching_iipt_sets(rows, spec)
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0]["PT"], "DTM")

    def test_extracts_ode_product_records_and_count(self):
        payload = {
            "ODEResults": {
                "Status": "Success",
                "Count": 1,
                "Products": {
                    "Product": [
                        {
                            "ode_id": 42,
                            "pdsid": "DTM_123",
                            "ihid": "MRO",
                            "iid": "HiRISE",
                            "pt": "DTM",
                            "Data_Set_Id": "MRO-M-HIRISE-5-DTM-V1.0",
                        }
                    ]
                },
            }
        }
        rows, count = extract_products(payload)
        self.assertEqual(count, 1)
        self.assertEqual(len(rows), 1)
        cleaned = _clean_product(rows[0])
        self.assertEqual(cleaned["pdsid"], "DTM_123")
        self.assertEqual(cleaned["Data_Set_Id"], "MRO-M-HIRISE-5-DTM-V1.0")

    def test_extracts_products_from_a_list_response(self):
        payload = {
            "ODEResults": {
                "Count": "2",
                "Products": [
                    {"pdsid": "A"},
                    {"pdsid": "B"},
                ],
            }
        }
        rows, count = extract_products(payload)
        self.assertEqual(count, 2)
        self.assertEqual(len(rows), 2)

    def test_unwrap_ode_handles_missing_wrapper(self):
        self.assertEqual(unwrap_ode({"Status": "Success"}), {"Status": "Success"})


if __name__ == "__main__":
    unittest.main()

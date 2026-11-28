import unittest

from scripts.fetch_planetary_archive_discovery import (
    NILI,
    ODE_TARGETS,
    _clean_iipt,
    _clean_product,
    _find_matching_iipt_sets,
    extract_iipt_sets,
    extract_products,
    unwrap_ode,
    xml_to_value,
)
import xml.etree.ElementTree as ET


class PlanetaryArchiveDiscoveryTests(unittest.TestCase):
    def test_nili_patera_aoi_matches_existing_mola_window(self):
        west, south, east, north = NILI["bbox_wsen"]
        self.assertAlmostEqual(west, 66.7438569302, places=6)
        self.assertAlmostEqual(south, 8.6469409271, places=6)
        self.assertAlmostEqual(east, 67.2561430698, places=6)
        self.assertAlmostEqual(north, 9.1530590729, places=6)

    def test_archive_searches_are_exact_known_datasets(self):
        by_id = {row["id"]: row for row in ODE_TARGETS}
        self.assertEqual(by_id["mars_hirise_dtm_nili"]["dataset_id"], "MRO-M-HIRISE-5-DTM-V1.0")
        self.assertEqual(by_id["mars_mola_megdr_nili"]["dataset_id"], "MGS-M-MOLA-5-MEGDR-L3-V1.0")
        self.assertEqual(by_id["moon_lola_reference"]["dataset_id"], "LRO-L-LOLA-5-GDR-V1.0")
        self.assertEqual(by_id["moon_diviner_prp"]["dataset_id"], "LRO-L-DLRE-5-PRP-V2.0")

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
        }
        rows = [
            {"IHID": "mro", "IID": "HiRISE", "IName": "High Resolution Imaging Science Experiment", "PT": "RDRV11", "DataSetId": "MRO-M-HIRISE-5-DTM-V1.0"},
            {"IHID": "mro", "IID": "HiRISE", "PT": "RDRV11", "DataSetId": "MRO-M-HIRISE-3-RDR-V1.1"},
            {"IHID": "mgs", "IID": "MOLA", "PT": "MEGDR", "DataSetId": "MRO-M-HIRISE-5-DTM-V1.0"},
        ]
        matches = _find_matching_iipt_sets(rows, spec)
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0]["PT"], "RDRV11")

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

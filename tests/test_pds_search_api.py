import unittest

from scripts.fetch_pds_search import (
    API,
    MARS,
    MOLA,
    OBSERVATIONAL_CLASS,
    QUERIES,
    compact_product,
    extract_products,
    is_observational_product,
)


class PdsSearchApiTests(unittest.TestCase):
    def test_uses_products_endpoint(self):
        self.assertTrue(API.endswith("/products"))

    def test_queries_are_scoped_to_observational_products(self):
        self.assertEqual(len(QUERIES), 6)
        for query in QUERIES:
            self.assertIn(f'product_class eq "{OBSERVATIONAL_CLASS}"', query["q"])

    def test_extracts_documented_data_array(self):
        rows = [{"lidvid": "urn:nasa:pds:test::1.0", "title": "Example"}]
        self.assertEqual(extract_products({"data": rows}), rows)

    def test_extracts_legacy_results_array(self):
        rows = [{"id": "legacy-example"}]
        self.assertEqual(extract_products({"results": rows}), rows)

    def test_rejects_non_list_or_non_object_payloads(self):
        self.assertEqual(extract_products({"data": {"not": "a list"}}), [])
        self.assertEqual(extract_products([]), [])

    def test_accepts_flat_observational_product(self):
        product = {
            "lidvid": "urn:nasa:pds:context:product:test::1.0",
            "product_class": "Product_Observational",
            "title": "MOLA example",
            "ref_lid_target": [MARS],
            "ref_lid_instrument": [MOLA],
            "ops:Data_File_Info.ops:file_ref": "https://example.test/data.tab",
            "ops:Data_File_Info.ops:file_name": "data.tab",
        }
        compact = compact_product(product)
        self.assertEqual(compact["id"], product["lidvid"])
        self.assertEqual(compact["type"], "Product_Observational")
        self.assertEqual(compact["targets"], [MARS])
        self.assertEqual(compact["instrument_refs"], [MOLA])
        self.assertEqual(compact["data_file_url"], "https://example.test/data.tab")
        self.assertEqual(compact["data_file_name"], "data.tab")

    def test_observational_class_filter_is_not_overly_restrictive(self):
        self.assertTrue(is_observational_product({"product_class": "Product_Observational"}))
        self.assertTrue(is_observational_product({}))
        self.assertFalse(is_observational_product({"product_class": "Product_Context"}))


if __name__ == "__main__":
    unittest.main()

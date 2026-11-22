import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import process_diviner_prp as diviner


class DivinerPDS3LayoutTests(unittest.TestCase):
    LABEL = """PDS_VERSION_ID = PDS3
RECORD_TYPE = FIXED_LENGTH
RECORD_BYTES = 210
FILE_RECORDS = 2880000
OBJECT = HEADER
  BYTES = 210
END_OBJECT = HEADER
OBJECT = TABLE
  ROW_BYTES = 210
  ROWS = 2880000
  COLUMNS = 15
END_OBJECT = TABLE
END
"""

    def test_reads_authoritative_header_and_record_layout(self):
        layout = diviner.parse_pds3_table_layout(self.LABEL)
        self.assertEqual(layout["records"], 2_880_000)
        self.assertEqual(layout["record_length_bytes"], 210)
        self.assertEqual(layout["header_offset_bytes"], 210)
        self.assertEqual(layout["columns"], 15)
        self.assertEqual(layout["declared_file_bytes"], 604_800_210)

    def test_rejects_mismatched_record_and_row_bytes(self):
        label = self.LABEL.replace("ROW_BYTES = 210", "ROW_BYTES = 209")
        with self.assertRaisesRegex(RuntimeError, "disagrees with RECORD_BYTES"):
            diviner.parse_pds3_table_layout(label)

    def test_rejects_missing_table_layout(self):
        with self.assertRaisesRegex(RuntimeError, "HEADER and TABLE"):
            diviner.parse_pds3_table_layout("RECORD_BYTES = 210")

    def test_rejects_record_count_mismatch(self):
        label = self.LABEL.replace("ROWS = 2880000", "ROWS = 2879999")
        with self.assertRaisesRegex(RuntimeError, "row count disagrees"):
            diviner.parse_pds3_table_layout(label)


if __name__ == "__main__":
    unittest.main()

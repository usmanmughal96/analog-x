import unittest

from scripts.validate_field_observations import valid_utc_timestamp


class UtcObservationTimestampTests(unittest.TestCase):
    def test_accepts_iso_8601_utc_timestamp(self):
        self.assertTrue(valid_utc_timestamp("2026-11-28T09:03:07.123Z"))

    def test_rejects_date_only_value(self):
        self.assertFalse(valid_utc_timestamp("2026-11-28"))

    def test_rejects_timestamp_without_timezone(self):
        self.assertFalse(valid_utc_timestamp("2026-11-28T09:03:07"))

    def test_rejects_non_utc_offset(self):
        self.assertFalse(valid_utc_timestamp("2026-11-28T14:03:07+05:00"))

    def test_rejects_invalid_calendar_date(self):
        self.assertFalse(valid_utc_timestamp("2026-02-30T09:03:07.000Z"))


if __name__ == "__main__":
    unittest.main()

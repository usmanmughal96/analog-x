import sys
import unittest
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import import_independent_review_labels as importer


def make_packet(label="positive"):
    review = {
        "label": label,
        "criterion_version": importer.CRITERION_VERSION,
        "evidence_refs": ["https://example.org/independent-map", "doi:10.0000/example"],
        "reviewer_name": "Independent Reviewer",
        "reviewer_affiliation": "External University",
        "reviewer_qualification": "Planetary geomorphology",
        "review_date_utc": "2026-11-28T10:20:30Z",
        "confidence_1_to_5": 4,
        "independent_of_analogx_score": True,
        "rationale": "The cited independent map supports the stated morphology at the supplied scale.",
        "limitations": ["Coverage is incomplete."],
    }
    packet = {
        "schema_version": "1.0.0",
        "review_version": importer.CRITERION_VERSION,
        "cases": [
            {
                "review_case_id": "AX-M-EXAMPLE",
                "target": "mars",
                "independent_review": review,
            }
        ],
    }
    key = {
        "review_version": importer.CRITERION_VERSION,
        "cases": {
            "AX-M-EXAMPLE": {
                "target": "mars",
                "candidate_id": "candidate-001",
                "spatial_group": "geologic-block-01",
                "core_terrain_index": 72.5,
            }
        },
    }
    return packet, key


class IndependentReviewImporterTests(unittest.TestCase):
    def test_imports_valid_binary_review_with_provenance(self):
        packet, key = make_packet()
        result, counts = importer.convert_responses(
            packet, key, {"labels": []}
        )
        self.assertEqual(counts["positive"], 1)
        self.assertEqual(counts["negative"], 0)
        row = result["labels"][0]
        self.assertEqual(row["candidate_id"], "candidate-001")
        self.assertEqual(row["spatial_group"], "geologic-block-01")
        self.assertEqual(row["core_terrain_index"], 72.5)
        self.assertIn("https://example.org/independent-map", row["evidence_ref"])

    def test_skips_inconclusive_and_insufficient_evidence(self):
        for label in ("inconclusive", "insufficient_evidence", None, ""):
            packet, key = make_packet(label)
            result, counts = importer.convert_responses(packet, key, {"labels": []})
            with self.subTest(label=label):
                self.assertEqual(result["labels"], [])
                self.assertEqual(counts["inconclusive_or_blank"], 1)

    def test_rejects_unknown_label_instead_of_silently_skipping(self):
        packet, key = make_packet("positve")
        with self.assertRaisesRegex(ValueError, "unsupported review label"):
            importer.convert_responses(packet, key, {"labels": []})

    def test_rejects_wrong_criterion_version(self):
        packet, key = make_packet()
        packet["cases"][0]["independent_review"]["criterion_version"] = "another_criterion"
        with self.assertRaisesRegex(ValueError, "criterion_version must be"):
            importer.convert_responses(packet, key, {"labels": []})

    def test_rejects_date_only_and_timezone_naive_review_dates(self):
        for date in ("2026-11-28", "2026-11-28T10:20:30"):
            packet, key = make_packet()
            packet["cases"][0]["independent_review"]["review_date_utc"] = date
            with self.subTest(date=date):
                with self.assertRaisesRegex(ValueError, "explicit ISO-8601 UTC"):
                    importer.convert_responses(packet, key, {"labels": []})

    def test_rejects_non_utc_offset_review_date(self):
        packet, key = make_packet()
        packet["cases"][0]["independent_review"]["review_date_utc"] = "2026-11-28T15:20:30+05:00"
        with self.assertRaisesRegex(ValueError, "explicit ISO-8601 UTC"):
            importer.convert_responses(packet, key, {"labels": []})

    def test_rejects_boolean_confidence(self):
        packet, key = make_packet()
        packet["cases"][0]["independent_review"]["confidence_1_to_5"] = True
        with self.assertRaisesRegex(ValueError, "integer from 1 to 5"):
            importer.convert_responses(packet, key, {"labels": []})

    def test_rejects_non_string_or_blank_evidence_references(self):
        for refs in ([], ["  "], [None], ["valid", 7]):
            packet, key = make_packet()
            packet["cases"][0]["independent_review"]["evidence_refs"] = refs
            with self.subTest(refs=refs):
                with self.assertRaisesRegex(ValueError, "non-empty list of non-empty strings"):
                    importer.convert_responses(packet, key, {"labels": []})

    def test_rejects_duplicate_candidate_label(self):
        packet, key = make_packet()
        existing = {
            "labels": [{
                "target": "mars",
                "candidate_id": "candidate-001",
                "label": "negative",
            }]
        }
        with self.assertRaisesRegex(ValueError, "already has a label"):
            importer.convert_responses(packet, key, existing)

    def test_rejects_private_key_target_or_candidate_mismatch(self):
        packet, key = make_packet()
        key["cases"]["AX-M-EXAMPLE"]["target"] = "moon"
        with self.assertRaisesRegex(ValueError, "target does not match"):
            importer.convert_responses(packet, key, {"labels": []})


if __name__ == "__main__":
    unittest.main()

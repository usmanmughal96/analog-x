import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import build_independent_review_pack as pack
import import_independent_review_labels as importer


def sample_data():
    targets = {}
    for target in ("moon", "mars"):
        rows = []
        for rank in range(1, 1201):
            lat = -70 + ((rank * 7) % 130)
            lon = -170 + ((rank * 13) % 340)
            rows.append({
                "id": f"T{rank:04d}", "tile_id": f"N{rank:02d}E{rank:03d}",
                "shortlist_rank": rank, "latitude": lat, "longitude": lon,
                "core_terrain_index": 100-rank/12,
                "secondary_diagnostic_index": (rank*17)%100,
                "window_footprint_km": 5.55, "analysis_support_m": 925,
                "terrain": {"median_slope_deg": 10.0}
            })
        targets[target] = {"candidate_windows": rows}
    return {
        "schema_version":"1.1.0","status":"complete","generated_at_utc":"2026-11-22T00:00:00Z",
        "ranking_contract":{"ranking_ready":True,"primary_feature_family":"core","consensus_score":False},
        "completion_contract":{"tile_failures":0,"tiles_processed":100,"global_land_tile_inventory_total":100},
        "targets":targets
    }


class ResearchPhasePackTests(unittest.TestCase):
    def test_builds_two_separate_ranked_lists_and_blind_packet(self):
        ranked, packet, key = pack.build_outputs(sample_data())
        self.assertEqual(len(ranked["targets"]["moon"]["top_25"]), 25)
        self.assertEqual(len(ranked["targets"]["mars"]["top_25"]), 25)
        self.assertEqual(len(packet["cases"]), 96)
        self.assertEqual(sum(x["target"]=="moon" for x in packet["cases"]),48)
        self.assertEqual(sum(x["target"]=="mars" for x in packet["cases"]),48)
        self.assertEqual(set(key["cases"]), {x["review_case_id"] for x in packet["cases"]})

    def test_reviewer_packet_hides_candidate_id_rank_and_scores(self):
        _, packet, _ = pack.build_outputs(sample_data())
        case = packet["cases"][0]
        self.assertNotIn("candidate_id", case)
        self.assertNotIn("shortlist_rank", case)
        self.assertNotIn("core_terrain_index", case)
        self.assertNotIn("secondary_diagnostic_index", case)

    def test_rank_bin_sampling_is_deterministic(self):
        _, packet1, _ = pack.build_outputs(sample_data())
        _, packet2, _ = pack.build_outputs(sample_data())
        self.assertEqual([x["review_case_id"] for x in packet1["cases"]], [x["review_case_id"] for x in packet2["cases"]])

    def test_import_requires_complete_independent_review(self):
        _, packet, key = pack.build_outputs(sample_data())
        case = packet["cases"][0]
        case["independent_review"] = {"label":"positive"}
        existing = {"labels":[]}
        with self.assertRaisesRegex(ValueError, "missing review fields"):
            importer.convert_responses(packet, key, existing)

    def test_import_restores_candidate_and_score_only_from_private_key(self):
        _, packet, key = pack.build_outputs(sample_data())
        case = packet["cases"][0]
        case["independent_review"] = {
            "label":"positive", "criterion_version":pack.REVIEW_VERSION,
            "evidence_refs":["doi:10.0000/example"], "reviewer_name":"External reviewer",
            "reviewer_affiliation":"Independent institution", "reviewer_qualification":"Planetary geologist",
            "review_date_utc":"2026-11-23T10:00:00Z", "confidence_1_to_5":4,
            "independent_of_analogx_score":True, "rationale":"Externally supported morphology assessment."
        }
        result, added = importer.convert_responses(packet,key,{"labels":[]})
        self.assertEqual(added["positive"],1)
        imported = result["labels"][0]
        priv = key["cases"][case["review_case_id"]]
        self.assertEqual(imported["candidate_id"],priv["candidate_id"])
        self.assertEqual(imported["core_terrain_index"],priv["core_terrain_index"])
        self.assertEqual(imported["spatial_group"],priv["spatial_group"])


if __name__ == "__main__":
    unittest.main()

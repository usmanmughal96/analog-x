import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import build_reproducibility_manifest as manifest


class ReproducibilityManifestScopeTests(unittest.TestCase):
    def test_manifest_and_quantitative_report_are_excluded_from_hash_inventory(self):
        self.assertFalse(manifest.include_in_manifest(ROOT / "data/provenance/reproducibility_manifest.json"))
        self.assertFalse(manifest.include_in_manifest(ROOT / "data/validation/quantitative_validation.json"))

    def test_scientific_outputs_and_source_registry_remain_in_hash_inventory(self):
        self.assertTrue(manifest.include_in_manifest(ROOT / "data/global_discovery/top_ranked_candidates.json"))
        self.assertTrue(manifest.include_in_manifest(ROOT / "data/moon/shackleton_rim_lola.json"))
        self.assertTrue(manifest.include_in_manifest(ROOT / "data/source_registry.json"))


if __name__ == "__main__":
    unittest.main()

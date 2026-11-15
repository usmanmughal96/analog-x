"""Smoke-test the self-hosted API against generated science packs."""
from __future__ import annotations
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
import app as api  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

client = TestClient(api.app)

def check(response, expected=200):
    assert response.status_code == expected, (response.status_code, response.text[:1000])
    return response.json()

assert check(client.get("/health"))["ok"] is True
manifest = check(client.get("/api/v1/science/manifest"))
assert manifest["earth_site_count"] == 10
assert manifest["experiment_pathway_count"] >= 30
assert manifest["pds_query_count"] == 6
assert manifest["modis_public_browse_count"] == 20

catalog = check(client.get("/api/v1/transferability"))
assert len(catalog["sites"]) == 10
assert catalog["planetary_targets"]["moon"]["terrain_surface"]["rows"] == 32
assert catalog["planetary_targets"]["moon"]["terrain_surface"]["columns"] == 32
site = check(client.get("/api/v1/transferability/sites/chagai_small_playas"))
assert site["id"] == "chagai_small_playas"
assert check(client.get("/api/v1/transferability/sites/not-a-site"), 404)["detail"]

products = check(client.get("/api/v1/planetary-products?target=Moon&limit=5"))
assert products["discovery_only"] is True
modis = check(client.get("/api/v1/earth-observation/modis-browse"))
assert modis["browse_download_count"] == 20

record = {
    "id": "ci-smoke-record",
    "site_id": "chagai_small_playas",
    "station_id": "ci-smoke-station",
    "observed_at": datetime.now(timezone.utc).isoformat(),
    "latitude": 28.58,
    "longitude": 62.63,
    "observation_type": "CI smoke test",
    "value_text": "synthetic test fixture; not a field observation",
    "method": "automated API integration test",
    "notes": "Temporary record created and deleted in the CI test database.",
}
created = check(client.post("/api/v1/field-records", json=record))
assert created["record_id"] == "ci-smoke-record"
listed = check(client.get("/api/v1/field-records?site_id=chagai_small_playas"))
assert any(x["id"] == "ci-smoke-record" for x in listed["records"])
deleted = check(client.delete("/api/v1/field-records/ci-smoke-record"))
assert deleted["deleted"] == "ci-smoke-record"

print("ANALOG-X API smoke test passed: science reads, PDS/MODIS indexes and field-record CRUD.")

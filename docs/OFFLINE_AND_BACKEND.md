# ANALOG-X offline-first operation and self-hosted backend

## What works without a network connection

The public GitHub Pages site is a static application. Its bundled science records, deterministic offline Mission Director, candidate dossiers, Mission Rehearsal Lab, Field Evidence Passport, field protocol export and local field notebook are designed to work without a cloud model or remote data API after the app has been installed/cached once.

The service worker caches the application shell and the current science pack. First open requires connectivity so the browser can install those files. Thereafter, reopen the app from the same browser/device; the offline status indicator reports local mode. The locator panels use bundled geometry and do not depend on an external map tile server. Satellite source links and external basemaps are not required for local decision functions.

Coordinate Scout works offline against the ten curated candidate/reference seeds. It measures distance from a supplied WGS84 coordinate to these records and reports which bundled evidence layers exist. It is not a new global discovery scan, does not fetch fresh NASA data, and does not infer unsampled geology.

## Local field record storage

The Field Evidence Passport stores user-entered observations in IndexedDB on the current device. A localStorage fallback is used where IndexedDB is unavailable (without binary photos). Records can be exported as JSON, CSV and GeoJSON or imported into another browser. GNSS coordinates are requested only after the user presses the location button and grants browser permission. A saved observation is labelled local-only until it is intentionally exported or synced.

No field measurement is fabricated. Do not enter estimates as measured observations. Preserve the operator, instrument/method, units, time, uncertainty, photo and station coordinate as appropriate. A local record is not automatically a validated scientific observation.

## Self-hosted record backend

GitHub Pages cannot execute a conventional persistent API server. For shared records and multi-user access, this repository includes a FastAPI service with PostgreSQL support.

### Run locally with Docker

1. Install Docker Engine and the Compose plugin.
2. Set two strong, independent secrets in your environment: POSTGRES_PASSWORD and WRITE_API_KEY.
3. From the backend/ directory, run:

    docker compose up --build -d

4. Check http://localhost:8000/health.
5. Open http://localhost:8000/docs for the OpenAPI interface.
6. In the Field Evidence Passport, enter the HTTPS backend URL and the same write token. Local records are not erased after syncing.

### API routes

- GET /health — database connectivity
- GET /api/v1/catalog — the versioned candidate catalogue bundled with the backend
- GET /api/v1/field-records?site_id=...&limit=...&offset=... — paginated station records
- POST /api/v1/field-records — create/upsert one station record
- POST /api/v1/field-records/bulk — validate and upsert a bounded batch of field records
- DELETE /api/v1/field-records/{record_id} — remove one record

Write routes require Authorization: Bearer <WRITE_API_KEY> when the secret is configured. CORS_ORIGINS must contain the precise published website origin. Do not use wildcard CORS with credentials. Terminate TLS at the hosting proxy and do not expose a database port publicly.

## Production scaling notes

PostgreSQL is the recommended shared datastore. The schema indexes record ID, site ID, station ID and observation time; bulk upserts are bounded to 500 records per request. The API is stateless and can run multiple app workers or replicas behind a TLS reverse proxy/load balancer. Set DATABASE_URL to a managed PostgreSQL service with connection pooling, monitor backups, and add a retention/export policy appropriate to the field programme. For larger image workflows, use an object store and retain only image metadata/object keys in PostgreSQL rather than increasing the JSON request size.

This release provides the API source and container configuration; it does not claim that a public backend host, database, write token or TLS endpoint has already been provisioned. The static application remains usable without deploying the optional backend.

## Data and scientific boundaries

Offline records and candidate assessments must retain original data timestamps, source attribution, units, spatial support and quality caveats. The app does not convert a coordinate proximity result into planetary equivalence, nor does it certify landing safety, rover trafficability, accessible water/ice or mineral resource abundance.


## ATFA science read API (v1.1)

The optional FastAPI service also serves the generated science packs when the corresponding build outputs exist:

- `GET /api/v1/science/manifest` — pack timestamps, site/pathway counts and PDS/MODIS discovery counts.
- `GET /api/v1/transferability` — complete ATFA experiment/site dossiers.
- `GET /api/v1/transferability/sites/{site_id}` — one site dossier.
- `GET /api/v1/planetary-products?target=Moon&limit=50&offset=0` — paginated PDS product metadata discovery records.
- `GET /api/v1/earth-observation/modis-browse` — MOD11A2 granule/browse provenance index.

These are read-only science endpoints. The field-observation write routes remain bearer-token protected when `WRITE_API_KEY` is configured. GitHub Pages continues to load the committed JSON science pack directly and does not depend on the optional API service.

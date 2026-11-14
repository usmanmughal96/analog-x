# Repository and Deployment Status

## Public project
- Repository: https://github.com/usmanmughal96/analog-x
- Application: https://usmanmughal96.github.io/analog-x/
- Demo: https://usmanmughal96.github.io/analog-x/demo.html

## Frontend
The root index.html is the dark Evidence Operations console inspired by the supplied mission-control UI reference. It contains:
- Pakistan study-area map with Koh-i-Sultan and Hispar study markers
- NASA GIBS true-colour contextual layer
- NASA POWER climate panels
- Sentinel-2 scene metadata and true-colour quicklook panels
- NASA EPIC global image panel
- evidence readiness / pipeline state
- institutional source and provenance register
- field validation card JSON export and methodology/submission modals

The UI avoids fake spacecraft telemetry. It shows real evidence and its actual status.

## Verified datasets and generated assets
- NASA POWER: 8/8 configured site snapshots, all seven requested parameters present, no errors in the current index.
- Planetary Computer Sentinel-2 L2A: scene metadata discovered for Koh-i-Sultan and Hispar.
- Sentinel-2 preview assets generated and committed:
  - data/pakistan/quicklooks/koh_i_sultan.png
  - data/pakistan/quicklooks/hispar_glacier.png
- NASA EPIC full-disc image generated and committed:
  - data/nasa/epic_latest.png
- Metadata/provenance:
  - data/power/index.json
  - data/pakistan/public_scene_catalog.json
  - data/pakistan/quicklooks/index.json
  - data/nasa/epic_latest.json

## Data pipeline reliability
The NASA POWER and Pakistan/EPIC data workflows share the same GitHub Actions concurrency group and rebase their commits on the current main branch before pushing. This mitigates concurrent push races. NASA POWER stale site JSONs are removed if a candidate is removed/renamed.

## External sources not fully integrated
- EvK2CNR's existing glacier inventory is acknowledged and linked; the GeoNetwork endpoint returned HTML rather than JSON and the official vector file has not been redistributed.
- NDMA products and the 2026 Vulnerable Glaciers and Glacial Lakes Atlas are linked as existing institutional evidence; a redistributable geospatial layer was not fetched.
- SUPARCO DisasterWatch, NatCat and Space4Climate remain official portal/workflow references; no suitable public bulk data endpoint and reuse licence have been verified.
- NASA MOLA, LOLA and Diviner are linked but raw rasters are not yet processed.

## Secret handling
The current integrations do not require the api.nasa.gov key. A key exposed in a chat should be rotated before any future use. The public repository includes only .env.example and ignores populated .env files. Never put API credentials into frontend code.

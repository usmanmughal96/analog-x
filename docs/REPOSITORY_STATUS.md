# Repository and Deployment Status

## Public project
- Repository: https://github.com/usmanmughal96/analog-x
- Application: https://usmanmughal96.github.io/analog-x/
- Demo: https://usmanmughal96.github.io/analog-x/demo.html

## Frontend
The root index.html is the dark Evidence Operations console inspired by the supplied mission-control UI reference. It contains:
- Pakistan study-area map with Koh-i-Sultan and Hispar markers
- NASA GIBS contextual imagery
- NASA POWER climate panels for both Pakistan sites
- Sentinel-2 scene metadata and true-colour preview panels
- NASA EPIC global Earth image
- matched-scale terrain profile cards for Nili Patera, Koh-i-Sultan and Hispar
- evidence readiness / pipeline status
- institutional source and provenance register
- downloadable field-validation card JSON, including available terrain descriptors

The UI avoids fake spacecraft telemetry. It shows actual evidence and its status.

## Verified datasets and generated assets
- NASA POWER: 8/8 configured site snapshots, all seven requested parameters present, no errors in the current index.
- Planetary Computer Sentinel-2 L2A: scene metadata discovered for Koh-i-Sultan and Hispar.
- Sentinel-2 preview assets:
  - data/pakistan/quicklooks/koh_i_sultan.png
  - data/pakistan/quicklooks/hispar_glacier.png
- NASA EPIC full-disc image:
  - data/nasa/epic_latest.png
- Copernicus DEM / MOLA terrain output:
  - data/terrain/terrain_comparison.json
  - data/terrain/koh_i_sultan_copdem_hillshade.png
  - data/terrain/hispar_glacier_copdem_hillshade.png
  - data/terrain/nili_patera_mola_hillshade.png

The terrain pipeline processes Copernicus DEM GLO-30 DSM windows at approximately 925 m support and MOLA MEGDR 64 ppd topography/counts around Nili Patera. Earth windows have 100% valid cells. The Nili Patera MOLA window has 50.53% observed-cell coverage (567/1,122) and 87 complete 3×3 neighborhoods. The application flags this limitation.

## Automated data pipeline reliability
- NASA POWER, Pakistan/EPIC evidence and terrain workflows share the same GitHub Actions concurrency group.
- Each repository data workflow rebases before pushing to avoid interrupted push races.
- NASA POWER stale per-site snapshots are removed when candidate records are removed or renamed.
- Raw MOLA data are cached in GitHub Actions and are not committed to the public repository.

## External sources not fully integrated
- EvK2CNR glacier and glacial-lake inventory work is acknowledged and linked; vector geometry is not redistributed here.
- NDMA 2026 Atlas products are linked as institutional evidence; a redistributable geospatial layer was not fetched.
- SUPARCO DisasterWatch, NatCat and Space4Climate remain official portal/workflow references; public bulk-data endpoints and reuse licences were not verified.
- NASA LRO LOLA and Diviner data are linked but raw rasters are not yet processed.

## Secret handling
The current project integrations do not require the api.nasa.gov key. A key pasted into a chat should be rotated before any future use. The public repository contains only a placeholder environment template and ignores populated .env files. Never put API credentials into frontend code.

# Data access, API keys and secret handling

## NASA api.nasa.gov key

A NASA API key was pasted into a chat transcript during development. Treat it as compromised and **revoke/rotate it in the NASA API account before reuse**. Do not copy it into this repository, browser JavaScript, a public JSON file, commit message or workflow log.

The connected GitHub integration can write repository files and workflows, but does not expose the GitHub Actions secrets API. The repository owner must manage secrets in GitHub Settings if a future workflow genuinely requires one.

**Current project status: no NASA API key is required for the integrations currently running.**
- NASA POWER Climatology API: public query used by the project; no api.nasa.gov key.
- NASA GIBS: public WMTS/WMS tiles; no api.nasa.gov key.
- Microsoft Planetary Computer STAC: anonymous metadata API.
- Microsoft Planetary Computer Copernicus DEM and Sentinel-2 COGs: short-lived SAS token requested from Microsoft's public token endpoint.
- NASA DSCOVR/EPIC: direct public GSFC API endpoint https://epic.gsfc.nasa.gov/api/natural, no api.nasa.gov key.

The optional environment variable NASA_API_KEY is retained in .env.example only as a placeholder for future NASA APIs that may require it. It is not consumed by the current workflows. Do not set it until a future data source requires it.

## Local environment

- .env.example contains a placeholder only.
- Copy to .env locally only when an API genuinely needs a key.
- .gitignore excludes .env and populated environment files.
- Never place credentials in static-site code, public JSON or public commits.

## Microsoft Planetary Computer

The public STAC API can be accessed anonymously. Some Azure-hosted COG assets require a short-lived SAS token. The project obtains it from the public collection token endpoint; it does not store the token in the repository or browser assets. Copernicus DEM and Sentinel-2 data retain their provider terms and attribution.

## Google Earth Engine

Earth Engine is not currently required. It needs a Google Cloud project, Earth Engine API enablement, project registration and appropriate roles. The current Microsoft Planetary Computer path provides the STAC/COG access required for this release.

## Data-source integrity

A public webpage does not imply an open API, bulk-download route or redistribution licence. NDMA, SUPARCO/DisasterWatch, Space4Climate and EvK2CNR products are labelled according to what was actually retrieved and validated. Portal-only references are never described as integrated data.

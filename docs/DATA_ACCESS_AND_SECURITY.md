# Data access, API keys and secret handling

## NASA API key

The NASA api.nasa.gov key is used only by the optional NASA DSCOVR/EPIC global Earth-image ingestion script (scripts/fetch_nasa_epic.py). It is read from the environment variable NASA_API_KEY in GitHub Actions. The key is never written to the repository, browser JavaScript, static JSON, image URLs in the frontend, or logs.

**Security action:** a key pasted into a chat or issue should be considered exposed. Revoke/rotate it in the NASA API key account before using it in production. Do not reuse a key that has been shared publicly or in a chat transcript.

GitHub Actions secret setup:
1. Open https://github.com/usmanmughal96/analog-x/settings/secrets/actions
2. Select New repository secret.
3. Name: NASA_API_KEY
4. Value: paste the newly rotated key.
5. Save. Run the Refresh global and Pakistan Earth-observation evidence workflow manually.

The connected GitHub integration can publish source files and workflows but does not expose the repository secrets API. The repository owner must add this secret in GitHub Settings.

Local development:
- Copy .env.example to .env.
- Set NASA_API_KEY to a newly rotated key.
- Never commit .env; .gitignore excludes it.

If the secret is not configured, the EPIC workflow uses NASA DEMO_KEY for a single low-frequency request. The app works without EPIC.

## What does not require registration or a key?

- NASA POWER Climatology: the verified public API calls in this project do not require the api.nasa.gov key.
- NASA GIBS: public WMTS/WMS tile services.
- Microsoft Planetary Computer open STAC metadata: anonymous access.
- Microsoft Planetary Computer Sentinel-2 COG assets: the public SAS token endpoint issues short-lived access tokens without a user account.
- NASA PDS / Earthdata metadata discovery: public metadata access; specific data assets may have separate Earthdata Login or distribution requirements.

## Microsoft Planetary Computer

Open Sentinel-2 L2A assets are discovered through the anonymous STAC API. The public SAS token endpoint signs data-asset requests. No Planetary Computer account is required for ordinary public STAC search or the open data access path used in this prototype. Sentinel-2 data remain subject to Copernicus Sentinel data terms; keep attribution and provider licences.

## Data-source limitations

The NDMA, SUPARCO/DisasterWatch, Space4Climate and EvK2CNR portals are documented in the application's source register. A page being publicly viewable does not mean its underlying datasets are open bulk-downloads, have an API, or may be redistributed. The application labels only data actually fetched and validated as integrated. Portal-only references are explicitly labelled as such.

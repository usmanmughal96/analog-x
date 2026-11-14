# API keys and environment variables

## Security warning

A NASA API key was pasted into a chat message. Treat that credential as exposed: revoke it and generate a new key at https://api.nasa.gov/ before using it again. Do not copy the previously shared value into a repository, website, log, issue, screenshot or presentation.

## Does the current ANALOG-X application need this key?

No. The current data pipeline uses:
- NASA POWER public climatology API;
- NASA GIBS public WMTS imagery;
- Microsoft Planetary Computer public STAC and short-lived SAS token access;
- Copernicus Sentinel-2 L2A hosted by Microsoft.

Those sources do not require the NASA developer key. Do not add the key to the browser bundle or embed it in index.html.

## When a NASA key is needed

Some api.nasa.gov services use a NASA developer key for request limits/authentication. If a later server-side workflow genuinely requires one, use an environment variable. Never expose the value in client-side JavaScript.

### Local development

1. Copy .env.example to .env.
2. Put the newly rotated key in the local .env file.
3. Keep .env out of Git. The repository .gitignore excludes it.

Example:
NASA_API_KEY=replace_with_new_rotated_key

### GitHub Actions

1. Open https://github.com/usmanmughal96/analog-x/settings/secrets/actions
2. Select New repository secret.
3. Name it NASA_API_KEY.
4. Paste only the newly rotated key.
5. In a workflow that actually needs the NASA API, read it as an environment variable:

env:
  NASA_API_KEY: ${{ secrets.NASA_API_KEY }}

The current NASA POWER / GIBS / Planetary Computer workflows do not reference this secret and will continue working without it.

## Rate limits

NASA states the default key limit is 1,000 requests per hour, shared across api.nasa.gov services. The DEMO_KEY limits are much lower. Check the current NASA authentication page before designing request volume:
https://api.nasa.gov/assets/html/authentication.html

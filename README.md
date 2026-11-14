# ANALOG-X — Pakistan Analog Evidence Operations

**NASA Space Apps Challenge 2026** · Team **X Æ A-Xii** · Participant **Muhammad Usman Mughal**

## Live project
- Evidence Operations console: https://usmanmughal96.github.io/analog-x/
- Seven-slide project demo: https://usmanmughal96.github.io/analog-x/demo.html
- Source repository: https://github.com/usmanmughal96/analog-x

## What the product does
ANALOG-X is a Pakistan-first evidence and field-readiness atlas for candidate terrestrial environments relevant to Moon/Mars exploration fieldwork.

The current console focuses on two contrasting Pakistan case studies:

1. **Koh-i-Sultan / Chagai** — a Smithsonian-catalogued volcanic-field candidate for outcrop reconnaissance, sample-context logging and remote-sensing-to-ground validation.
2. **Hispar Glacier / Karakoram** — a cryosphere case study for ice/debris mapping, remote-sensing interpretation and field-data validation.

It assembles verified climate snapshots, Sentinel-2 scene metadata and true-colour previews, planetary references, local institutional baselines and explicit data gaps. It does not claim that either Earth location is a complete Moon/Mars analog.

## Verified integrations

### NASA POWER
Server-side GitHub Actions fetch the public NASA POWER Climatology API for eight coordinates: Koh-i-Sultan, Hispar Glacier, Dallol, Atacama, McMurdo Dry Valleys, Haughton impact structure, Iceland and Death Valley.

Variables include T2M, T2M_MAX, T2M_MIN, RH2M, WS10M, PRECTOTCORR and ALLSKY_SFC_SW_DWN. The current committed index has eight records and no failed sites. Records include the original source response, request URL, community, timestamps, monthly values, metrics and missing-parameter information.

NASA POWER is gridded climatology, not a ground weather station.

### Microsoft Planetary Computer / Sentinel-2 L2A
The anonymous STAC API is queried for Koh-i-Sultan and Hispar study windows. The pipeline discovers scenes, records acquisition date, platform, cloud fraction, MGRS tile and asset provenance, then obtains a public SAS token and clips 768×768 true-colour previews from COG assets.

Current previews:
- data/pakistan/quicklooks/koh_i_sultan.png
- data/pakistan/quicklooks/hispar_glacier.png

This is RGB visual evidence, not mineral classification or field validation. Copernicus Sentinel data terms apply.

### NASA DSCOVR / EPIC
The pipeline retrieves an optional full-disc natural-colour Earth image from the public GSFC EPIC endpoint. It is global context only and is not used in site-scale metrics. This endpoint does not need an api.nasa.gov key.

## Institutional and planetary evidence
- **EvK2CNR:** Existing Pakistan Glacier Inventory: 13,032 glaciers, combined area 13,546.93 km². We acknowledge and link this prior work; the project does not claim to have discovered or remapped those glaciers.
- **SUPARCO / UN-SPIDER:** Official remote-sensing and disaster-monitoring capabilities, recommended practices, DisasterWatch and NatCat are documented. No public bulk-data/API integration from DisasterWatch or Space4Climate has yet been verified.
- **NDMA:** Official hazard projections, disaster early-warning documents and the 2026 Vulnerable Glaciers and Glacial Lakes Atlas listing are linked as existing institutional work. No redistributable geospatial layer has yet been ingested.
- **NASA MOLA / LRO LOLA / Diviner:** Planetary data pathways are identified, but raw rasters are not processed by the current public console.
- **NASA Global Volcano Hazard Frequency:** Historical coarse grid is linked as context only; it is not current volcano alerting or site-scale geology.

See docs/AGENCY_DATA_AUDIT.md for source status and docs/DATA_SOURCES.md for provenance.

## What is differentiated
Other public 2026 entries already demonstrate broad Earth/Moon/Mars matching, experiment-specific ranking, topographic similarity, or evidence-gap reporting. ANALOG-X does not claim those concepts are globally unsolved.

Our narrower contribution is a **Pakistan-first evidence-readiness workflow**:
- actual multi-source records for two contrasting Pakistan case studies;
- a traceable Sentinel-2 scene-to-preview pipeline;
- a clear distinction between integrated data, discovered metadata, reviewed portals and linked references;
- reuse and attribution of existing national glacier/disaster work;
- explicit field validation tasks and non-transferability limits.

A single universal analog score is deliberately withheld until Earth and planetary datasets can be harmonized to defensible spatial/temporal support and a scientist validates the method.

## Run the data pipelines
NASA POWER:
    python -m pip install --upgrade requests
    python scripts/fetch_nasa_power.py

Scene discovery and previews:
    python -m pip install --upgrade requests rasterio pillow numpy
    python scripts/fetch_public_evidence.py
    python scripts/build_scene_quicklooks.py

Optional EPIC global image:
    python scripts/fetch_nasa_epic.py

Automated workflows:
- .github/workflows/fetch-nasa-power.yml
- .github/workflows/fetch-public-evidence.yml

The data workflows share a concurrency lock and rebase before pushing to avoid interrupted commits. Weekly refresh is configured.

## Credentials
The current NASA POWER, NASA GIBS, Microsoft Planetary Computer STAC/SAS and direct NASA EPIC workflows do not need the api.nasa.gov key. A NASA API key pasted into a chat should be considered exposed and rotated before future use. Never commit a key or put it in browser JavaScript. See docs/DATA_ACCESS_AND_SECURITY.md.

## Limitations
- No raw MOLA, LOLA or Diviner raster-derived comparison is claimed in the current release.
- No Chagai mineralogy or Syrtis Major equivalence is inferred from RGB imagery.
- No official EvK2CNR glacier shapefile is redistributed in this repository.
- NDMA, SUPARCO DisasterWatch and Space4Climate are portal/reference status until data endpoints, access terms and product licences are verified.
- NASA POWER is gridded climate context, not local instrumentation.
- Field access, permits and site-level geology require independent validation.

## Licence
Original project code and text are MIT-licensed. NASA, Copernicus, Microsoft, USGS, EvK2CNR and other third-party products retain their original terms and attribution.

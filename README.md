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

The console assembles verified climate snapshots, Sentinel-2 scene metadata and true-colour previews, matched-scale terrain descriptors, institutional baselines and explicit data gaps. It does not claim that either Earth location is a complete Moon/Mars analog.

## Verified integrations

### NASA POWER
Server-side GitHub Actions fetch the public NASA POWER Climatology API for eight coordinates: Koh-i-Sultan, Hispar Glacier, Dallol, Atacama, McMurdo Dry Valleys, Haughton impact structure, Iceland and Death Valley.

Variables include T2M, T2M_MAX, T2M_MIN, RH2M, WS10M, PRECTOTCORR and ALLSKY_SFC_SW_DWN. The current committed index has eight records and no failed sites. Records include original source response, request URL, community, timestamps, monthly values, metrics and missing-parameter information.

NASA POWER is gridded climatology, not a ground weather station.

### Microsoft Planetary Computer / Sentinel-2 L2A
The anonymous STAC API is queried for Koh-i-Sultan and Hispar study windows. The pipeline records acquisition date, platform, cloud fraction, MGRS tile and asset provenance, then obtains a public SAS token and clips 768×768 true-colour previews from COG assets.

Current previews:
- data/pakistan/quicklooks/koh_i_sultan.png
- data/pakistan/quicklooks/hispar_glacier.png

This is RGB visual evidence, not mineral classification or field validation. Copernicus Sentinel data terms apply.

### Copernicus DEM GLO-30 + NASA MOLA MEGDR 64 ppd
The project now computes a coarse matched-support terrain profile for:
- Koh-i-Sultan / Chagai, Pakistan;
- Hispar Glacier / Karakoram, Pakistan;
- Nili Patera, Syrtis Major quadrangle, Mars.

Earth Copernicus DEM GLO-30 DSM tiles are mosaicked across neighbouring one-degree tiles, reprojected to local UTM and averaged to approximately 925 m. Mars MOLA MEGDR topography and observation-count rasters at 64 pixels/degree are cropped around Nili Patera. Slope and 3×3 local relief are calculated on approximately comparable support.

Current terrain output:
- data/terrain/terrain_comparison.json
- data/terrain/koh_i_sultan_copdem_hillshade.png
- data/terrain/hispar_glacier_copdem_hillshade.png
- data/terrain/nili_patera_mola_hillshade.png

**Coverage caveat:** the selected Nili Patera MOLA window has 50.53% valid observed-cell coverage (567/1,122 cells) and 87 complete 3×3 neighborhoods. The app flags this as limited coverage. The results are coarse terrain descriptors—not a geological-equivalence score, rover safety assessment or landing suitability rating. Absolute elevation is not compared across different vertical datums. Earth DSM is not bare-earth elevation.

### NASA DSCOVR / EPIC
The pipeline retrieves an optional full-disc natural-colour Earth image from the public GSFC EPIC endpoint. It is global context only and is not used in site-scale metrics. No api.nasa.gov key is required for this endpoint.

## Institutional and planetary evidence
- **EvK2CNR:** Existing Pakistan Glacier Inventory: 13,032 glaciers, combined area 13,546.93 km². We acknowledge and link this prior work; the project does not claim to have discovered or remapped those glaciers. EvK2CNR has also published preliminary Pakistan glacial-lake inventory work.
- **SUPARCO / UN-SPIDER:** Official remote-sensing and disaster-monitoring capabilities, recommended practices, DisasterWatch and NatCat are documented. No public bulk-data/API integration from DisasterWatch or Space4Climate has yet been verified.
- **NDMA:** Official hazard projections, disaster early warnings and the 2026 Vulnerable Glaciers and Glacial Lakes Atlas listing are linked as existing institutional work. No redistributable geospatial layer has yet been ingested.
- **NASA LRO LOLA / Diviner:** Lunar data pathways are identified, but raw lunar rasters are not processed in the current release.
- **NASA Global Volcano Hazard Frequency:** Historical coarse grid is linked as context only; it is not current volcano alerting or site-scale geology.

See docs/AGENCY_DATA_AUDIT.md for source status and docs/DATA_SOURCES.md for provenance.

## What is differentiated
Other public 2026 challenge entries already demonstrate analog ranking, mission-to-experiment planning and topographic/lighting comparisons. ANALOG-X does not claim those broad ideas are globally unsolved.

Our narrower contribution is a Pakistan-first evidence operations workflow:
- NASA POWER climate snapshots for eight coordinates;
- Sentinel-2 L2A scene discovery and clipped previews for two Pakistan case studies;
- Copernicus DEM GLO-30 and MOLA 64 ppd terrain descriptors at matched coarse support;
- explicit MOLA observation-count coverage and data-quality warnings;
- reuse and attribution of existing EvK2CNR, NDMA and SUPARCO/UN-SPIDER work;
- a clear distinction between integrated data, discovered metadata, reviewed portals and reference-only sources;
- field validation tasks and planetary non-transferability limits.

No single universal analog score is calculated.

## Run the data pipelines
NASA POWER:
    python -m pip install --upgrade requests
    python scripts/fetch_nasa_power.py

Scene discovery and Sentinel-2 previews:
    python -m pip install --upgrade requests rasterio pillow numpy
    python scripts/fetch_public_evidence.py
    python scripts/build_scene_quicklooks.py

Terrain comparison:
    python -m pip install --upgrade requests rasterio pillow numpy scipy
    python scripts/build_terrain_comparison.py

Optional NASA EPIC global image:
    python scripts/fetch_nasa_epic.py

Automated workflows:
- .github/workflows/fetch-nasa-power.yml
- .github/workflows/fetch-public-evidence.yml
- .github/workflows/build-terrain-comparison.yml

The data workflows share a concurrency lock and rebase before pushing to avoid interrupted commits. Weekly source refresh is configured where appropriate.

## Credentials
The current NASA POWER, NASA GIBS, Microsoft Planetary Computer STAC/SAS and direct NASA EPIC workflows do not need an api.nasa.gov key. A NASA API key pasted into a chat should be considered exposed and rotated before future use. Never commit a key or put it in browser JavaScript. See docs/DATA_ACCESS_AND_SECURITY.md.

## Limitations
- Nili Patera MOLA observation coverage is 50.53% in the selected 30 km window and only 87 complete 3×3 neighborhoods remain for terrain derivatives.
- 925 m terrain descriptors are too coarse for rover-scale hazards or field-scale obstacles.
- No Koh-i-Sultan mineralogy or Syrtis Major equivalence is inferred from RGB imagery.
- No official EvK2CNR glacier shapefile is redistributed in this repository.
- NDMA, SUPARCO DisasterWatch and Space4Climate are portal/reference status until data endpoints, access terms and product licences are verified.
- Raw lunar LOLA and Diviner rasters are not yet processed.
- NASA POWER is gridded climate context, not local instrumentation.
- Field access, permits, site-level geology and scientist review remain necessary.

## Licence
Original project code and text are MIT-licensed. NASA, Copernicus, Microsoft, USGS, EvK2CNR and other third-party products retain their original terms and attribution.

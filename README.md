# ANALOG-X — Pakistan Analog Evidence Operations

**NASA Space Apps Challenge 2026** · Team **X Æ A-Xii** · Participant **Muhammad Usman Mughal**

## Live project
- Evidence Operations console: https://usmanmughal96.github.io/analog-x/
- Seven-slide project demo: https://usmanmughal96.github.io/analog-x/demo.html
- Source repository: https://github.com/usmanmughal96/analog-x

## What the product does
ANALOG-X is a Pakistan-first evidence and field-readiness atlas for candidate terrestrial environments relevant to Moon/Mars exploration fieldwork.

The current console focuses on two contrasting Pakistan case studies:

1. **Koh-i-Sultan / Chagai** — a Smithsonian-catalogued Pleistocene volcanic field and a candidate for volcanic/hydrothermal reconnaissance, alteration mapping and remote-sensing-to-ground validation. USGS maps the Koh-i-Sultan Volcanic Group as agglomerate, tuff and andesitic lava; it is not a basaltic composition match for Mars.
2. **Hispar Glacier / Karakoram** — a cryosphere case study for ice/debris mapping, remote-sensing interpretation and field-data validation.

The console assembles verified climate snapshots, Sentinel-2 scene metadata and true-colour previews, matched-scale terrain descriptors, institutional baselines and explicit data gaps. It does not claim that either Earth location is a complete Moon/Mars analog. The current work identifies task-specific analog potential, not a proven globally novel analog discovery. The USGS geological report is cited as an existing baseline, not claimed as new field geology.

### Mission Rehearsal Lab
The live console includes an interactive, evidence-led terrain comparator. Select **Shackleton Rim (Moon)** or **Nili Patera (Mars)**, then choose a task (terrain morphology, lunar cryosphere/ice-debris field-method rehearsal, or Martian volcanic outcrop/alteration mapping). It compares three measured descriptors—median slope, P90 slope and P90 3×3 local relief—between the planetary reference and both Pakistan case studies at approximately common 925 m support. For each dimension, it shows absolute differences and which Earth site is numerically closer. It then creates a task-specific field protocol and exports an auditable JSON record containing source values, differences, recommendations, methods and limitations.

The comparator intentionally does **not** collapse the three metrics into a universal similarity score. A numerically closer terrain descriptor does not prove matching geology, surface material, rover trafficability, landing safety, ice access or complete planetary analogy. The ~925 m products support regional reconnaissance planning only; rover-scale work requires higher-resolution data and independent validation. The lab also extracts the three lowest-precipitation months from the NASA POWER monthly climatology for each Earth site, shows the associated mean air temperature and 10 m wind, and adds a field kit checklist for the chosen task. These are seasonal planning signals, not weather forecasts or site-access/safety recommendations. The exported JSON includes the climate summaries and equipment checklist.

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

### NASA Earthdata / CMR discovery

The public NASA Common Metadata Repository API is queried for Terra/Aqua MODIS land-surface-temperature collections, MODIS land cover and MERRA-2 aerosol diagnostics. Ten MOD11A2 granule metadata records were discovered for each Pakistan study box, and one October 2026 global MERRA-2 aerosol granule record was discovered. These are catalogue records only: protected LP DAAC/GES DISC data have not yet been downloaded or decoded, and the MERRA-2 granule is global rather than site-clipped.

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

### NASA LRO LOLA / Shackleton Rim

A public NASA LRO LOLA PDS GDR 80 m south-polar elevation grid (LDEM_80S_80M) and matching observation-count grid (LDEC_80S_80M) are processed around Shackleton Rim. The 29.6 × 29.6 km window contains 90,000 native cells; the interpolated elevation surface is valid throughout, and 89,996 cells have positive laser-return counts. The DEM is also averaged to 32 × 32 cells at approximately 925 m support so the coarse terrain profile can be compared with the Earth/Mars profiles.

At ~925 m support the Shackleton window has median slope 13.40°, P90 slope 30.94°, and P90 3×3 local relief 1,391 m (the relief statistic spans a ~2.775 km footprint). These values describe a rugged selected rim window; they do not establish suitability for landing or a permanent base.

The original PGDA 5 m Site04 files were inaccessible from the automated runner. The working 80 m products are read from NASA's LOLA PDS GDR mirror at MIT Imbrium. The surface DEM is interpolated, so LDEC counts are measurement support—not a mask for discarding interpolated elevation. Diviner annual thermal / water-ice-permafrost products and shadow/illumination analysis are not integrated.

### NASA DSCOVR / EPIC
The pipeline retrieves an optional full-disc natural-colour Earth image from the public GSFC EPIC endpoint. It is global context only and is not used in site-scale metrics. No api.nasa.gov key is required for this endpoint.

## Institutional and planetary evidence
- **EvK2CNR:** Existing Pakistan Glacier Inventory: 13,032 glaciers, combined area 13,546.93 km². We acknowledge and link this prior work; the project does not claim to have discovered or remapped those glaciers. EvK2CNR has also published preliminary Pakistan glacial-lake inventory work.
- **SUPARCO / UN-SPIDER:** Official remote-sensing and disaster-monitoring capabilities, recommended practices, DisasterWatch and NatCat are documented. No public bulk-data/API integration from DisasterWatch or Space4Climate has yet been verified.
- **NDMA:** Official hazard projections, disaster early warnings and the 2026 Vulnerable Glaciers and Glacial Lakes Atlas listing are linked as existing institutional work. No redistributable geospatial layer has yet been ingested.
- **NASA LRO LOLA:** An 80 m south-polar LDEM and matched LDEC count map are processed around Shackleton Rim. Native 80 m terrain descriptors and a coarse ~925 m profile are stored. **Diviner** annual surface-temperature and water-ice-permafrost products remain reference-only; illumination/PSR mapping is not yet integrated.
- **NASA Global Volcano Hazard Frequency:** Historical coarse grid is linked as context only; it is not current volcano alerting or site-scale geology.

See docs/AGENCY_DATA_AUDIT.md for source status, docs/DATA_SOURCES.md for provenance, and docs/RESOURCE_INTEGRATION_MATRIX.md for the status of every NASA and partner resource supplied for the challenge.

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
- an interactive Mission Rehearsal Lab that compares Earth/Moon/Mars terrain descriptors dimension-by-dimension and exports field protocols.

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
- USGS maps Koh-i-Sultan as agglomerate, tuff and andesitic lava; no basaltic equivalence with Syrtis Major is claimed. No site-scale mineral map or field samples are integrated.
- No official EvK2CNR glacier shapefile is redistributed in this repository.
- NDMA, SUPARCO DisasterWatch and Space4Climate are portal/reference status until data endpoints, access terms and product licences are verified.
- Diviner annual surface-temperature and water-ice-permafrost products are not yet processed. LOLA elevation is interpolated; its LDEC return-count support is reported separately. The Shackleton profile is terrain context, not a landing-safety or base-suitability assessment.
- NASA Earthdata CMR discovery is not measurement ingestion; MODIS LST and MERRA-2 aerosol granules remain to be downloaded, QA-screened and decoded. NASA POWER is gridded climate context, not local instrumentation.
- Field access, permits, site-level geology and scientist review remain necessary.

## Licence
Original project code and text are MIT-licensed. NASA, Copernicus, Microsoft, USGS, EvK2CNR and other third-party products retain their original terms and attribution.

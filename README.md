# ANALOG-X — Pakistan Analog Evidence Operations

**NASA Space Apps Challenge 2026** · Team **X Æ A-Xii** · Participant **Muhammad Usman Mughal**

## Live project
- Evidence Operations console: https://usmanmughal96.github.io/analog-x/
- Seven-slide project demo: https://usmanmughal96.github.io/analog-x/demo.html
- Source repository: https://github.com/usmanmughal96/analog-x

## What the product does
ANALOG-X is a Pakistan-first evidence and field-readiness atlas for candidate terrestrial environments relevant to Moon/Mars exploration fieldwork.

The console now covers ten Earth study/reference windows: four Pakistan field leads (Koh-i-Sultan, Hispar Glacier, Chagai small salt playas and Hamun-i-Mashkel) plus six global reference environments (Dallol, Atacama, McMurdo Dry Valleys, Haughton, Iceland and Death Valley).

1. **Chagai small salt playas near Nok Kundi** — an under-characterized evaporite/playa-process lead grounded in a 1974 NASA technical report that identifies two small salt-surfaced playas. Its coordinates and bounding box are screening references, not a surveyed polygon.
2. **Hamun-i-Mashkel / Kharan Basin** — a regional closed-basin/intermittent-playa process candidate. Its point and AOI remain approximate; basin-scale hydrology needs current verification.
3. **Koh-i-Sultan / Chagai** — a documented Pleistocene volcanic field for volcanic/hydrothermal reconnaissance, alteration mapping and remote-sensing-to-ground validation. USGS maps agglomerate, tuff and andesitic lava; it is not a basaltic composition match for Mars.
4. **Hispar Glacier / Karakoram** — a cryosphere case study for ice/debris interpretation and cold-region field-method rehearsal, using EvK2CNR's existing glacier inventory as a prior baseline.

The console combines NASA POWER climatology, Sentinel-2 scene discovery and spectral-context screens, true-colour previews, Copernicus DEM terrain descriptors, Moon/Mars reference profiles, institutional baselines and explicit data gaps. The two playa areas are research leads—not confirmed mineral/brine deposits or validated new-to-science analogs. No site is presented as a complete Moon/Mars analog.

### Mission Rehearsal Lab and evidence decision layer
The Mission Rehearsal Lab compares regional terrain descriptors for selected Earth sites against **Shackleton Rim (Moon)** and **Nili Patera (Mars)** separately. It reports median slope, P90 slope and P90 3×3 local relief at approximately common 925 m support, plus absolute differences and the closest Earth profile on each descriptor. The app also derives three low-precipitation months from NASA POWER climatology and provides task-specific protocols and equipment checklists. These are planning signals, not forecasts or safe-access guarantees.

The Agent Bay adds a wider **10-site candidate decision engine**. It reads each site's documented rehearsal tasks and environment tags, filters by Moon/Mars eligibility, and displays four separate evidence layers: NASA POWER, Sentinel-2 spectral context, processed terrain and source references. Strict mode requires mission eligibility, a documented task overlap, a traceable source, NASA POWER and at least one site-specific Sentinel-2 or processed terrain layer. Exploratory mode surfaces weaker environmental-context leads with their limits. The ordering is a transparent research-triage rule, not a calibrated similarity score or probability. Ties remain ties.

The two systems intentionally do **not** collapse unlike measurements into a universal Earth-to-Moon/Mars percentage. A numerically closer terrain descriptor does not prove matching geology, surface material, rover trafficability, landing safety, ice access or complete planetary analogy. The ~925 m products support regional reconnaissance only; rover-scale work requires higher-resolution data and independent validation. The interactive Field School adds persistent learning XP for the quiz; XP has no effect on the scientific decision.


## Discovery Atlas and Agentic Science Operations

The live portal includes a map-led candidate atlas with ten curated Earth seeds. It separates **under-characterized candidate leads** (the two Balochistan playa study windows) from established Pakistan and global references. This is a documented seed set, not an exhaustive global scan.

The Agent Bay has four deterministic evidence specialists: terrain morphology, climate/campaign planning, surface spectral context and evidence integrity. Its offline review runs without an LLM/API key and exports a JSON decision brief. The cloud Mission Director is optional; it is not a dependency for core assessments. The Worker source and deployment instructions are in docs/AGENTIC_AI_SETUP.md. Model output is not a measurement or validation result.

The four-stage Field School simulator teaches playa/evaporite, volcanic mapping, lunar cryosphere and terrain-data-quality decisions. Its learning XP is browser-local and does not affect scientific ranking. A completed scenario can be sent straight into the offline Mission Director for evidence review.

## Live web layers and offline resilience

The main console now prefers a real interactive Leaflet map. It uses standard OpenStreetMap streets as its free default basemap, and exposes NASA GIBS VIIRS corrected-reflectance true-colour imagery as an optional dated WMS overlay. Study-site markers use the curated WGS84 coordinates already stored in the science pack.

The climate panel attempts a browser-side NASA POWER Daily Point API request for the selected site, using the latest 30-day window ending three days before the current date to reduce near-real-time data-latency issues. It reports the returned period explicitly and labels the values as a 30-day daily mean. If the live request fails, the console retains the committed NASA POWER climatology snapshot and all existing local science assets.

The map itself degrades to the built-in schematic SVG locator if the Leaflet CDN fails or the live basemap cannot load its tiles. The offline locator is deliberately labelled as schematic and is not presented as a geospatial basemap. Live map tiles and NASA imagery require an internet connection; the science pack, saved terrain profiles, quicklooks and offline tools remain local.

## Verified integrations

### NASA POWER
Server-side GitHub Actions fetch the public NASA POWER Climatology API for ten coordinates: Koh-i-Sultan, Hispar Glacier, Chagai small salt playas, Hamun-i-Mashkel, Dallol, Atacama, McMurdo Dry Valleys, Haughton impact structure, Iceland and Death Valley.

Variables include T2M, T2M_MAX, T2M_MIN, RH2M, WS10M, PRECTOTCORR and ALLSKY_SFC_SW_DWN. The current committed index has ten records and no failed sites. Records include original source response, request URL, community, timestamps, monthly values, metrics and missing-parameter information.

NASA POWER is gridded climatology, not a ground weather station.

### Microsoft Planetary Computer / Sentinel-2 L2A
The anonymous STAC API is queried for ten Earth study/reference windows: four Pakistan field leads plus Dallol, Atacama, McMurdo Dry Valleys, Haughton, Iceland and Death Valley. The pipeline records acquisition date, platform, cloud fraction, MGRS tile and asset provenance, then obtains a public SAS token and clips 768×768 true-colour previews from COG assets.

Current previews:
- data/pakistan/quicklooks/koh_i_sultan.png
- data/pakistan/quicklooks/hispar_glacier.png
- data/pakistan/quicklooks/chagai_small_playas.png
- data/pakistan/quicklooks/hamun_i_mashkel.png

This is RGB visual evidence, not mineral classification or field validation. Copernicus Sentinel data terms apply.

### NASA Earthdata / CMR discovery

The public NASA Common Metadata Repository API is queried for Terra/Aqua MODIS land-surface-temperature collections, MODIS land cover and MERRA-2 aerosol diagnostics. Ten MOD11A2 granule metadata records were discovered for each Pakistan study box, and one October 2026 global MERRA-2 aerosol granule record was discovered. These are catalogue records only: protected LP DAAC/GES DISC data have not yet been downloaded or decoded, and the MERRA-2 granule is global rather than site-clipped.

### Copernicus DEM GLO-30 + NASA MOLA MEGDR 64 ppd
The project computes coarse matched-support terrain profiles for up to ten Earth windows where Copernicus GLO-30 tiles are available, plus Nili Patera on Mars. Shackleton Rim has a separate LOLA terrain profile aggregated to the same nominal support.

Earth Copernicus DEM GLO-30 DSM tiles are mosaicked across neighbouring one-degree tiles, reprojected to local UTM and averaged to approximately 925 m. Mars MOLA MEGDR topography and observation-count rasters at 64 pixels/degree are cropped around Nili Patera. Slope and 3×3 local relief are calculated on approximately comparable support.

Current terrain output:
- data/terrain/terrain_comparison.json
- data/terrain/koh_i_sultan_copdem_hillshade.png
- data/terrain/hispar_glacier_copdem_hillshade.png
- data/terrain/chagai_small_playas_copdem_hillshade.png
- data/terrain/hamun_i_mashkel_copdem_hillshade.png
- data/terrain/nili_patera_mola_hillshade.png

**Coverage caveat:** the selected Nili Patera MOLA window has 50.53% valid observed-cell coverage (567/1,122 cells) and 87 complete 3×3 neighborhoods. The app flags this as limited coverage. The results are coarse terrain descriptors—not a geological-equivalence score, rover safety assessment or landing suitability rating. Absolute elevation is not compared across different vertical datums. Earth DSM is not bare-earth elevation.

### NASA LRO LOLA / Shackleton Rim

A public NASA LRO LOLA PDS GDR 80 m south-polar elevation grid (LDEM_80S_80M) and matching observation-count grid (LDEC_80S_80M) are processed around Shackleton Rim. The 29.6 × 29.6 km window contains 90,000 native cells; the interpolated elevation surface is valid throughout, and 89,996 cells have positive laser-return counts. The DEM is also averaged to 32 × 32 cells at approximately 925 m support so the coarse terrain profile can be compared with the Earth/Mars profiles.

At ~925 m support the Shackleton window has median slope 13.40°, P90 slope 30.94°, and P90 3×3 local relief 1,391 m (the relief statistic spans a ~2.775 km footprint). These values describe a rugged selected rim window; they do not establish suitability for landing or a permanent base.

The original PGDA 5 m Site04 files were inaccessible from the automated runner. The working 80 m products are read from NASA's LOLA PDS GDR mirror at MIT Imbrium. The surface DEM is interpolated, so LDEC counts are measurement support—not a mask for discarding interpolated elevation. Diviner PRP V2.0 has been processed for 6,823 Shackleton-window triangles: median annual average temperature at 2 cm depth is 103.786 K and median annual maximum surface temperature is 238.568 K. These are historical model-derived thermal summaries. The ice-depth field contains negative and -999 censored values and is withheld pending QA; no accessible-ice claim is made. Illumination / PSR mapping is not integrated.

### NASA DSCOVR / EPIC
The pipeline retrieves an optional full-disc natural-colour Earth image from the public GSFC EPIC endpoint. It is global context only and is not used in site-scale metrics. No api.nasa.gov key is required for this endpoint.

## Institutional and planetary evidence
- **EvK2CNR:** Existing Pakistan Glacier Inventory: 13,032 glaciers, combined area 13,546.93 km². We acknowledge and link this prior work; the project does not claim to have discovered or remapped those glaciers. EvK2CNR has also published preliminary Pakistan glacial-lake inventory work.
- **SUPARCO / UN-SPIDER:** Official remote-sensing and disaster-monitoring capabilities, recommended practices, DisasterWatch, NatCat and Space4Climate are documented as institutional context. The repository does **not** claim ingestion from SUPARCO SGSS / Space4Climate / DisasterWatch: a public machine-readable endpoint, product schema, AOI coverage and reuse licence have not been verified.
- **NDMA:** Official hazard projections, disaster early warnings and the 2026 Vulnerable Glaciers and Glacial Lakes Atlas listing are linked as existing institutional work. No redistributable geospatial layer has yet been ingested.
- **NASA LRO LOLA + Diviner:** An 80 m south-polar LDEM and matched LDEC count map are processed around Shackleton Rim. Diviner PRP V2.0 temperature fields are processed for 6,823 Shackleton-window triangles (median annual-average temperature at 2 cm: 103.786 K; median annual maximum surface temperature: 238.568 K). These are historical model-derived summaries. The ice-depth field contains negative and censored values requiring QA; no accessible-ice claim is made. Formal illumination / PSR mapping is not integrated.
- **NASA Global Volcano Hazard Frequency:** Historical coarse grid is linked as context only; it is not current volcano alerting or site-scale geology.

See `docs/AGENCY_DATA_AUDIT.md` for source status, `docs/DATA_SOURCES.md` for provenance, `docs/RESOURCE_INTEGRATION_MATRIX.md` for integration status, and `docs/COMPETITOR_METHOD_NOTES.md` for the public-method benchmark and source-code reuse record.

## What is differentiated
Other public 2026 challenge entries already demonstrate analog ranking, mission-to-experiment planning and topographic/lighting comparisons. ANALOG-X does not claim those broad ideas are globally unsolved.

Our contribution is a Pakistan-first, open-data evidence workflow with a reusable global seed atlas:
- NASA POWER climatology for ten Earth coordinates;
- Sentinel-2 L2A scene discovery, spectral-context screening and RGB quicklooks across ten Earth study/reference windows;
- Copernicus DEM GLO-30 terrain profiles for all ten Earth study/reference windows in the current processing run, compared at coarse support with Mars MOLA and lunar LOLA;
- a reproducible 5.55 km regional-window scan of the ten existing Earth grids (7,290 valid Earth windows), with lunar/Martian reference windows and 500-draw weight-sensitivity diagnostics; this is a regional scan, not global coverage;
- explicit MOLA observed-cell coverage and LOLA return-count / interpolation caveats;
- a mission-specific candidate decision layer that distinguishes documented task overlap, environmental context and four independent evidence layers;
- an offline coordinate-proximity Scout over ten curated candidate/reference points (not an exhaustive global cell search or fresh-data API);
- transparent attribution of existing EvK2CNR, NDMA, SUPARCO/UN-SPIDER and NASA source material;
- field protocols, equipment planning, next measurements and explicit planetary non-transferability limits.

The ten-site atlas is a curated starting set—not an exhaustive global scan. The two Chagai playa study windows are under-characterized research leads, not newly discovered or validated mineral/evaporite deposits.

No single universal cross-domain analog score is calculated. The new regional scanner exposes a separate terrain-only screening index, with its scope and limitations stated explicitly.


## Field Evidence Passport / offline differentiator

The Field Evidence Passport is the Pakistan-first field-validation feature. Select an Earth candidate, Moon/Mars target and named field experiment; inspect six independent evidence layers; stress-test claims that are not supported; and export a site-specific proposed protocol. It does not create a planetary similarity percentage or certify mineral resources, accessible ice, landing safety or rover trafficability.

The local field notebook stores user-entered GNSS station observations, methods, notes and optional photos in browser IndexedDB. Records can be exported/imported as JSON, CSV or GeoJSON. The service worker caches the app shell and published science pack after the first connected visit. The ten-seed Coordinate Scout measures proximity to bundled candidate/reference points; it is not an exhaustive global raster search.

## Offline use and optional backend

Open the live portal once while connected, allow the offline pack to cache, then reopen it from the same browser/device. The deterministic Mission Director, terrain profiles, Field School, Field Evidence Passport, local candidate-proximity Scout and station-record exports do not require a cloud LLM or live NASA API. See [Offline & Backend Setup](docs/OFFLINE_AND_BACKEND.md).

GitHub Pages is static hosting and cannot run a persistent API. The repository includes a self-hostable FastAPI service with PostgreSQL support, Dockerfile and Compose configuration for shared field-record storage. It is an optional deployment path, not a publicly provisioned live backend in this release. The offline browser notebook remains usable without it.

## Run the data pipelines
NASA POWER:
    python -m pip install --upgrade requests
    python scripts/fetch_nasa_power.py

Scene discovery and Sentinel-2 previews:
    python -m pip install --upgrade requests rasterio pillow numpy
    python scripts/fetch_public_evidence.py
    python scripts/build_scene_quicklooks.py

Terrain comparison and regional window scan:
    python -m pip install --upgrade requests rasterio pillow numpy scipy
    python scripts/build_terrain_comparison.py
    python science/build_regional_window_scan.py

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
- Diviner PRP V2.0 has been streamed and processed for a 29.6 × 29.6 km analyst-defined Shackleton comparison window (6,823 triangles). The annual-average temperature-at-2-cm and annual-maximum surface-temperature summaries are available; the ice-depth field includes negative values and -999 censored values and is withheld from scientific interpretation pending QA. These values do not demonstrate exposed or accessible lunar ice. LOLA elevation is interpolated; its LDEC return-count support is reported separately. The Shackleton profile is terrain context, not a landing-safety or base-suitability assessment.
- NASA Earthdata CMR discovery is not measurement ingestion; MODIS LST and MERRA-2 aerosol granules remain to be downloaded, QA-screened and decoded. NASA POWER is gridded climate context, not local instrumentation.
- Chagai's historic playa coordinates and Hamun-i-Mashkel's point are not surveyed AOIs; verify current geomorphology, hydrology, land tenure and access before field use.
- Hamun-i-Mashkel's spectral screen contains 109,692 valid pixels in a 1,108 × 99-cell 20 m grid; this is a narrow Sentinel-2 sample, not a basin-wide survey.
- The playa terrain profiles describe 30 km windows at ~925 m support; they do not establish salt-crust thickness, bearing strength, brine, mineralogy or rover traversability.
- Field access, permits, site-level geology and scientist review remain necessary.

## Licence
Original project code and text are MIT-licensed. NASA, Copernicus, Microsoft, USGS, EvK2CNR and other third-party products retain their original terms and attribution.


## New: Analog Transferability & Failure Analysis (ATFA)

Open the interactive [ATFA science module](https://usmanmughal96.github.io/analog-x/transferability.html). It shifts the unit of analogy from whole-site resemblance to **specific field experiments and physical processes**: what can be rehearsed on Earth, where the analogy breaks, and what measurement is needed next.

The module includes ten curated Earth study/reference sites, experiment-level transferability dossiers, explicit evidence-state auditing, lunar Shackleton / Mars Nili Patera reference context, a Leaflet map with OpenStreetMap and optional NASA GIBS imagery, Plotly evidence charts and a 3D site/pathway landscape. The 3D vertical axis is experiment-pathway count, not elevation or a similarity score.

### New reproducible pipelines

- `science/build_transferability.py` builds the ATFA site dossiers from the existing NASA POWER, Sentinel-2, Copernicus DEM, MOLA, LOLA and candidate catalogue outputs.
- `science/build_regional_window_scan.py` derives matched-support 5.55 km regional windows, terrain-only Moon/Mars proximity indices and local rank-sensitivity outputs from the ten existing Earth DEM areas.
- `scripts/fetch_pds_search.py` queries the public NASA PDS Search API for Nili Patera, MOLA, HiRISE, Shackleton, LOLA and Diviner product metadata.
- `scripts/fetch_modis_browse.py` queries NASA CMR for MOD11A2 V061 8-day LST granules over ten Earth sites and downloads available public browse JPEGs.

The weekly/manual GitHub Actions workflow validates the science pack and dashboard JavaScript, then commits generated metadata and browse assets. Browse JPEGs are tile-level visual context—not AOI-clipped or calibrated LST measurements. MODIS science HDF access and QA decoding remain separate. PDS metadata is discovery, not binary ingestion. See `docs/ANALOG_TRANSFERABILITY_AND_FAILURE_ANALYSIS.md`.

### Regional terrain-window discovery

Open the [Regional Discovery Scan](https://usmanmughal96.github.io/analog-x/discovery.html) to explore the newly generated sub-window shortlist. The current run derives **7,290 valid Earth windows** (729 in each of ten pre-selected 30 km areas), **729 Shackleton windows** and **21 valid Nili Patera windows**. Each window is approximately 5.55 km across and retains approximately 925 m terrain support. The shortlist also carries the matching ATFA site dossier: priority experiment, named rehearsal pathways, analogy breaks, next measurements and individual evidence-layer states. This context is displayed separately and does not affect the terrain index.

The displayed 0–100 terrain index is calculated from equal-weight IQR-normalized differences in median slope, P90 slope and P90 3×3 local relief. Every shortlist entry also exposes ATFA experiment context from the corresponding site dossier; these qualitative research pathways are not mixed into the numerical terrain calculation. A 500-draw deterministic weight-sensitivity analysis reports how often a window stays in the top decile of its own parent area. This is a regional screening and robustness aid—not a whole-Earth search, probability, confidence interval, geological analogue score or landing/mobility assessment. The source parent grids remain coarse; overlapping windows are spatially dependent; displayed coordinates are approximate map locators derived from nominal grid spacing, not surveyed coordinates. See `docs/REGIONAL_WINDOW_SCAN.md` for the method and interpretation.

## Interactive views and backend

The ATFA module includes a monthly NASA VIIRS true-colour time scrub/animation and a 3D site/pathway scatter view (z = authored experiment-pathway count, not elevation). The FastAPI service now exposes read-only ATFA, PDS metadata and MODIS provenance routes alongside the existing paginated field-notebook CRUD. `backend/smoke_test.py` exercises the science reads and temporary field-record create/list/delete flow in CI. The public GitHub Pages app remains fully usable without deploying the optional API.

The 3D terrain-twin view renders source-derived ~925 m elevation grids from Copernicus DSM for the global Earth sites for all ten Earth sites, Mars MOLA and lunar LOLA, with each grid expressed relative to its own median elevation. It does not imply cross-body vertical registration or rover/landing safety.

## NASA Space Apps submission material

See [`docs/CHALLENGE_SUBMISSION_BRIEF.md`](docs/CHALLENGE_SUBMISSION_BRIEF.md) for the scientific narrative, current evidence, limitations and next validation steps.

## Latest verified science snapshot (18 Nov 2026)

- 10 Earth study/reference sites; 10 NASA POWER profiles.
- 10/10 Copernicus DEM GLO-30 local grids (32×32 at ~925 m support), plus Mars MOLA (33×34) and lunar LOLA (32×32) grids.
- 20 public NASA MOD11A2 browse JPEGs downloaded and indexed across the ten Earth sites. These are visual browse assets, not calibrated LST arrays.
- 41 experiment pathways across nine tracks, including biosignature/contamination-control method rehearsal.
- 500 unique PDS observational metadata records across six capped target/instrument queries; MOLA, LOLA and Diviner instrument queries returned records. The HiRISE target-filtered API query returned no relevant rows; its PDS RDR dataset profile is linked in the dashboard.
- Regional terrain-window scan: 7,290 valid Earth sub-windows, 729 Shackleton windows and 21 Nili Patera windows; up to 30 spatially separated shortlist windows per target. The scan is confined to the ten existing parent regions.
- FastAPI read endpoints and field-notebook create/list/delete behavior passed CI smoke tests. The public static site loads the science pack without requiring the optional API.

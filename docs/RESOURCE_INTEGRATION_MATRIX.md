# NASA Space Apps Resource Integration Matrix

**Project:** ANALOG-X — Pakistan Analog Evidence Operations Atlas  
**Repository:** https://github.com/usmanmughal96/analog-x  
**Status review:** 18 November 2026

## How to read this matrix

- **Integrated — data:** a source product or data values have actually been fetched/processed and are stored in the repository.
- **Integrated — discovery:** a live/search API has been queried and catalogue metadata or scene/granule records are stored, but the science data itself has not been decoded.
- **Visual layer:** imagery or map tiles are displayed for context only.
- **Reviewed / reference:** the official source, product or access instructions have been checked, but no science data from that source is in the application.
- **Blocked / pending:** an attempted integration failed or requires a separate account, access approval, or manual download.

The NASA challenge says participants may consider the listed portals and dimensions. It does not require every listed agency or product to be integrated. The submission should demonstrate enough trustworthy Earth, Moon and Mars evidence to support the specific analog claim, explain what matches and what does not, and show how the site helps exploration.

## NASA Earth resources

| Resource | Current status | What ANALOG-X actually uses | What is not yet done / access notes |
|---|---|---|---|
| NASA POWER | **Integrated — data** | Public climatology snapshots for ten Earth study/reference coordinates; T2M, T2M_MAX, T2M_MIN, RH2M, WS10M, PRECTOTCORR, ALLSKY_SFC_SW_DWN. Original responses and timestamps are retained. | Gridded climatology, not station measurements. Does not measure rock temperature, dust flux or water resources. |
| NASA Earthdata Search | **Integrated — discovery** | The NASA Common Metadata Repository (CMR) API is queried by scripts/fetch_nasa_cmr_catalog.py. Four collection records and site/period granule searches are saved to data/nasa/earthdata_cmr_catalog.json. | Discovery is not ingestion. MOD11A2 links returned as protected LP DAAC data paths; Earthdata Login and provider authorization are required to download. |
| Terra MODIS MOD11A2 V061 | **Integrated — discovery + browse visuals** | CMR granule metadata was discovered for the ten Earth study/reference windows; 20 public browse JPEGs (two per Earth site in the current release) are downloaded and indexed. | The JPEGs are tile-level visual context, not AOI-clipped or calibrated LST arrays. No science HDF granule has been downloaded/decoded here; scale factors, per-pixel QA, day/night layers, fill values and temporal statistics remain unprocessed. |
| Aqua MODIS MYD11A2 V061 | **Collection discovered** | The global collection record was found via CMR. | No Pakistan granule search or data download is included in this release. |
| MODIS MCD12Q1 V061 | **Collection discovered** | The global 500 m annual land-cover collection record was found via CMR. | No site-specific granule ingestion or land-cover classification is included. |
| NASA MERRA-2 M2T1NXAER V5.12.4 | **Integrated — discovery** | CMR found the 1 October 2026 global hourly aerosol-diagnostic NetCDF granule; its catalogue metadata is recorded. | The query is global, not clipped to either Pakistan site. No NetCDF data are downloaded or decoded. Dust column mass, surface concentration and AOT are not yet calculated for either site. GES DISC data download requires Earthdata Login/authorization. |
| NASA Worldview | **Visual layer / linked** | The app uses NASA GIBS VIIRS true-colour WMTS tiles as a global map context layer. | The Worldview user interface is not embedded, and its full time-series exploration/download workflow is not integrated. |
| NASA GIBS | **Integrated — visual layer** | Public VIIRS true-colour GIBS tiles are used on the map for broad context. | These are browse tiles. The map layer does not substitute for analysis-ready science granules or local AOI cloud masks. |
| NASA Earthdata Login | **Access dependency identified** | The resource matrix records where EDL is needed. | The api.nasa.gov API key supplied during development is not an Earthdata Login credential. Never publish either credential. |
| NASA Global Volcano Hazard Frequency and Distribution | **Reference only** | Official dataset page is linked in the portal. | Not downloaded or processed. It is a coarse historical event-frequency product, not current activity, lithology or site-scale hazard assessment. |

## NASA Moon and Mars resources

| Resource | Current status | What ANALOG-X actually uses | What is not yet done / access notes |
|---|---|---|---|
| NASA Planetary Data System (PDS) | **Integrated — discovery + selected data products** | The public PDS Search API returns 500 unique observational-product metadata records across six capped target/instrument queries. MOLA, LOLA and Diviner instrument queries return records. Separate LOLA elevation/count grids and the Diviner PRP table are processed as described below. | The 500 catalogue records are metadata, not 500 downloaded/decoded science products. The target-filtered HiRISE query returned no relevant rows; its RDR collection profile is linked separately. Formats, detached labels, coordinate systems, scale factors and uncertainty remain product-specific. |
| LRO LOLA — south-pole 5 m site products (PGDA product 78) | **Blocked / pending** | NASA's Site04 file list was tested from GitHub Actions. | Primary PGDA host returned HTTP 403 for related assets and failed pixel-range reads for the elevation TIFF; alternate core2 host did not resolve. This 5 m product is not used in the application. |
| LRO LOLA — south-pole PDS GDR 80 m (MIT Imbrium mirror) | **Integrated — data** | LDEM_80S_80M.JP2 and matching LDEC_80S_80M.JP2 plus PDS labels/AUX metadata from https://imbrium.mit.edu/DATA/LOLA_GDR/POLAR/JP2/. | Processed for a 29.6 × 29.6 km Shackleton Rim window (370 × 370 cells). 89,996/90,000 native cells have positive returns. LDEM is interpolated; LDEC is measurement support, not a validity mask. The 80 m DEM is area-averaged to 925 m for common-support comparison. |
| LRO Diviner PRP V2.0 | **Integrated — data (thermal summary)** | `scripts/process_diviner_prp.py` streams the PDS4 south-polar table, validates the label/units and summarizes 6,823 triangles in an analyst-defined 29.6 × 29.6 km Shackleton Rim window. Median annual-average temperature at 2 cm is **103.786 K**; median annual-maximum surface temperature is **238.568 K**. Output: `data/moon/shackleton_diviner_prp.json`. | These are historical thermal-model summaries, not in-situ measurements. The ice-depth field has 4,309 numerically usable values and 2,514 `-999` censored entries; negative values also remain in the valid numeric sample. It is not used for an accessible-ice conclusion. Product units/semantics and uncertainty must be preserved. No formal illumination/PSR map is integrated. |
| MGS MOLA MEGDR | **Integrated — data, limited support** | 64 pixels/degree topography and observation-count grid are processed around Nili Patera, Syrtis Major. | Current 30 km window has 50.53% valid MOLA observed-cell coverage and only 87 complete 3×3 neighborhoods. Terrain profile is provisional and coarse; not a landing safety or rover traversability model. |
| Mars planetary comparison | **Integrated — terrain descriptors only** | Earth Copernicus DEM DSM is averaged to approximately 925 m support and compared with MOLA slope/local-relief descriptors. | No CRISM mineralogy, THEMIS thermal inertia, atmosphere, regolith strength, dust activity or rover mobility model is integrated. Absolute elevations are not compared across vertical datums. |

## International space-agency and partner resources

| Resource | Current status | What ANALOG-X actually uses | What is not yet done / access notes |
|---|---|---|---|
| CSA RADARSAT-1 | **Access reviewed / not integrated** | Official CSA/EODMS data access route and public-data policy were reviewed. | No SAR scene is downloaded for either Pakistan AOI. RADARSAT-1 open archive access and product-specific licence/coverage must be verified in EODMS. |
| CSA RADARSAT Constellation Mission (RCM) | **Access reviewed / not integrated** | CSA public data access policy was checked. | Public access is product-, geography- and resolution-limited; EODMS registration is required. The Canadian land mosaic is not relevant coverage for Pakistan. |
| CSA SAR Python tutorial | **Reference only** | Linked as an implementation learning resource. | No SAR processing workflow is currently part of the application. |
| ESA Copernicus Data Space Ecosystem / DEM GLO-30 | **Indirect integration via Microsoft Planetary Computer** | Sentinel-2 L2A imagery and Copernicus DEM GLO-30 are queried and processed through Microsoft Planetary Computer. Ten Earth regions now have matched-support ~925 m terrain grids plus separate ~30 m parent-area DSM slope/3×3-relief diagnostics; all ten passed current fine-grid coverage (98.36–100%). | The ~30 m diagnostic is Earth-only parent-area context, not matched to Moon/Mars or local to each sub-window. The ~925 m layer is the matched-support cross-planet input. Neither layer is rover-scale. Direct CDSE STAC/OData/Sentinel Hub/openEO calls are not used. |
| ESA Open Science Catalogue | **Reference only** | Official catalogue and STAC-based discovery capability are documented. | No ESA Open Science Catalogue research product or workflow has been downloaded or integrated. |
| JAXA G-Portal / GCOM-C SGLI | **Access reviewed / not integrated** | Official G-Portal documentation identifies standard and near-real-time HDF products, GUI search/download and SFTP access. | No JAXA product has been queried or processed. A G-Portal account and SFTP credentials may be needed for bulk access. |

## Pakistan and other institutional sources

| Resource | Current status | What ANALOG-X actually uses | What is not yet done / access notes |
|---|---|---|---|
| SUPARCO Space4Climate / SGSS | **Portal reviewed / reference only** | Official portal themes, institutional context and source links are documented. | No machine-readable public endpoint, exact AOI product, product schema, coverage, access terms and redistribution licence have been verified together. No Space4Climate/SGSS science layer is claimed as ingested. |
| SUPARCO DisasterWatch / SACRED / NatCat / SACCS | **Capability and method reference** | Existing services and UN-SPIDER recommended practices are acknowledged. | No portal raster/layer is claimed as integrated. Obtain a documented service endpoint, data licence and product metadata before ingestion. |
| NDMA / NEOC | **Official product reference** | Hazard projections, early-warning products and the 2026 Vulnerable Glaciers and Glacial Lakes Atlas are acknowledged. | No atlas geometry, web-service layer or redistributable geospatial file has been integrated. |
| UN-SPIDER / UNOOSA | **Method reference** | Recommended flood, drought and fire remote-sensing workflows and SUPARCO's institutional role are documented. | This is methodological reference, not a new UN-SPIDER data feed. |
| EvK2CNR / Pakistan Glacier Inventory | **Existing baseline acknowledged** | Published inventory facts and official project links are used to contextualize Hispar. | The project does not claim to discover the national inventory. The selected catalogue endpoint did not return machine-readable vector data; no official glacier polygon dataset is redistributed. |

## Scientific interpretation of the Pakistani candidates

### Koh-i-Sultan / Chagai
The Smithsonian Global Volcanism Program identifies Sultan as a Pleistocene volcanic field at approximately 29.1°N, 62.8°E. The USGS Chagai report maps the Koh-i-Sultan Volcanic Group as agglomerate, tuff and andesitic lava. This is important: the site is **not a direct basalt-composition match** for basaltic Martian terrains such as parts of Syrtis Major.

A defensible analogy is volcanic-field and hydrothermal/alteration-process fieldwork: mapping volcanic materials, recognizing alteration zones, logging outcrops and testing remote-sensing-to-field workflows. The analogy does not establish identical mineralogy, atmosphere, gravity, dust behaviour or landing conditions. USGS geological context is linked, but no site-scale mineral map or new field samples are integrated.

### Hispar Glacier / Karakoram
Hispar is a cold-region cryosphere case study for ice/debris mapping, imagery interpretation and ground-validation protocols. EvK2CNR already has a Pakistan-wide glacier inventory, so this is not a newly discovered glacier site. A glacier is not a lunar permanently shadowed region; it is a workflow/environment comparator only.

## What would upgrade this project from prototype to stronger challenge submission?

1. Add processed, QA-screened surface-temperature evidence (for example MODIS Terra/Aqua granules after Earthdata Login and authorization) for the Pakistan sites; do not confuse air temperature with surface temperature.
2. Add a valid aerosol/dust analysis from MERRA-2 after acquiring the NetCDF granule and decoding the dust variables, with a proper AOI/temporal aggregation.
3. Complete QA of the already processed Diviner ice-depth field, add LOLA uncertainty products where available, and compute authoritative lunar illumination / permanently shadowed-region metrics. The current Diviner temperature summaries are processed; they are historical model outputs, not direct ice measurements.
4. Obtain or derive a georeferenced geological/alteration map for Koh-i-Sultan, and validate spectral interpretation against published geology or field samples.
5. Replace generic analog language with a task-specific comparison: “volcanic-hydrothermal field reconnaissance and alteration mapping” versus “basaltic terrain landing/mobility” are different tasks.
6. Add field access/permit constraints and ground truth before calling either site operationally field-ready.

## Credential and account note

- The api.nasa.gov API key is not used by current NASA POWER, GIBS, EPIC, CMR catalogue or Planetary Computer workflows. A key shared in a chat should be revoked/rotated before reuse.
- NASA Earthdata Login is a separate account/authentication service. It is required for protected LP DAAC/GES DISC granule downloads and is not the same thing as an api.nasa.gov key.
- Microsoft Planetary Computer STAC metadata and its public SAS-token path used in the current project do not require a separate Planetary Computer account.

## Shackleton Rim 80 m LOLA profile result

The integrated PDS GDR window is 29.6 km × 29.6 km, native 80 m/pixel, aligned LDEM/LDEC grids, 370 × 370 pixels. The native elevation surface is interpolated; LDEC positive returns occur in 89,996 of 90,000 cells (99.9956%). At common ~925 m support, the 32 × 32 profile has median slope 13.40°, P90 slope 30.94°, and P90 3×3 local relief 1,391 m over a ~2.775 km footprint. This indicates a rugged sampled rim window and is not a base suitability assessment. Diviner PRP V2.0 thermal summaries are separately processed for 6,823 triangles in the same analyst-defined Shackleton comparison window: median annual-average temperature at 2 cm is 103.786 K and median annual-maximum surface temperature is 238.568 K. The ice-depth field includes 2,514/6,823 -999 censored rows and negative numeric values; it remains withheld pending QA. The summary does not establish exposed or accessible water ice.

## Global discovery and broader evidence layers (added 18 November 2026)

| Resource | Current status | What ANALOG-X actually uses | What remains / caveat |
|---|---|---|---|
| Copernicus DEM GLO-90 | **Global processing pipeline implemented; release status comes from generated coverage report** | Public one-degree land-tile inventory split into 24 longitude shards; GLO-90 COGs resampled to ~925 m and scanned in non-overlapping 5.55 km windows; separate Moon and Mars rankings | Do not state "global complete" unless `data/global_discovery/global_discovery.json` says `status=complete`, all inventory tiles are processed, and there are zero tile failures. It is a terrain-only DSM scan; not geology or operational suitability. Existing GLO-30 products remain a separate finer local layer. |
| NASADEM / SRTM-derived global elevation | **Independent-source validation pipeline implemented; per-site status reported** | Selected Earth profiles within NASADEM coverage are compared against Copernicus GLO-30 at nominal ~925 m support | This is an independent raster source, not ground truth. NASADEM's approximate extent is 60°N–56°S; outside-coverage sites remain untested. |
| Planetary Computer io-lulc-annual-v02 (2023) | **Global shortlist enrichment pipeline implemented; per-candidate status reported** | Annual categorical classes (water, trees, flooded vegetation, crops, built area, bare ground, snow/ice, clouds, rangeland) are sampled for retained global candidate windows | This is a global 10 m Sentinel-2-derived classification, but ANALOG-X runs enrichment only on the retained shortlist. It does not classify geology, minerals, brines or soil chemistry. Source attribution: CC BY 4.0. |
| NASA POWER climatology at global candidate coordinates | **Global shortlist enrichment pipeline implemented; per-coordinate status reported** | Annual and monthly 2 m air temperature, relative humidity, 10 m wind, corrected precipitation and all-sky shortwave context at top 100 candidates per target | It is gridded climatology sampled at candidate window centres—not site weather-station evidence, a full global climate raster, or Moon/Mars environmental equivalence. Missing parameters stay null. |
| ANALOG-X field evidence kit | **Capture workflow implemented; ground observations pending** | Offline browser capture for Pakistan station location, GNSS accuracy, photos, observed geology/geomorphology, rock/soil notes, measurements, sample custody, calibration, access/safety, uncertainty and independent review | No field observations are pre-populated. A candidate is field validated only after real georeferenced observations and independent review are recorded. |

See `docs/COMPETITIVE_CAPABILITY_RESPONSE.md` for how these additions translate the public benchmark patterns into independent ANALOG-X methods, without copying competitors' data or claiming their reported results.

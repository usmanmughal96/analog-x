# ANALOG-X Data Sources and Integration Status

Status is explicit:
- **Integrated:** queried/downloaded, validated, processed and stored in this repository.
- **Metadata discovered:** catalogue/STAC records returned; raw scientific analysis may not yet be complete.
- **Portal reviewed:** official portal inspected, but no suitable public machine-readable endpoint or redistributable layer has been verified.
- **Reference only:** official dataset/product linked but not yet ingested or processed.

## Live browser services

| Provider / service | Runtime use | Authentication | Fallback / interpretation |
|---|---|---|---|
| OpenStreetMap via CARTO dark tiles | Free default interactive basemap in the main console | No app key configured | Online tiles only; if Leaflet cannot load, the main map falls back to the clearly labelled schematic SVG locator |
| NASA GIBS WMS, VIIRS SNPP Corrected Reflectance True Color | Optional date-stamped satellite imagery overlay in the map layer selector | Public GIBS service; no app key configured | Imagery is a browse visualization, not calibrated site-level measurements; availability depends on GIBS and browser connectivity |
| NASA POWER Daily Point API (RE community) | Selected-site trailing 30-day daily means for T2M, RH2M, WS2M, PRECTOTCORR and ALLSKY_SFC_SW_DWN; window ends three days before request date | Public API; no app key configured | If request fails, committed climatology snapshot remains displayed; live means are not climatological normals or forecasts |

NASA POWER Daily API documentation: https://power.larc.nasa.gov/docs/services/api/temporal/daily/

NASA GIBS WMS documentation: https://nasa-gibs.github.io/gibs-api-docs/access-basics/

## Integrated

| Provider / product | Use in ANALOG-X | Stored output | Current limits |
|---|---|---|---|
| NASA POWER Climatology API (RE community) | Monthly/annual Earth climate context for ten coordinates | data/power/*.json, data/power/index.json | Gridded climatology; not local station data |
| Microsoft Planetary Computer STAC, Sentinel-2 L2A | Discover scenes over four Pakistan windows: Koh-i-Sultan, Hispar, Chagai small playas and Hamun-i-Mashkel | data/pakistan/public_scene_catalog.json | Metadata discovery is not full archive completeness |
| Sentinel-2 L2A visual COGs | 768×768 clipped RGB quicklooks | data/pakistan/quicklooks/*.png and index.json | RGB browse product; no geology/mineral classification |
| NASA DSCOVR / EPIC | Optional full-disc Earth context image | data/nasa/epic_latest.png, epic_latest.json | Global context only; not a site metric |
| NASA Earthdata / CMR | MODIS LST, MODIS land-cover and MERRA-2 aerosol collection/granule catalogue discovery | data/nasa/earthdata_cmr_catalog.json | Catalogue metadata only; protected granule files not downloaded/decoded |
| Copernicus DEM GLO-30 DSM | Ten Earth study/reference windows: four Pakistan leads plus Dallol, Atacama, McMurdo, Haughton, Iceland and Death Valley | `data/terrain/terrain_comparison.json`, ten derived hillshades and `native_30m_diagnostics` per Earth site | 30 m DSM source is used for separate ~30 m parent-area slope/relief diagnostics (10/10 current areas, 98.36–100% valid cells) and area-averaged to ~925 m for matched Moon/Mars terrain comparison; the DSM is not bare-earth or rover-scale |
| MGS MOLA MEGDR 64 pixels/degree | Mars terrain around Nili Patera, Syrtis Major | data/terrain/terrain_comparison.json and MOLA hillshade PNG | Only 50.53% valid observation coverage in current 30 km window; 87 complete 3×3 neighborhoods |

### NASA POWER variables
- T2M: 2 m air temperature (°C)
- T2M_MAX / T2M_MIN: monthly climatological mean daily max/min 2 m air temperature (°C)
- RH2M: 2 m relative humidity (%)
- WS10M: 10 m wind speed (m/s)
- PRECTOTCORR: corrected precipitation (mm/day)
- ALLSKY_SFC_SW_DWN: all-sky surface shortwave downward radiation (kWh/m²/day)

NASA POWER climatology API: https://power.larc.nasa.gov/docs/services/api/temporal/climatology/

### Matched-scale terrain processing
- Earth DSM: Copernicus DEM GLO-30, accessed through the Microsoft Planetary Computer STAC catalogue and public SAS token flow.
- Mars: MOLA MEGDR 64 ppd topography and counts, Nili Patera centre 8.90°N, 67.00°E.
- Study windows: approximately 30 km square at Koh-i-Sultan, Hispar, Chagai small playas, Hamun-i-Mashkel and Nili Patera.
- Analysis support: Earth DSM averaged to 925 m; MOLA native pixel spacing around Nili Patera is approximately 926 m north-south and 915 m east-west.
- Derived descriptors: median/P90/P95 slope, 3×3 local relief, valid-cell coverage and count of complete 3×3 neighborhoods.
- Absolute elevation percentiles are retained for provenance but must not be compared between Earth DSM and Mars areoid datums.
- This is a coarse local terrain profile, not a geological-equivalence score, landing-safety rating or rover traversability model.

Current Nili Patera observation coverage: 567 / 1,122 cells (50.53%); 87 complete 3×3 neighborhoods. Its terrain statistics must be interpreted with this coverage limitation.


### Balochistan playa candidate evidence (14 November 2026)

- **Chagai small salt playas near Nok Kundi:** study-window centre at 28.583333°N, 62.633333°E, based on the midpoint of two small salt-playa coordinates in NASA NTRS report 19740023693 (28°35′N, 62°36′E and 28°35′N, 62°40′E). The bounding box [62.54, 28.53, 62.73, 28.64] is an analyst-defined data-search AOI, not a surveyed playa polygon.
- **Hamun-i-Mashkel / Kharan Basin:** approximate place-reference point 28.25°N, 62.91667°E; bounding box [62.82, 28.13, 63.02, 28.33] is an analyst-defined search AOI, not a hydrological boundary.
- NASA POWER climatology: both have all seven requested parameters in the 12-month snapshot fetched 2026-11-14.
- Sentinel-2 L2A spectral context:
  - Chagai: scene S2C_MSIL2A_20251102T063041_R077_T41RMM_20251102T092816, 20 m common grid, 569,772 valid pixels.
  - Hamun: scene S2C_MSIL2A_20260809T062631_R077_T41RNM_20260809T110108, 20 m common grid, 109,692 valid pixels in a 1,108 × 99 grid. This is a narrow image strip, not full basin coverage.
  - These are single-scene spectral descriptors; BSI/SWIR/NDMI do not identify evaporite minerals, prove brine, establish salt-crust thickness or reconstruct inundation history.
- Sentinel-2 RGB quicklooks use separate newer scenes:
  - Chagai: 2026-09-18, STAC scene cloud-cover metadata 0.000179%.
  - Hamun: 2026-10-25, STAC scene cloud-cover metadata 0.001989%.
  - Scene cloud fraction is not a substitute for an AOI-level cloud/shadow mask.
- Copernicus DEM GLO-30 DSM: both 30 km selected windows have 100% valid output cells at approximately 925 m support.
  - Chagai: median slope 0.397°, P90 slope 1.010°, P90 3×3 local relief 38.8 m.
  - Hamun: median slope 0.0065°, P90 slope 0.0965°, P90 3×3 local relief 4.9 m.
  - These values describe coarse regional terrain windows only, not surface strength, salt-pan thickness, brine, field access, or rover traversability.
- Historical context: NASA NTRS report 19740023693, https://ntrs.nasa.gov/api/citations/19740023693/downloads/19740023693.pdf. It is a prior report, not a new discovery claim.

## Metadata discovered / institutional baseline

| Provider | Product / evidence | Status | Why it matters |
|---|---|---|---|
| EvK2CNR / UNDP / university partners | Pakistan Glacier Inventory: 13,032 glaciers, 13,546.93 km²; project reports Sentinel-2 outlines, multitemporal analysis and field validation | Official project facts linked; selected GeoNetwork record endpoint returned HTML, not machine-readable JSON | Existing baseline for Hispar; do not claim to discover or redraw the national inventory |
| Microsoft Planetary Computer | Sentinel-2 L2A STAC items | Anonymous scene discovery working; scene IDs, item IDs, asset links, MGRS tiles and acquisition dates stored | Open scene discovery without a user account |
| Microsoft Planetary Computer | Copernicus DEM GLO-30 STAC items | Tile metadata discovered and corresponding COG assets processed in terrain workflow | DEM metadata provenance is recorded in JSON |
| NASA EPIC | Natural-colour DSCOVR full-disc images | Public GSFC endpoint working without api.nasa.gov key | Global visual context only |
| NASA Planetary Data System Search API | Six metadata queries for Mars/MOLA/HiRISE and Moon/LOLA/Diviner observational products | `data/planetary/pds_search.json` | Metadata only; the registry may be incomplete, and a returned file reference is not proof of binary access, calibration or analysis readiness |
| PDS Geosciences Node ODE REST API | Archive-specific MOLA MEGDR, LOLA GDR, Diviner PRP and Nili Patera HiRISE DTM metadata searches using the live instrument/product-type catalogue | `data/planetary/archive_discovery.json` | Metadata only; HiRISE DTM query is spatially bounded to the existing Nili AOI; product binaries are not downloaded or processed |
| USGS Astrogeology STAC API | HiRISE RDR image-observation records intersecting the Nili Patera study window | `data/planetary/archive_discovery.json` | These are image observations, not stereo DTM products; asset links are not downloaded by discovery |


## Candidate discovery and agent evidence layer

- `data/agents/candidate_catalog.json` contains ten curated Earth candidate/reference seeds and separates under-characterized leads from established references. It is not an exhaustive global search and does not claim the two playa leads are new-to-science discoveries.
- The offline Agent Bay uses deterministic candidate-tag retrieval, NASA POWER climatology, Sentinel-2 spectral-context profiles, Copernicus/MOLA/LOLA terrain profiles and explicit evidence gaps.
- The optional Cloudflare Worker uses an open-weight model for tool-using synthesis after the deterministic specialists have assembled evidence. It does not produce scientific measurements. Deployment and quota limits are documented in `docs/AGENTIC_AI_SETUP.md`.

## Official portals reviewed; machine-readable data not verified

| Provider | Existing service/capability | ANALOG-X status / restraint |
|---|---|---|
| NDMA / NEOC | Hazard projections, disaster early warnings, hazard outlooks, 2026 Vulnerable Glaciers and Glacial Lakes Atlas listing | Official products linked. No public geospatial API, bulk download and reuse licence for the atlas was verified |
| SUPARCO / UN-SPIDER | DisasterWatch, SACRED, NatCat, flood mapping, Sentinel-2 flood mapping and drought-monitoring practices | Existing capabilities acknowledged. No direct public API/redistributable DisasterWatch layer integrated |
| SUPARCO Space4Climate | Glacier, air quality, forestry, coast, waterways, land-cover and climate indicators | Portal reviewed; no public bulk endpoint or product licence verified |
| SACCS / SUPARCO | Spatial planning / climate applications portal | Public portal; no usable API/schema verified |
| EvK2CNR Geoportal | SHARE/GeoNetwork catalogue and Pakistan glacier inventory records | Selected metadata endpoint returned HTML; official vector file is not redistributed here |



### NASA LRO Diviner PRP V2.0 processing result
The PDS4 product label was fetched and validated before processing the south-polar table. `scripts/process_diviner_prp.py` verifies the declared 2,880,000 records, record length, field names, temperature units (Kelvin), ice-depth units (metres) and the `-999` invalid/censored constant. It streams the approximately 604.8 MB table and summarizes 6,823 triangle centroids inside an analyst-defined 29.6 × 29.6 km Shackleton Rim comparison window. The committed output is `data/moon/shackleton_diviner_prp.json`.

The median annual-average temperature at 2 cm is 103.786 K; the median annual-maximum surface temperature is 238.568 K. These are historical thermal-model outputs, not in-situ measurements. The extracted ice-depth field has 4,309 numerically usable values and 2,514 `-999` censored values (36.85% of the AOI); negative numeric values also remain. The ice-depth field is therefore withheld from resource interpretation pending QA. This does not establish exposed, accessible or mineable lunar water ice.

## Reference-only NASA / planetary datasets

| Dataset | Intended role | Current state |
|---|---|---|
| NASA LRO LOLA | Lunar south-pole elevation, slope, counts and uncertainty | Integrated: NASA LRO LOLA PDS GDR `LDEM_80S_80M` and matching `LDEC_80S_80M` are processed around Shackleton Rim; native 80 m profile and ~925 m matched-support aggregate are stored in `data/moon/shackleton_lola_80m.json`. DEM is interpolated; return counts describe measurement support, not illumination, permanently shadowed regions, ice or landing safety. The original 5 m PGDA Site04 access route remained unavailable. |
| NASA LRO Diviner PRP V2.0 | Polar resource product table with thermal and ice-depth fields (`temp_avg`, `temp_max`, `ice_depth`) | Thermal summary integrated for the Shackleton comparison window: 6,823 triangles; median annual-average temperature at 2 cm 103.786 K; median annual-maximum surface temperature 238.568 K. Output: `data/moon/shackleton_diviner_prp.json`. These are historical model outputs, not in-situ measurements. The ice-depth field has negative and -999 censored values and is withheld pending QA; no accessible-ice claim. Formal PSR / illumination analysis is not integrated. |
| NASA Global Volcano Hazard Frequency and Distribution | Historical volcano hazard frequency grid | Official data page linked; grid not ingested; historical events 79–2000, 2.5 arc-minute context, not current hazard intelligence |
| NASA GIBS / Worldview | Earth global imagery/context | GIBS VIIRS tile layer displayed on map; visual context only |
| NASADEM / SRTM / other DEMs | Earth elevation | Alternate sources identified; Copernicus DEM is the terrain input in this release |
| USGS Syrtis Major MC-13 | Mars regional geological reference | Map linked; not a site-scale terrain hazard model |
| USGS OFR 75-550 | Chagai / Koh-i-Sultan geological context | Official report linked and cited; it maps the Koh-i-Sultan Volcanic Group as agglomerate, tuff and andesitic lava. No spatial geology layer ingested. |

## Access notes

Microsoft Planetary Computer public STAC is anonymous. Some Azure COG assets use a short-lived SAS token. The project obtains it from Microsoft's public token endpoint. No Planetary Computer registration is required for the current workflow. Copernicus DEM and Sentinel-2 products retain their provider terms.

Google Earth Engine is optional for a later phase. It requires a Google Cloud project, Earth Engine API enablement and project registration; the existing Planetary Computer pipeline already supplies the open STAC/COG path used by this release.

## Higher-detail Earth DEM diagnostics

The matched-support terrain pipeline now calculates a separate nominal ~30 m Copernicus DEM GLO-30 DSM summary over each 30 × 30 km Earth parent area before the existing ~925 m cross-planet aggregation. It reports parent-area slope and 3 × 3 local-relief distributions when at least 90% of the fine grid is valid. These diagnostics are stored per Earth site as `native_30m_diagnostics` in `data/terrain/terrain_comparison.json`.

This is an Earth-only roughness/context layer. It is not matched to lunar/Martian input resolution, not specific to each 5.55 km candidate sub-window, and not adequate for rover-scale obstacle detection, bearing strength or trafficability. The ~925 m layer remains the only matched-support terrain input to the cross-planet regional-window index.

## Source caveats

NASA POWER is not a weather station. T2M is not rock/surface temperature. WS10M is not dust emission. PRECTOTCORR is not water/ice availability. Sentinel-2 RGB does not establish mineralogy. Copernicus DEM is a DSM rather than a bare-earth DEM. MOLA terrain statistics rely on 50.53% observed coverage in the selected Nili Patera window. A public portal is not proof that data may be bulk downloaded or redistributed.

## Resource matrix

For the complete source-by-source status of NASA Earthdata Search, Worldview/GIBS, PDS, LRO LOLA and Diviner, CSA RADARSAT-1/RCM, ESA Copernicus Data Space, ESA Open Science Catalogue, JAXA G-Portal, and Pakistan agency portals, see [RESOURCE_INTEGRATION_MATRIX.md](RESOURCE_INTEGRATION_MATRIX.md).

### Lunar matched-support profile (Shackleton Rim)
- Product: NASA LRO LOLA PDS GDR LDEM_80S_80M and matching LDEC_80S_80M, hosted by MIT Imbrium mirror.
- Native window: 29.6 × 29.6 km at 80 m/pixel (370 × 370 cells).
- Native LDEM: interpolated gridded surface; 90,000/90,000 elevation cells present. LDEC has positive returns in 89,996/90,000 cells (99.9956%). The count map is observational support, not an elevation-validity mask.
- Coarse profile: aggregated by area averaging to 925 m (32 × 32 cells) over the same window as the Earth/Mars coarse profiles.
- Coarse descriptors: median slope 13.40°, P90 slope 30.94°, P90 3×3 local relief 1,391 m; the relief footprint is approximately 2.775 km.
- Interpretation: this selected Shackleton Rim window is rugged. This is not an illumination/PSR, water-ice, landing-safety or habitat-suitability analysis.
- Diviner PRP V2.0 thermal summaries are processed for 6,823 Shackleton-window triangles; the ice-depth interpretation remains withheld pending QA of negative and censored values. No exposed or accessible lunar ice is inferred.

## Global discovery and candidate enrichment (18 November 2026)

| Provider / product | Actual role | Output | Status semantics and limitations |
|---|---|---|---|
| Copernicus DEM GLO-90 | Global one-degree land-tile COG inventory; 90 m DSM resampled to ~925 m local metric grids for candidate-window terrain screening | `scripts/build_global_discovery.py`, `scripts/merge_global_discovery.py`, `data/global_discovery/global_discovery.json` | A 24-shard workflow records every tile as assigned, processed, no-valid-window or failed. The merged dataset is complete only when all published land-tile inventory entries have been processed with zero failures. It excludes ocean (no elevation tile), and the GLO-90 results are not interchangeable with existing local GLO-30 products. |
| NASADEM (SRTM-derived, NASA LP DAAC) | Independent elevation-source cross-check for selected sites within its 60°N–56°S coverage | `scripts/validate_nasadem_crosscheck.py`, `data/validation/nasadem_crosscheck.json` | A second raster source for terrain descriptor comparison, not a ground survey. Different acquisition/source and DSM/DEM semantics are documented; site coverage and result status are explicit. |
| Microsoft Planetary Computer `io-lulc-annual-v02` | 2023 global annual 10 m land-cover classes sampled for retained global candidate windows | `scripts/enrich_global_landcover.py`, `data/global_discovery/global_landcover_enrichment.json`, candidate `environmental_context` | Applied to the bounded global shortlist only, not every global terrain window. Sentinel-2-derived categorical predictions are environmental context, not geology/mineralogy or field truth. CC BY 4.0 attribution is retained. |
| NASA POWER Climatology API (RE community) | Annual and monthly climate context at the top 100 retained candidate windows per target, deduplicated by candidate ID | `scripts/enrich_global_power.py`, `data/global_discovery/global_power_enrichment.json`, candidate `climate_context` | Global shortlist coordinate sample only, not a global climate raster. Values are gridded climatology, not ground-station observations or forecasts. Missing values remain null. |

The current scan page is [Global Discovery Engine](../global-discovery.html). The central source state register is `data/source_registry.json`; inspect its live `state` and actual coverage fields rather than assuming every planned enrichment has completed.

The global terrain index uses the existing ten-region Earth reference pack's IQR scales. A second terrain-feature family tests descriptor sensitivity using the same GLO-90 DEM. NASADEM is the independent raster-source cross-check; the two same-DEM feature families are not independent validation. Neither is a substitute for expert-labelled geologic validation or physical field measurements.

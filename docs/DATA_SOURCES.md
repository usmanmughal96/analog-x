# ANALOG-X Data Sources and Integration Status

Status is explicit:
- **Integrated:** queried/downloaded, validated, processed and stored in this repository.
- **Metadata discovered:** catalogue/STAC records returned; raw scientific analysis may not yet be complete.
- **Portal reviewed:** official portal inspected, but no suitable public machine-readable endpoint or redistributable layer has been verified.
- **Reference only:** official dataset/product linked but not yet ingested or processed.

## Integrated

| Provider / product | Use in ANALOG-X | Stored output | Current limits |
|---|---|---|---|
| NASA POWER Climatology API (RE community) | Monthly/annual Earth climate context for eight coordinates | data/power/*.json, data/power/index.json | Gridded climatology; not local station data |
| Microsoft Planetary Computer STAC, Sentinel-2 L2A | Discover scenes over Koh-i-Sultan and Hispar | data/pakistan/public_scene_catalog.json | Metadata discovery is not full archive completeness |
| Sentinel-2 L2A visual COGs | 768×768 clipped RGB quicklooks | data/pakistan/quicklooks/*.png and index.json | RGB browse product; no geology/mineral classification |
| NASA DSCOVR / EPIC | Optional full-disc Earth context image | data/nasa/epic_latest.png, epic_latest.json | Global context only; not a site metric |
| Copernicus DEM GLO-30 DSM | Earth terrain surface for Koh-i-Sultan and Hispar | data/terrain/terrain_comparison.json and two derived hillshade PNGs | Copernicus Digital Surface Model (includes surface objects); 30 m source averaged to about 925 m |
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
- Study windows: approximately 30 km square at Koh-i-Sultan, Hispar and Nili Patera.
- Analysis support: Earth DSM averaged to 925 m; MOLA native pixel spacing around Nili Patera is approximately 926 m north-south and 915 m east-west.
- Derived descriptors: median/P90/P95 slope, 3×3 local relief, valid-cell coverage and count of complete 3×3 neighborhoods.
- Absolute elevation percentiles are retained for provenance but must not be compared between Earth DSM and Mars areoid datums.
- This is a coarse local terrain profile, not a geological-equivalence score, landing-safety rating or rover traversability model.

Current Nili Patera observation coverage: 567 / 1,122 cells (50.53%); 87 complete 3×3 neighborhoods. Its terrain statistics must be interpreted with this coverage limitation.

## Metadata discovered / institutional baseline

| Provider | Product / evidence | Status | Why it matters |
|---|---|---|---|
| EvK2CNR / UNDP / university partners | Pakistan Glacier Inventory: 13,032 glaciers, 13,546.93 km²; project reports Sentinel-2 outlines, multitemporal analysis and field validation | Official project facts linked; selected GeoNetwork record endpoint returned HTML, not machine-readable JSON | Existing baseline for Hispar; do not claim to discover or redraw the national inventory |
| Microsoft Planetary Computer | Sentinel-2 L2A STAC items | Anonymous scene discovery working; scene IDs, item IDs, asset links, MGRS tiles and acquisition dates stored | Open scene discovery without a user account |
| Microsoft Planetary Computer | Copernicus DEM GLO-30 STAC items | Tile metadata discovered and corresponding COG assets processed in terrain workflow | DEM metadata provenance is recorded in JSON |
| NASA EPIC | Natural-colour DSCOVR full-disc images | Public GSFC endpoint working without api.nasa.gov key | Global visual context only |

## Official portals reviewed; machine-readable data not verified

| Provider | Existing service/capability | ANALOG-X status / restraint |
|---|---|---|
| NDMA / NEOC | Hazard projections, disaster early warnings, hazard outlooks, 2026 Vulnerable Glaciers and Glacial Lakes Atlas listing | Official products linked. No public geospatial API, bulk download and reuse licence for the atlas was verified |
| SUPARCO / UN-SPIDER | DisasterWatch, SACRED, NatCat, flood mapping, Sentinel-2 flood mapping and drought-monitoring practices | Existing capabilities acknowledged. No direct public API/redistributable DisasterWatch layer integrated |
| SUPARCO Space4Climate | Glacier, air quality, forestry, coast, waterways, land-cover and climate indicators | Portal reviewed; no public bulk endpoint or product licence verified |
| SACCS / SUPARCO | Spatial planning / climate applications portal | Public portal; no usable API/schema verified |
| EvK2CNR Geoportal | SHARE/GeoNetwork catalogue and Pakistan glacier inventory records | Selected metadata endpoint returned HTML; official vector file is not redistributed here |

## Reference-only NASA / planetary datasets

| Dataset | Intended role | Current state |
|---|---|---|
| NASA LRO LOLA | Lunar elevation/topography | PDS source linked; raw raster not processed |
| NASA LRO Diviner | Lunar surface temperature, including polar environments | PDS source linked; raw raster not processed |
| NASA Global Volcano Hazard Frequency and Distribution | Historical volcano hazard frequency grid | Official data page linked; grid not ingested; historical events 79–2000, 2.5 arc-minute context, not current hazard intelligence |
| NASA GIBS / Worldview | Earth global imagery/context | GIBS VIIRS tile layer displayed on map; visual context only |
| NASADEM / SRTM / other DEMs | Earth elevation | Alternate sources identified; Copernicus DEM is the terrain input in this release |
| USGS Syrtis Major MC-13 | Mars regional geological reference | Map linked; not a site-scale terrain hazard model |
| USGS OFR 75-550 | Chagai regional geology context | Reference only; not a site-scale mapping layer |

## Access notes

Microsoft Planetary Computer public STAC is anonymous. Some Azure COG assets use a short-lived SAS token. The project obtains it from Microsoft's public token endpoint. No Planetary Computer registration is required for the current workflow. Copernicus DEM and Sentinel-2 products retain their provider terms.

Google Earth Engine is optional for a later phase. It requires a Google Cloud project, Earth Engine API enablement and project registration; the existing Planetary Computer pipeline already supplies the open STAC/COG path used by this release.

## Source caveats

NASA POWER is not a weather station. T2M is not rock/surface temperature. WS10M is not dust emission. PRECTOTCORR is not water/ice availability. Sentinel-2 RGB does not establish mineralogy. Copernicus DEM is a DSM rather than a bare-earth DEM. MOLA terrain statistics rely on 50.53% observed coverage in the selected Nili Patera window. A public portal is not proof that data may be bulk downloaded or redistributed.

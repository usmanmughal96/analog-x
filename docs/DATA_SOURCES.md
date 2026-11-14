# ANALOG-X Data Sources and Integration Status

Status is explicit:
- **Integrated:** requested, downloaded/queried, validated and stored in this repository.
- **Metadata discovered:** catalogue/STAC records returned; raw scientific analysis may not yet be complete.
- **Portal reviewed:** official portal inspected, but no suitable public machine-readable endpoint or redistributable layer has been verified.
- **Reference only:** official data/product linked but not yet ingested or processed.

## Integrated

| Provider / product | Use in ANALOG-X | Stored output | Current limits |
|---|---|---|---|
| NASA POWER Climatology API (RE community) | Monthly/annual Earth climate context for eight coordinates | data/power/*.json, data/power/index.json | Gridded climatology; not local station data |
| Microsoft Planetary Computer STAC, Sentinel-2 L2A | Discover true-colour scenes over Koh-i-Sultan and Hispar | data/pakistan/public_scene_catalog.json | Metadata and selected scenes; not complete temporal inventory |
| Sentinel-2 L2A visual COGs | 768×768 clipped RGB site quicklooks | data/pakistan/quicklooks/*.png and index.json | RGB browse product; no geology/mineral classification |
| NASA DSCOVR / EPIC natural images | Optional full-disc Earth context image | data/nasa/epic_latest.png, epic_latest.json | Global context only; not a site metric |

NASA POWER parameters:
- T2M: 2 m air temperature (°C)
- T2M_MAX / T2M_MIN: monthly climatological mean daily max/min 2 m air temperature (°C)
- RH2M: 2 m relative humidity (%)
- WS10M: 10 m wind speed (m/s)
- PRECTOTCORR: corrected precipitation (mm/day)
- ALLSKY_SFC_SW_DWN: all-sky surface shortwave downward radiation (kWh/m²/day)

NASA POWER climatology API documentation: https://power.larc.nasa.gov/docs/services/api/temporal/climatology/

## Metadata discovered / institutional baseline

| Provider | Product / evidence | Status | Why it matters |
|---|---|---|---|
| EvK2CNR / UNDP / university partners | Pakistan Glacier Inventory: 13,032 glaciers, 13,546.93 km²; project reports Sentinel-2 outlines, multitemporal analysis and selected field validation | Official project facts linked; GeoNetwork record endpoint returned HTML, not machine-readable JSON in current automation | Existing baseline for the Hispar case; do not claim to discover or redraw the national inventory |
| Microsoft Planetary Computer | Sentinel-2 L2A STAC items | Metadata search working anonymously; scene item, asset URL, MGRS tile, platform, acquisition date and cloud percentage stored | Open scene discovery without a Planetary Computer user account |
| NASA EPIC | Natural-colour DSCOVR full-disc images | Public GSFC endpoint working without api.nasa.gov key | Global visual context, not site-scale evidence |

## Official portals reviewed; machine-readable data not verified

| Provider | Existing service/capability | ANALOG-X status / restraint |
|---|---|---|
| NDMA / NEOC | Hazard projections, disaster early warnings, hazard outlooks, National Vulnerable Glaciers and Glacial Lakes Atlas 2026 listing | Official product pages linked. No public geospatial API, bulk data download or reuse licence for the atlas was verified in this build |
| SUPARCO / UN-SPIDER | DisasterWatch, SACRED, NatCat, flood mapping, Sentinel-2 flood mapping and drought monitoring practices | These are existing capabilities. No direct public API/redistributable DisasterWatch layer is integrated |
| SUPARCO Space4Climate | Portal themes include glacier, air quality, forestry, coastal, waterways and land cover/climate indicators | Portal reviewed; no public bulk endpoint or downloadable product licence verified |
| SACCS / SUPARCO | Spatial planning / climate applications portal | Public portal; no usable API/schema verified by the current pipeline |
| EvK2CNR Geoportal | SHARE/GeoNetwork catalogue and Pakistan glacier inventory records | Metadata endpoint for selected record returned HTML; a vector file is not redistributed by this repository |

## Reference-only NASA / planetary datasets

| Dataset | Intended role | Current state |
|---|---|---|
| NASA MOLA MEGDR | Mars topography | PDS source linked; raw raster not processed in live console |
| NASA LRO LOLA | Lunar elevation/topography | PDS source linked; raw raster not processed |
| NASA LRO Diviner | Lunar surface temperature, including polar environments | PDS source linked; raw raster not processed |
| NASA GIBS / Worldview | Earth global imagery/context | GIBS VIIRS tile layer displayed on the map; visual context only |
| NASA Global Volcano Hazard Frequency and Distribution | Historical volcano hazard frequency grid | Metadata and official data page linked; no grid ingested; historical events 79–2000, 2.5 arc-minute grid, not current hazard intelligence |
| NASADEM / SRTM / Copernicus DEM | Earth elevation, slope and roughness | Dataset pathways identified; no site-specific terrain metrics claimed |
| USGS Syrtis Major MC-13 | Mars regional geological reference | Map linked; not a site-scale terrain hazard model |
| USGS OFR 75-550 | Chagai regional geology context | Reference only; not a site-scale mapping layer |

## Microsoft Planetary Computer: account/access
The public STAC API can be queried anonymously. Some Azure-hosted assets need a short-lived SAS token, available from Microsoft's public Data Authentication API without registering a Planetary Computer account. This project already obtains the token to read Sentinel-2 COG previews. Copernicus Sentinel data terms apply.

Docs:
- https://planetarycomputer.microsoft.com/docs/
- https://planetarycomputer.microsoft.com/docs/concepts/sas/
- https://planetarycomputer.microsoft.com/api/stac/v1/collections/sentinel-2-l2a

## Google Earth Engine: optional, not currently needed
Earth Engine access now requires a Google Cloud project, the Earth Engine API enabled, project registration for commercial or noncommercial use and the appropriate roles. Noncommercial access requires completing Google's eligibility questionnaire. The existing pipeline already obtains Sentinel-2 via Planetary Computer, so Earth Engine registration is optional for this version. It may be worthwhile later for larger temporal composites, Landsat/Sentinel analysis or regional reducers if a registered project is available.

Official access guide: https://developers.google.com/earth-engine/guides/access

## Source caveats
NASA POWER is not a weather station. T2M is not rock/surface temperature. WS10M is not dust emission. PRECTOTCORR is not water/ice availability. Sentinel-2 RGB does not establish mineralogy. A publicly viewable portal is not proof that its data can be downloaded or redistributed. Never promote a reference layer to “integrated” without a successful fetch, validated product, timestamp, metadata and reuse terms.

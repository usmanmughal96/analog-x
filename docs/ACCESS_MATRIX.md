# Public data and access matrix

Status is based on public-page and API checks performed 14 November 2026. "Portal described" does not mean the underlying raw data were downloaded or independently validated.

| Source | Relevant information | Access/verification | ANALOG-X status |
|---|---|---|---|
| NASA POWER | Earth T2M, T2M_MAX/MIN, RH2M, WS10M, PRECTOTCORR, ALLSKY_SFC_SW_DWN | Public climatology point endpoint; no API key required | **Fetched and committed for eight Earth candidates** |
| NASA GIBS | Satellite browse imagery and scientific visualization layers | Public WMTS/WMS/TMS services; no NASA developer key required | **Map layer configured in app** |
| NASA MOLA / PDS | Mars regional topography | Public PDS archive and product files | Linked; raw raster not yet processed in app |
| NASA LRO LOLA / Diviner | Lunar topography and surface temperature | Public PDS products | Linked; raw rasters not yet processed in app |
| NASA Global Volcano Hazard Frequency | Historical 2.5 arc-minute relative hazard frequency, dataset temporal span 1979–2000 | Public NASA Open Data record; underlying data resource linked via SEDAC | Reference only; too coarse and old for current site safety |
| Microsoft Planetary Computer | Sentinel-2 L2A STAC metadata and COG assets | Public STAC metadata; temporary SAS token available without registration | **STAC discovery completed; COG processing workflow added** |
| Google Earth Engine | Landsat/MODIS/Sentinel-derived analyses and other public catalogs | Requires project registration; non-commercial eligibility verification | Optional; not needed for current pipeline |
| EvK2CNR / UNDP | Pakistan glacier inventory, 13,032 glaciers / 13,546.93 km²; basin data, weather-station and glacier monitoring context | Public project pages and inventory publication; geoportal says climate-data downloads require authentication; selected vector access/licence needs confirmation | Publication facts recorded; no authenticated climate downloads claimed |
| SUPARCO Space4Climate / SACCS | Public thematic monitoring pages for glaciers, snow, land cover, aerosols, GHG, forestry, waterways, coastal dynamics; dated bulletins | Public web pages are accessible, but no stable public bulk-download/API endpoint for selected Chagai/Hispar layers was verified | **Source registry only; no raw SACCS raster claimed as ingested** |
| SUPARCO DisasterWatch | Near-real-time satellite-based disaster information and damage assessment | Public portal is referenced by UN-SPIDER; direct portal returned gateway/access issue in this check | Source link only; not scraped |
| NDMA | Early-warning advisories, hazard projections, GLOF outlooks, situation reports | Public pages and PDF advisories | Source links only; not converted into an independent hazard product |
| UN-SPIDER / UNOOSA | Recommended practices for flood, drought, wildfire and remote-sensing workflows | Public knowledge portal and procedures | Linked and cited as existing practice; not duplicated |
| NASA API key | Authentication/rate limits for selected api.nasa.gov services | Key is not needed for POWER/GIBS/Planetary Computer data already used in ANALOG-X | Never commit the key; see API key instructions |

## Important source distinctions

- The NASA POWER endpoint used here is a temporal climatology endpoint; its results are a climatological baseline, not near-real-time weather.
- GIBS serves visualizations/tiles; it is not interchangeable with raw Level-2 satellite reflectance.
- Planetary Computer's public STAC API exposes metadata. Azure COG asset access requires short-lived SAS signing, not a user account.
- SUPARCO's public Space4Climate pages describe datasets and monitoring products. A product should only be marked integrated after its original raster/API, date range, spatial coverage, CRS, resolution and reuse conditions are verified.
- EvK2CNR Geoportal explicitly says climate-data download requires authentication. Do not scrape protected or authenticated data without permission.
- NDMA's early-warning system is an authoritative operational service. ANALOG-X only uses public material as field-planning context; it is not an emergency-warning system.

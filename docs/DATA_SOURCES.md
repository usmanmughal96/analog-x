# Data Sources

| Source | Role | Current implementation |
|---|---|---|
| NASA POWER Climatology API | Earth temperature, humidity, precipitation, wind and solar resource | **Live browser API calls** for each selected coordinate |
| NASA MOLA MEGDR | Mars topography and observation counts | Reference link; no raw raster processed in live app |
| NASA LRO Diviner | Lunar surface temperature, including polar contexts | Reference link; no raw raster processed in live app |
| NASA LRO / LOLA | Lunar altimetry | Reference link; no raw raster processed in live app |
| NASA GIBS / Worldview | Earth imagery and environmental browse layers | Reference pathway; no pixel analytics claimed in current app |
| NASADEM / SRTM | Earth elevation | Future terrain-analysis pathway; not in live climate index |
| Smithsonian GVP Sultan | Koh-i-Sultan catalogue context | Curated site metadata, volcano number 232801 |
| USGS Syrtis Major MC-13 | Martian geological reference | Curated reference |
| USGS OFR 75-550 | Chagai regional geology | Regional context; not a site-scale map for the catalogue point |
| SUPARCO Space4Climate | Potential Pakistan Earth-observation source | Not ingested; product-level access, coverage and reuse terms unverified |

## NASA POWER parameters
Standard climate scan (AG community): `T2M,T2M_MAX,T2M_MIN,RH2M,WS10M,PRECTOTCORR`.

Solar task (RE community): `ALLSKY_SFC_SW_DWN`.

Official API documentation: https://power.larc.nasa.gov/docs/services/api/temporal/climatology/

## Interpretation
NASA POWER provides gridded Earth climatology. It is not an on-site station, rock-surface temperature, dust emission, mineralogy or subsurface resource product. Third-party datasets and imagery retain their own source terms.

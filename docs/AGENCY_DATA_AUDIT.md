# Pakistan / NASA / International Data Agency Audit

**Checked:** 14 November 2026  
**Project:** ANALOG-X — Pakistan Analog Evidence Operations Atlas

This audit distinguishes existing agency capabilities from data that have actually been integrated into the repository. A public portal, webpage or dashboard is not evidence that its backing data are available through an open API or may be redistributed.

## 1. NASA Space Apps Challenge: exact problem

The official challenge asks teams to use open Earth, Moon and Mars data from NASA and other space agencies to identify and characterize new terrestrial analogs for future bases or landing sites. The prompt explicitly notes that environments such as the Atacama, Haughton Crater and Death Valley are known analogs but are not entirely well characterized.

Official brief:
https://www.spaceappschallenge.org/2026/challenges/permanent-moon-base-locations-and-mars/

**Implication for ANALOG-X:** do not submit a generic analog directory. Characterize specific sites with evidence and explain what their data can and cannot support for an exploration task.

## 2. NDMA Pakistan

Official sources:
- https://ndma.gov.pk/
- https://ndma.gov.pk/public/projection-impact-list_new

### Existing capabilities discovered

The official Hazard Projections page lists:
- weekly weather watches;
- disaster early warnings, including 2026 DEW products;
- hazard outlooks and guidance;
- the **NDMA Vulnerable Glaciers and Glacial Lakes Atlas 2026**, listed 8 October 2026;
- GLOF Guidelines 2026 and Avalanche Guidelines 2026.

### What this means

NDMA already publishes national hazard outlooks, warnings and glacier/GLOF-related work. ANALOG-X must not claim that Pakistan lacks national hazard monitoring or that it is building a replacement for NDMA.

### Integration status

**Portal reviewed / official product linked.** A direct, public, machine-readable geospatial API, downloadable atlas geometry and an explicit redistribution licence were not verified in this build. The app links NDMA and labels it as an existing institutional baseline rather than an integrated raster layer.

## 3. SUPARCO and UN-SPIDER / UNOOSA

Official sources:
- https://www.suparco.gov.pk/
- https://un-spider.org/network/regional-support-offices/space-and-upper-atmosphere-research-commission-suparco
- https://un-spider.org/advisory-support/recommended-practices
- http://disasterwatch.sgs-suparco.gov.pk/
- https://saccs.sgs-suparco.gov.pk/
- https://space4climate.gov.pk/

### Existing capabilities discovered

UN-SPIDER identifies SUPARCO as a Regional Support Office and describes:
- Space Application Centre for Response in Emergency and Disasters (SACRED), established in 2014;
- SUPARCO's DisasterWatch Web GIS for near-real-time dissemination of space-based information during natural disasters;
- SUPARCO's role as a national/international focal point including UN-SPIDER, the International Charter Space and Major Disasters, Sentinel Asia and APSCO.

UN-SPIDER's Recommended Practices provide step-by-step remote-sensing workflows for hazards such as floods, drought and forest fires, with products and instructions using Landsat 8 and Sentinel-2 in tools such as QGIS, R and Python.

The SUPARCO/UN-SPIDER portal also describes NatCat probabilistic hazard, exposure, vulnerability, risk and loss modelling across multiple perils.

### What this means

Satellite-based disaster intelligence, flood mapping and drought monitoring are already established activities in Pakistan. ANALOG-X should consume those products where their open access and licence permit, not re-create a national disaster dashboard.

### Integration status

**Portal and methods reviewed / reference only.** Public access to portal pages was confirmed, but a documented public bulk-download/API interface and reuse licence for DisasterWatch, NatCat, SACCS or Space4Climate layers were not verified. No data from these services is presented as ingested in the current release.

## 4. SUPARCO Space4Climate

Official portal:
https://space4climate.gov.pk/

The portal describes climate and Earth-observation themes such as:
- glaciers and snow;
- air quality;
- forestry and vegetation;
- coastal and waterways;
- land cover and related climate indicators.

### What this means

Space4Climate is relevant to the Pakistan case studies, especially for independent glacier, land-cover and environmental context. It is a potentially valuable data partner/source, but the portal's existence is not proof of a public API or downloadable, reusable raster product.

### Integration status

**Portal reviewed.** No authenticated or anonymous bulk data endpoint, product schema, spatial coverage and licence combination was verified. The project does not claim Space4Climate data integration. A formal request to SUPARCO for the relevant Chagai and Hispar layers would be a strong next step.

## 5. EvK2CNR / UNDP / university partners

Official sources:
- https://www.evk2cnr.org/en/projects/glacier-and-students
- https://evk2cnr.org/en/p-e-p/other-publications/glacier-inventory
- https://www.evk2cnr.org/en/news/news/preliminary-inventory-of-glacial-lakes-in-pakistan-a-step-toward-understanding-supraglacial-lake-dynamics

### Existing capabilities and datasets discovered

The Glaciers and Students project reports a Pakistan inventory of **13,032 glaciers with a combined area of 13,546.93 km²**. It describes Sentinel-2-based glacier outlines, multitemporal change analysis, field monitoring and validation, weather stations, and collaboration with Pakistani universities and institutions.

EvK2CNR has also published a preliminary inventory of Pakistan glacial lakes, using the same 2022 Sentinel-2 imagery and resolution as the glacier inventory to maintain methodological consistency.

### What this means

ANALOG-X must not claim that it discovered Pakistan's glacier inventory or is producing the first Pakistan glacier map. The stronger and more honest use of Hispar is as a contrasting cryosphere field-work case study that connects existing glacier outlines and imagery to a clearly bounded lunar-polar field-rehearsal question.

### Integration status

**Official baseline acknowledged and linked; source-data access not yet automated.** The selected GeoNetwork record endpoint returned an HTML web page instead of a machine-readable JSON response through the current automation. The official inventory is linked; its vector geometry is not redistributed in this repository. The public scene pipeline independently discovers Sentinel-2 scenes for the Hispar area.

## 6. Microsoft Planetary Computer

Official sources:
- https://planetarycomputer.microsoft.com/docs/
- https://planetarycomputer.microsoft.com/docs/concepts/sas/
- https://planetarycomputer.microsoft.com/api/stac/v1/collections/sentinel-2-l2a
- https://planetarycomputer.microsoft.com/api/stac/v1/collections/cop-dem-glo-30

### Access and datasets

The STAC API is publicly accessible without an account. Some Azure-hosted Cloud-Optimized GeoTIFF assets use a short-lived SAS token. The project obtains this token through Microsoft's public collection token endpoint.

### Current integration

- Sentinel-2 L2A metadata queried for Koh-i-Sultan and Hispar.
- Scene IDs, capture dates, platform, MGRS tile, cloud fraction, footprints and source asset references recorded.
- Clipped RGB previews generated from actual Sentinel-2 true-colour COGs.
- Copernicus DEM GLO-30 STAC item discovery added for both Pakistan case studies, including neighbouring one-degree tiles to support the planned 30 km terrain window.

### Limits

Sentinel-2 RGB is not geology or mineral classification. Copernicus DEM GLO-30 is a Digital Surface Model; it includes surface objects and is not a bare-earth model. All terrain products require CRS, support and nodata validation.

## 7. NASA Earthdata Search / CMR and surface-environment datasets

The CMR search API was queried from the repository's scheduled workflow. It returned catalogue records for Terra MODIS MOD11A2 V061 (8-day land-surface temperature/emissivity, 1 km), Aqua MYD11A2 V061, MODIS annual land cover MCD12Q1 V061, and MERRA-2 hourly aerosol diagnostics M2T1NXAER V5.12.4. Ten MOD11A2 granule metadata records were discovered over each Pakistan study bounding box. One global October 2026 MERRA-2 aerosol granule record was discovered; it is not spatially clipped to Pakistan.

These are **catalogue-discovery results only**. The MODIS and MERRA-2 science files have not been downloaded and decoded; protected LP DAAC/GES DISC links require Earthdata Login and provider authorization. The portal must not label them as integrated temperature/aerosol measurements until arrays, QA flags, scale factors, units and AOI statistics have been processed.

## 8. NASA / planetary data sources

Official pathways:
- MOLA MEGDR: https://pds-geosciences.wustl.edu/missions/mgs/megdr.html
- PDS MOLA 64 ppd data collection: https://pds.nasa.gov/ds-view/pds/viewCollection.jsp?identifier=urn%3Anasa%3Apds%3Amgs_mola_topography_derived%3Adata_meg064
- USGS Gazetteer / Nili Patera: https://planetarynames.wr.usgs.gov/Feature/4272
- NASA LRO PDS: https://pds-geosciences.wustl.edu/missions/lro/
- NASA GIBS: https://nasa-gibs.github.io/gibs-api-docs/access-basics/
- NASA Global Volcano Hazard Frequency: https://data.nasa.gov/dataset/global-volcano-hazard-frequency-and-distribution

The MOLA archive has MEGDR topography products at 4, 16, 32, 64 and 128 pixels/degree, and polar products at 128, 256 and 512 pixels/degree. MOLA 64 ppd is selected for the initial Nili Patera regional terrain-profile test. This is intentionally coarse-scale and is not rover-hazard resolution.

For the Moon, PGDA product 78 documents 5 m/pixel LOLA site products including elevation, count, slope and uncertainty at Shackleton Rim and other south-pole sites. Our Site04 remote-access test failed: some primary-host assets returned HTTP 403 and the elevation COG failed byte-range reads; the alternate core2 hostname did not resolve in the runner. PGDA product 90 offers large-area south-polar COG products at 80 m/pixel and finer grids, and is a more promising future access route, but has not yet been processed. Diviner polar resource products include annual surface-temperature and estimated water-ice-permafrost-depth layers, but remain reference-only in this build.

NASA's Global Volcano Hazard Frequency and Distribution is a historical event-frequency product, not real-time volcanic activity or site-scale geology. It is a reference layer only in this release.

Raw lunar LOLA and Diviner products are linked for later work; they are not yet processed in the current comparison.

## 9. Is the underlying idea already solved?

Public 2026 challenge entries already demonstrate:
- mission-brief-to-experiment/site planning and explicit analogy limits (ODYSSEY);
- topography and low-sun/lighting comparisons for fixed Earth candidate sites (Earth Analog Explorer);
- other global Earth/Moon/Mars matching, mapping and dashboard implementations.

Examples:
- https://github.com/MahmoudAdelbghany/ODYSSEY
- https://github.com/azrialahmad/earth-analog-explorer

Therefore ANALOG-X does not claim that “Earth analog ranking” or “multi-source planetary dashboards” are globally unsolved.

Its defensible contribution is narrower: a Pakistan-first evidence operations workflow with actual, reproducible NASA/Planetary Computer data, two contrasting Pakistani field-study areas, institutional data reuse, matched-scale terrain profiles when validated, and transparent data gaps/transferability limits.

## 10. Open work and requested institutional access

To improve the project without duplicating agency platforms, request or verify:
1. SUPARCO Chagai regional Sentinel-2/SAR, land-cover, geological and climate products, including product dates, resolution, metadata and reuse licence.
2. Space4Climate glacier/land-cover products around Hispar and Chagai, including WMS/WMTS/COG/API details and open-data terms.
3. NDMA Atlas 2026 map layers or web-service endpoints and redistribution conditions.
4. EvK2CNR Pakistan Glacier Inventory and glacial-lake vector data under an explicit research/reuse licence.
5. Local geological field-map and sample metadata for Koh-i-Sultan.
6. A planetary geologist's review of the selected Nili Patera / Koh-i-Sultan and lunar / Hispar experiment-transferability framing.

No portal-only dataset is promoted to “integrated” until a real downloadable/queried product is acquired, parsed, validated, timestamped and cited.

## 11. Resource-by-resource integration record

See RESOURCE_INTEGRATION_MATRIX.md for the precise status of NASA Earthdata Search, Worldview/GIBS, PDS/LRO/LOLA/Diviner, CSA RADARSAT-1/RCM, ESA Copernicus Data Space, ESA Open Science Catalogue, JAXA G-Portal and Pakistan institutional portals. The matrix distinguishes product ingestion from catalogue discovery and links only what has actually been verified.

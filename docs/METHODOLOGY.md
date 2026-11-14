# ANALOG-X Methodology — Evidence Readiness, Not a Black-Box Analog Score

## Research question
For a proposed Moon/Mars field-rehearsal task, is a candidate Earth site characterized by traceable, sufficiently resolved environmental and imagery evidence—and what must still be measured on the ground or retrieved from planetary archives before anyone can claim the analogy is useful?

## Work packages
1. **Candidate definition.** Use a documented coordinate or area of interest with provenance. A catalogue point is not a surveyed site boundary.
2. **Earth climate context.** Retrieve NASA POWER climatology, preserve original responses, source URL, variables, units, monthly values and fetch time.
3. **Satellite scene discovery.** Query Microsoft Planetary Computer STAC for Sentinel-2 L2A items. Preserve item IDs, dates, MGRS tiles, cloud percentages, footprints and asset links.
4. **Visual quicklook.** Use a public SAS token to read cloud-optimized Sentinel-2 true-colour COG assets and clip a preview to the study bounding box.
5. **Terrain profile.** Use Copernicus DEM GLO-30 DSM for Koh-i-Sultan and Hispar, mosaic neighbouring tiles, project to local UTM and average to approximately 925 m. Use MOLA MEGDR 64 pixels/degree topography and observation-count products around Nili Patera, Syrtis Major. Compute slope and 3×3 local-relief distributions at comparable coarse support.
6. **Institutional evidence.** Record existing EvK2CNR glacier inventory, NDMA hazard outlooks, SUPARCO/UN-SPIDER recommended practices, Space4Climate and DisasterWatch capabilities with an explicit integration status.
7. **Planetary reference.** Link MOLA, LOLA, Diviner and USGS Mars geology products. MOLA is now processed for the Nili Patera window. Raw lunar LOLA/Diviner products are not processed.
8. **Field-readiness card.** Convert gaps into validation tasks: georeferenced field stations, ground photos, rock/soil descriptions, local weather loggers, surface-temperature sensors, sample provenance and permissions.

## Matched-scale terrain method

### Earth inputs
- Copernicus DEM GLO-30 Digital Surface Model (DSM), accessed as Cloud-Optimized GeoTIFF assets through Microsoft Planetary Computer STAC and public SAS token access.
- Koh-i-Sultan and Hispar windows are approximately 30 km × 30 km.
- Earth data is mosaicked across adjacent one-degree tiles, reprojected to the local UTM zone and averaged to 925 m cells.

### Mars input
- MGS MOLA MEGDR 64 pixels/degree topography and observation-count grid.
- Target: Nili Patera, Syrtis Major, approximately 8.90°N, 67.00°E.
- The selected 64 ppd grid has about 926 m north-south and 915 m east-west pixel spacing at the target latitude.
- Cells with no MOLA observations are masked using the count grid; no missing terrain cells are filled before calculating the reported valid-cell coverage.

### Descriptors
For each approximately 30 km window, the pipeline reports:
- valid-cell count and coverage;
- elevation percentiles (stored for product-level context, not compared across vertical datums);
- median, P90 and P95 slope in degrees;
- median and P90 3×3 local relief in metres;
- slope fractions under 5°, under 10° and over 20°.

The 3×3 local-relief descriptor has an approximate footprint of 2.8 km at this support. It is a coarse terrain descriptor, not a rover-scale roughness measure.

### Current result and quality warning
- Koh-i-Sultan: 100% valid cells in its 1,024-cell window.
- Hispar: 100% valid cells in its 1,024-cell window.
- Nili Patera: 567 of 1,122 MOLA cells observed (50.53%); only 87 complete 3×3 neighborhoods remain for slope/relief derivatives.

Nili Patera's coverage is materially lower than the Earth windows. Its summary is useful as a provisional regional profile, but any site-to-site interpretation should be treated as limited and reviewed with a higher-resolution or complementary Mars product before drawing a conclusion.

## Evidence classes and confidence
- **Integrated measurement:** data payload received, parsed, validated, timestamped and stored.
- **Metadata discovered:** STAC or catalogue item exists, but measurement/analysis is not yet complete.
- **Portal reviewed:** an institution publishes a service, but no open machine-readable endpoint or reuse terms are established.
- **Reference only:** official dataset or archive linked, but no processed data in this release.
- **Field validation required:** remote sensing cannot establish site-scale geology, surface strength, dust flux or access/safety.

## Study areas

### Koh-i-Sultan / Chagai
The Smithsonian GVP catalogue identifies Sultan as a volcanic field. The current NASA POWER point is 29.1°N, 62.8°E. Sentinel-2 L2A scenes are discovered in MGRS tile 41RMN and a true-colour preview has been clipped to the stated study bounding box. Copernicus DEM GLO-30 is processed over an approximately 30 km window at matched coarse support to MOLA. This supports reconnaissance and field documentation workflows, not a claim of Syrtis basalt equivalence. Geological field validation and site-scale terrain data remain required.

### Hispar Glacier / Karakoram
Sentinel-2 scene discovery includes a late-summer 2022 inventory-reference period and recent scenes. A true-colour preview has been clipped to an approximate bounding box near 36.10572°N, 75.23341°E. Copernicus DEM is processed over an approximately 30 km window at matched coarse support. EvK2CNR already published a Pakistan glacier inventory. The project's contribution is to cross-reference existing evidence and show transferability gaps, not to remap Pakistan's glaciers.

## No universal similarity score
Climate, imagery, terrain and geology have different physical meanings, temporal windows and spatial support. A weighted score would be misleading without a specific mission task, harmonized units/resolution, missing-data accounting, scientifically defensible weights, sensitivity testing and independent domain review. Therefore the current release shows source status, measurements and gaps separately instead of generating a spurious “Mars similarity %”.

## Known limitations
- Nili Patera MOLA coverage is only 50.53% in the selected window; slope/relief statistics use 87 complete neighborhoods.
- Copernicus DEM GLO-30 is a DSM, not bare-earth terrain.
- The 925 m analysis is too coarse for rover-scale hazards or field-scale obstacles.
- Absolute elevations are not compared between Earth DSM and Mars areoid reference.
- Raw lunar LOLA and Diviner data are not processed.
- Sentinel-2 true-colour is not mineral classification; spectral indices need cloud/snow/shadow masks and validation.
- The EvK2CNR glacier inventory is cited, not redistributed.
- No NDMA or SUPARCO data API or redistribution licence is confirmed.
- Candidate AOIs are approximate and are not permissions or survey boundaries.
- Climate data are gridded climatology, not local conditions at the field site.

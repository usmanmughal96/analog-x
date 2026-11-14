# ANALOG-X Methodology — Evidence Readiness, Not a Black-Box Analog Score

## Research question
For a proposed Moon/Mars field-rehearsal task, is a candidate Earth site characterized by traceable, sufficiently resolved environmental and imagery evidence—and what must still be measured on the ground or retrieved from planetary archives before anyone can claim the analogy is useful?

## Work packages
1. **Candidate definition.** Use a documented coordinate or area of interest with provenance. A catalogue point is not a surveyed site boundary.
2. **Earth climate context.** Retrieve NASA POWER climatology, preserve original responses, source URL, variables, units, monthly values and fetch time.
3. **Satellite scene discovery.** Query Microsoft Planetary Computer STAC for Sentinel-2 L2A items. Preserve item IDs, dates, MGRS tiles, cloud percentages, footprints and asset links.
4. **Visual quicklook.** Use a public SAS token to read cloud-optimized Sentinel-2 true-colour COG assets and clip a preview to the study bounding box.
5. **Institutional evidence.** Record existing EvK2CNR glacier inventory, NDMA hazard outlooks, SUPARCO/UN-SPIDER recommended practices, Space4Climate and DisasterWatch capabilities with an explicit integration status.
6. **Planetary reference.** Link MOLA, LOLA, Diviner and USGS Mars geology products. Do not report raster-derived comparison unless rasters are downloaded, harmonized and processed.
7. **Field-readiness card.** Convert gaps into validation tasks: georeferenced field stations, ground photos, rock/soil descriptions, local weather loggers, surface-temperature sensors, sample provenance and permissions.

## Evidence classes and confidence
- **Integrated measurement:** data payload received, parsed, validated, timestamped and stored.
- **Metadata discovered:** STAC or catalogue item exists, but measurement/analysis is not yet complete.
- **Portal reviewed:** an institution publishes a service, but no open machine-readable endpoint or reuse terms are established.
- **Reference only:** official dataset or archive linked, but no processed data in this release.
- **Field validation required:** remote sensing cannot establish site-scale geology, surface strength, dust flux or access/safety.

## Study areas

### Koh-i-Sultan / Chagai
The Smithsonian GVP catalogue identifies Sultan as a volcanic field. The current NASA POWER point is 29.1°N, 62.8°E. Sentinel-2 L2A scenes are discovered in MGRS tile 41RMN and a true-colour preview has been clipped to the stated study bounding box. This supports reconnaissance and field documentation workflows, not a claim of Syrtis basalt equivalence. Geological field validation and site-scale terrain data remain required.

### Hispar Glacier / Karakoram
Sentinel-2 scene discovery includes a late-summer 2022 inventory-reference period and recent scenes. A true-colour preview has been clipped to an approximate bounding box near 36.10572°N, 75.23341°E. EvK2CNR already published a Pakistan glacier inventory. The project's contribution is to cross-reference existing evidence and show transferability gaps, not to remap Pakistan's glaciers.

## No universal similarity score
NASA POWER climate variables, Sentinel-2 RGB imagery, historical volcano hazard grids, Earth DEM metrics and planetary MOLA/LOLA/Diviner products have different physical meanings, temporal windows and spatial support. A weighted score would be misleading without:
- a specific mission task;
- compatible units and data support;
- harmonized resolution and coordinate systems;
- missing-data accounting;
- scientifically defensible weighting;
- sensitivity testing;
- review by a planetary geologist or domain scientist.

Therefore the current release shows source status, measurements and gaps separately instead of generating a spurious “Mars similarity %”.

## Known limitations
- Raw MOLA, LOLA and Diviner data are not processed.
- Sentinel-2 true-colour is not mineral classification; spectral indices need cloud/snow/shadow masks and validation.
- The EvK2CNR glacier inventory is cited, not redistributed.
- No NDMA or SUPARCO data API or redistribution licence is confirmed.
- Candidate AOIs are approximate and are not permissions or survey boundaries.
- Climate data are gridded climatology, not local conditions at the field site.

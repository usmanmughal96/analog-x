# ANALOG-X Methodology — Evidence Readiness, Not a Black-Box Analog Score

## Research question
For a proposed Moon/Mars field-rehearsal task, is a candidate Earth site characterized by traceable, sufficiently resolved environmental and imagery evidence—and what must still be measured on the ground or retrieved from planetary archives before anyone can claim the analogy is useful?

## Work packages
1. **Candidate definition.** Maintain a provenance-linked seed set of ten Earth environments: two under-characterized Balochistan playa leads, two Pakistan reference case studies and six established global reference sites. A catalogue point or analyst-defined search window is not a surveyed site boundary; the seed set is not an exhaustive global discovery scan.
2. **Earth climate context.** Retrieve NASA POWER climatology, preserve original responses, source URL, variables, units, monthly values and fetch time.
3. **Satellite scene discovery.** Query Microsoft Planetary Computer STAC for Sentinel-2 L2A items. Preserve item IDs, dates, MGRS tiles, cloud percentages, footprints and asset links.
4. **Visual quicklook.** Use a public SAS token to read cloud-optimized Sentinel-2 true-colour COG assets and clip a preview to the study bounding box.
5. **Terrain profile.** Use Copernicus DEM GLO-30 DSM for four Pakistan windows—Koh-i-Sultan, Hispar Glacier, Chagai small salt playas and Hamun-i-Mashkel—mosaic neighbouring tiles, project to local UTM and average to approximately 925 m. Use MOLA MEGDR 64 pixels/degree topography and observation-count products around Nili Patera, Syrtis Major. Compute slope and 3×3 local-relief distributions at comparable coarse support. Process a separate lunar LOLA 80 m Shackleton Rim window and aggregate it to ~925 m for regional descriptor comparison.
6. **Institutional evidence.** Record existing EvK2CNR glacier inventory, NDMA hazard outlooks, SUPARCO/UN-SPIDER recommended practices, Space4Climate and DisasterWatch capabilities with an explicit integration status.
7. **Planetary reference.** MOLA is processed for Nili Patera. Lunar LOLA PDS GDR 80 m elevation and count grids are processed for Shackleton Rim, with a coarse ~925 m profile aggregated for cross-body terrain comparison. The original 5 m PGDA Site04 path was blocked, but the MIT Imbrium mirror provides the 80 m PDS GDR. Diviner PRP V2.0 collection metadata and south-polar table range access are verified, but field units/semantics and site-level thermal/ice-depth statistics remain unprocessed.
8. **Field-readiness card.** Convert gaps into validation tasks: georeferenced field stations, ground photos, rock/soil descriptions, local weather loggers, surface-temperature sensors, sample provenance and permissions.

## Matched-scale terrain method

### Earth inputs
- Copernicus DEM GLO-30 Digital Surface Model (DSM), accessed as Cloud-Optimized GeoTIFF assets through Microsoft Planetary Computer STAC and public SAS token access.
- Four Pakistan windows—Koh-i-Sultan, Hispar Glacier, Chagai small salt playas and Hamun-i-Mashkel—are approximately 30 km × 30 km.
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
- Chagai small salt playas: 100% valid cells in its 1,024-cell window (median slope 0.397°, P90 slope 1.010°, P90 local relief 38.8 m).
- Hamun-i-Mashkel: 100% valid cells in its 1,024-cell window (median slope 0.0065°, P90 slope 0.0965°, P90 local relief 4.9 m).
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
The Smithsonian GVP catalogue identifies Sultan as a Pleistocene volcanic field. USGS Open-File Report 75-550 maps the Koh-i-Sultan Volcanic Group as agglomerate, tuff and andesitic lava. The current NASA POWER point is 29.1°N, 62.8°E. Sentinel-2 L2A scenes are discovered in MGRS tile 41RMN and a true-colour preview has been clipped to the stated study bounding box. Copernicus DEM GLO-30 is processed over an approximately 30 km window at matched coarse support to MOLA. The defensible rehearsal themes are volcanic/hydrothermal reconnaissance, alteration mapping, outcrop logging and satellite-to-field validation. This is not a basaltic composition match to Syrtis Major. The USGS report is a regional reference, not a newly ingested geology raster; site-scale mineral mapping, field samples and specialist validation remain required.

### Hispar Glacier / Karakoram
Sentinel-2 scene discovery includes a late-summer 2022 inventory-reference period and recent scenes. A true-colour preview has been clipped to an approximate bounding box near 36.10572°N, 75.23341°E. Copernicus DEM is processed over an approximately 30 km window at matched coarse support. EvK2CNR already published a Pakistan glacier inventory. The project's contribution is to cross-reference existing evidence and show transferability gaps, not to remap Pakistan's glaciers.

## Lunar LOLA terrain method — Shackleton Rim

- Product: NASA LRO LOLA PDS GDR `LDEM_80S_80M` and `LDEC_80S_80M`, 80 m/pixel, Moon ME / DE421 south-polar stereographic projection.
- Study window: 29.6 km × 29.6 km, centred on the Shackleton Rim R04/Site04 coordinate (-89.7668°, 188.13°E).
- Native LDEM is an interpolated gridded surface model. Its elevation samples remain valid even when the LDEC count is zero; the count grid is separately summarized as observation support.
- Native window: 370 × 370 cells; 89,996 of 90,000 cells have positive laser-return counts (99.9956%).
- Coarse comparison: area-average the 80 m LDEM to a 32 × 32 grid at 925 m, same spatial support as the Earth/Mars coarse windows.
- Coarse descriptors: median/P90 slope 13.40°/30.94°; P90 3×3 local relief 1,391 m over an approximately 2.775 km footprint.
- This is a rugged local topographic profile. It does not compute illumination, permanently shadowed-region status, water ice, landing suitability, engineering hazards or permanent-base feasibility.

## No universal similarity score
Climate, imagery, terrain and geology have different physical meanings, temporal windows and spatial support. A weighted score would be misleading without a specific mission task, harmonized units/resolution, missing-data accounting, scientifically defensible weights, sensitivity testing and independent domain review. Therefore the current release shows source status, measurements and gaps separately instead of generating a spurious “Mars similarity %”.


## Mission-specific decision support (Agent Bay)

The offline decision engine reads the curated candidate catalogue and current published evidence. It does not use an LLM to calculate a score.

### Inputs kept separate
- **Mission eligibility:** candidate record lists Moon, Mars or both.
- **Documented task overlap:** selected experiment is matched against each site's documented rehearsal tasks and environment tags.
- **Evidence layers:** NASA POWER climatology, Sentinel-2 spectral-context profile, processed Copernicus terrain profile and traceable source references are displayed independently.
- **Candidate class:** an under-characterized research lead remains distinct from an established/reference site.
- **Planning context:** three lowest-precipitation NASA POWER climatology months are shown with air temperature and 10 m wind; they are not weather forecasts.

### Strict and exploratory policies
- **Strict:** a candidate must be eligible for the selected mission, have at least one documented rehearsal-task overlap, a source reference, NASA POWER context, and either a site-specific Sentinel-2 profile or a processed terrain profile.
- **Exploratory:** environmental-tag matches and reference sites may be shown even when that strict evidence threshold is not met. They remain hypotheses or reference baselines.

### Ordering and interpretation
The shortlist is ordered by documented task overlap, then under-characterized leads before established references, then by the number of evidence layers present. Ties are retained. This is a transparent retrieval/triage rule, not a calibrated analog similarity metric, confidence probability, landing suitability or rover-safety rating. For a Moon + Mars request, the terrain tool returns separate Moon and Mars comparisons. The Field School XP system is a learning aid and never influences a scientific decision.

## Known limitations
- Nili Patera MOLA coverage is only 50.53% in the selected window; slope/relief statistics use 87 complete neighborhoods.
- Copernicus DEM GLO-30 is a DSM, not bare-earth terrain.
- The 925 m analysis is too coarse for rover-scale hazards or field-scale obstacles.
- Absolute elevations are not compared between Earth DSM and Mars areoid reference.
- LOLA 80 m elevation/count products are now processed; Diviner annual-temperature and water-ice-permafrost products are not yet processed. The LOLA surface is interpolated and its count map is reported separately.
- Sentinel-2 true-colour is not mineral classification; spectral indices need cloud/snow/shadow masks and validation.
- The EvK2CNR glacier inventory is cited, not redistributed.
- No NDMA or SUPARCO data API or redistribution licence is confirmed.
- Candidate AOIs are approximate and are not permissions or survey boundaries.
- Climate data are gridded climatology, not local conditions at the field site.

## NASA Earthdata discovery status

CMR returned collection metadata for MOD11A2, MYD11A2, MCD12Q1 and MERRA-2 M2T1NXAER. The app stores ten MOD11A2 granule metadata records over each Pakistan study box and one global October 2026 MERRA-2 granule record. No MODIS or MERRA-2 scientific arrays are decoded in this release. A metadata link must not be presented as a measured temperature or dust field.

## Global candidate-discovery and validation work package (18 November 2026)

The original ten-site seed set and 7,290 regional windows remain a regional study. A separate worldwide terrain search is implemented against the public Copernicus DEM GLO-90 land-tile inventory.

1. **Inventory:** read the provider's one-degree land-tile list and deterministically assign tiles to 24 longitude shards. Each shard records assigned/processed/no-valid-window/failed tiles.
2. **Terrain grid:** read the 90 m COG, reproject each tile into an appropriate local UTM or polar stereographic CRS, and area-average to nominal ~925 m cells.
3. **Candidate unit:** calculate non-overlapping 6×6-cell windows (~5.55 km). A window must have at least 70% valid elevation cells and at least 15 valid slope and relief samples.
4. **Core terrain features:** median slope, P90 slope and P90 3×3 local relief. **Secondary diagnostics:** P95 slope, elevation IQR, detrended roughness RMS and slope fractions. The secondary feature family is computed from the same DEM and is a robustness check, not independent-data validation.
5. **Planet-specific reference:** calculate reference-window medians for the selected Shackleton Rim (LOLA) and Nili Patera (MOLA) terrain surfaces. Score candidate features against those medians using IQR scales from the ten-region Earth reference dataset. The displayed consensus is the mean of the two feature-family indices. It is exploratory, sample-normalized terrain proximity, not probability, accuracy, geology, trafficability or landing safety.
6. **Global release gate:** the merged dataset is labelled complete only if all public inventory tiles are assigned and processed and there are zero tile failures. A partial run reports actual tile coverage and failure details; an empty/failed tile is never silently removed from the denominator.
7. **Independent terrain source:** the NASADEM/SRTM-derived script cross-checks selected overlapping Earth sites against Copernicus GLO-30, reporting per-site coverage, absolute descriptor differences and small-sample rank correlation. This validates source sensitivity of terrain descriptors only; it is not physical ground truth.
8. **Environmental enrichment:** retained terrain candidates are sampled with 2023 Planetary Computer `io-lulc-annual-v02` global land cover (shortlist only) and NASA POWER monthly/annual climatology at top-100 candidates per target (shortlist only). Both have independent per-candidate coverage and missingness states.
9. **Field evidence:** the Field Validation Kit exports planned stations and actual observations separately. No candidate is marked field validated without georeferenced measurements, photos, sample/instrument provenance, calibration declaration, permissions/safety notes and independent review.

The reproducibility workflow hashes source code, UI, tests, workflows, documentation and generated data. Its manifest records file SHA-256, size, repository commit before manifest generation, runtime versions and the source registry. A hash proves byte-level identity, not scientific validity. Acquisition dates, source item IDs, licences, analysis parameters, CRS, units and product-specific limitations are retained alongside generated outputs where available.

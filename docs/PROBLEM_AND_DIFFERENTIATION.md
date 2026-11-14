# ANALOG-X: problem statement and differentiation

## Challenge-aligned problem statement

Planetary analog field campaigns need more than a list of visually similar landscapes. Before a team can use a terrestrial site to rehearse a specific lunar/Martian science or operations task, it needs compatible, traceable evidence across imagery, terrain, climate and geology—and a clear account of what remains missing or incompatible in scale.

**ANALOG-X addresses this evidence-readiness gap for Pakistan case studies:** it assembles open Earth-observation and environmental records, links them to planetary reference products, records spatial/temporal support and provenance, and converts evidence gaps into targeted field-validation tasks. It deliberately avoids an unvalidated universal planetary-similarity percentage.

## Current Pakistan case studies

### Koh-i-Sultan / Chagai
A Smithsonian-catalogued Pleistocene volcanic-field candidate for volcanic/hydrothermal reconnaissance, alteration mapping, outcrop logging and remote-sensing-to-ground validation. USGS OFR 75-550 maps the Koh-i-Sultan Volcanic Group as agglomerate, tuff and andesitic lava. Sentinel-2 L2A scenes and true-colour previews are integrated. Copernicus DEM GLO-30 DSM has been processed for an approximately 30 km window at about 925 m terrain support. This is a volcanic-process/workflow candidate, not a basaltic composition match to Syrtis Major or a validated Mars analog. The regional USGS report is cited, but a site-scale geology raster, mineral map and field samples are not integrated.

### Hispar Glacier / Karakoram
A cryosphere case study for ice/debris image interpretation and field-data validation. Sentinel-2 scenes and true-colour previews are integrated; Copernicus DEM terrain descriptors are processed at the same approximate support as the Mars profile. EvK2CNR already published a Pakistan inventory of 13,032 glaciers and a preliminary glacial-lake inventory. ANALOG-X credits those baselines rather than claiming to discover or remap Pakistan's glaciers. An Earth glacier does not reproduce lunar permanently shadowed-region conditions.

## Mars terrain reference

Nili Patera in the Syrtis Major quadrangle is used as a specific Mars terrain reference rather than comparing an entire Earth province to a planetary region. MGS MOLA MEGDR 64 pixels/degree topography and observation counts are processed for an approximately 30 km window. Earth Copernicus DEM GLO-30 DSM windows are mosaicked, reprojected and averaged to about 925 m before slope and local-relief descriptors are computed.

The current MOLA window contains 567 observed cells of 1,122 (50.53%) and only 87 complete 3×3 neighborhoods. This is a major quality limitation, explicitly surfaced in the app. The comparison is descriptors only; it does not prove geological equivalence, rover mobility, landing suitability or mineralogical similarity.

## Why not simply build another site-ranking dashboard?

Public 2026 challenge submissions already include mission-to-experiment/site planners and terrain/lighting matching tools. ANALOG-X does not claim that analog ranking, multi-source dashboards or terrain similarity are globally unsolved.

Its differentiating contribution is a Pakistan-first evidence operations workflow, not a claim that Koh-i-Sultan is a previously unknown volcano or that a new analog has already been scientifically validated:
- NASA POWER climate snapshots for eight coordinates;
- Sentinel-2 L2A scene discovery and clipped RGB previews over two Pakistan case studies;
- Copernicus DEM GLO-30 and MOLA 64 ppd terrain descriptors at matched coarse support;
- explicit MOLA observation-count coverage and data-quality warnings;
- reuse and attribution of existing EvK2CNR, NDMA and SUPARCO/UN-SPIDER work;
- a clear distinction between integrated data, discovered metadata, reviewed portals and reference-only data;
- field validation tasks and planetary non-transferability limits.

## What remains to prove

1. Retrieve and process lunar south-polar LOLA/Diviner products to complement the Hispar cryosphere case.
2. Improve Nili Patera terrain coverage using an independent Mars gridded topography product or a better-covered nearby subregion.
3. Compare the MOLA result with other Mars DEMs and validate coordinate/grid transforms and no-data handling.
4. Add primary-source geological mapping or field observations for Koh-i-Sultan before making lithology/mineralogy claims.
5. Validate Sentinel-2 spectral classifications using cloud, shadow and snow masks and independent ground truth.
6. Request open, licensed NDMA/Space4Climate/SUPARCO and EvK2CNR GIS layers where available.
7. Have a planetary geologist review the field-rehearsal tasks and transferability statements.

## Evidence vocabulary
- Integrated: downloaded/queried, parsed, validated and stored.
- Metadata discovered: catalogue or STAC records returned; raw scientific analysis may still be pending.
- Portal reviewed: official portal checked; open machine-readable access/reuse is not verified.
- Reference only: official dataset linked but not processed.
- Field validation required: remote sensing cannot establish the site-level claim alone.

## Novelty and validation boundary

The current release has identified a potentially under-characterized field-rehearsal candidate, but it has not proved that Koh-i-Sultan is a new-to-science analog site. The published USGS Chagai geology and existing regional alteration studies are prior work. A competition-grade novelty claim requires a clearly bounded field area, a comparison target tied to a mission task, site-scale lithology/alteration evidence, QA-screened multi-sensor analysis and a plan for field validation. Hispar is a known glacier region and is retained as a cryosphere workflow comparator, not as the new discovery.

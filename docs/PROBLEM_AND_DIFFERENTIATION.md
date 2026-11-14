# ANALOG-X: problem statement and differentiation

## Challenge-aligned problem statement

Planetary analog field campaigns need more than a list of visually similar landscapes. Before a team can use a terrestrial site to rehearse a specific lunar/Martian science or operations task, it needs compatible, traceable evidence across imagery, terrain, climate and geology—and a clear account of what remains missing or incompatible in scale.

**ANALOG-X addresses this evidence-readiness gap with a Pakistan-first discovery seed atlas and mission-specific evidence workflow:** it assembles open Earth-observation and environmental records, links them to planetary reference products, records spatial/temporal support and provenance, and converts evidence gaps into targeted field-validation tasks. It deliberately avoids an unvalidated universal planetary-similarity percentage.

## Current Pakistan case studies

### Koh-i-Sultan / Chagai
A Smithsonian-catalogued Pleistocene volcanic-field candidate for volcanic/hydrothermal reconnaissance, alteration mapping, outcrop logging and remote-sensing-to-ground validation. USGS OFR 75-550 maps the Koh-i-Sultan Volcanic Group as agglomerate, tuff and andesitic lava. Sentinel-2 L2A scenes and true-colour previews are integrated. Copernicus DEM GLO-30 DSM has been processed for an approximately 30 km window at about 925 m terrain support. This is a volcanic-process/workflow candidate, not a basaltic composition match to Syrtis Major or a validated Mars analog. The regional USGS report is cited, but a site-scale geology raster, mineral map and field samples are not integrated.

### Hispar Glacier / Karakoram
A cryosphere case study for ice/debris image interpretation and field-data validation. Sentinel-2 scenes and true-colour previews are integrated; Copernicus DEM terrain descriptors are processed at the same approximate support as the Mars profile. EvK2CNR already published a Pakistan inventory of 13,032 glaciers and a preliminary glacial-lake inventory. ANALOG-X credits those baselines rather than claiming to discover or remap Pakistan's glaciers. An Earth glacier does not reproduce lunar permanently shadowed-region conditions.
 
### Chagai small salt playas near Nok Kundi — under-characterized research lead
NASA NTRS report 19740023693 describes two small salt-surfaced playas at 28°35′N, 62°36′E and 28°35′N, 62°40′E and discusses possible evaporite/brine context. ANALOG-X uses their midpoint and an analyst-defined screening AOI, not a measured playa boundary. The selected Copernicus DEM window is processed at ~925 m support (median slope 0.397°, P90 slope 1.010°, P90 3×3 local relief 38.8 m). A Sentinel-2 L2A 20 m profile has 569,772 valid pixels (2025-11-02); the separately displayed RGB quicklook is from 2026-09-18. These outputs support a first-pass salt-playa/sediment-process field plan, but do not identify evaporite minerals, confirm brine, or prove an analog to a particular Martian deposit. Field geology, mineralogical sampling and multi-date surface-change analysis remain outstanding.

### Hamun-i-Mashkel / Kharan Basin — under-characterized regional process candidate
Hamun-i-Mashkel is retained as a closed-basin/intermittent-playa process candidate with an approximate place-reference point and analyst-defined search window, not a mapped hydrological polygon. Its ~925 m Copernicus DSM window is exceptionally flat (median slope 0.0065°, P90 slope 0.0965°, P90 3×3 local relief 4.9 m). The current Sentinel-2 spectral screen (2026-08-09) contains 109,692 valid pixels in a 1,108 × 99 cell grid; it is a narrow sample, not full basin coverage. A separate 2026-10-25 RGB quicklook provides recent visual context. It may support process rehearsal around playa sedimentation and wetting-drying, but no brine, mineral, inundation history or sediment strength has been measured.


## Mars terrain reference

Nili Patera in the Syrtis Major quadrangle is used as a specific Mars terrain reference rather than comparing an entire Earth province to a planetary region. MGS MOLA MEGDR 64 pixels/degree topography and observation counts are processed for an approximately 30 km window. Earth Copernicus DEM GLO-30 DSM windows are mosaicked, reprojected and averaged to about 925 m before slope and local-relief descriptors are computed.

The current MOLA window contains 567 observed cells of 1,122 (50.53%) and only 87 complete 3×3 neighborhoods. This is a major quality limitation, explicitly surfaced in the app. The comparison is descriptors only; it does not prove geological equivalence, rover mobility, landing suitability or mineralogical similarity.

## Why not simply build another site-ranking dashboard?

Public 2026 challenge submissions already include mission-to-experiment/site planners and terrain/lighting matching tools. ANALOG-X does not claim that analog ranking, multi-source dashboards or terrain similarity are globally unsolved.

Its differentiating contribution is a Pakistan-first evidence operations workflow, not a claim that Koh-i-Sultan is a previously unknown volcano or that a new analog has already been scientifically validated:
- NASA POWER climate snapshots for ten coordinates;
- Sentinel-2 L2A scene discovery, clipped RGB previews and 20 m spectral-context profiles over four Pakistan study windows;
- Copernicus DEM GLO-30 profiles for four Pakistan windows, MOLA 64 ppd at Nili Patera, and LOLA 80 m / 925 m profiles at Shackleton Rim;
- explicit MOLA observation-count coverage and data-quality warnings;
- reuse and attribution of existing EvK2CNR, NDMA and SUPARCO/UN-SPIDER work;
- a map-led candidate discovery atlas that separates under-characterized leads from established references;
- deterministic specialist agents and an optional tool-using open-weight Mission Director, with a local offline fallback;
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

The current release has identified two potentially under-characterized playa-process leads in Balochistan, but has not proved that either is a new-to-science analog site. The NASA 1974 playa report is prior work and must be cited; the current AOIs are approximate screening windows rather than surveyed landform polygons. A competition-grade novelty claim requires confirmation of playa geometry, modern multi-date imagery, site-scale lithology/evaporite evidence, field sampling, comparison to a specific Mars process/site, and a transparent assessment of what differs. Hispar and Koh-i-Sultan remain reference case studies rather than new discoveries.

## Permanent lunar-base terrain reference

ANALOG-X now includes a separate lunar terrain reference: NASA LRO LOLA PDS GDR 80 m elevation and count grids around Shackleton Rim. The 29.6 km window is area-averaged to 925 m for a common-support terrain profile. This adds actual lunar topography to the portal, but it does not make Hispar a permanently shadowed-region analog. Diviner annual temperature / water-ice-permafrost products, illumination analysis, neutron data, and resource mapping remain outstanding. The Shackleton window has median/P90 slope of 13.40°/30.94° and P90 3×3 local relief of 1,391 m at coarse support; it should be treated as rugged terrain context, not a base recommendation.

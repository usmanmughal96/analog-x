# ANALOG-X — research gap and positioning

## Challenge alignment

The NASA Space Apps 2026 challenge asks teams to identify and characterize new terrestrial analogs for future permanent lunar-base locations and Mars, using open Earth, Moon and Mars data, and to present the findings as a map, visualization or tool.

Official brief: https://www.spaceappschallenge.org/2026/challenges/permanent-moon-base-locations-and-mars/

## What is already solved (do not claim as new)

1. **NASA Planetary Analog Explorer** already documents established terrestrial analog environments.
   https://science.nasa.gov/solar-system/analog-explorer/
2. **Existing 2026 teams** have published comparable ideas:
   - ODYSSEY: mission brief → experiment tasks → Earth-site ranking → planetary limitations. https://github.com/MahmoudAdelbghany/ODYSSEY
   - Earth Analog Explorer: terrain, illumination and stability comparisons for lunar/Mars sites. https://github.com/azrialahmad/earth-analog-explorer
   - Analog Fingerprint: task-focused analog comparison and similarity tooling. https://github.com/Gharbawy1/Nasa-2026
3. **Pakistan already has operational satellite monitoring.**
   - NDMA publishes early-warning advisories, GLOF outlooks, hazard projections and situation reports: https://www.ndma.gov.pk/
   - SUPARCO/SACCS Space4Climate monitors glaciers, snow, air quality/aerosols, forests, land cover, waterways and coastal dynamics: https://space4climate.gov.pk/
   - SUPARCO DisasterWatch distributes satellite-based disaster information for floods, drought, landslides, GLOFs, heatwaves, forest fire, smog/fog and earthquakes.
   - UN-SPIDER already hosts SUPARCO-developed flood mapping, flood hazard and Google Earth Engine drought practices.
   - EvK2CNR/UNDP published a Pakistan inventory of 13,032 glaciers covering 13,546.93 km².
4. **Global data discovery and Earth-observation processing already exist.** Microsoft Planetary Computer offers public Sentinel-2 STAC metadata and short-lived SAS data access without a registered account. Google Earth Engine is another option, but non-commercial use requires project registration and eligibility verification.

## What is actually differentiated about this submission

ANALOG-X is repositioned as a **Pakistan-first Planetary Analog Evidence Atlas**, not another global analog ranking engine.

Its concrete contribution is a reproducible characterization package for two distinct Pakistan field environments:

- **Koh-i-Sultan / Chagai:** volcanic and arid outcrop context for rehearsing geological mapping, sample-context documentation and orbital-to-ground observation workflows relevant to Mars volcanic terrain.
- **Hispar Glacier / Karakoram:** high-altitude cryosphere context for rehearsing snow/ice remote-sensing interpretation, debris-boundary observation, cold-weather sensor deployment and remote field data workflows. This is not claimed to reproduce lunar permanently shadowed regions or Mars ice deposits.

The output couples:
- real NASA POWER climatology snapshots at candidate coordinates;
- Copernicus Sentinel-2 L2A scenes discovered through Microsoft Planetary Computer;
- common-grid spectral screening descriptors with scene ID, date, cloud metadata, CRS, valid-pixel coverage and source attribution;
- published Pakistan glacier and geological context;
- links to NDMA and UN-SPIDER field-risk / remote-sensing practices;
- explicit distinctions between measured evidence, curated context, missing data and physically non-transferable planetary conditions.

## Narrow problem statement

**Under-characterized Pakistani analog environments are difficult to evaluate reproducibly for specific lunar/Martian field-rehearsal tasks because their orbital observations, local climate records, geological context and partner-agency evidence are scattered across different systems and have inconsistent spatial/temporal support.**

ANALOG-X assembles those evidence layers into an auditable site dossier and field-validation plan. It does not replace NASA's analog catalogue, SUPARCO's Space4Climate/DisasterWatch, NDMA's early-warning operations or UN-SPIDER's established recommended practices.

## Research questions

1. What repeatable spectral-context descriptors can be extracted from public Sentinel-2 L2A observations around Koh-i-Sultan and Hispar Glacier?
2. How do NASA POWER climatology conditions contextualize a field campaign at each site?
3. Which specific mission field methods can be rehearsed at each location, and which cannot?
4. What evidence is missing or access-restricted, and what field measurement or agency data request would close each gap?
5. How sensitive are interpretations to scene date, cloud/shadow masking, spatial support and resampling?

## Scientific safeguards

- No site is labelled a validated lunar/Mars analog without ground truth and specialist review.
- Sentinel-2 ratios and indices are screening descriptors only, not mineral identification or glacier boundary certification.
- NASA POWER is gridded climatology, not an on-site station or surface temperature.
- High-NDSI pixels are not automatically glacier ice; terrain shadow, snow, debris and seasonal state require validation.
- A field-campaign index is not planetary similarity, landing safety or rover traversability.
- No SUPARCO raw layer is claimed as ingested until a real download/API, coverage, date, licence and metadata are confirmed.

## What could make this stronger before final submission

1. Finish the Sentinel-2 COG processing and publish the two site profile JSONs and previews.
2. Retrieve and cite the relevant EvK2CNR inventory map/vector with permission and licence recorded.
3. Obtain written access/metadata for a Chagai-relevant SUPARCO/SACCS or PRSS-1 product, if available.
4. Add scale-matched terrain morphology from NASADEM/SRTM and Mars MOLA / lunar LOLA.
5. Have a geologist or planetary-science mentor review the candidate site interpretations and the field protocols.

# Methodology

## Research question
Which aspects of the Koh-i-Sultan volcanic field in Chagai, Pakistan, can inform selected field-geology methods and robotic geological reconnaissance workflows for Martian volcanic terrain represented by the Syrtis Major MC-13 quadrangle?

## Scope
This is a reconnaissance and evidence-curation prototype. It does not claim complete Earth–Mars environmental equivalence. Earth and Mars geological histories, gravity, atmospheric pressure, radiation and thermal environments differ.

## Candidate comparison dimensions
- Geological setting and mapped lithologic evidence (qualitative, source-attributed).
- Terrain morphology (quantitative only after compatible DEM processing).
- Earth surface reflectance and Martian surface products (not interchangeable without calibration and careful interpretation).
- Thermal context (keep measurement types, temporal coverage and units distinct).
- Mission relevance: geological mapping, outcrop logging, sample-context documentation, field imaging and procedural rehearsal.

## Quantitative workflow
1. Acquire the exact NASADEM/SRTM tile covering the selected Koh-i-Sultan study area and verify product version, vertical units, void treatment, CRS and licence.
2. Acquire MOLA MEGDR elevation and observation-count products for the Syrtis Major reference. Exclude no-observation cells and report coverage.
3. Reproject Earth data to a local metric CRS. Do not compare 30 m Earth pixels directly with ~14.8 km MOLA cells. Aggregate to defensible common spatial support before any comparison.
4. Calculate elevation, slope and local-relief descriptors independently. Publish distributions and data coverage, not a black-box similarity percentage.
5. Link each geological assertion to a map or publication and record map scale and geographic coverage.
6. Report limitations and uncertainties alongside each metric.

## Current status
The public repository build is a source-grounded prototype. The raw rasters have not been processed; no numerical analog score or terrain statistic is claimed. NASA GIBS is a visual browse service only. SUPARCO Space4Climate is a potential data source; no Chagai-specific product has been verified or ingested.

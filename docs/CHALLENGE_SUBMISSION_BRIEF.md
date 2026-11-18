# ANALOG-X — Challenge submission brief

## Title

**ANALOG-X: Experiment-Level Planetary Analog Discovery, Transferability and Failure Intelligence**

## The question

What can Earth teach us about operating on the Moon and Mars—not merely which landscapes look similar, but which field experiments, measurements and operational procedures can be transferred to another world, and where those analogies fail?

## Why this is different

Most analog maps rank Earth places by visual or environmental similarity. ANALOG-X changes the unit of analysis: it evaluates a **specific experiment or physical process at a specific Earth site**.

For every experiment pathway, the system records:

1. What can be rehearsed on Earth.
2. Why the selected environment is relevant.
3. Which planetary conditions invalidate or limit the transfer.
4. What additional measurement is required before relying on the analogy.
5. Which data products and evidence layers support the claim.

This is the Analog Transferability & Failure Analysis (ATFA) framework. Its classes are transparent, qualitative expert-authored rules—not probabilities, a universal similarity score, or NASA certification.

## Earth study/reference network

The current atlas includes ten Earth environments:

- **Pakistan:** Chagai small salt playas, Hamun-i-Mashkel playa, Koh-i-Sultan volcanic field and Hispar Glacier.
- **Global references:** Dallol / Danakil Depression, Atacama Desert, McMurdo Dry Valleys, Haughton impact structure, Icelandic volcanic fields and Death Valley.

The Pakistan locations are treated as under-characterized candidate leads, not confirmed new planetary analog discoveries. The global references provide established comparison environments and process controls.

## Planetary reference targets

- **Moon:** Shackleton Rim / lunar south pole, using LRO LOLA elevation plus processed Diviner PRP V2.0 thermal summaries for an analyst-defined 29.6 × 29.6 km comparison window.
- **Mars:** Nili Patera / Syrtis Major, using MGS MOLA MEGDR topography and observation-count data.

## Data and methods

The reproducible pipeline combines:

- NASA Earthdata CMR for MODIS/Terra MOD11A2 V061 granule discovery and public browse imagery.
- NASA POWER gridded climate context for ten Earth sites.
- Sentinel-2 L2A scene discovery and spectral-context previews.
- Copernicus DEM GLO-30 DSM for matched-scale Earth terrain analysis.
- MGS MOLA MEGDR 64 pixels/degree topography and observation counts around Nili Patera.
- LRO LOLA 80 m polar elevation data, aggregated to approximately 925 m support around Shackleton Rim.
- LRO Diviner PRP V2.0 thermal summary: 6,823 Shackleton-window triangles; median annual-average temperature at 2 cm is 103.786 K and median annual-maximum surface temperature is 238.568 K. The ice-depth field contains negative and -999 censored values and is withheld from interpretation pending QA.
- NASA PDS Search API metadata queries for Mars, MOLA, HiRISE, Moon, LOLA and Diviner holdings.

### Current reproducible outputs

- Ten Earth sites with NASA POWER profiles.
- Ten Earth Copernicus DEM local terrain grids, each 32 × 32 cells at approximately 925 m support.
- One Mars MOLA grid (33 × 34 cells) and one lunar LOLA grid (32 × 32 cells) at comparable regional support.
- Twenty public MODIS browse JPEGs (two per Earth site), indexed with CMR granule and source URL provenance. These are tile-level visual browse assets, not calibrated, AOI-clipped LST science arrays.
- 7,290 valid 5.55 km Earth sub-windows sampled from the ten existing 30 km DEM regions, plus 729 valid Shackleton windows and 21 valid Nili Patera windows. The Earth pipeline also calculates a separate ~30 m parent-area DSM roughness summary for all ten regions (98.36–100% valid-cell coverage in the current run); it is shown as Earth-only context and is not mixed into the ~925 m cross-planet terrain index. The scan uses median slope, P90 slope and P90 local relief at ~925 m support, with 500 deterministic weight-sensitivity draws.
- Forty-one site-specific experiment pathways across terrain mobility, spectral ground truth, evaporite processes, cryosphere remote sensing, volcanic morphology, dust processes, impact geology, biosignature/contamination-control methods and human/robotic operations.
- Six PDS Search API target/instrument queries, capped at 100 results each; the current index returns 500 unique observational product records across the queries, including instrument-specific MOLA, LOLA and Diviner products. The target-filtered HiRISE query returns no relevant product rows in this index, so the dashboard links the MRO HiRISE RDR dataset profile separately.

The 3D terrain views display elevation relative to each local grid's median. They are not vertically co-registered across bodies and are not a landing-safety or rover-trafficability model.

## Each shortlisted sub-window also exposes its parent site's ATFA priority experiment, rehearsal pathways, analogy breaks, next measurements and evidence states. This experiment context remains separate from the terrain index. The regional discovery shortlist is deliberately bounded to the ten pre-selected Earth areas; it is not a global Earth scan. Its terrain index is exploratory and terrain-only, not an analog probability, geological match or landing/rover-safety score. The 21 Mars windows that pass the stated local data threshold do not remove the parent MOLA coverage limitation.

## Data-status transparency

NASA CMR/PDS granule and product records are catalogue discovery, not science-array ingestion. MODIS browse JPEGs are visual context only; the underlying MOD11A2 HDF arrays and QA layers have not been decoded for site-level temperature statistics. The 500 PDS records are metadata records, not 500 processed science products. SUPARCO SGSS / Space4Climate / DisasterWatch portals are cited as institutional context; no machine-readable dataset from those portals is claimed as integrated because a reusable endpoint and licence have not been verified.

## The operational deliverable

The interactive web module provides:

- A ten-site Earth atlas with Moon/Mars filtering.
- A mission-specific analog selector that compares candidate field experiments across sites without collapsing them into one universal score.
- Side-by-side 3D DEM surfaces for Earth and the selected planetary target.
- A 3D site/pathway landscape and evidence-coverage charts.
- OpenStreetMap basemap with NASA GIBS VIIRS true-colour imagery and a monthly time scrub/animation.
- A MODIS browse gallery and PDS product metadata links.
- A downloadable mission experiment brief in JSON, suitable for review, adaptation and field planning.
- A self-hostable FastAPI backend with read-only science-pack endpoints and a field-evidence notebook API.

The static science pack makes the public dashboard usable without a hosted backend. The API is optional for deployments that need shared field observations or integration with other systems.

## What the analogs can and cannot teach us

Earth environments can help rehearse remote sensing, field spectroscopy, terrain mapping, route-planning workflows, sample handling, sensor deployment, dust monitoring, cold-region operations, impact-geology mapping and human/robotic field procedures.

They cannot reproduce lunar vacuum, one-sixth gravity, the radiation environment, electrostatic lunar dust, Martian atmospheric pressure/composition, lower gravity or Martian regolith chemistry. Terrestrial glacier ice is not equivalent to accessible lunar permanently shadowed region ice. A salt playa is not proof of a Martian evaporite match. A coarse DEM is not evidence of landing safety.

## Next validation steps

1. Download and decode MOD11A2 HDF science arrays and per-pixel QA; browse JPEGs are not quantitative LST.
2. Ground-truth the Balochistan playa and Koh-i-Sultan hypotheses with field spectroscopy, XRD/XRF, grain-size, crust-strength and sediment-facies observations.
3. Collect field spectra and temperature transects at selected sites.
4. Add higher-resolution local DEM/LiDAR and metre-scale mobility trials.
5. Complete QA of the processed Diviner ice-depth field, then add authoritative lunar illumination / permanently shadowed region analysis. Current Diviner temperature statistics are historical thermal-model summaries, not direct ice measurements.
6. Run controlled mission-rehearsal protocols with instrument, operator, communications and equipment-failure logs.

## Scientific integrity statement

ANALOG-X does not claim that any Earth location is a perfect Moon or Mars analog. It does not certify landing sites, accessible resources, mineral abundance, field access or rover safety. It distinguishes direct measurements, derived metrics, qualitative hypotheses and missing evidence. Its purpose is to help scientists select more defensible Earth experiments—and understand exactly what those experiments can and cannot tell us about another world.

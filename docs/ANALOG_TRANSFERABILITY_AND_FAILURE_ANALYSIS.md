# Analog Transferability & Failure Analysis (ATFA)

## Purpose

ATFA changes the unit of analogy from “this whole Earth site resembles the Moon/Mars” to “this named experiment or physical process can be rehearsed at this Earth site, within stated boundaries.”

It is an experiment-planning and evidence-audit layer, not a universal similarity score, a probability model, a landing-site selector, or a NASA-certified tool.

## Reproducible build

From the repository root:

    python -m pip install requests
    python science/build_transferability.py
    python scripts/fetch_pds_search.py

Outputs:

- \`data/transferability/transferability.json\`: ten site dossiers, experiment pathways, evidence states, planetary reference context, transferability limits and next measurements.
- \`data/planetary/pds_search.json\`: public PDS Search API query records and returned product metadata, where available.

The GitHub Actions workflow \`.github/workflows/build-transferability.yml\` builds and validates both outputs on relevant pushes, manual dispatch and weekly schedule.

## Classification contract

- **Moderate:** a bounded Earth process or field method is useful to rehearse; planetary environmental transfer remains limited.
- **Limited:** only a subset of the method/process transfers, or important site-specific evidence is missing.
- **High:** reserved for direct evidence plus independent validation. This release intentionally assigns no high classifications automatically.

These are transparent qualitative rules authored in \`science/build_transferability.py\`. They are not learned probabilities and should be reviewed by planetary geologists, remote-sensing scientists and mission-operations specialists.

## Site and experiment scope

The first release contains ten curated study/reference environments:

- Chagai small salt playas and Hamun-i-Mashkel, Pakistan: evaporite/playa process leads.
- Koh-i-Sultan, Pakistan: volcanic mapping and alteration-reconnaissance methods; USGS mapping describes andesitic lava, tuff and agglomerate, not a basaltic compositional match.
- Hispar Glacier, Pakistan: cryosphere remote-sensing and field-method rehearsal; existing glacier inventory work is attributed as prior work.
- Dallol, Atacama, McMurdo Dry Valleys, Haughton impact structure, Iceland and Death Valley: established process/field-method references.

Candidate coordinates are map reference points, not surveyed polygons, access permissions or field-safety assessments. The two Balochistan playa sites remain historical/under-characterized leads pending modern field validation.

## Evidence states

ATFA displays NASA POWER, Copernicus/MOLA/LOLA terrain, Sentinel-2 context and dossier/source evidence independently. A processed terrain profile does not mean every environmental variable is measured. A missing layer is not silently filled with a proxy.

Known constraints include:

- NASA POWER climatology is gridded climate context, not a local weather station or surface-temperature record.
- Sentinel-2 indices and RGB quicklooks are screening context, not mineral identification, brine detection or ground truth.
- Copernicus DEM GLO-30 is a DSM; the latest processing run produced matched ~925 m local grids for all ten Earth study/reference windows. These aggregates are regional context, not rover-scale hazard analysis.
- Nili Patera MOLA selected-window observation coverage is approximately 50.53%, with only 87 complete 3×3 neighbourhoods in the current product.
- Shackleton LOLA elevation is integrated at 80 m native support and aggregated to approximately 925 m for regional comparison. LOLA return counts describe measurement support; they are not PSR or ice maps.
- Diviner PRP V2.0 has been diagnosed in the project; ice-depth interpretation and accessible-resource claims remain withheld pending authoritative product metadata and QA.
- Earth cannot reproduce lunar vacuum, one-sixth gravity, planetary radiation or electrostatic lunar dust. Earth cannot reproduce the Martian thin CO2 atmosphere, lower gravity, radiation or Martian regolith chemistry.

## NASA PDS discovery integration

The PDS script queries the public Search API for Nili Patera, MOLA, HiRISE, Shackleton, LOLA and Diviner terms. The API is used for product metadata discovery. A result does not establish that a binary file is public, downloaded, calibrated, spatially complete or analysis-ready. NASA PDS documentation explicitly notes that the Search API registry is not fully populated; zero results must not be interpreted as proof that the archive contains no relevant data.

The next ingestion phase should resolve product labels, check instrument calibration and coordinate metadata, select a manageable product subset, download through the documented distribution path, and record checksums and provenance before analysis.

## Visualization and maps

\`transferability.html\` is a standalone interactive science view. It uses:

- Leaflet with OpenStreetMap as the free street/terrain context base.
- NASA GIBS VIIRS imagery as an optional imagery overlay.
- Plotly charts for evidence coverage, experiment portfolio and a 3D site/pathway exploration view.
- The committed JSON science pack as its deterministic data source.

OpenStreetMap tile service is community-funded; respect its tile usage policy and attribution. For production/high-traffic deployments, configure a suitable tile provider or self-host tiles rather than assuming unlimited public tile capacity.

## Scientific review checklist before submission

1. Confirm the selected Earth AOI and the planetary target are both precisely defined.
2. Confirm product version, acquisition date, instrument, units, spatial support, quality flags and coordinate reference system.
3. Keep measurement, derived metric, qualitative interpretation and hypothesis visibly distinct.
4. State where the analogy breaks down and what controlled experiment would address the gap.
5. Avoid claims of mineral abundance, accessible ice, landing safety, rover trafficability or “new discovery” without direct evidence and independent validation.
6. Preserve links, licences, citations, processing scripts and reproducible output files.


## MODIS land-surface-temperature browse evidence

`scripts/fetch_modis_browse.py` queries NASA CMR for MOD11A2 V061 8-day land-surface-temperature granules over the ten study/reference windows and downloads two available public browse JPEGs from the most recent returned granule per site. The generated `data/nasa/modis_browse_index.json` records CMR granule IDs, acquisition intervals, original browse URLs and local image paths; the browse files are stored under `data/nasa/modis_browse/`.

In the current successful pipeline run, public browse imagery was downloaded for all ten sites (20 JPEGs total). These are granule/tile browse previews, not AOI-clipped imagery or calibrated LST values. The dashboard offers them as visual context only. Quantitative MOD11A2 science-file analysis still requires the HDF science bands, scale factors, fill values and per-pixel QA decoding; do not infer temperatures from browse colours.


## 3D DEM surface grids

The latest Earth–Mars terrain build successfully exported compact elevation arrays for all ten curated Earth sites from Copernicus GLO-30, on the approximately 925 m analysis support used for the existing slope/relief comparison. The lunar LOLA workflow exports its own approximately 925 m aggregate grid. Values in the 3D view are expressed as elevation relative to each local grid's median, with no-data cells preserved as null. This permits visual inspection of local morphology without comparing absolute elevations across different datums or projections. Grid orientation is not co-registered across bodies, and the display is not a landing, traversability or hazard model.


Latest verified terrain coverage: 10/10 Earth sites processed, plus the Nili Patera MOLA grid and Shackleton Rim LOLA grid. Each is a 32×32 Earth/Moon or 33×34 Mars local surface array, with no-data masks retained and relative elevation referenced to each grid's own median.

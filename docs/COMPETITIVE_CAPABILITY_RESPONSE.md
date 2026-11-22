# Competitive capability response: ANALOG-X

**Benchmark review date:** 22 November 2026  
**Purpose:** Translate publicly reported competitor strengths into implemented ANALOG-X capabilities while preserving methodological differences. Competitor numbers below are self-reported project claims, not independently audited measurements.

## 1. Public benchmark comparison

| Project | Publicly reported scope | Strength to learn from | What the public scope does not establish |
|---|---|---|---|
| **Earth's Moon Twins / Team Shoemaker** | The team's demo reports 22,147 Earth windows at approximately 10 km scale against 13 lunar reference sites, and 65 robust candidate areas. Its public presentation describes separate rock and terrain dimensions and test AUC figures around 0.92 for mare and 0.90 for Hadley-region cases. | A broader target set, rock-plus-terrain screening, separate evidence dimensions and explicit candidate robustness. | These are the team's published counts and model claims. Their AUC is not independently reproduced by ANALOG-X; interpretation depends on labels, test split, sample count and spatial leakage control. |
| **TwinWorlds** | The public project repository describes 354,342 Earth land cells on a 0.25-degree grid, 16 planetary targets, 33 datasets and approximately 2.48 GB of raw data, with a multi-dimensional matching workflow. | Greater declared planetary-target and dataset breadth, broad global grid coverage, multi-dimensional evidence and a model-card/validation narrative. | Publicly reported dataset counts do not by themselves establish equal spatial support, consistent processing, full global coverage for every variable or independent validation quality. |
| **Earth Analog Explorer** | The public repository describes 30 ranked sites, including 12 seed/reference locations plus 18 scanned candidate sites, with approximately 6 km windows and terrain, low-sun and bare-ground comparisons over selected additional regions. | Focused terrain and environmental candidate screening, lighting-related comparison and explicit candidate expansion beyond seed sites. | The documented scan is a bounded regional search, not an exhaustive global scan; site count does not equal global coverage or field validation. |
| **ANALOG-X** | The committed 18 November 2026 GLO-90 release processed 26,475/26,475 listed land tiles (100% of that provider inventory), 0 tile failures and evaluated 5,852,396 terrain windows. It retained 1,200 Moon-target and 1,200 Mars-target shortlist windows. | Worldwide land-tile terrain screening, separate Moon/Mars targets, tile-aware candidate provenance, ~5.55 km windows at ~925 m support, Pakistan-first study leads, ATFA task transferability, mission rehearsal, deterministic Agent Bay, evidence passports and a permission-gated field evidence workflow. | Global search is a GLO-90 terrain screen, not a globally complete multi-sensor geology/climate/illumination model. The stored shortlist is bounded. Terrain indices are not calibrated accuracy or analog probabilities. Pakistan ground truth has not yet been collected. |

### Public source links

- Earth's Moon Twins / Team Shoemaker demo: https://shoemaker-spaceapps.github.io/demo/
- Earth's Moon Twins / Team Shoemaker data explorer: https://shoemaker-spaceapps.github.io/explore/
- TwinWorlds public repository: https://github.com/TayyabXtreme/Twin_World_Nasa_Space_APP_Challenge_2026
- Earth Analog Explorer public repository: https://github.com/azrialahmad/earth-analog-explorer

## 2. Do not compare the headline numbers as if they were equivalent

The projects do not use the same unit of analysis or input data. ANALOG-X global screening uses non-overlapping ~5.55 km windows with nominal ~925 m terrain analysis support from GLO-90 DSM input; Earth's Moon Twins reports ~10 km windows; TwinWorlds describes a 0.25-degree grid (roughly 28 km at the equator, with latitude-dependent east-west dimensions); Earth Analog Explorer describes ~6 km windows over selected regions. Counts of grid cells, windows, candidates, datasets and target sites are different quantities and cannot be ranked as a single performance metric.

ANALOG-X should not claim that it beats competitors on data breadth, mineralogical characterization, model accuracy, lighting or field validation. Its strongest defensible distinction is that it joins a complete inventory-driven GLO-90 land scan with a mission-task workflow, separate evidence states, target-specific analysis, provenance and a Pakistan field-validation pathway.

## 3. Capability changes made in ANALOG-X

| Competitor capability pattern | ANALOG-X implementation | Evidence in repository | Remaining limitation |
|---|---|---|---|
| Broader Earth candidate discovery | 24-shard GLO-90 inventory scan and spatially diversified shortlists | scripts/build_global_discovery.py; scripts/merge_global_discovery.py; data/global_discovery/global_discovery.json; global-discovery.html | Complete for the listed public land-tile inventory only; ocean excluded; shortlist is bounded and terrain-only. |
| More target and source breadth | Separate global GLO-90 terrain, 2023 land-cover sampling, NASA POWER climatology, processed GLiM centre-point generalized geology context (200/200 retained top-candidate queries), regional GLO-30, Sentinel-2 L2A, NASA CMR/PDS discovery, LOLA, MOLA and Diviner evidence | data/source_registry.json; data/global_discovery; data/validation | Each source has a different support, coverage and state. Metadata-only and browse-only inputs remain visibly distinguished. |
| Rock/geology contextualization | GLiM centre-point polygon lookup script and automatic enrichment workflow for retained leading windows | scripts/enrich_global_lithology.py; tests/test_global_lithology.py; data/source_registry.json | A committed output records 200/200 successful point queries for the retained top-100-per-target shortlist. Generalized centre-point mapping at coarse scale; no area-weighting or field verification; excluded from ranking. The served derivative's licence terms require confirmation. |
| Terrain robustness and validation | Primary core-family ranking, secondary feature diagnostics, source-to-source NASADEM cross-check and explicit shortlist rank-sensitivity reports | scripts/build_quantitative_validation.py; scripts/validate_nasadem_crosscheck.py; data/validation | Two feature families from the same DEM are not independent. NASADEM comparison covers only selected overlapping Earth sites. No calibrated analog-ranking accuracy. |
| Environmental candidate scan | NASA POWER and 2023 land-cover context at shortlisted global candidates; regional Sentinel-2 spectral context remains separate | scripts/enrich_global_power.py; scripts/enrich_global_landcover.py; data/global_discovery | Context is limited to the retained shortlist, not a full global climate or land-cover reprocessing of every candidate window. Sentinel-derived products are not geological or mineral labels. |
| Mission workflow and field evidence | ATFA, Mission Rehearsal Lab, deterministic Agent Bay, Field Validation Kit and Pakistan campaign plan | docs/ANALOG_TRANSFERABILITY_AND_FAILURE_ANALYSIS.md; field-validation.html; data/field_validation/campaign_plan.json | Field ledger is empty until real, permission-led observations are collected and independently reviewed. |

## 4. Ranking governance — no synthetic consensus

The prior global output combined the core and secondary indices by arithmetic average. The quantitative diagnostic showed poor concordance between the two families in the retained set (Moon Spearman -0.6650, Mars -0.7122, with almost no top-100 overlap). This is a material ranking-stability problem, not a strength.

The global workflow has been revised so:
1. The primary shortlist is ordered by the core terrain feature family only: median slope, P90 slope and P90 local relief.
2. The secondary diagnostic family (P95 slope, elevation IQR and detrended roughness) is reported separately.
3. The secondary rank is displayed within the retained primary shortlist, making the feature-family disagreement inspectable.
4. No averaged consensus score or score-family "agreement percentage" is presented.

The two feature families use the same DEM and are not independent-data validation. The current quantitative report is diagnostic only. The merge code now enforces schema 1.1.0, core-only ordering, unique IDs, finite score values, WGS84 bounds and secondary-rank permutations. The saved dataset remains stale until the 24-shard workflow regenerates it; the interface and quantitative report expose this as a ranking-release gate.

## 5. Validation engineering added in the current development branch

- Merge-time checks reject incomplete shard sets, inconsistent inventories/reference profiles, invalid per-shard processed/failed accounting, duplicate candidates, non-finite scores, invalid WGS84 coordinates and malformed target outputs.
- The quantitative report now verifies schema 1.1.0, the core-only ranking contract, primary ordering, sequential ranks, secondary diagnostic rank permutations and unique IDs. A ranking-ready release is not labelled accuracy-validated.
- A separate independent-label evaluator accepts only reviewer-attributed positive/negative labels with evidence references and spatial groups. It uses a deterministic spatial-group holdout and withholds ROC-AUC when the held-out split lacks both classes. No labels or scores are fabricated.
- Pull requests run a fast scientific-contract and unit-test job; the expensive 24-shard scan is reserved for non-PR release runs.

## 6. Competitive priorities still open

- Improve evidence depth with additional independently processed datasets, not merely a larger source list.
- Add defensible illumination / shadow / solar geometry context for the Moon and Mars with compatible time and terrain support.
- Build independent labels and spatially blocked validation for candidate rankings; publish test design and uncertainty.
- Collect and independently review Pakistan field observations after permission and safety requirements.
- Expand geology from point context toward appropriate regional mapping and field evidence, while keeping source scale and mapping uncertainty visible.
- Retain reproducible run manifests, failed-tile reporting, source licences and exact method parameters for each released dataset.

## 7. Release language

Use "global terrain-screening candidate" rather than "confirmed planetary analog"; report competitors' headline counts as their own published claims; do not describe browse imagery or catalogue metadata as processed science arrays; do not claim physical field validation until documented, independently reviewed observations are actually present.

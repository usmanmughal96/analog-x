# Competitor method review and reuse record

**Reviewed:** 18 November 2026  
**Purpose:** document which public 2026 NASA Space Apps analog-research approaches informed ANALOG-X's next iteration, and distinguish methodological benchmarking from source-code reuse.

## What was reviewed

| Public project | Publicly described method / contribution | License check and reuse decision |
|---|---|---|
| [Team Shoemaker — Earth's Moon Twins](https://github.com/shoemaker-spaceapps/shoemaker-spaceapps.github.io) | Large Earth-window screening against multiple lunar targets; robust terrain-distance features; AHP weighting and rock-label match; known-analog / hard-negative evaluation with AUC and bootstrap intervals; candidate ranking and sensitivity checks. | A repository MIT license was present. We reviewed its analysis/evaluation scripts as a methodological benchmark. **No Shoemaker source code, project data, or output assets were copied into ANALOG-X.** The regional scan was implemented independently against ANALOG-X's own Copernicus, LOLA and MOLA grids. |
| [Earth Analog Explorer](https://github.com/azrialahmad/earth-analog-explorer) | The README describes regional candidate windows, matched terrain descriptors, a 6 km analysis scale, low-sun/lighting considerations, and user-adjustable parameter/weight sensitivity. | No repository license file was surfaced in the files inspected on 18 November 2026. **No source code or assets were copied.** The ideas were used only as a public design/method comparison and independently implemented with ANALOG-X data. |
| [TwinWorlds](https://github.com/TayyabXtreme/Twin_World_Nasa_Space_APP_Challenge_2026) | The README describes a much broader scan of Earth land cells, 16 planetary targets, multiple datasets and seven measurement dimensions, with machine-learning components. | No repository license file was surfaced in the files inspected on 18 November 2026. **No source code, datasets, or assets were copied.** Its breadth was used as a benchmark for identifying ANALOG-X's global-search and multi-dimensional evidence gaps. |

A missing license file is not permission to copy. This review therefore makes no unlicensed source reuse claim. General research ideas and published descriptions were used to inform the design; implementation code and generated results in this repository were authored from ANALOG-X's own data and codebase.

## What ANALOG-X implemented independently

The new `science/build_regional_window_scan.py` pipeline:

1. Uses the ten existing 30 km Copernicus DEM GLO-30 DSM study windows and the local NASA LOLA/MOLA reference grids already processed by ANALOG-X.
2. Derives overlapping 6 × 6 cell (~5.55 km) regional windows at approximately 925 m support.
3. Applies an explicit minimum-data rule: at least 70% valid elevation cells and at least 15 valid slope and local-relief samples.
4. Calculates median slope, P90 slope and P90 3 × 3 local relief.
5. Compares each Earth window with the median profile of valid windows in the selected Moon/Mars reference grid using equal-weight, IQR-normalized absolute feature gaps.
6. Repeats the local top-decile selection under 500 deterministic random feature-weight draws and reports rank sensitivity within each parent Earth study area.
7. De-duplicates the displayed shortlist by minimum approximate geographic separation and limits the number of shortlist entries per parent region.

The generated output is `data/analog_benchmark/regional_window_scan.json`, displayed at [discovery.html](https://usmanmughal96.github.io/analog-x/discovery.html).

## Deliberate differences and validation boundaries

- The current search is **not global**. It scans only the ten pre-selected parent regions already in ANALOG-X. It must not be described as a 7,290-window scan of the whole Earth.
- The index is terrain-only. It does not include rock type, mineralogy, regolith properties, dust, illumination, temperature, radiation, resources or mission operations.
- The weight-sensitivity statistic is a rank-stability diagnostic, not a confidence interval, probability or independent-sample test. Adjacent windows overlap and are spatially dependent.
- The Mars parent window has only 50.53% observed MOLA cell coverage. Only local windows meeting the stated valid-data threshold are ranked.
- The source terrain support is approximately 925 m. It cannot resolve rover-scale hazards, bearing strength or local traversability.
- The scan discovers candidate sub-windows within existing reference areas. It does not establish new-to-science geological analog sites; field mapping and independent geological validation are still required.

## Sources inspected

- Team Shoemaker repository: https://github.com/shoemaker-spaceapps/shoemaker-spaceapps.github.io
- Earth Analog Explorer repository: https://github.com/azrialahmad/earth-analog-explorer
- TwinWorlds repository: https://github.com/TayyabXtreme/Twin_World_Nasa_Space_APP_Challenge_2026
- ANALOG-X regional scan source: https://github.com/usmanmughal96/analog-x/blob/main/science/build_regional_window_scan.py


## 23 November 2026 — refreshed public benchmark

This refresh adds public project descriptions surfaced in the 2026 challenge period. Counts below are **team-published claims**, not independently rerun measurements or audited scientific results. They are useful for capability comparison, not a leaderboard or accuracy comparison.

| Public project | Publicly stated scope | Strong capability to benchmark against | What the claim does not establish |
|---|---|---|---|
| [Earth Dev Defense](https://earthdevdefense.github.io/) | 43 Earth places, 12 Moon/Mars targets, 480 tiles, 17 features per tile | Multi-site, multi-target feature coverage | Independent label accuracy, ground truth or directly comparable resolution/method |
| [TerraNova / DaRK_MATTER](https://github.com/Yakiyo/terra-nova) | 78,247 land cells at 0.5° (~55 km at equator); target-specific matching, cited criteria and benchmark validation are described | Broad global candidate-cell inventory and transparent target criteria | The 55 km grid is not directly comparable to ANALOG-X's ~5.55 km windows; the README claim is not independently audited here |
| [Earth Analog Explorer](https://github.com/azrialahmad/earth-analog-explorer) | 30 Earth sites (12 initially reported analog locations + 18 DEM-scanned candidates); 3 planetary target areas; one combined ranked list | Named known analogs plus generated candidates; explicit warning that terrain match is not site safety | Not a whole-Earth search; the published README describes terrain matching rather than full operational/field validation |
| [Planetary Analog Finder](https://github.com/shishir-kuet/terrestrial-analog-finder) | 12 planetary reference regions; 558 Earth windows (469 complete, 89 excluded); multi-source thermal/mineral context is described | Explicit missing-data exclusions and thermal/mineral context | Candidate pool and coverage are narrower than a global land-tile scan; self-reported outputs require independent verification |
| [Planetary Analogue Catalogue](https://github.com/rachellelecussan/planetary-analogue-catalogue) | 16 curated sites, 96 references and 42 photos in its published README | Site-level geology, access, safety, evidence references, review status and controlled vocabularies | A curated catalogue is not a global quantitative discovery/ranking engine |

### ANALOG-X position after the latest release

| Dimension | ANALOG-X evidence | Assessment |
|---|---|---|
| Global terrain inventory | 26,475 / 26,475 Copernicus GLO-90 land tiles processed; 24 / 24 shards; 5,852,396 terrain windows evaluated; zero tile failures | Strongest breadth claim in the reviewed set by declared tile/window count, but not directly comparable to other teams' cell sizes or candidate definitions |
| Published ranking | 1,200 Moon + 1,200 Mars candidates; core-only order and rank-integrity release gate now passes | Ranking file is release-ready; no independent accuracy claim |
| Environmental/geology context | 2023 land-cover for 2,391 / 2,400 retained windows; NASA POWER and GLiM context for top 100 per target | Multi-layer evidence exists but is shortlist-limited, not full-global raster enrichment |
| Lunar evidence | 5 m Shackleton LOLA terrain; separate 80 m LOLA profile; 100 m WAC illumination products; Diviner PRP V2.0 thermal/ice-stability model | Better lunar evidence depth than a terrain-only comparison; still not mission-date lighting, formal PSR polygons, accessible ice or rover safety certification |
| Process-level analog reasoning | ATFA experiment/task-specific transferability and explicit failure modes | Distinctive conceptual layer; transfer classes remain expert-authored rules, not a calibrated model |
| Pakistan field readiness | Four candidate field campaigns, offline GNSS/instrument/uncertainty capture workflow and permission gates | Strong field-readiness workflow; **zero actual field observations** |
| Independent evaluation | Empty independent positive/negative label ledger; spatial-group evaluator and group-bootstrap interval implementation | Evaluation machinery improved; **no AUC, accuracy, sensitivity or specificity is currently defensible** |

### What to adopt next — and what not to imitate

1. **Catalogue quality:** adopt the competitor catalogue's explicit evidence references, access/safety metadata, review status and controlled vocabularies for each named site. ANALOG-X already has a field ledger and provenance registry; the next step is to normalize these into a site-level reviewed dossier.
2. **Benchmark design:** adopt explicit known-positive and hard-negative examples, but do not label sites from ANALOG-X's own score. Independent reviewers must predeclare task-specific criteria and spatial groups.
3. **Multi-target coverage:** use additional LOLA/MOLA regions only where planetary reference products and valid-data support are documented. More targets without comparable reference data would inflate breadth without improving evidence.
4. **Thermal/mineral enrichment:** treat EMIT, ECOSTRESS, TES and Diviner as possible source families, but preserve their target-specific coverage, scale, retrieval and model semantics. Do not merge unlike values into a single similarity score.
5. **Operational readiness:** retain separate eligibility and evidence layers. A high terrain score must never become a landing, mobility, resource or safety recommendation without the corresponding engineering data.

### Benchmark conclusion

ANALOG-X's defensible edge is not a claim that its candidates are more scientifically accurate than every other team. Its strongest differentiators are the **complete, auditable GLO-90 land-tile scan; experiment-level transferability/failure analysis; a source-state/provenance system; and a comparatively deep Shackleton evidence stack**. Its most important scientific deficits remain independent labels, Pakistan field measurements, mission-epoch illumination/PSR integration and a real rover-scale hazard/traverse model.


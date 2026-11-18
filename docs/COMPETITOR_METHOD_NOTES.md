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

# ANALOG-X Regional Terrain-Window Scan

**Generated dataset:** `data/analog_benchmark/regional_window_scan.json`  
**Builder:** `science/build_regional_window_scan.py`  
**Interactive view:** https://usmanmughal96.github.io/analog-x/discovery.html  
**Status:** regional terrain-screening prototype, 18 November 2026

## Why this exists

The existing ANALOG-X terrain pack describes each Earth and planetary reference area as a regional 32 × 32 (or nearby) grid at approximately 925 m support. A single 30 km parent profile can hide local variation. The new scan divides those existing grids into overlapping smaller windows and asks where three terrain descriptors are numerically closer to a selected Moon/Mars reference.

This is an added level of regional screening. It does not expand the geographic coverage of the source DEM pack.

## Current run

| Input | Valid local windows |
|---|---:|
| Ten existing Earth DEM regions | 7,290 total (729 in each region) |
| Shackleton Rim LOLA grid | 729 |
| Nili Patera MOLA grid | 21 |

Each window is 6 × 6 raster cells, nominally 5.55 km across at ~925 m spacing. Earth input grids are Copernicus DEM GLO-30 digital surface models; Moon input is an 80 m LOLA elevation product area-aggregated to ~925 m; Mars input is MOLA MEGDR 64 pixels/degree. Window counts are reproducible from the committed source grids using the builder.

The Nili Patera parent grid remains limited: it has 50.53% observed-cell coverage and only 87 complete 3 × 3 neighbourhoods before sub-window scanning. Candidate windows are retained only when they meet the validity rule below; this does not repair missing parent-grid coverage.

## Window derivation

For each source grid:

1. Treat missing values as invalid; do not fill them for terrain derivatives.
2. Calculate slope in degrees using central differences in the source grid's nominal x/y pixel spacing. A slope value is created only when the four cardinal neighbours are valid.
3. Calculate 3 × 3 local relief as local maximum minus minimum only when all nine elevation cells are valid.
4. Move a 6 × 6 window across the raster. Keep a window only when it has at least 26 of 36 valid elevation cells (70%, rounded up), and at least 15 valid slope samples and 15 valid local-relief samples.
5. Summarize each retained window with median slope, P90 slope and P90 3 × 3 local relief.

The relief footprint of a 3 × 3 neighbourhood is approximately 2.775 km at 925 m grid spacing. The 5.55 km window size is the sampling support for the local summary; it is not a 5.55 km-resolution DEM.

## Terrain-only comparison index

For the selected planetary target, the builder summarizes each of the three features by the median across valid target windows. For each feature it calculates the interquartile range (IQR) across valid Earth windows.

For Earth window (i), the normalized mean absolute feature gap is:

[
D_i = \frac{1}{3} \sum_{j=1}^{3} \frac{|x_{ij}-m_j|}{IQR_j}
]

where (x_{ij}) is an Earth-window descriptor and (m_j) is the median descriptor for the planetary reference windows.

The displayed proximity index is:

[
S_i = 100 e^{-D_i}
]

The three baseline features receive equal weights. The index is bounded between 0 and 100 and is useful only as an exploratory comparison within this particular data pack. It is not a percentage probability, an accuracy score, a calibrated similarity measure, a geological equivalence score or an operational safety metric.

Each feature's individual closeness indicator is also exposed, so a combined index cannot conceal which descriptor is driving the result.

## Weight sensitivity

A deterministic pseudo-random sequence generates 500 normalized exponential weight triples, equivalent to draws from a symmetric Dirichlet(1,1,1) distribution. For each draw, candidate windows are ranked within their own parent Earth region. The output reports the percentage of draws in which a window remains in that region's top decile.

This is a sensitivity diagnostic for feature-weight choice. It is not a confidence interval, a probability that a site is a planetary analog, or an independent-sample statistic. Adjacent 6 × 6 windows overlap heavily and are spatially dependent.

## Coordinates and shortlist

WGS84 candidate centres are estimated by offsetting the stored parent reference centre using nominal raster spacing. They are approximate map locators only. They are not surveyed GPS points, an authoritative raster geotransform, a field station or site/parcel boundaries.

The user-facing shortlist contains up to 30 windows per planetary target, at most four per parent Earth region, with a nominal minimum 6 km separation between displayed centres. The full top-30 network ordering is also stored in the JSON output; network rank refers only to the 7,290 sampled Earth windows.

## Interpretation and limitations

- **Not a global search:** the scan evaluates only ten curated 30 km parent study/reference areas. It does not search all Earth land or discover new geologic provinces.
- **Terrain only:** no lithology, mineralogy, spectral mineral classification, geochemistry, regolith grain size/strength, dust flux, thermal inertia, illumination, radiation, water, ice, resources, atmosphere or gravity dimensions enter the score.
- **Scale:** ~925 m source support is too coarse for rover-scale roughness, obstacles, slopes, trafficability, bearing strength or landing safety.
- **Surface model:** Copernicus GLO-30 is a DSM, not a bare-earth model.
- **Moon:** LOLA elevation is interpolated in the stored surface grid. LDEC return support is reported separately; it is not a mask that proves every elevation cell was measured.
- **Mars:** parent MOLA observations are sparse in the selected area. The valid local-window rule is disclosed and output is still provisional.
- **Field validation:** coordinate estimates, geological context and transferability need independent field mapping, laboratory analysis and planetary-science review.

A promising numerical match can help prioritize a closer look. It cannot establish that a location is a scientifically validated Moon/Mars analog or safe place to conduct a mission rehearsal.

## Rebuild

Install only Python 3.11+ (the builder uses the standard library) and run from the repository root:

```bash
python science/build_regional_window_scan.py
```

The script reads `data/terrain/terrain_comparison.json`, `data/moon/shackleton_lola_80m.json` and `data/agents/candidate_catalog.json`, then writes `data/analog_benchmark/regional_window_scan.json`. It fails rather than silently substituting missing grids or changing the ten-region scope.

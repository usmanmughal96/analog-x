# ANALOG-X — Mission-to-Field Planner

NASA Space Apps Challenge 2026 · Team **X Æ A-Xii** · Participant: **Muhammad Usman Mughal**

## What it does

ANALOG-X turns a Moon/Mars exploration objective into an actionable Earth field-campaign plan.

1. Select a planetary reference: Mars Syrtis Major, Mars Jezero or the lunar south-polar/Shackleton context.
2. Choose a field task: volcanic geology/sample-context work, rover-traverse workflow, wind/dust experiments, thermal-stress trials or solar-powered operations.
3. Select candidate Earth environments or add custom coordinates.
4. Fetch live NASA POWER climatology for the selected coordinates.
5. Compare measured Earth meteorology, calculate a transparent relative Field-Campaign Index, and identify candidate field months.
6. Generate and download a field-test plan containing protocol, equipment, evidence and non-transferable planetary conditions.

**Important:** the index ranks Earth field-campaign conditions among the selected candidates. It is not a Moon/Mars similarity score, geological equivalence, safety rating or landing-site recommendation.

## Live links
- Application: https://usmanmughal96.github.io/analog-x/
- Seven-slide demo: https://usmanmughal96.github.io/analog-x/demo.html
- Repository: https://github.com/usmanmughal96/analog-x

## Live data
NASA POWER Climatology API:
- T2M, T2M_MAX, T2M_MIN
- RH2M
- WS10M
- PRECTOTCORR
- ALLSKY_SFC_SW_DWN for solar tasks

The app requests data in the user's browser, caches responses locally for up to 12 hours and reports failed sites rather than fabricating values.

## Planetary and geology references
NASA MOLA, NASA LRO Diviner/LOLA, USGS Syrtis Major MC-13, Smithsonian Global Volcanism Program Sultan record, USGS Chagai geology and SUPARCO Space4Climate. The live climate index does not process raw planetary rasters. SUPARCO data are not claimed as ingested.

## Scientific limits
NASA POWER climatology is gridded Earth meteorology, not a field weather station or surface-temperature record. Wind at 10 m is not dust flux. The app does not infer geology, mineralogy, water/ice, rover traction or planetary environmental equivalence. See `docs/ALGORITHM.md`, `docs/METHODOLOGY.md` and `docs/LIMITATIONS.md`.

## Repository structure
- `index.html` — interactive mission-to-field planner.
- `demo.html` — seven-slide browser demo.
- `docs/` — method, algorithm, sources, limitations, AI disclosure and NASA submission copy.
- `science/` — separate MOLA/DEM processing scripts for future raster analysis.

## License
Original project code and text: MIT. Third-party datasets and imagery retain provider terms.

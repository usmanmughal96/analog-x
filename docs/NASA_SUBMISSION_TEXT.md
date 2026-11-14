# NASA Project Page — ANALOG-X

## Project Name
ANALOG-X — Mission-to-Field Planetary Analog Planner

## High-Level Project Summary
ANALOG-X turns a Moon or Mars exploration objective into an actionable Earth field-campaign plan. Users select a planetary reference and field task, screen candidate Earth environments with live NASA POWER climatology, compare temperature, humidity, precipitation, wind and (for solar tasks) solar resource, identify promising field months, and generate a downloadable field-test plan with protocols, equipment, data provenance and non-transferable planetary conditions.

The relative Field-Campaign Index ranks only the Earth candidates selected by the user for the chosen field task. It is not a Moon/Mars similarity score, geological equivalence, landing-safety rating or mission-site recommendation. Geological evidence is maintained separately from the climate calculations.

Flagship Pakistan candidate: Koh-i-Sultan, Chagai, with established and alternative environments included for comparison. NASA MOLA and LRO Diviner/LOLA, USGS Syrtis Major MC-13 and SUPARCO Space4Climate are identified as planetary/local data pathways; raw planetary rasters and SUPARCO products are not claimed as processed or integrated in this build.

## Link to Project Demo
https://usmanmughal96.github.io/analog-x/demo.html

## Link to Final Project
https://usmanmughal96.github.io/analog-x/

## Detailed Description
The challenge asks teams to discover and characterize terrestrial analogs, explain which characteristics are useful, identify where analogies break down and show how the location or process can prepare exploration. ANALOG-X operationalizes that requirement as a mission-to-field workflow.

Users select Mars Syrtis Major, Mars Jezero or lunar south-polar/Shackleton context; select volcanic geology/sample-context work, rover-traverse workflow, wind/dust experiments, thermal equipment trials or solar-powered field operations; and choose candidate Earth sites or enter custom coordinates. The browser fetches NASA POWER point climatology at each selected coordinate. It summarizes 2-m air temperature, monthly maximum/minimum air temperature, relative humidity, corrected precipitation and 10-m wind. Solar tasks also request all-sky surface shortwave radiation. The app calculates a transparent, task-specific relative Field-Campaign Index across successful candidates, suggests months from monthly climatology and generates a field-test card with protocol, equipment, source observations and non-transferable planetary conditions.

The tool explicitly separates measured Earth meteorology from curated geological evidence and planetary reference products. It does not infer geology from weather or claim Earth reproduces lunar vacuum, reduced gravity, radiation, polar shadow cycles or Martian pressure. Raw MOLA/Diviner/LOLA raster analysis is not claimed in this version. SUPARCO data are not claimed as ingested.

## Use of Super Intelligence
See `docs/AI_DISCLOSURE.md`. Disclose the actual use of AI-assisted early brainstorming, concept refinement, code assistance, drafting and documentation. Do not state that the initial idea was wholly unaided. The Local Lead was informed and reportedly approved proceeding; this does not replace any organizer interpretation of SI requirements.

## NASA Data and Resources
NASA POWER Climatology API is used live to retrieve Earth meteorology/solar climatology. NASA PDS MOLA, LRO Diviner/LOLA and NASA GIBS/Worldview are linked as planetary/Earth reference resources; raw planetary rasters are not processed by this build.

## Other References
Smithsonian Global Volcanism Program Sultan catalogue (232801); USGS Syrtis Major MC-13; USGS OFR 75-550; NASA Planetary Analog Explorer; NASA Iceland fieldwork; SUPARCO Space4Climate as a potential local data source, not yet integrated.

## Before Submission
Run at least one live scan from the public app, capture a screenshot of actual API results, generate a field-test plan and verify the app/demo URLs in a private browser. Do not claim raster-derived planetary comparisons or SUPARCO integration unless completed and documented.

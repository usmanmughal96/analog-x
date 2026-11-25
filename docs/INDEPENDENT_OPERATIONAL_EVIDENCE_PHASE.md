# Independent Operational Evidence Phase

**Status:** research protocol and release plan. This document does not claim external review, field deployment, rover trials, or mission validation.

## 1. The question we must answer

ANALOG-X has already built a large candidate-discovery funnel. The next scientific question is narrower and more demanding:

> Does selecting an Earth environment through ANALOG-X help a team rehearse a named lunar or Martian operation more effectively than a reasonable baseline—and can that usefulness be demonstrated with evidence independent of the ranking itself?

The unit of proof is not “this place looks like Mars.” It is a named task, its measurable outcome, the instrument and method used, and the planetary constraints that do not transfer.

Three claims must be evaluated separately:

1. **Discovery validity:** does the candidate-screening process retrieve environments that independent experts consider relevant to a predeclared process or field task?
2. **Operational utility:** does the chosen site support a repeatable rehearsal that improves or tests a measurable procedure, such as mapping accuracy, sampling yield, route prediction, task time, or instrument reliability?
3. **Transfer boundary:** which parts of the method transfer to a named lunar or Martian operation, and which fail because of gravity, pressure, radiation, regolith, thermal regime, hydrology, or scale?

No single score should combine these claims. A site can be useful for one procedure and unsuitable for another.

## 2. What exists now

The current repository provides the starting evidence, not the final validation:

- Four Pakistan study windows have processed Sentinel-2 L2A spectral-context profiles and true-colour/index-screen assets: Chagai small playas, Hamun-i-Mashkel, Koh-i-Sultan, and Hispar Glacier.
- Four Pakistan Copernicus GLO-30 digital-surface-model windows have terrain descriptors on an approximately 925 m analysis grid. These are regional descriptors, not rover-scale terrain.
- NASA POWER provides gridded climatology at curated Earth-site coordinates. These are not local weather-station observations.
- ATFA defines experiment tracks for evaporite processes, spectral ground truth, volcanic morphology, cryosphere remote sensing, terrain/mobility and human/robotic operations. Its qualitative transferability classes are research rules, not calibrated probabilities.
- The blind independent-review packet contains 96 cases: 48 Moon and 48 Mars, with six rank strata per target and eight cases per stratum. Candidate IDs, ranks, scores and terrain metrics are withheld from reviewers.
- Global GLO-90 discovery has processed 26,475/26,475 enumerated land tiles and evaluated 5,852,396 terrain windows. The retained target-specific ranking is a screening shortlist, not a global accuracy result.

**What does not exist yet:** the independent-review packet has no returned labels; the physical field-observation ledger is empty; no field spectroscopy, laboratory mineralogy, rover/UGV trial, mission-date lunar illumination simulation, or vehicle-specific mobility validation is claimed.

Primary records: [quantitative validation](../data/validation/quantitative_validation.json), [blind review packet](../data/validation/independent_analog_review_packet.json), [Pakistan image profiles](../data/pakistan/imagery/), [terrain comparison](../data/terrain/terrain_comparison.json), [ATFA transferability data](../data/transferability/transferability.json), and [field observation ledger](../data/field_validation/observations.json).

## 3. Work package A — independent, blinded candidate review

### Design

Use the existing 96-case packet as the first independent review exercise. Recruit reviewers with relevant planetary geology, geomorphology, remote sensing, field geology, or planetary surface operations experience. A reviewer must disclose relevant affiliations and any involvement in ANALOG-X.

Reviewers must not see the candidate ID, score, rank, or ANALOG-X interpretation before submitting a label. They should cite independent literature, map sheets, mission data, or other evidence that existed independently of the ranking.

For each case, record:

- positive, negative, inconclusive, or insufficient evidence;
- the specific process or task for which it is relevant;
- evidence references and what each source actually establishes;
- confidence, reviewer qualification, affiliation, review date, and rationale;
- whether the reviewer is independent of the ANALOG-X score and site selection.

The controlled importer must restore candidate identities only after review fields are complete. Keep the private case key separate from the public repository and never send it to reviewers.

### Analysis

Keep neighbouring or geologically related candidates in the same spatial group. The existing deterministic 20% spatial-group holdout is a starting rule, not a substitute for reviewing whether the 10-degree grouping separates real geological provinces. Merge related cells into larger predeclared spatial groups before examining the candidate scores where necessary.

Report label counts, missingness, reviewer agreement, spatial-group counts, class balance, held-out results, and uncertainty. Only calculate ROC-AUC when the held-out split contains both positive and negative cases and the predeclared minimum group requirements are met. Do not tune the ranking to the blind packet and then reuse the same labels as independent test data.

**Release gate A:** independent labels are provenance-complete, spatially blocked, reviewed for group leakage, and sufficient for a held-out test. Otherwise publish the sample and disagreement/missingness report only—no accuracy claim.

## 4. Work package B — Pakistan field-to-orbit experiments

The four Pakistan windows should be treated as complementary task environments, not as four interchangeable analogs.

| Study window | First experiment | Required independent evidence | Main failure boundary |
|---|---|---|---|
| Chagai small playas near Nok Kundi | Salt-crust/facies mapping and orbital-to-ground spectral validation | Repeat-season Sentinel-2/Landsat scenes; georeferenced facies transects; calibrated field spectra; permitted samples with XRD/XRF/FTIR and chain of custody | Reflectance does not identify evaporite minerals or subsurface brine; Earth hydrology differs from Mars |
| Hamun-i-Mashkel / Kharan Basin | Wetting-drying and intermittent-playa observation protocol | Multi-season imagery; mapped basin/facies boundaries; repeat observations; sediment profiles and conductivity where permitted | One scene cannot establish seasonality, basin-wide water history, brine, or mineralogy |
| Koh-i-Sultan | Volcanic outcrop mapping and orbital-to-ground geology workflow | Qualified geological mapping; exposure photographs; calibrated spectra; permitted petrography/XRF/XRD | Published context includes andesite, tuff and agglomerate; do not relabel it as a basaltic Mars match |
| Hispar Glacier | Debris/ice boundary interpretation and cold-region sensor protocol | Specialist-led safe proximal transects; field-verified ice/debris boundary; thermal observations and instrument calibration | Terrestrial glacier ice is not lunar PSR ice; glacier access is a specialist high-hazard activity |

### Minimum field record

Every real observation must include station ID, UTC time, WGS84 coordinates and reported accuracy, observer, method, instrument make/model/serial, calibration or field-check evidence, units, repeats, uncertainty, photo IDs, permissions, safety observations, and any non-observation or instrument failure.

Keep original files immutable. Maintain checksums and sample chain-of-custody. A second team member checks transcription and spatial/photo linkage. An independent reviewer may validate only the station, observation and property actually inspected.

### Comparison protocol

For each task, pre-register a baseline before fieldwork: (a) a conventional expert-selected site or reference, (b) a simple terrain/imagery shortlist, and (c) the ANALOG-X-selected candidate. Use the same task definition, instruments, operator training, time budget and acceptance criteria. Randomize task order where feasible and blind the outcome assessor to the site-selection method.

Possible task outcomes include mapping confusion matrices, boundary-position error, georeferencing RMSE, usable sample yield, repeatability, task completion time, route-prediction error, and instrument uptime. Choose only outcomes that can be measured with the available instruments and a declared reference standard. Do not invent a pass threshold after seeing the results.

## 5. Work package C — mission-relevant terrain and mobility

The current approximately 925 m terrain profiles are useful for regional screening only. They cannot resolve boulders, craters, scarps, wheel-scale roughness, bearing strength, sinkage, or safe traverses.

A mobility experiment requires:

1. a named terrestrial test corridor and a high-resolution DEM/LiDAR survey, ideally metre-to-centimetre scale where the experiment requires it;
2. RTK-GNSS or another traceable position reference, obstacle inventory, surface-material description, grain-size and bearing-strength measurements;
3. a named rover/UGV with documented wheel geometry, clearance, mass, traction and slope/step limits;
4. instrumented traverses with route, wheel-slip, sinkage, tilt, energy, operator intervention and failure logs;
5. a blind comparison between predicted traversability and observed traverse outcome.

Use measured route outcomes to test the planning workflow, not to imply that terrestrial vehicle dynamics reproduce lunar or Martian dynamics. A generic slope cutoff must never be converted into a “rover safe” label.

## 6. Work package D — lunar south-pole operational evidence

The Shackleton Rim evidence base now includes 5 m LOLA elevation, return-count, slope, elevation-RMS-error and slope-RMS-error products, plus 80 m regional context and historical WAC/Diviner products. These layers are not yet a mission-date operations model.

The next lunar sequence is:

1. ingest and spatially verify the official LROC Permanently Shadowed Regions Atlas records intersecting the AOI, retaining atlas ID, map metadata, pixel-scale range and quality/coverage;
2. pin NASA/JPL NAIF SPICE kernels, leap-second data, lunar frames and time system;
3. simulate the Sun vector and terrain illumination over a declared mission date range, terrain resolution, observer height and time step;
4. propagate DEM uncertainty or use the published elevation-clone ensemble through illumination and route statistics;
5. compare results against the historical WAC layer as a consistency check, not an interchangeable forecast;
6. test candidate routes against a specified rover's mobility, thermal, communication and contingency constraints.

**Release gate D:** PSR evidence is sourced from the official atlas; the ephemeris/kernel configuration is pinned; uncertainty is propagated; and a named vehicle's engineering limits are documented. Until then, do not publish mission-date illumination forecasts, accessible-ice claims, rover-safe labels, or landing recommendations.

## 7. What would count as a breakthrough

A defensible result would look like this:

- Independent reviewers, blinded to ANALOG-X scores, identify a set of candidates as useful for a predeclared process or task.
- A field campaign measures the relevant property using traceable instruments and a documented sampling design.
- The orbit-to-ground method is tested against those observations, with uncertainty and false positives shown.
- A controlled operational rehearsal measures task outcomes against a conventional baseline.
- The report states which procedure transfers, which does not, and why.
- Another researcher can rerun the analysis from source products, parameters, station records and code.

A higher index, a prettier map, a new data layer, or a positive anecdote is not sufficient on its own.

## 8. Execution order and stop rules

1. **External review first:** invite qualified independent reviewers; complete the 96-case blinded packet and report agreement, evidence references and spatial grouping.
2. **Remote time-series preparation:** add multi-season scenes for Chagai and Hamun-i-Mashkel; record acquisitions, masks, processing parameters and missing seasons. Do not substitute catalogue discovery for processed science arrays.
3. **Field readiness:** obtain written permissions, local access and safety clearance; pre-register stations, measurements, instruments, calibration and comparison baselines. No travel is authorized by this document.
4. **First permitted field experiment:** prioritize the playa/spectral workflow only after local authorities, experienced local partners and the field lead approve a site-specific risk assessment.
5. **Volcanic and cryosphere tasks:** require qualified geologists for Koh-i-Sultan and specialist glacier professionals for any Hispar activity. Hispar remains deferred until a dedicated glacier hazard plan is approved.
6. **Lunar operations track:** ingest PSR Atlas and SPICE evidence, propagate uncertainty, and apply vehicle-specific engineering constraints before releasing any operational claim.

Stop or defer a task when permissions, safety, calibration, sample custody, independent references, or measurement quality are missing. Record the failed or inaccessible attempt; do not silently remove it.

## 9. Current evidence status

| Evidence item | Current state |
|---|---|
| Global terrain discovery | Complete inventory screen; target-specific ranking shortlist available |
| Pakistan Sentinel-2 spectral screens | Four processed windows; 20 m analysis grids |
| Pakistan Copernicus terrain | Four regional DSM profiles; approximately 925 m support |
| Independent blind review | 96-case packet prepared; no returned labels |
| Physical Pakistan field observations | 0 in repository |
| Field spectroscopy / mineralogy | Not available |
| Instrumented rover/UGV validation | Not available |
| Lunar 5 m LOLA terrain and uncertainty | Integrated; uncertainty layers are not safety probabilities |
| Official PSR Atlas geometry | Not yet ingested as a verified AOI layer |
| Mission-date SPICE illumination | Planned; not generated |
| Vehicle-specific lunar traverse validation | Not available |

The next defensible milestone is a completed independent-review cycle plus one permitted, instrumented Pakistan field experiment linked to repeat satellite observations. Until those exist, ANALOG-X remains a candidate-discovery and experiment-planning research platform—not a validated operational analog selector.

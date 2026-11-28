# ANALOG-X — Operational Readiness and Validation Gates

**Status:** evidence-gate specification and research workflow. This document does not claim field deployment, independent expert approval, rover testing, landing clearance, or mission certification.

## Purpose

ANALOG-X now separates four questions that should never be compressed into one score:

1. **Discovery completeness:** did the pipeline process the declared source inventory and produce reproducible candidate records?
2. **Scientific validity:** do independent experts and independent evidence support the stated terrain/process criterion?
3. **Field utility:** can a team collect repeatable measurements at a permitted Earth site and compare them with a pre-registered protocol?
4. **Operational suitability:** does a specified vehicle or mission system meet its engineering and environmental constraints at a defined location and time?

Passing one gate does not imply passing another.

## Current evidence state

The workbench at [mission-readiness.html](../mission-readiness.html) reads committed project records and presents their scope and limitations.

| Workstream | Evidence currently committed | What remains open |
|---|---|---|
| Global terrain discovery | 26,475 / 26,475 enumerated Copernicus GLO-90 land tiles processed; 5,852,396 terrain windows evaluated; 1,200 Moon and 1,200 Mars shortlist candidates | Independent confirmation of what the ranking retrieves; source/data/feature sensitivity beyond the current diagnostics |
| ATFA | Ten curated Earth environments; nine experiment tracks; site-specific pathways and analogy breaks | External domain review of qualitative rules and site dossiers; physical measurements for individual hypotheses |
| Pakistan Earth observation | Four Sentinel-2 spectral-context profiles, browse-only RGB previews, four processed GLO-30 DSM regional profiles and NASA POWER context | Field spectra, sample mineralogy, local instrument measurements, repeat-season ground observations |
| Independent analog review | A 96-case blinded packet (48 Moon, 48 Mars) with score/rank withheld | Qualified reviewers, evidence-backed labels, reviewer agreement and sufficient spatially blocked labels |
| Pakistan field validation | Campaign plan, station designs, offline capture kit and empty observation ledger | Permissions, local security and weather review, field team, calibrated instruments, actual observations and independent checking |
| Lunar terrain and environment | Shackleton Site04 5 m LOLA terrain summary (100% interpolated coverage; 9.154% positive-return support), 100 m LROC WAC historical illumination-frequency products, and Diviner PRP V2.0 thermal / modelled ice-stability summaries over 6,823 AOI triangles | Formal PSR atlas polygons for this AOI, mission-date NAIF SPICE illumination, local-horizon forecasts, thermal/resource uncertainty analysis, communications/power/radiation constraints, and vehicle-specific route hazards |
| Mars terrain and high-resolution reference | Nili Patera MOLA regional profile at about 925 m support; 567/1,122 observed cells (50.53%) and 87 complete 3×3 neighborhoods; catalogued University of Arizona HiRISE dune-field DTM at 1.01 m/pixel (metadata-only, approx. 430 MB); a capped PDS-label read confirms its bounding box does **not** intersect the core MOLA AOI | Download and validate the adjacent DTM for a separately defined dune-field study; inspect its projection, vertical reference, data quality and artifacts; find finer-scale terrain covering the actual MOLA comparison window; independent validation |
| Rover / mission suitability | Regional terrain descriptors and a documented list of missing engineering evidence | High-resolution co-registered hazard maps, vehicle specifications, surface mechanics, instrumented trials and qualified engineering sign-off |

The quantitative report status **diagnostic_only** is intentional. The ranking-release status **ready** refers to schema, ordering and rank-integrity checks only. It is not accuracy, field validation, analog validity or mission suitability.

## Gate A — independent scientific review

### Review scope

The first review release evaluates **terrain morphology only** for the predeclared terrain_morphology_transfer_v1 criterion. It does not validate mineralogy, chemistry, water or ice accessibility, biological potential, landing safety, rover mobility, or whole-environment equivalence.

The [independent-review.html](../independent-review.html) reviewer desk is local-first. It loads the public anonymized packet, hides shortlist IDs/ranks/scores from the reviewer interface, records a rationale and evidence references, and exports a response JSON. No response is uploaded automatically.

### Required review procedure

1. Recruit reviewers with relevant planetary geology, geomorphology, remote-sensing, field-geology or planetary-surface expertise.
2. Disclose qualifications, affiliation, conflicts and any involvement in ANALOG-X.
3. Have reviewers agree to the criterion before looking at cases.
4. Assess cases independently of ANALOG-X ranks and scores. Cite independent source records for positive or negative judgments.
5. Permit inconclusive and insufficient_evidence; do not force a binary label.
6. Keep the private case key separate from reviewers and the public repository.
7. Import only returned packets using the repository's controlled importer and local private key.
8. Review spatial-group independence and class balance before interpreting a holdout metric.

### Import and evaluation

The project owner should follow [INDEPENDENT_LABEL_VALIDATION_PROTOCOL.md](INDEPENDENT_LABEL_VALIDATION_PROTOCOL.md). In summary, from the repository root:

    python scripts/build_independent_review_pack.py --key-output "$HOME/analogx-private/independent-review-case-key.json"
    # Keep the private case key outside the repository. Send only the public packet.
    python scripts/import_independent_review_labels.py --key "$HOME/analogx-private/independent-review-case-key.json" --dry-run
    python scripts/import_independent_review_labels.py --key "$HOME/analogx-private/independent-review-case-key.json"
    python scripts/validate_analog_labels.py
    python scripts/build_quantitative_validation.py

Never commit, email to reviewers or publish the private case key. The evaluator must withhold AUC when the held-out spatial groups do not contain both labels or do not meet the configured group requirements. One review validates only the stated criterion and evidence scope.

## Gate B — Pakistan field experiments

The [field-validation.html](../field-validation.html) kit captures observations locally in the browser. The repository ledger remains empty until real, documented observations are deliberately exported, checked and incorporated.

### Site-specific sequence

| Priority | Candidate | First bounded experiment | Minimum independent evidence | Caution |
|---|---|---|---|---|
| 1 | Chagai small playas / Nok Kundi | Playa-margin to interior facies and crust documentation | Georeferenced transect, repeatable photo geometry, calibrated field spectra; permitted samples with laboratory mineralogy if a mineral claim is made | A remote-sensing ratio is not a salt or brine identification |
| 2 | Hamun-i-Mashkel / Kharan Basin | Basin-margin, playa and ephemeral-channel observations | Repeat-season records, station-scale sediment/facies descriptions, calibrated conductivity only if appropriately sampled | One visit cannot establish seasonal hydrology or groundwater |
| 3 | Koh-i-Sultan | Expert-led volcanic outcrop and mapped-unit checks | Qualified geological descriptions; permitted samples and petrography/XRF/XRD for material claims | Published regional context includes andesite, tuff and agglomerate; do not call it a basaltic Mars match by assumption |
| Specialist only | Hispar Glacier | Safe proximal ice/debris observation, potentially by a professional glacier team | Specialist hazard review, trained guides, rescue capability and calibrated observations | No glacier-surface access is implied; do not enter crevasse, avalanche or unstable ice terrain |

### No-fieldwork-without gate

Before any visit, obtain and document all applicable items:

- landowner or competent-authority access permission;
- protected-area, environmental and sampling clearances where applicable;
- current local security, travel and route review;
- a site-specific hazard assessment and weather check;
- named field lead, trained roles, check-in schedule, emergency contacts, communications and evacuation plan;
- instrument IDs, calibration certificates or field checks, units and uncertainty;
- station plan, consent/permission restrictions, photography and data custody procedures.

The plan is not a travel authorization. Access, security, weather and site safety must be checked with competent local authorities and qualified local partners immediately before any field activity. Any team member can stop work.

### Minimum observation record

Record immutable station and observer identifiers; `date_utc` and `measurement_time_utc` as ISO 8601 UTC timestamps ending in `Z` (`YYYY-MM-DDTHH:MM:SS.sssZ`); WGS84 coordinate and accuracy; coordinate method; original photo IDs and bearings; observed properties; instrument make/model/serial; calibration or field-check record; measurement method, units, repeats and uncertainty; sample ID and custody where authorized; permissions; access constraints; safety observations; and non-observations. The form uses the station capture time as the initial instrument-reading batch time; record separate timestamps for later repeats in their method records. Date-only values are insufficient. Never infer a missing measurement time from the device clock or export time. Separate direct observation from interpretation. Preserve original instrument exports and photos.

A field observation validates only the property and station actually observed. It does not establish planetary equivalence or rover safety.

## Gate C — terrain hazard screening and rover suitability

### What current terrain data supports

- Earth: Copernicus GLO-30 **DSM** source data are aggregated to approximately 925 m cells for regional comparison over approximately 29.6 km windows.
- Mars: the selected Nili Patera MOLA window has approximately 925 m cells, but only 50.53% observed-cell coverage and 87 complete 3×3 neighborhoods. A separate University of Arizona HiRISE stereo DTM titled “Topography of Moving Dunes in Nili Patera” is catalogued at a published map scale of 1.01 m/pixel. A capped read of the embedded PDS label (256 KiB of the approximately 430 MB file) returned complete latitude/longitude bounds and confirms **no bounding-box intersection** with the original MOLA AOI: the DTM's westernmost longitude is 67.26487883°E, east of the MOLA AOI's 67.25614307°E eastern edge. The DTM is an adjacent dune-field reference and must not be treated as co-located MOLA support. Its raster has not been downloaded or processed.
- Moon: Shackleton Site04 has a separate 5 m LOLA product summary. Its slope P90 is approximately 33.16 degrees; 51.02% of reported pixels exceed 20 degrees; P90 3×3 local relief over a 15 m footprint is approximately 8.61 m. Interpolated coverage and positive direct-return support are different measures (100% versus 9.154%).

These metrics show why spatial support and source-quality indicators must be visible. They are not a universal hazard scale, a pass/fail slope threshold, or a certification.

### Minimum additional evidence for a rover traverse claim

1. A precisely bounded route and high-resolution, co-registered terrain surface at a scale appropriate to the vehicle and obstacles.
2. Explicit no-data, uncertainty, illumination and image-registration layers.
3. Boulder, crater, scarp, slope, roughness and obstacle mapping with stated detection limits.
4. Surface material and geotechnical properties: grain-size distribution, cohesion, bearing strength, sinkage and traction, with method and uncertainty.
5. The actual rover/UGV model and engineering envelope: mass, wheel geometry, clearance, suspension, power, thermal limits, steering and permitted attitude/slope/step limits.
6. Instrumented trials recording route, position, wheel slip, sinkage, tilt, energy, communication, operator interventions and failures.
7. A blind comparison of predicted versus observed route outcomes and an independent engineering review.

Do not convert generic slope thresholds, Earth UGV performance or visual similarity into lunar/Martian safety claims. A terrestrial trial tests a procedure under terrestrial gravity, atmosphere, soil and vehicle dynamics; the transfer boundary must remain explicit.

### Lunar south-pole evidence available and still needed

ANALOG-X now includes more than terrain context for the Shackleton study window:

- **LOLA Site04, 5 m:** 3,200 × 3,200 terrain pixels. Interpolated elevation coverage is 100%, while positive direct-return support is 9.154%; these are distinct quality measures.
- **LROC WAC, 100 m:** historical time-weighted and percentage-based illumination-frequency products. In the time-weighted layer, mean illumination frequency is 24.86% and 60.62% of valid pixels are at or below 5%; the percentage-based sensitivity layer reports a 25.97% mean and 58.65% at or below 5%.
- **Diviner PRP V2.0:** model-derived annual average temperature at 2 cm (median 103.786 K) and annual maximum surface temperature (median 238.568 K), summarised over 6,823 Shackleton-window triangles. Ice-stability-depth values are QA-limited: 2,812 valid depth values, 2,514 values censored beyond 2.8738 m, and 1,497 invalid or unreadable records.

The WAC layers describe historical observations from 15 February 2010 to 5 February 2011; they are not a mission-date illumination forecast. The ≤5% WAC threshold is a low-illumination screening proxy, not a formal permanently shadowed region (PSR) boundary. Diviner PRP is a historical model-derived product based on the first year of LRO mapping observations (2010–2011), not an in-situ ice measurement. A modelled stability depth does not establish ice concentration, thickness, purity, accessibility or reserves.

Still required are verified PSR Atlas polygons intersecting the AOI, pinned mission-date NAIF SPICE kernels and illumination simulation, local-horizon modelling with terrain uncertainty, QA of thermal/volatile interpretation, communications and power visibility, radiation exposure, vehicle/lander constraints and route-specific hazard mapping. No accessible-ice, safe-landing, rover-safety or permanent-base claim is made by ANALOG-X.

## Gate D — operational rehearsal utility

A future controlled test should compare three selection methods under the same task definition:

- a conventional expert-selected site;
- a baseline imagery / terrain shortlist;
- an ANALOG-X-selected candidate.

Pre-register the task, instrument, operators, repeat count, reference standard, outcome measure and acceptance criterion before the experiment. Blind the outcome assessor to the selection method where feasible. Suitable outcomes include boundary mapping error, classification confusion matrix, GNSS / mapping RMSE, usable sample yield, repeatability, elapsed task time, instrument uptime, route-prediction error, wheel slip, sinkage and energy. Do not choose thresholds after seeing the results.

## Release language

Use these precise states:

- **Processed:** source payload received and transformed with a traceable method.
- **Screened:** a candidate or region has passed stated data-quality and feature filters.
- **Prepared for external review:** a blinded packet and protocol exist, but no reviewer decision is implied.
- **Field planned:** station design and prerequisites exist; no observation is implied.
- **Field observed, unreviewed:** a real observation has been supplied, but independent review is incomplete.
- **Independently reviewed:** a named reviewer has checked the stated observation or criterion and scope.
- **Operationally tested:** a specified instrument/vehicle completed a documented test; this still does not confer lunar/Martian safety certification.

The public workbench is an evidence ledger, not a self-certification interface.

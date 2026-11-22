# Pakistan Field Campaign Execution Plan

**Status:** executable preparation plan; no field visit or measurement is claimed.  
**Protocol:** `science/field_validation_protocol.json`  
**Ledger:** `data/field_validation/observations.json`

## 1. Campaign objective

Collect a small, high-quality, georeferenced dataset that tests named properties at named stations. This is not a broad exploration trip and it does not validate planetary equivalence. Every field result must be traceable to the sampled location, method, instrument, calibration, operator, time and uncertainty.

## 2. Deployment sequence

### Phase A — remote preparation (before any travel)

1. Assign a field lead, geologist, instrument operator, data manager and safety contact; one person may hold multiple roles only where competence is documented.
2. Obtain written land access and competent-authority permission; check protected-area and environmental requirements.
3. Complete current security, travel, weather, heat/flood/flash-flood, road-access and communications reviews with local authorities and experienced local partners.
4. Confirm emergency contacts, check-in schedule, evacuation route, medical support, vehicle suitability and stop-work authority.
5. Inventory equipment, serial numbers, calibration certificates/field checks, spare power, GNSS datum, camera time sync and storage.
6. Pre-register station IDs, sampling methods, measurement units, repeat counts and the exact research question before visiting.

**Go/no-go:** no visit proceeds until all five governance items in the campaign_plan.json are documented and the field lead signs the site-specific risk assessment. This plan itself grants no access or travel clearance.

### Phase B — first campaign priority: Chagai small playas near Nok Kundi

**Why first:** the current plan supports a bounded, property-specific surface campaign and does not require subsurface/resource claims. This is a planning priority, not a statement that the site is safe or accessible.

Use the existing station sequence:
- CHG-M01 — playa-margin / fan transition
- CHG-T01 — permitted intermediate transect point
- CHG-I01 — playa interior only if separately permitted and judged safe; otherwise record the non-observation.

At each accessible station, capture geomorphic setting, visible surface crust and continuity, sediment texture/grain-size method, clast description, photos with scale and bearings, GNSS accuracy, and environmental measurements only when the corresponding calibrated instrument is used. Do not dig, sample or cross a playa without express permission and a task-specific safety plan.

### Phase C — second campaign: Hamun-i-Mashkel / Kharan Basin

Use HAM-B01 (basin margin), HAM-P01 (playa surface) and HAM-D01 (ephemeral channel/fan transition). Record what is directly visible on the visit date. A single visit cannot establish seasonal hydrology, groundwater, brine or basin-wide boundaries.

### Phase D — expert-only campaign: Koh-i-Sultan

Proceed only with a qualified field geologist and access clearance. Verify mapped units at safe, exposed contacts. Use cautious lithology descriptions; no basaltic, mineralogical or alteration classification without appropriate field/lab evidence.

### Phase E — deferred specialist campaign: Hispar Glacier

Do not treat this as a routine campaign. Any glacier work is deferred to a specialist glacier team with a specific hazard assessment, rescue plan, weather window and professional access controls. Safe proximal observations may be considered separately; no glacier-surface access is implied.

## 3. Minimum station protocol

- GNSS: record WGS84 latitude/longitude, device/model, coordinate method, fix duration or averaging method, reported horizontal accuracy and UTC timestamp.
- Photographs: preserve originals, sync camera time, assign immutable IDs, record bearing and scale reference; include overview, context and close-up images.
- Surface description: use a predeclared vocabulary for crust continuity, visible clasts, grain size/sorting, moisture appearance and geomorphic setting. Separate observation from interpretation.
- Instruments: record make/model/serial, calibration date or field-check, operator, units, measurement height/depth, stabilization time, repeat values and uncertainty/detection limit.
- Replicates: where practical, collect at least three independent readings for continuous sensor measurements at the same station and report all readings, not only the mean. Do not invent a value if a sensor is unavailable.
- Samples: collect only with explicit permission; preserve a sample ID, mass/volume where appropriate, location, UTC collection time, collector, seal and chain-of-custody. Do not infer mineralogy from field appearance.
- Non-observations: record inaccessible stations, failed GNSS, instrument failure, weather changes and denied access rather than silently dropping them.

## 4. Quality control and independent review

1. Before deployment, run a calibration/field-check against the manufacturer's procedure and retain a photo or certificate.
2. At the end of each day, reconcile station, photo, sample and instrument IDs; verify UTC, units, coordinate bounds and file checksums.
3. Keep raw data read-only. Store cleaned/transformed values in a separate derivative file with processing notes.
4. Have a second team member independently check transcription and coordinate/photo linkage.
5. A qualified external reviewer must state which specific property and stations were reviewed, what evidence was inspected, what was not assessable and the review date.
6. Only then may a record move from field_observed_unreviewed to independently_reviewed. The reviewer must not promote desk imagery or a protocol to field evidence.

## 5. Required deliverables after a real campaign

- Completed station ledger (JSON) and a human-readable field report.
- Original photos and instrument exports with checksums.
- Calibration/field-check register and uncertainty notes.
- Permission/access and safety record (sensitive details redacted from public outputs where necessary).
- Sample custody register and any laboratory certificates.
- Independent review statement with explicit property-level scope.
- Updated source registry and quantitative-validation report. No result should be generalized beyond the sampled station/property.

## 6. Current boundary

The committed observation ledger is empty. Chagai, Hamun-i-Mashkel and Koh-i-Sultan remain proposed campaigns; Hispar remains a specialist-only option. This document prepares the work but does not claim a field observation, access permission, laboratory result or site validation.

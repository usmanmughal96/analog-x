# ANALOG-X Mission Decision Engine

## Purpose

The decision engine helps a planetary field team decide which Earth locations deserve the next round of field validation for a named experiment. It is a research-triage system, not an analog-certification system.

It is designed around the NASA Space Apps challenge requirement to look beyond visual similarity, combine Earth/Moon/Mars evidence, distinguish what is similar from what is different, and explain how an Earth campaign could help exploration.

## Candidate universe

The current catalogue contains ten curated Earth seeds/reference sites. The under-characterized leads are:

- **Chagai small salt playas near Nok Kundi, Pakistan** — a historical NASA-report-derived lead; its midpoint and search AOI are not a surveyed playa boundary.
- **Hamun-i-Mashkel / Kharan Basin, Pakistan** — a regional closed-basin/intermittent-playa lead; its point and search AOI are approximate.

The catalogue also includes Koh-i-Sultan and Hispar Glacier as Pakistan reference case studies and six global reference environments (Dallol, Atacama, McMurdo Dry Valleys, Haughton impact structure, Iceland and Death Valley). This is a curated seed set, not an exhaustive search of all Earth.

## Evidence dimensions

The engine exposes four separate site-level evidence layers:

1. **NASA POWER climatology** — long-term gridded climate context and monthly planning values. It is not a local weather station, field forecast, rock/surface temperature, dust flux or water-resource measurement.
2. **Sentinel-2 L2A spectral context** — scene provenance, image coverage and screening indices. RGB and indices do not identify minerals, prove brine, measure crust thickness or validate ice boundaries.
3. **Processed terrain** — Copernicus DEM GLO-30 DSM profiles at approximately 925 m support for four Pakistan windows. These are regional descriptors, not rover-scale roughness, surface strength or route safety.
4. **Traceable source references** — links that explain why a site is in the catalogue. A historical report is prior context, not a new discovery claim.

For every candidate, the dossier also shows its mission tags, documented rehearsal tasks, candidate class, evidence gaps, and three low-precipitation climatology months when POWER data are available.

## Task alignment

The objective selector maps to task-specific retrieval terms:

- **Playa / evaporite** — playa, salt-crust, paleolake, sediment, inundation, drying and related environment tags.
- **Volcanic mapping** — volcanic outcrop, alteration, lava, tuff, agglomerate and mapped volcanic processes.
- **Cryosphere** — snow/ice, debris mapping, glacier observation and cold-region sensor/field workflows.
- **Terrain / traverse** — slope, roughness, topography, impact geology and regional traverse documentation.

The system checks both the candidate's documented rehearsal tasks and its environment tags. A match is labelled as either **documented rehearsal-task overlap**, **environmental context overlap**, or **no direct task/environment overlap**. It does not treat a broad tag as proof of a complete planetary analogy.

## Strict evidence policy

A candidate appears as a strict evidence-qualified lead only when all of these are true:

- Its candidate record is eligible for the selected mission target (Moon, Mars or Both).
- At least one of its documented rehearsal tasks overlaps the selected experiment.
- It has a traceable source reference.
- It has a NASA POWER climate record.
- It has either a site-specific Sentinel-2 spectral-context profile or a processed terrain profile.

The exploratory policy may show environmental-context matches and established references even when this threshold is not met. They remain labelled as context or hypotheses and are not promoted to validated analogs.

## Transparent ordering rule

The shortlist is ordered lexicographically:

1. Documented rehearsal-task overlap before environment-only context.
2. Under-characterized research leads before established/reference sites when task alignment is equal.
3. More available evidence layers (out of the four listed above) before fewer layers.
4. Alphabetical site name as the final stable tie-breaker.

No weighted composite score is calculated. The ordering is a practical way to organize the evidence queue; it is not a probability, calibrated similarity metric, scientific confidence score, landing suitability, rover-safety rating or resource prospectivity assessment. Ties remain visible.

## Moon and Mars are separate

For a **Both** request, the terrain tool performs one comparison against Shackleton Rim and a separate comparison against Nili Patera. Their values are not merged. The current terrain descriptors are:

- Median slope.
- P90 slope.
- P90 3×3 local relief.

Earth DSM, Mars MOLA and lunar LOLA have different geology, gravity, surface processes, sensor histories and data-quality properties even when their nominal spatial support is similar. MOLA around Nili Patera has only 50.53% observed-cell coverage and 87 complete 3×3 neighborhoods. Shackleton's LOLA elevation surface is interpolated; its LDEC return counts are observation support, not an illumination or ice map.

## Decision output

The offline brief includes:

- Mission target and experiment.
- Strict or exploratory decision status.
- Leads to validate and the rule that surfaced them.
- Candidate matrix with task alignment, four evidence layers and campaign-climate context.
- Separate Moon/Mars terrain comparisons, when selected.
- Next proposed field measurements for the selected task.
- Data timestamps, provenance references and scientific stop conditions.

Proposed field measurements are recommendations for future validation; they are not measurements already taken.

## Agentic layer

Four deterministic specialists are run before the optional Mission Director:

- Terrain Morphology Analyst.
- Climate & Campaign Planner.
- Surface / Process Analyst.
- Evidence Integrity Officer.

The optional Cloudflare Worker uses an open-weight gpt-oss-20b model with an allow-listed tool set. The model may inspect the candidate inventory, compare terrain, derive campaign windows, read surface context or run a coordinate scout. Tool results and specialist reports are passed to the model for synthesis. The model does not create measurements. Its tool trace and model-usage metadata are exported with the brief.

The offline review remains usable without a Worker or LLM. The coordinate scout and cloud Mission Director require the Worker endpoint; cloud inference additionally requires the Workers AI binding.

## Educational interaction

The Field School quiz awards browser-local XP for attempting and answering its three learning scenarios. XP is for teaching and engagement only. It is not included in the candidate triage, evidence completeness, terrain comparisons or any scientific result.

## What would raise confidence next

For the Balochistan playa leads, the next decisive work is to verify the geomorphic AOI and hydrology across multiple dates, screen imagery for cloud/shadow/seasonal artefacts, and collect authorized ground samples for mineralogical and chemical analysis. For other tasks, the proposed next measurements are displayed in the Mission Director brief.

Across all sites, field access, permits, site-level geology, ground truth, scale-appropriate terrain and specialist review remain necessary. Diviner thermal/ice-depth processing, lunar illumination and permanently shadowed-region mapping, dust measurements and site-specific mineralogical work remain outstanding.

# 2026 challenge benchmark and ANALOG-X differentiation

**Reviewed:** 15 November 2026  
**Challenge:** Identify Earth Locations that Analog the Permanent Moon Base Locations and Mars  
**Scope:** Public project pages and public GitHub repositories available during the hackathon. Team capability figures below are project/README claims, not independent scientific audits.

## What other teams are showing

| Public project | Publicly described strength | Relevant lesson for ANALOG-X | Code reuse status |
|---|---|---|---|
| TwinWorlds — https://github.com/TayyabXtreme/Twin_World_Nasa_Space_APP_Challenge_2026 | README reports 354,342 Earth land cells, 16 lunar/Mars targets, 33 catalogued datasets, seven measured dimensions, Pakistan spotlights and a per-target non-transferability panel. It also describes a fast quantised-grid worker and a scripted demo mode. | A ten-seed atlas is not a credible substitute for an exhaustive global raster scan. Keep our search scope explicit. Borrow the seven-dimension framing and the visible physics-mismatch explanation, not unverified scale claims. | No licence was listed in the public repository at review time. No code copied. |
| Team Shoemaker — https://shoemaker-spaceapps.github.io/demo/ | Public demo reports comparison of 22,147 Earth windows with 13 lunar locations, and highlights that terrain similarity alone cannot distinguish salt desert from basalt. | Separate landform morphology from surface-material evidence. Explain how a numerically similar terrain profile can still be the wrong rehearsal environment. | The public repository is MIT-licensed. We did not copy its implementation. |
| Analog Twin — https://github.com/escapeboy/analog-twin | Reverse Earth–Moon–Mars lookup, terrain plus sunlight matching, custom landing-site comparison and AI-assisted field-campaign plans. | Make mission tasks and lighting conditions explicit; consider reverse lookup and campaign planning as later upgrades. | Apache-2.0. No source code copied into this release. |
| Earth Analog Explorer — https://github.com/azrialahmad/earth-analog-explorer | Separates lunar illumination from terrain matching and focuses on lunar south-pole / Mars target comparisons. | A terrain resemblance should not be treated as a lighting or permanent-shadow resemblance. Our current release explicitly lists formal illumination/PSR analysis as missing. | No licence listed at review time. No code copied. |
| TerraNova — https://github.com/Yakiyo/terra-nova and https://github.com/KraKEn-bit/TerraNova | Public materials describe global grid search, candidate novelty checks, per-criterion explanations, known-analog calibration, leave-one-criterion-out sensitivity and negative controls. | Robustness, novelty and negative controls are valuable. A candidate's evidence should be tested, not simply ranked. | Yakiyo repository declares Apache-2.0; KraKEn-bit repository declares Apache-2.0. No code copied into this release. |
| PTAE — https://github.com/JFJubayer/nasa-space-apps-2026-ptae | Public README describes a broad multi-site terrain engine and a reproducible pipeline. It also states that the default quick run uses calibrated procedural DEMs, with real downloads as a separate path. | Always show when a dataset is synthetic, metadata-only or actually measured. Do not let a visually convincing score imply real source data. | MIT licence. No code copied. |
| Analog Atlas — https://github.com/end13s/analog-atlas | Public README describes a multi-dimensional physical fingerprint, per-cell scoring and a Pareto/uncertainty-oriented engine; it explicitly labels its current scaffold data as synthetic. | Use uncertainty and trade-offs rather than one universal score. Make demonstration data impossible to confuse with observations. | MIT licence. No code copied. |
| EarthTwin — https://github.com/es-ratt/earthtwin | Public README describes a data-centre import workflow and openly labels its current catalogue/measurements as illustrative demo data pending verified imports. | Clear demo-data labelling is essential; polished UI alone does not validate science. | No licence listed at review time. No code copied. |

## What this means for ANALOG-X

A global ranking contest is not the most defensible route for this release. Several teams report six-figure global grids and many planetary targets. ANALOG-X currently has ten curated Earth seeds, four processed Pakistan study windows and two under-characterized Balochistan playa leads. It must not claim to have searched every land pixel, discovered a new site, or validated a new-to-science analog.

Instead, this release focuses on a narrower and useful gap: **Pakistan-first field-evidence adjudication**.

### New differentiating function — Field Evidence Passport

The Passport is designed around a decision a field team can actually make:

1. Select a real candidate, planetary target and field experiment.
2. Inspect which source, NASA POWER, Sentinel-2 and terrain layers exist in the bundled evidence.
3. See whether a documented task overlap exists and which material/operational claims remain unproven.
4. Compare strict and exploratory evidence policy without producing a false similarity percentage.
5. Generate a site-specific proposed field protocol with controls, sample provenance, methods, quality checks and transferability caveats.
6. Capture real GNSS-referenced station observations, notes, units, methods and optional photographs offline; export JSON, CSV or GeoJSON.

The feature's edge is not a claim that it has more data than every competitor. It is that it makes the next field validation step operational, traceable and usable in disconnected field conditions.

### Other release choices informed by the benchmark

- **Offline-first core:** no external tile/CDN or AI API is required for the local atlas, deterministic Mission Director, field protocol, Passport or local candidate-proximity Scout after the app/data pack is cached once.
- **Coordinate Scout honesty:** it measures proximity to the ten bundled candidate/reference points. It does not pretend to be an exhaustive raster scan or a live global discovery API.
- **Separate evidence dimensions:** no weighted Earth-to-Moon/Mars percentage is invented.
- **Negative evidence stays visible:** MOLA coverage at Nili Patera is 50.53%; this warning is kept adjacent to terrain comparisons.
- **Lunar science is specific:** Diviner thermal summaries have been processed for the Shackleton comparison window. The ice-depth field remains withheld from the interface pending interpretation QA; formal illumination/PSR mapping is not integrated.
- **Optional backend:** GitHub Pages cannot run a persistent API server. The repository now contains a FastAPI/PostgreSQL backend that can be self-hosted, while the public static application remains functional without deploying it.

## Benchmark interpretation cautions

- Competitor metrics quoted here are self-reported in public project pages/README files and were not independently recalculated.
- A large cell count is not, by itself, evidence of scientifically valid site boundaries, matched spatial support, uncertainty treatment or validated mineralogy.
- A high match score may be less useful than a task-specific explanation of why an environment is or is not a good rehearsal location.
- Several public repositories do not declare a code licence. Their implementation was not copied. The benchmark uses public descriptions to inform product priorities only.
- This document is a dated snapshot of public hackathon work, not an official NASA ranking of competing teams.

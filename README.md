# ANALOG-X
### Experiment-Level Planetary Analog Discovery, Transferability & Failure Intelligence

**A Pakistan-first, open-data research and field-readiness platform for testing what Earth environments can teach us about operating on the Moon and Mars.**

[![GitHub Pages](https://github.com/usmanmughal96/analog-x/actions/workflows/pages.yml/badge.svg?branch=main)](https://github.com/usmanmughal96/analog-x/actions/workflows/pages.yml)
[![MIT License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

**NASA Space Apps Challenge 2026** · Team **X Æ A-Xii** · Participant **Muhammad Usman Mughal**

---

## Explore ANALOG-X

| Experience | What it offers |
|---|---|
| [Evidence Operations Console](https://usmanmughal96.github.io/analog-x/) | Main map-led project workspace and candidate atlas |
| [Seven-slide demo](https://usmanmughal96.github.io/analog-x/demo.html) | Short project walkthrough |
| [ATFA Science Module](https://usmanmughal96.github.io/analog-x/transferability.html) | Experiment-level transferability and analogy-failure analysis |
| [Regional Discovery Scan](https://usmanmughal96.github.io/analog-x/discovery.html) | Local terrain-window comparison within the ten curated Earth regions |
| [Global Discovery Engine](https://usmanmughal96.github.io/analog-x/global-discovery.html) | Worldwide Copernicus GLO-90 land-inventory screening |
| [Pakistan Field Validation Kit](https://usmanmughal96.github.io/analog-x/field-validation.html) | Offline-first field protocols, stations and observation capture |
| [Source repository](https://github.com/usmanmughal96/analog-x) | Code, datasets, tests, methods and provenance |

## The mission

Choosing a terrestrial analog is not simply a matter of finding a landscape that looks like the Moon or Mars. A useful analog depends on the **specific experiment, physical process or operational procedure** being rehearsed—and on understanding exactly where that comparison breaks down.

ANALOG-X is built around five questions:

1. What can a mission team realistically rehearse at this Earth site?
2. Which observations and source products support that claim?
3. Which planetary conditions make the analogy incomplete or invalid?
4. What measurement or field validation is still needed?
5. Can another researcher trace the result back to its data, method and limitations?

The system deliberately separates measured data, browse imagery, catalogue metadata, institutional references, planned integrations and field observations. It does not present a universal Earth-to-Moon/Mars similarity percentage.

## What is implemented

### 1. A Pakistan-first Earth study network

The atlas combines ten curated environments:

- **Pakistan field leads:** Chagai small salt playas near Nok Kundi, Hamun-i-Mashkel / Kharan Basin, Koh-i-Sultan and Hispar Glacier.
- **Global reference environments:** Dallol, Atacama, McMurdo Dry Valleys, Haughton impact structure, Iceland and Death Valley.

The Pakistan locations are under-characterized research leads, not confirmed new analog discoveries or validated mineral/brine deposits. Coordinates and study windows are screening references; they are not surveyed field boundaries.

### 2. Analog Transferability & Failure Analysis (ATFA)

ATFA changes the unit of comparison from whole-site resemblance to a named experiment or physical process. Each pathway records the Earth rehearsal opportunity, why the environment is relevant, where transfer fails, what evidence supports the claim and what should be measured next.

Transferability classes are transparent, expert-authored research rules. They are not model probabilities, calibrated scientific accuracy or NASA certification.

### 3. Mission Rehearsal Lab and evidence decision layer

The Mission Rehearsal Lab compares selected Earth terrain descriptors with two planetary reference areas:

- **Moon:** Shackleton Rim, using NASA LRO LOLA products.
- **Mars:** Nili Patera, using MOLA MEGDR topography.

The common-support terrain comparison uses approximately 925 m grids and reports median slope, P90 slope and P90 3×3 local relief, with absolute differences. These are regional reconnaissance descriptors. They do not prove geological equivalence, surface-material similarity, rover trafficability, landing safety or resource access.

The Agent Bay separates mission/task eligibility from four evidence layers: NASA POWER climate context, Sentinel-2 spectral context, processed terrain and source references. Its deterministic review works without an LLM or API key. An optional cloud Mission Director can provide an additional tool-using review; model output is not a measurement.

### 4. Regional and global terrain discovery

The [Regional Discovery Scan](https://usmanmughal96.github.io/analog-x/discovery.html) divides the ten existing Earth DEM regions into approximately 5.55 km windows at approximately 925 m terrain support. The committed regional run contains:

| Input | Valid windows |
|---|---:|
| Ten curated Earth regions | 7,290 |
| Shackleton Rim | 729 |
| Nili Patera | 21 |

A 500-draw deterministic weight-sensitivity diagnostic shows how shortlist placement changes under alternative terrain-feature weights. Overlapping windows are spatially dependent; the index is a terrain-screening aid, not a probability, field truth or planetary analog verdict. This regional scan does not expand the geographic coverage of its ten source regions.

The separate [Global Discovery Engine](https://usmanmughal96.github.io/analog-x/global-discovery.html) processes the public Copernicus DEM GLO-90 land-tile inventory using 24 longitude shards. Its previous completed inventory release processed 26,475 of 26,475 land tiles, with zero reported tile failures, and evaluated 5,852,396 terrain windows. Ocean coverage is not implied.

**Global ranking release status:** the latest quantitative-validation artifact currently reports `ranking_ready = false` because the saved shortlist does not yet satisfy the required ranking-contract gate. The full-inventory baseline above is a completed prior release; the refreshed core-only shortlist must pass the current 24-shard aggregation and validation workflow before its ranks should be treated as current. See [Global Discovery & Quantitative Validation](docs/GLOBAL_DISCOVERY_AND_VALIDATION.md).

### 5. Field Evidence Passport and Pakistan Field Validation Kit

The Field Evidence Passport helps define a site-specific field experiment, inspect independent evidence layers, identify unsupported claims and export a proposed protocol.

The offline-first Field Validation Kit supports station plans and user-entered GNSS observations, methods, instruments, uncertainty, notes and optional photos. Records remain in the browser until a user exports them. The committed observation ledger is currently empty: **no physical field observations or independent field validation are claimed.**

### 6. Offline-first operation and optional services

The public GitHub Pages application is a static web app. After its first connected visit and cache setup, the core science pack, deterministic Mission Director, Field School, Field Evidence Passport and local field notebook can operate offline on the same browser/device.

Optional deployment paths are included but are not required for the core experience:

- **FastAPI + PostgreSQL:** self-hostable backend for shared field records and read-only science endpoints. GitHub Pages itself does not run a persistent API.
- **Cloudflare Workers AI:** optional server-side Mission Director. Provider credentials stay server-side; the browser does not need an AI key for deterministic assessments.

Live basemaps, NASA imagery overlays and fresh remote-data requests require connectivity. When external map assets fail, the application retains its labelled schematic locator and local science assets.

## Evidence and data integrations

| Source | Use in ANALOG-X | Evidence state / important limit |
|---|---|---|
| NASA POWER | Monthly/annual climate context for ten curated Earth sites and top retained global candidates | Processed gridded climatology, not local weather-station observations or forecasts |
| Sentinel-2 L2A | Scene discovery, spectral-context screens and RGB quicklooks | Spectral screens are not mineral/brine classification; RGB previews are browse-only |
| Copernicus DEM GLO-30 | Higher-detail terrain context for the ten curated Earth regions | Digital surface model; selected-site processing, not a complete global GLO-30 layer |
| Copernicus DEM GLO-90 | Global land-tile terrain screening | 90 m nominal DSM resampled to local metric grids; current ranking release remains subject to its validation gate |
| NASA LRO LOLA | 80 m south-polar context and a separate 5 m Shackleton Rim site product | Interpolated terrain validity and direct laser-return support are reported separately |
| NASA MOLA MEGDR | Nili Patera reference terrain | Selected reference window has limited observed-cell coverage |
| NASA Diviner PRP V2.0 | Historical thermal summaries for 6,823 Shackleton-window triangles | Ice-depth values are withheld pending QA; no accessible-ice claim |
| 2023 global land cover | Context for retained global shortlist windows | 2,391 of 2,400 unique retained windows processed in the latest validation artifact; not geology or field truth |
| GLiM global lithology | Generalized lithology point context for retained candidates | 200 of 200 top-shortlist point queries returned features; not area-weighted geology or mineral identification |
| NASA Earthdata CMR | MODIS and MERRA-2 collection/granule discovery | Metadata-only; the underlying science arrays have not been downloaded and decoded by this integration |
| NASA DSCOVR / EPIC | Optional full-disc Earth image | Global visual context only, not a site-scale metric |

The authoritative status for each source is maintained in [data/source_registry.json](data/source_registry.json). Source descriptions, access routes, licences and caveats are documented in [docs/DATA_SOURCES.md](docs/DATA_SOURCES.md) and [docs/AGENCY_DATA_AUDIT.md](docs/AGENCY_DATA_AUDIT.md).

## Latest verified evidence snapshot

The latest committed validation and lunar-reference products used for this README were generated on **22 November 2026**.

- **Regional scan:** 7,290 Earth windows, 729 Shackleton windows and 21 Nili Patera windows.
- **Global land-inventory baseline:** 26,475 Copernicus GLO-90 land tiles processed, zero reported tile failures and 5,852,396 terrain windows evaluated in the previous completed release. The newer shortlist release remains not ranking-ready until its refreshed artifact passes the ranking-contract gate.
- **Global shortlist context:** 2,391 / 2,400 retained windows have 2023 land-cover enrichment; NASA POWER climatology covers 200 / 200 unique top-100-per-target candidate coordinates; GLiM returned generalized lithology features for 200 / 200 retained candidate points. The latter two are contextual enrichment layers, not independent analog validation.
- **Shackleton Rim 5 m LOLA:** the PGDA Site04 elevation, count and slope products are processed on a 3,200 × 3,200 grid (10,240,000 pixels). The interpolated terrain surface is valid across the grid; positive direct-return pixels cover 9.154%. A zero direct-return count does not invalidate an interpolated elevation cell.
- **Independent analog labels:** awaiting independently sourced and reviewed positive/negative reference labels. No AUC, accuracy or calibrated ranking performance is claimed.
- **Field validation:** the observation ledger remains empty until physical measurements are collected and reviewed.

The machine-readable snapshot is [data/validation/quantitative_validation.json](data/validation/quantitative_validation.json); the LOLA processing summary is [data/moon/shackleton_rim_lola.json](data/moon/shackleton_rim_lola.json). Counts and evidence states can change when scheduled or manually triggered pipelines publish new outputs.

## Scientific guardrails

ANALOG-X is a research and field-planning system, not an operational mission-safety tool.

- A curated ten-site atlas is not an exhaustive global search.
- The Chagai and Hamun-i-Mashkel study windows are approximate screening areas, not surveyed or field-validated playas.
- Terrain descriptors at approximately 925 m support cannot resolve rover-scale hazards or field-scale obstacles.
- Earth DSM products include surface objects and are not bare-earth elevation.
- The selected Nili Patera MOLA window has limited observed-cell coverage; the application exposes this limitation.
- The 5 m Shackleton LOLA DEM is interpolated. Direct return counts are a separate support indicator. These data alone do not establish illumination, permanent shadow, water-ice abundance, landing suitability or engineering safety.
- Diviner ice-depth values remain withheld pending QA; formal illumination / PSR mapping is not integrated.
- Catalogue discovery and browse imagery are not equivalent to downloading, decoding and validating science arrays.
- Field access, permissions, safety review, ground measurements and independent scientific review remain necessary.

See [docs/LIMITATIONS.md](docs/LIMITATIONS.md) for the expanded limitation register.

## Reproducibility, validation and automated workflows

ANALOG-X keeps methods, source states, generated products and validation outputs in the repository:

- [data/source_registry.json](data/source_registry.json) — canonical source and evidence states.
- [data/validation/](data/validation/) — quantitative checks, independent-label status and NASADEM cross-check outputs.
- [data/provenance/reproducibility_manifest.json](data/provenance/reproducibility_manifest.json) — generated SHA-256 file inventory and build context.
- [tests/](tests/) — scientific contracts, parsers, data validation and regression tests.
- [scripts/](scripts/) and [science/](science/) — reproducible source ingestion and analysis.
- [.github/workflows/](.github/workflows/) — scheduled, push-triggered and manual processing pipelines.

Generated-data publishing is centralised through [scripts/commit_generated_data.sh](scripts/commit_generated_data.sh). It stages only declared output paths, skips no-op updates, retries non-conflicting rebases and stops rather than automatically resolving scientific-data conflicts. Data-refresh concurrency is scoped by workflow so unrelated jobs do not cancel one another.

Useful entry points:
- [Algorithm and decision engine](docs/ALGORITHM.md)
- [Methodology](docs/METHODOLOGY.md)
- [Global discovery and validation](docs/GLOBAL_DISCOVERY_AND_VALIDATION.md)
- [Regional window scan](docs/REGIONAL_WINDOW_SCAN.md)
- [Independent label validation protocol](docs/INDEPENDENT_LABEL_VALIDATION_PROTOCOL.md)
- [Offline and backend setup](docs/OFFLINE_AND_BACKEND.md)
- [Agent API setup](docs/AGENTIC_AI_SETUP.md)
- [NASA Space Apps submission brief](docs/CHALLENGE_SUBMISSION_BRIEF.md)
- [Competitive capability benchmark](docs/COMPETITIVE_CAPABILITY_RESPONSE.md)

## Run locally

The main console is a static site. Python is sufficient to serve it locally:

```bash
git clone https://github.com/usmanmughal96/analog-x.git
cd analog-x
python -m http.server 8000
```

Open http://localhost:8000 in your browser. Live maps and remote imagery require internet access; the local science pack and offline tools are designed to remain available after the app has been cached once.

For the optional API, Docker-based FastAPI and PostgreSQL instructions are in [docs/OFFLINE_AND_BACKEND.md](docs/OFFLINE_AND_BACKEND.md). To deploy the optional Cloudflare Agent API, follow [docs/AGENTIC_AI_SETUP.md](docs/AGENTIC_AI_SETUP.md). Current public data integrations do not require an api.nasa.gov key. Never commit populated environment files or secrets.

## Repository map

| Path | Purpose |
|---|---|
| `index.html`, `*.html` | Main console and interactive research views |
| `assets/` | Frontend styles, scripts and icons |
| `science/` | Transferability and regional analysis modules |
| `scripts/` | Data ingestion, processing, validation and publication helpers |
| `data/` | Source records, derived science products, validation and provenance |
| `backend/` | Optional FastAPI / PostgreSQL service |
| `agent-worker/` | Optional Cloudflare Workers AI service |
| `tests/` | Regression and scientific contract tests |
| `docs/` | Methods, source audits, deployment guides and research notes |
| `.github/workflows/` | Automated data pipelines and deployment workflows |

## Licence and attribution

Original ANALOG-X code and project text are MIT-licensed. NASA, Copernicus, Microsoft Planetary Computer, USGS, GLiM, EvK2CNR and other third-party datasets retain their own licences, attribution requirements and reuse conditions. See [LICENSE](LICENSE) and the relevant source records before redistributing derived data.

**Project status:** an independent research prototype developed for NASA Space Apps Challenge 2026. ANALOG-X is not an official NASA, ESA, SUPARCO or other agency product, and its outputs are not operational guidance or certification.

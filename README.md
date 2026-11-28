<div align="center">

<a href="https://www.spaceappschallenge.org/brand/" target="_blank" rel="noopener">
  <img src="https://assets.spaceappschallenge.org/media/images/Space_Apps_Logo_Color_and_Black.width-580.png" alt="Official NASA Space Apps Challenge logo" width="190">
</a>

# ANALOG-X

### From Mars-like places to testable mission rehearsals.

**An evidence-first Earth–Moon–Mars analog research and field-operations platform.**

Built for the **NASA Space Apps Challenge 2026** · Participant project · **Team X Æ A-Xii**

[![NASA Space Apps 2026 Participant Project](https://img.shields.io/badge/NASA%20Space%20Apps-2026%20Participant%20Project-175A9B?style=for-the-badge)](https://www.spaceappschallenge.org/2026/)
[![GitHub Pages](https://github.com/usmanmughal96/analog-x/actions/workflows/pages.yml/badge.svg?branch=main)](https://github.com/usmanmughal96/analog-x/actions/workflows/pages.yml)
[![MIT License](https://img.shields.io/badge/License-MIT-2E8B76.svg)](LICENSE)

[**Launch the live console**](https://usmanmughal96.github.io/analog-x/) · [**Watch the 7-slide demo**](https://usmanmughal96.github.io/analog-x/demo.html) · [Explore the source](https://github.com/usmanmughal96/analog-x)

</div>

---

> **The question is not “does this place look like Mars?”**
>
> It is: **which mission experiment can we rehearse here, what evidence supports that choice, where does the analogy fail, and what should we measure next?**

ANALOG-X is a Pakistan-first research platform connecting candidate Earth environments to specific lunar and Martian field tasks. It brings source records, satellite context, regional terrain, transferability rules, field protocols and validation gaps into one inspectable workflow—without hiding uncertainty behind a universal similarity score.

## Explore the platform

| Workspace | What you can inspect |
|---|---|
| [Evidence Operations Console](https://usmanmughal96.github.io/analog-x/) | Interactive Pakistan map, climate, satellite previews, terrain, Agent Bay and evidence status |
| [Seven-slide demo](https://usmanmughal96.github.io/analog-x/demo.html) | Project story, scientific evidence and validation boundaries |
| [ATFA Science Module](https://usmanmughal96.github.io/analog-x/transferability.html) | Experiment-level transferability and analogy-failure analysis |
| [Planetary archive discovery](data/planetary/archive_discovery.json) | Spatially bounded PDS Geosciences ODE and USGS HiRISE metadata for MOLA, LOLA, Diviner and Nili Patera |
| [Nili Patera HiRISE DTM reference](https://www.uahirise.org/dtm/dtm.php?ID=ESP_017762_1890) | Catalogued stereo DTM of the moving-dune field (1.01 m/pixel published map scale); footprint overlap with the current MOLA AOI is not yet verified |
| [Regional Discovery Scan](https://usmanmughal96.github.io/analog-x/discovery.html) | Local terrain-window comparison across ten curated Earth regions |
| [Global Discovery Engine](https://usmanmughal96.github.io/analog-x/global-discovery.html) | Copernicus GLO-90 land-inventory screening and target-specific shortlists |
| [Pakistan evidence network](https://usmanmughal96.github.io/analog-x/#pakistanEvidenceNetwork) | Four processed Pakistan satellite and terrain study windows |
| [Field Validation Kit](https://usmanmughal96.github.io/analog-x/field-validation.html) | Offline-first stations, protocols and observation capture |
| [Mission Readiness & Evidence Gates](https://usmanmughal96.github.io/analog-x/mission-readiness.html) | Global-scan status, terrain evidence, field prerequisites and rover-suitability gaps |
| [Independent Reviewer Desk](https://usmanmughal96.github.io/analog-x/independent-review.html) | Local-first blinded review interface for the 96-case terrain-morphology packet |
| [Independent-review packet](data/validation/independent_analog_review_packet.json) | 96 blinded Moon/Mars cases prepared for external review |
| [Source registry](data/source_registry.json) | Canonical data-source and evidence states |

## The research network

ANALOG-X maintains **ten curated Earth environments**: four Pakistan field leads and six global comparison environments.

| Pakistan study window | Rehearsal focus | Evidence in this release |
|---|---|---|
| **Chagai small salt playas / Nok Kundi** | Evaporite facies and salt-crust mapping | Sentinel-2 spectral context, RGB quicklook, Copernicus GLO-30 terrain and NASA POWER |
| **Hamun-i-Mashkel / Kharan Basin** | Closed-basin and wet/dry observations | Sentinel-2 spectral context, RGB quicklook, Copernicus GLO-30 terrain and NASA POWER |
| **Koh-i-Sultan / Chagai** | Volcanic outcrop and alteration-mapping workflow | USGS regional geology context, Sentinel-2, Copernicus GLO-30 terrain and NASA POWER |
| **Hispar Glacier / Karakoram** | Cryosphere and ice/debris interpretation | Sentinel-2, Copernicus GLO-30 terrain, NASA POWER and EvK2CNR baseline context |

Global comparison environments: Dallol, Atacama, McMurdo Dry Valleys, Haughton, Iceland and Death Valley.

These are **candidate study windows**, not newly discovered or field-validated planetary analogs. Coordinates are screening references, not surveyed boundaries. Sentinel-2 RGB previews are browse imagery; spectral-context profiles do not identify minerals or brines.

## What makes ANALOG-X different

### ATFA — Analog Transferability & Failure Analysis

ATFA changes the unit of comparison from an entire landscape to a named experiment or physical process. Its pathways record what can be rehearsed, what cannot be transferred, the evidence behind the assessment and the next measurement needed.

### Four-site Mission Rehearsal Lab

The Lab compares all four Pakistan terrain profiles against selected lunar or Martian reference data, dimension by dimension: median slope, P90 slope and P90 3×3 local relief. It supports task-specific protocols for playa/evaporite mapping, basin observations, volcanic mapping, cryosphere work and terrain documentation.

A nearest descriptor is not a planetary-equivalence verdict. The Lab does not calculate a blended analog probability, rover-trafficability score or mission-safety certification.

### Four deterministic evidence specialists

The local Agent Bay reviews terrain morphology, climate and campaign context, surface spectral context, and evidence integrity. Its deterministic core works without an LLM or API key. The optional cloud Mission Director is an additional review interface—not a source of measurements.

### Field operations, not just a map

The Field Evidence Passport and offline-first Field Validation Kit support station planning, GNSS observations, explicit UTC station and instrument-batch timestamps, instrument/calibration provenance, units, uncertainty, notes, optional photos and exportable records. The observation ledger remains empty until physical measurements are collected and reviewed.

## From discovery to independent validation

The [Mission Readiness & Evidence Gates workbench](https://usmanmughal96.github.io/analog-x/mission-readiness.html) connects the global scan, ATFA, Pakistan field campaign, lunar terrain and independent-review status without converting any of them into a safety or accuracy claim.

The [Independent Reviewer Desk](https://usmanmughal96.github.io/analog-x/independent-review.html) provides a local-first interface for the 96 anonymized terrain-morphology cases (48 Moon, 48 Mars). It hides candidate IDs, ranks and scores, records reviewer qualifications and evidence references, and exports a response JSON. It does not submit responses automatically. The private case key is kept by the project owner and must never be sent to reviewers or committed.

### Three open validation gates

- **Physical field evidence:** the Pakistan campaign is planned; the committed field-observation ledger remains empty. No field experiment is claimed.
- **Rover / mission suitability:** current Earth comparison cells are about 925 m; Shackleton Site04 has a separate 5 m LOLA terrain product plus historical 100 m LROC WAC illumination-frequency and Diviner PRP thermal-model context. Nili Patera also has a catalogued HiRISE dune-field DTM reference at 1.01 m/pixel. A bounded read of its PDS label confirms that its footprint does **not** intersect the current MOLA comparison AOI; it is a separate adjacent reference, and its approximately 430 MB raster has not been downloaded or processed. These datasets do not provide mission-date illumination, formal PSR geometry, traction evidence, landing suitability or safety. No rover/UGV trial or vehicle-specific engineering review is claimed.
- **Independent expert confirmation:** 96 blinded cases are prepared, but no binary labels have been returned. No independent AUC, accuracy or reviewer endorsement is claimed.

See [Operational Readiness & Validation Gates](docs/OPERATIONAL_READINESS_AND_VALIDATION.md) and the [Independent Reviewer Guide](docs/INDEPENDENT_REVIEWER_GUIDE.md) for protocols, evidence requirements and next actions.

## Evidence snapshot — 28 November 2026

<sub>Counts describe the committed research release. They are processing and evidence counts—not competition placements or independent scientific accuracy.</sub>

| Evidence layer | Current release | Interpretation |
|---|---:|---|
| NASA POWER climatology | **10 / 10 site snapshots** | Seven requested parameters; gridded context, not station observations or forecasts |
| Pakistan Earth observation | **4 study windows** | Four Sentinel-2 spectral-context profiles and four local RGB quicklooks; RGB is browse-only |
| Pakistan terrain | **4 processed profiles** | Copernicus GLO-30 DSM at approximately 925 m support over 30 km windows |
| Regional discovery | **7,290 Earth windows** | Ten parent regions subdivided into overlapping ~5.55 km windows |
| Planetary reference windows | **729 Moon · 21 Mars** | Shackleton Rim LOLA and Nili Patera MOLA comparison windows |
| Global GLO-90 inventory | **26,475 / 26,475 land tiles** | Complete enumerated land inventory; zero reported tile failures; 5,852,396 windows evaluated |
| Moon shortlist | **1,200 candidates** | Target-specific core terrain shortlist passes schema, ordering and rank-integrity checks |
| Mars shortlist | **1,200 candidates** | Separate target-specific core terrain shortlist passes schema, ordering and rank-integrity checks |
| 2023 land-cover context | **2,391 / 2,400 windows** | Shortlist enrichment; not geology or field truth |
| NASA POWER global context | **200 / 200 points** | Top-100-per-target coordinate context; not field measurements |
| GLiM lithology context | **200 / 200 points** | Generalized point-query context; not area-weighted geology or mineral identification |
| Blinded independent review | **96 cases · 0 labels** | 48 Moon and 48 Mars cases await external review |
| Physical field observations | **0** | No physical Pakistan field validation is claimed |

### What “ranking ready” means

The latest quantitative-validation report records the ranking release as **ready**. Both target-specific shortlists pass the required schema, core-only ordering, sequential-rank and unique-ID checks. That is **release integrity**, not scientific accuracy. No independent reviewer labels, AUC or calibrated accuracy are available. These are terrain-screening ranks—not a NASA Space Apps competition leaderboard position.

### Lunar south-pole evidence

The Shackleton pack includes NASA LOLA 80 m terrain context and a separate NASA PGDA Site04 **5 m** elevation, count, slope and RMS-error product set on a 3,200 × 3,200 grid (10.24 million pixels). Interpolated terrain coverage is 100%; positive direct-return support is 9.154%. Those are different measures.

Historical Diviner PRP V2.0 summaries cover 6,823 Shackleton-window triangles: median annual-average temperature at 2 cm is 103.786 K and median annual-maximum surface temperature is 238.568 K. These are model-derived summaries from the first year of LRO mapping observations (2010–2011), not forecasts or in-situ measurements. Separate 100 m LROC WAC illumination-frequency products (15 February 2010–5 February 2011) report mean illumination frequency of 24.86% in the time-weighted layer and 25.97% in the percentage-based layer. At or below 5% illumination frequency, the corresponding area fractions are 60.62% and 58.65%. This threshold is only a low-illumination screening proxy, not a formal PSR polygon. Diviner ice-stability-depth values remain QA-limited and do not establish ice abundance or accessibility. Formal PSR Atlas geometry and mission-date NAIF SPICE illumination are not integrated.

Machine-readable status: [quantitative validation](data/validation/quantitative_validation.json) · [global rankings](data/global_discovery/top_ranked_candidates.json) · [source registry](data/source_registry.json) · [Shackleton LOLA report](data/moon/shackleton_rim_lola.json). · [planetary archive discovery](data/planetary/archive_discovery.json)

## Evidence sources and limitations

| Source | Role | Important limit |
|---|---|---|
| NASA POWER | Ten-site and global candidate climatology | Gridded context, not local station observations or forecasts |
| Sentinel-2 L2A | Scene discovery, spectral-context screens and RGB quicklooks | Spectral screens do not establish mineralogy or brine; RGB is browse-only |
| Copernicus DEM GLO-30 | Terrain context for ten curated Earth regions | Digital surface model; selected windows, not global GLO-30 coverage |
| Copernicus DEM GLO-90 | Global land-inventory terrain screening | Screening index, not independent analog validation |
| NASA MOLA MEGDR | Nili Patera Mars reference | Selected window has 50.53% observed-cell coverage |
| University of Arizona HiRISE DTM | Nili Patera moving-dune stereo DTM reference | Catalogued at 1.01 m/pixel; a 256 KiB PDS-label read confirms that its bounding box does not intersect the original MOLA AOI. The 430 MB raster is not downloaded or processed |
| NASA LRO LOLA | Shackleton Rim 80 m and separate 5 m Site04 products | Interpolated elevation and direct-return support are separate measures |
| NASA Diviner PRP V2.0 | Historical model-derived thermal and ice-stability-depth context | Not in-situ; depth QA, accessible-ice interpretation and resource claims remain open |
| NASA LROC WAC | Historical 100 m south-pole illumination-frequency products | 2010–2011 observation period; not a mission-date forecast or formal PSR delineation |
| NASA Earthdata CMR | MODIS and MERRA-2 catalogue discovery | Metadata-only; science arrays have not been decoded by this integration |
| NASA PDS Search API | Federated Moon/Mars product catalogue queries | API returned HTTP 500 during the latest build; this is a service error, not evidence that archives lack products |
| PDS Geosciences ODE | Archive-specific MOLA, LOLA, Diviner and Nili Patera HiRISE DTM discovery | Metadata-only; uses live IIPT types and a separate east-expanded DTM search box; original MOLA comparison AOI is unchanged |
| USGS Astrogeology STAC | HiRISE RDR image-observation metadata around Nili Patera | Image observations are not stereo DTMs; no imagery assets are downloaded by discovery |
| GLiM / 2023 land cover | Retained-candidate context | Generalized layers, not field-validated geology |

ANALOG-X is a research and field-planning prototype, not an operational mission-safety tool. Ten curated regions are not an exhaustive global search; ~925 m terrain does not resolve rover-scale hazards; the selected MOLA window is coverage-limited; no mineral assays, independent labels, field observations, rover trials or safety certifications are claimed.

Canonical source states live in [data/source_registry.json](data/source_registry.json). See [data sources](docs/DATA_SOURCES.md), [limitations](docs/LIMITATIONS.md) and the [Independent Operational Evidence Phase](docs/INDEPENDENT_OPERATIONAL_EVIDENCE_PHASE.md).

## Run locally

<pre><code>git clone https://github.com/usmanmughal96/analog-x.git
cd analog-x
python -m http.server 8000</code></pre>

Open [http://localhost:8000](http://localhost:8000). Live basemaps, imagery overlays and fresh remote-data requests need connectivity. The local science pack and deterministic tools are designed to work offline after the app has been cached once.

Optional services: [FastAPI + PostgreSQL](docs/OFFLINE_AND_BACKEND.md) for self-hosted persistence, and [Cloudflare Workers AI](docs/AGENTIC_AI_SETUP.md) for the optional cloud Mission Director. GitHub Pages itself does not run a persistent API.

## Repository map

| Path | Purpose |
|---|---|
| index.html and other HTML pages | Main console and research views |
| assets/ | Frontend styles and scripts |
| science/ | Transferability and analysis modules |
| scripts/ | Data ingestion, processing, validation and publication |
| data/ | Source records, derived products, validation and provenance |
| backend/ | Optional FastAPI / PostgreSQL service |
| agent-worker/ | Optional Cloudflare Workers AI service |
| tests/ | Regression and scientific contract tests |
| docs/ | Methods, source audits, deployment and research plans |
| .github/workflows/ | Data pipelines and GitHub Pages deployment |

Useful entry points: [Algorithm](docs/ALGORITHM.md) · [Methodology](docs/METHODOLOGY.md) · [Global validation](docs/GLOBAL_DISCOVERY_AND_VALIDATION.md) · [Independent-label protocol](docs/INDEPENDENT_LABEL_VALIDATION_PROTOCOL.md) · [AI disclosure](docs/AI_DISCLOSURE.md) · [NASA submission brief](docs/CHALLENGE_SUBMISSION_BRIEF.md).

## Licence and attribution

Original ANALOG-X code and project text are MIT-licensed. NASA, Copernicus, Microsoft Planetary Computer, USGS, GLiM, EvK2CNR and other third-party datasets retain their own licences and attribution rules. Review [LICENSE](LICENSE) and the relevant source records before redistributing derived data.

<div align="center">

**ANALOG-X · Team X Æ A-Xii · Muhammad Usman Mughal**

Independent participant-built research prototype for NASA Space Apps Challenge 2026. Not an official NASA, ESA, SUPARCO or other agency product; not endorsed by those organisations.

[Live platform](https://usmanmughal96.github.io/analog-x/) · [Seven-slide demo](https://usmanmughal96.github.io/analog-x/demo.html) · [Official Space Apps brand guidance](https://www.spaceappschallenge.org/brand/)

</div>
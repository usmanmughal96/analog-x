# Global Discovery, Quantitative Validation & Field Evidence

**Last evidence review:** 19 November 2026  
**Project:** ANALOG-X · NASA Space Apps Challenge 2026

This document distinguishes completed processing, robustness diagnostics, generalized map context, browse/metadata-only inputs, field plans and evidence that does not yet exist.

## 1. Global discovery — implemented and run

### Verified global inventory build

The 18 November 2026 global release used the public Copernicus DEM GLO-90 one-degree land-tile inventory and the 24-shard processing workflow.

| Measure | Reported result |
|---|---:|
| Provider land tiles in inventory | 26,475 |
| Tiles assigned to shards | 26,475 |
| Tiles processed | 26,475 |
| Tile failures in merged release | 0 |
| Inventory processing coverage | 100% |
| Candidate terrain windows evaluated | 5,852,396 |
| Stored shortlist | 1,200 Moon + 1,200 Mars windows |

**Meaning of 100%:** every tile in the published Copernicus GLO-90 land-tile inventory was opened and processed in that release. Ocean has no DEM land tile and is not covered. This does not mean all of Earth's surface or every 5.55 km window has valid terrain observations. The output is a bounded shortlist, not an export of all 5.85 million evaluated windows.

### Method

- Source: Copernicus DEM GLO-90 (COP-DEM_GLO-90-DGED), a nominal 90 m digital surface model.
- Processing: 24 longitude shards; each one-degree tile is read from its Cloud Optimized GeoTIFF asset and resampled by area averaging to a local metric grid at nominal 925 m support.
- Unit of analysis: non-overlapping 6 × 6 grid-cell windows, approximately 5.55 km × 5.55 km.
- Terrain features: median slope, P90 slope, P95 slope, P90 3 × 3 local relief, elevation IQR, detrended roughness RMS and slope-fraction diagnostics.
- Planet references are kept separate: a selected Shackleton Rim LOLA window and a selected Nili Patera MOLA window.
- The shortlist is spatially diversified by limiting the number of retained candidates per one-degree source tile.

### Ranking correction and limitation

The earlier release averaged a core feature-family index and a second diagnostic-family index into a single consensus score. The diagnostic report for that release found strong rank disagreement over the retained 1,200-window subsets:

| Target | Spearman rank correlation, core vs secondary | Top-25 overlap | Top-100 overlap |
|---|---:|---:|---:|
| Shackleton / Moon | -0.6650 | 0 / 25 | 0 / 100 |
| Nili Patera / Mars | -0.7122 | 0 / 25 | 1 / 100 |

Those results show that feature selection materially changes candidate order. They are **not** evidence of model accuracy. The release pipeline has therefore been changed: the primary shortlist is ordered by the declared core feature family only (median slope, P90 slope, P90 local relief); the secondary family (P95 slope, elevation IQR, detrended roughness) is displayed separately as a diagnostic. No consensus or averaged index is produced. The next global workflow run will regenerate the shortlist using that corrected rule and calculate the secondary rank within the retained primary shortlist.

A score is an exploratory terrain-distance transform on IQR-normalized features, not a probability, calibrated accuracy, geological-equivalence claim, safe-access estimate or landing-site decision.

## 2. Quantitative validation — partially implemented, not model validation

### Independent elevation-source check

The repository contains a separate NASADEM (SRTM-derived) comparison against Copernicus GLO-30 for selected sites:

- 10 candidate sites attempted; 7 processed within NASADEM's approximate 56°S–60°N coverage.
- Approximate rank concordance across the seven selected sites was 0.9643 for median slope, P90 slope and P90 local relief.
- McMurdo, Haughton and Iceland were outside the stated NASADEM coverage and were not counted as processed.

This is a useful second-source consistency check for coarse terrain descriptors. It is a small, selected comparison set; NASADEM uses SRTM with auxiliary inputs, and its product semantics differ from Copernicus DSM. The result is not ground truth, global accuracy, a test of the Moon/Mars analog ranking, or field validation.

### Candidate-ranking robustness

The quantitative validation workflow reports core-versus-secondary rank correlation, top-25 and top-100 shortlist overlap, geographic spread across 10-degree cells and unique source tiles, candidate-pool size and score-family gap, and separate Moon and Mars results.

The secondary family is generated from the same GLO-90 elevation source and is not an independent validation set. Weight/feature sensitivity is a diagnostic. A strong ranking claim still requires independent reference labels, defensible positive and negative examples, spatially blocked held-out testing, predeclared metrics and independent expert review. Overlapping or spatially adjacent windows must not be treated as independent observations.

### More environmental context

- **Global land cover:** 2023 Impact Observatory / Esri / Microsoft Planetary Computer io-lulc-annual-v02, a Sentinel-2-derived 10 m annual land-cover classification. Current recorded enrichment: 2,380 of 2,400 unique retained candidate windows (99.167%). Sampling uses a 30 m modal grid within the retained 5.55 km windows. This is not geology, mineralogy, soil chemistry or field truth; coverage is limited to the retained shortlist.
- **NASA POWER:** point climatology was processed for 200 of 200 unique retained candidate coordinates (top 100 per target, deduplicated). It includes 2 m air temperature, relative humidity, 10 m wind, corrected precipitation and all-sky shortwave radiation. It is gridded climatology, not a full global climate raster, local weather station or current forecast.
- **GLiM global geology context:** the new enrichment looks up generalized lithology polygons at approximate candidate-window centres for the retained top-100-per-target subset. It is contextual evidence only and is explicitly excluded from terrain ranking. The served ArcGIS derivative's reuse terms must be confirmed before redistribution; the PANGAEA GLiM data record carries CC BY 3.0. No feature returned remains unknown. This is not an area-weighted lithology survey, field geology, mineral identification or regolith measurement.
- **Existing regional layers:** selected Pakistan/global reference regions retain finer Copernicus GLO-30 context, Sentinel-2 L2A spectral-derived screens, and curated study dossiers. These remain a separate resolution tier; they are not silently mixed with the GLO-90 global scan.

## 3. Pakistan field validation — campaign is planned; no ground truth claimed

The repository's field observation ledger currently has zero observations and remains not_started. No new in-situ Pakistan field measurements have been supplied, verified or independently reviewed. This is a real-world dependency and cannot be completed by writing code or synthesizing plausible measurements.

The field campaign plan is data/field_validation/campaign_plan.json; the protocol schema is science/field_validation_protocol.json; the browser capture tool is the Field Validation Kit. The plan defines candidate station types and property-specific observations for:

1. **Chagai small salt playas:** playa-margin, transect and (only if permitted and safe) interior observations; crust and sediment texture, georeferenced photographs and environmental conditions. No resource-volume or brine claims.
2. **Hamun-i-Mashkel / Kharan Basin:** basin margin, playa surface and ephemeral channel/fan transitions; direct observations are separated from regional hydrological inference.
3. **Koh-i-Sultan:** expert-led descriptions of accessible mapped volcanic exposures and contacts. Mapped context includes tuff, agglomerate and andesitic lava; no assumed basaltic match.
4. **Hispar Glacier:** high-hazard professional glacier-team-only work, starting from safe proximal viewpoints. No glacier-surface access without a specific specialist hazard and rescue plan.

### Field evidence gate

Before any field visit: obtain land access and protected-area/environmental permissions, local security and travel clearance, current weather and hazard review, a named field lead and emergency plan, and documented instrument checks. Every observation must record WGS84 coordinates and accuracy, UTC date, observers, photo/sample identifiers, instrument IDs and calibration, method/units, uncertainty, non-observations, access/permit and safety context. Independent review needs an identified reviewer, date and review scope.

The Field Validation Kit stores data in the browser's local storage and exports JSON/CSV; it does not upload to GitHub or any server. The exported records must be reviewed and added to the repository ledger through a controlled commit. A field observation validates only the sampled property at the sampled location. It does not certify planetary equivalence, ice access, resource abundance, landing safety or rover traversability.

## 4. Data depth and evidence states

The versioned data/source_registry.json is the canonical register. Its states mean:

| State | What it means |
|---|---|
| processed | Source arrays/data were retrieved or decoded and an analysis artifact was generated |
| browse_only | Visual reconnaissance preview, not calibrated quantitative science |
| metadata_only | Catalogue/collection/granule records found; source science arrays not downloaded and decoded |
| reference_only | Published/institutional context linked, not ingested as a machine-readable layer |
| partially_processed | Some target records were processed, with explicit remaining failures or gaps |
| planned | Workflow/plan exists, but no verified product has been built |
| unavailable | Attempted source could not be retrieved or decoded |
| field_observed_unreviewed | Actual field entry exists but has not passed independent review |
| independently_reviewed | A named reviewer accepted the evidence for a stated scope |

Concrete distinctions:
- Sentinel-2 RGB quicklooks remain browse_only; visual previews are not substitutes for calibrated multispectral arrays.
- NASA CMR MODIS/MERRA records remain metadata_only until the underlying granule science files are acquired and decoded.
- NASA EPIC remains browse_only for global visual context.
- NASA POWER climatology, DEM-derived terrain metrics, LOLA/MOLA terrain products and Diviner PRP summaries have processed outputs, each with their own resolution, product semantics and known limitations.
- A link, STAC item or catalogue record does not upgrade a source to processed.

## 5. Scientific reproducibility

The build workflow runs scripts/build_reproducibility_manifest.py and writes data/provenance/reproducibility_manifest.json. It inventories and SHA-256 hashes committed repository science inputs, generated outputs, scripts, tests, workflows and documentation; records source-register context, repository commit before the manifest commit, UTC build timestamp, Python version and selected runtime package versions.

The manifest makes repository artifacts traceable at byte level. It does not prove scientific validity, independently authenticate third-party assets, or reconstruct missing historical acquisition metadata. For each source-backed product, reviewers should also inspect provider, collection/product, DOI or catalogue item/granule IDs and exact asset URLs; retrieval timestamp and data period; script path and commit, package versions and processing parameters; CRS, units, resampling, masks and valid-data thresholds; input/output hashes, coverage, failure counts and tests; licence, missingness and scientific limitations.

The quantitative report includes the manifest hash and record count where available. The manifest cannot hash its own final committed bytes because its commit ID refers to the commit preceding the manifest write.

## 6. Competitor capability translation

ANALOG-X has now translated competitor strengths into concrete, separately evidenced capabilities:
- broad candidate discovery → global GLO-90 land-tile scan and bounded downloadable Moon/Mars shortlists;
- greater data breadth → separate global DEM, land-cover, climatology and GLiM context plus the regional NASA/ESA products;
- terrain/environment scanning → multiple declared terrain feature families, spatial sampling, candidate provenance and transparent sensitivity diagnostics;
- field evidence workflow → permission-gated Pakistan campaign plan and station capture/validation kit.

The competitor comparison with source-linked reported claims is in docs/COMPETITIVE_CAPABILITY_RESPONSE.md. The competitors' reported counts and scores are their own published claims and are not independently audited by ANALOG-X.

## Release language

- Say **global terrain scan complete** only for a build with all enumerated public land tiles processed and zero tile failures.
- Say **topographic screening candidate**, not confirmed analog, when referring to a ranked window.
- Say **second-source terrain cross-check** for NASADEM, not ground truth.
- Say **GLiM generalized lithology context** for the map lookup, not field-verified geology.
- Say **field validated** only for a specific measured property/location after documented observation and independent review.
- Always preserve the explicit state for browse-only imagery and metadata-only catalogue records.

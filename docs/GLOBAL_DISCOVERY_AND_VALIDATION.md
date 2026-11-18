# Global Discovery, Quantitative Validation & Field Evidence

## Purpose

This work package addresses the five remaining scientific maturity gaps in ANALOG-X. It separates implemented capabilities from planned expansion and from evidence that does not yet exist. A roadmap item is not reported as a completed result.

## 1. Global discovery

### Current implemented scope

The reproducible regional scan in `science/build_regional_window_scan.py` subdivides ten curated Earth parent DEM regions into 5.55 km windows. The 18 November 2026 build reports 7,290 valid Earth windows. It is a regional sample, not a global Earth scan. Candidate coordinates are approximate locators derived from nominal raster spacing.

### Expansion architecture

A genuine global scan must be built from a defined, versioned global input grid rather than extrapolating from the ten seeds. The next global release must:

1. Define a global AOI tiling scheme, land/ice mask policy, projection strategy and minimum valid-data threshold.
2. Discover and record DEM assets by AOI using a documented STAC/catalogue query; retain collection, item ID, asset URL, acquisition/production date, licence and checksum.
3. Download and process only assets whose access and reuse terms permit it. Record failed, unavailable and cloud/coverage-limited tiles.
4. Derive terrain descriptors at declared native and common support; never silently upsample coarse planetary data and call it higher resolution.
5. De-duplicate overlapping candidate windows and cluster adjacent windows into candidate areas.
6. Keep planetary reference targets separate (Moon and Mars) and preserve target-specific feature gaps.
7. Publish AOI coverage, valid-cell coverage, processed/failed tile counts, spatial sampling bias and exclusions alongside every shortlist.

**Status:** global coverage is not yet implemented. The current 7,290-window regional scan must not be described as global.

## 2. Quantitative validation

### Implemented baseline

The current scan computes median slope, P90 slope and P90 3×3 local relief from matched-support regional terrain grids. Its displayed terrain index uses feature gaps normalized by the Earth-window IQR; it also runs 500 deterministic weight-sensitivity draws. The index is exploratory, not calibrated probability, accuracy or geological equivalence.

### Validation additions required for a defensible release

- Add independent terrain descriptors only where source resolution and semantics support them (e.g. elevation distribution within each local reference frame, slope fractions, roughness at stated support).
- Compare candidate ordering against independent reference labels or expert-reviewed site dossiers. Do not use the same inputs both to create and validate a ranking.
- Report per-feature raw units, normalized gap, missingness, sample count and support scale.
- Test ranking sensitivity to feature selection, normalization, spatial resolution, missing-data thresholds and target-window selection.
- Use spatially blocked validation; overlapping windows are not independent samples.
- Report bootstrap or other uncertainty only when the sampling design supports it. Weight perturbation alone is sensitivity, not confidence.
- Include negative controls and known non-analog examples where defensible labels exist.

**Status:** existing terrain comparison and weight sensitivity are implemented; independent validation labels and calibrated performance estimates are not established.

## 3. Pakistan field validation

The Pakistan playa and volcanic study areas are candidate leads/reference cases, not field-validated planetary analogs. Ground-truth collection must be explicit and permission-led.

Use `science/field_validation_protocol.json` as the structured station template. The browser-based [Field Validation Kit](../field-validation.html) can capture planned stations and real observations, store drafts locally, and export station records as JSON/CSV. The browser kit does not upload observations; exported evidence must be reviewed and added to the repository ledger through a controlled commit. Each field station should record:
- WGS84 coordinates, coordinate method and accuracy;
- UTC time, observer, instrument identifiers and calibration;
- georeferenced photographs with bearing and station IDs;
- observed geomorphology, lithology, rock/soil description and sampling method;
- surface and air temperature, humidity, wind and pressure where relevant;
- sample IDs and chain of custody;
- access, safety, non-observation and uncertainty notes;
- independent reviewer and review status.

Do not schedule fieldwork without land-access permission, protected-area review, local safety planning and appropriate institutional/field expertise. Field evidence validates only the measured property at the sampled location. It does not establish Moon/Mars equivalence, mineral/resource abundance, accessible ice, landing safety or rover traversability.

**Status:** field-validation protocol/template added; no new field observations are claimed by this repository change.

## 4. Data depth and evidence classes

Every displayed dataset must be assigned one of these explicit states:

| State | Meaning |
|---|---|
| processed | Source data downloaded/decoded and analysis output generated |
| browse_only | Visual preview for reconnaissance; not calibrated quantitative science |
| metadata_only | Catalogue/collection/granule discovery; underlying science arrays not processed |
| reference_only | Institutional or literature context; not ingested as machine-readable data |
| planned | Intended future integration; not currently available |
| unavailable | Access failed or product could not be retrieved |
| field_observed_unreviewed | Raw field observation exists but has not passed independent review |
| independently_reviewed | Evidence reviewed with reviewer, method and scope recorded |

Examples: Sentinel-2 RGB quicklooks are browse_only; NASA CMR records are metadata_only until science arrays are downloaded and processed; NASA POWER climatology and DEM-derived metrics have processed outputs with their own resolution/semantic limitations. Never upgrade a status because a link or catalogue record exists.

## 5. Reproducibility and provenance

Each generated product should retain:
- input file paths and SHA-256 hashes;
- source provider, collection/product identifier, item/granule IDs and source URLs;
- retrieval timestamp and data period;
- script path, repository commit and software/runtime versions;
- parameters, coordinate reference system, units, resampling and masking rules;
- output path/hash, row/cell counts and coverage;
- validation/test result and known limitations.

The script `scripts/build_reproducibility_manifest.py` generates a machine-readable manifest for repository science inputs and outputs. It records hashes and file metadata; it does not prove that a source is scientifically valid or that an external dataset is fully processed.

## Release gate

A candidate may be called **globally discovered** only when it comes from the documented global scan and its AOI/data coverage is traceable. It may be called **quantitatively validated** only when independent reference evidence and validation results are reported. It may be called **field validated** only for properties supported by documented observations and independent review. All other cases retain their lower evidence state.

## Current honest status

- Global scan: planned; regional scan implemented.
- Quantitative terrain screening and weight sensitivity: implemented; independent performance validation pending.
- Pakistan field evidence: protocol/template implemented; new ground observations pending.
- Data-depth labelling: documented; existing source-specific limitations remain in force.
- Reproducibility manifest: generator added; full historical provenance completeness depends on the metadata available for each source asset.

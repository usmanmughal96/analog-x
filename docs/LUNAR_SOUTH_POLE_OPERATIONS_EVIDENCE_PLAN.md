# Lunar South-Pole Operations Evidence Plan

**Scope:** ANALOG-X Shackleton Rim / Site04 evidence. This plan adds source QA and defines what is still needed for a mission-relevant operational assessment.

## Already integrated

- NASA GSFC PGDA LRO-LOLA product 78 Site04 at 5 m/pixel: elevation, LDEC return count and slope.
- NASA LRO LROC WAC 100 m time-weighted and percentage-based historical illumination layers.
- NASA Diviner PRP V2.0 model-derived temperature and water-ice stability-depth context.
- A separate 80 m LOLA polar elevation/support profile.

## Newly adopted uncertainty products

NASA PGDA product 78 publishes Site04 total elevation RMS-error and slope RMS-error GeoTIFFs alongside the DEM, count and slope products, as well as 100 DEM clones. ANALOG-X will ingest the two uncertainty rasters first, preserve their units and masks, and report distributions separately from the terrain measurements. The current 5 m build does not yet calculate clone-based illumination intervals; no illumination uncertainty should be implied until that analysis is implemented.

## Formal PSR and illumination sources

1. **LROC Permanently Shadowed Regions Atlas:** use the original PSR map, PSR record and source image/coverage metadata, not a 5% threshold applied to WAC frequency. Each PSR geometry must be intersected with the project AOI in the correct lunar coordinate system and linked to its atlas ID, pixel scale and coverage/quality metadata.
2. **NASA LROC WAC historical illumination:** retain current two integrated WAC products as historical screening evidence only. Do not label their 2010–2011 frequency as a 2026–2030 forecast.
3. **Mission-date illumination:** use a terrain-based Sun-vector/ephemeris simulation over the planned mission interval, with explicit latitude/longitude, reference frame, terrain resolution, observer height and time step. Compare modeled illumination with the LROC WAC historical product as a consistency check, not as interchangeable data.
4. **LOLA uncertainty ensemble:** use the published Site04 clones or propagate the supplied height/slope RMS error through an appropriate ensemble method. Report the spread in slope and illumination statistics. A per-pixel RMS layer alone is not a probability of safety.

## Rover-scale hazard and traverse requirements

A defensible rover assessment needs more than median/P90 slope and 15 m local relief. It should include:
- NAC-derived ~1 m or better terrain where coverage is available, plus shadowed-terrain support from LOLA.
- Boulders, craters, scarps, local roughness and hazard-detection probability.
- DEM vertical/slope uncertainty and interpolation/laser-return support.
- Rover-specific slope, step, sinkage, wheel/ground clearance and tilt constraints from a specified vehicle.
- Route continuity, turning radius, energy, communication geometry, illumination/thermal exposure, and contingency/escape routes.
- Independent review by lunar terrain and mobility engineers.

No generic slope cutoff should be translated into a rover-safe label without a named rover and operational design constraints.

## Release gates

- **Lunar terrain QA:** DEM, count, slope and both uncertainty rasters have identical CRS, transform and dimensions; masks and units are verified.
- **PSR evidence:** atlas polygon/map IDs and coverage/quality fields are traced; candidate PSRs are not inferred from thresholded WAC raster alone.
- **Illumination:** mission-date calculation has a pinned ephemeris, terrain version, time window and uncertainty method.
- **Mobility:** terrain hazards and route feasibility are evaluated against a specified vehicle, not a generic rover.
- **Interpretation:** all source layers remain separate; no combined habitability, resource, landing or safety score is published without a validated model and reviewer sign-off.

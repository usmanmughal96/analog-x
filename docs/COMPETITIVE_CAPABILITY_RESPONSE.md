# Competitive capability response: ANALOG-X

## Purpose

This note translates public challenge-entry patterns into independent ANALOG-X capabilities. It is a method comparison, not a claim that ANALOG-X has copied competitor software, datasets, or results.

## Capability mapping

| Public benchmark pattern | Capability translated into ANALOG-X | Implementation evidence | Remaining distinction |
|---|---|---|---|
| Earth's Moon Twins — broad Earth candidate discovery and a larger shortlist | Worldwide land-tile terrain screening, tile-aware candidate windows, global candidate shortlist and downloadable evidence records | `scripts/build_global_discovery.py`, `scripts/merge_global_discovery.py`, `global-discovery.html` | Global search is based on Copernicus GLO-90 terrain. It is not a global multi-sensor mineral/climate classification or a complete environmental analog model. A release is complete only when all public land inventory tiles are processed. |
| TwinWorlds — claimed wide data breadth and global quantitative coverage | Separate GLO-90 global terrain input, global 2023 10m land-cover enrichment for retained candidates, existing ten-region GLO-30/30m context, NASA POWER, Sentinel-2 spectral context, NASA CMR/PDS metadata discovery, Moon LOLA, Mars MOLA, Diviner polar thermal summaries, and NASADEM second-source checks where available | `data/source_registry.json`, `scripts/validate_nasadem_crosscheck.py`, `scripts/build_quantitative_validation.py` | The evidence registry deliberately distinguishes processed, browse-only, metadata-only and reference-only products. Global land-cover enrichment uses the 2023 10 m annual global classification product but is applied to the retained terrain shortlist only. Global terrain coverage does not mean every environmental variable is globally measured. |
| Earth Analog Explorer — terrain and environment candidate screening | Terrain feature families, local projected windows, slope fractions, roughness, relief, elevation spread, metric-family sensitivity, and target-specific Moon/Mars profiles | `scripts/build_global_discovery.py`, `science/build_regional_window_scan.py` | Copernicus GLO-90 is a DSM and terrain-only. It does not provide geology, mineralogy, soil strength, dust behaviour, trafficability or mission safety. |

## How the combined engine works

1. **Global inventory:** enumerate GLO-90 one-degree land COG tiles from the provider's public tile list.
2. **Distributed processing:** split the inventory into 24 longitude shards. Preserve assigned, processed, empty and failed tile counts.
3. **Metric surface:** resample each tile to a local metric grid at nominal ~925 m support and derive non-overlapping 6×6-cell windows.
4. **Two terrain metric families:** a core median-slope/P90-slope/P90-relief group and an alternative P95-slope/elevation-IQR/detrended-roughness group.
5. **Planet-specific comparison:** score each window against the selected Shackleton Rim and Nili Patera reference profiles separately.
6. **Shortlist and inspect:** retain spatially distributed windows, display the source tile, metrics, approximate centre and known interpretation limits, and export CSV/JSON.
7. **Second-source diagnostic:** where NASADEM is available, compare selected Earth region descriptors with the Copernicus regional profiles. Report the processed site count and descriptor differences rather than describing the result as ground truth.
8. **Field handoff:** convert candidates into structured field station plans and receive geotagged, instrumented observations in a separate field evidence ledger.

## Global environmental enrichment

The retained global terrain shortlist is additionally enriched from the Microsoft Planetary Computer `io-lulc-annual-v02` collection for 2023. The source is a global annual 10 m land-cover classification derived from Sentinel-2 imagery; it reports nine classes (water, trees, flooded vegetation, crops, built area, bare ground, snow/ice, clouds and rangeland). For each shortlisted window, intersecting COGs are sampled into a local 30 m grid using modal class aggregation. The output records valid-pixel coverage, class fractions and exact STAC item IDs. This is applied to the bounded shortlist, not every terrain window in the full world scan. The producer reports assessed average accuracy above 75%; class- and region-specific performance varies. Land cover is environmental context, not lithology, soil chemistry, mineralogy or field validation. The product is available under CC BY 4.0.

A second global environmental layer samples NASA POWER climatology at the top 100 retained terrain candidates per target, deduplicated by window. It records annual/monthly 2 m air temperature, relative humidity, 10 m wind speed, corrected precipitation and all-sky shortwave radiation, plus the three driest climatology months. This is point-based access to gridded climatology, not a full global climate grid or local field-station observation.

## Scoring and validation language

The two metric-family indices use the median profile of each planetary reference window collection and IQR scales derived from the selected ten-region Earth reference data pack. The consensus index is the mean of the two indices. Metric-family agreement is a robustness diagnostic against feature choice, not independent-data validation. NASADEM cross-checks are an independent elevation-source diagnostic only where a second source successfully processes; they are not in-situ truth. Physical field validation requires observations, sample/photo provenance, calibration and independent review.

## Public data facts and source limits

- Copernicus GLO-90 offers worldwide 90 m coverage in the public COG bucket; ocean areas do not have elevation tiles.
- The publicly available GLO-30 bucket has limited worldwide coverage because some tiles are not publicly released. ANALOG-X therefore keeps its selected local GLO-30 studies separate from the GLO-90 global scan.
- Copernicus DEM is a digital surface model, including vegetation, buildings and infrastructure. It is not a bare-earth model.
- NASADEM is based on SRTM with auxiliary void filling; its approximate coverage is 56°S–60°N. It does not cover all high-latitude sites.

## Release gate

ANALOG-X may only report "global scan complete" when the merge product records all expected inventory tiles as assigned and processed, with zero tile failures. A partial run reports its actual coverage. No dataset is treated as processed merely because a catalogue record, URL or preview exists. A candidate is not called field validated without complete field evidence and independent review.

## Sources

- Copernicus DEM AWS open-data registry: https://registry.opendata.aws/copernicus-dem/
- Copernicus DEM bucket/readme and tile inventory: https://copernicus-dem-90m.s3.amazonaws.com/readme.html
- Copernicus DEM GLO-90 tile list: https://copernicus-dem-90m.s3.amazonaws.com/tileList.txt
- NASADEM dataset: https://data.nasa.gov/dataset/nasadem-srtm-image-mosaic-global-1-arc-second-v001

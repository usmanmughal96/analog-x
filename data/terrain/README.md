# Matched-scale Earth–Mars terrain descriptors

The terrain comparison pipeline uses Copernicus DEM GLO-30 DSM for up to ten curated Earth analog/reference sites and MOLA MEGDR 64 px/degree topography/counts around Nili Patera in Syrtis Major. The Earth DSM is aggregated to approximately the MOLA pixel scale for the common-support Earth/Mars terrain profile. A separate ~30 m Earth-only terrain diagnostic is also calculated before downsampling to preserve higher-detail slope and 3x3 local-relief context. The 30 m diagnostic is not compared directly with Moon/Mars values and is not rover-scale. The common-support comparison remains coarse and is not geological equivalence, rover traversability or landing safety.

See terrain_comparison.json for values, spatial support, data provenance and limitations. Raw MOLA files are not committed.

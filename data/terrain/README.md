# Matched-scale Earth–Mars terrain descriptors

The terrain comparison pipeline uses Copernicus DEM GLO-30 DSM for the Pakistan sites and MOLA MEGDR 64 px/degree topography/counts around Nili Patera in Syrtis Major. The Earth DSM is aggregated to approximately the MOLA pixel scale before slope and 3x3 local-relief descriptors are computed for all candidate AOIs with tiles in the refreshed Copernicus STAC catalogue. This is a coarse terrain-profile comparison, not geological equivalence, rover traversability or landing safety.

See terrain_comparison.json for values, spatial support, data provenance and limitations. Raw MOLA files are not committed.

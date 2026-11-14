# Scientific and Operational Limitations

## Terrain comparison
- The Earth–Mars terrain product is a local profile comparison, not a geological-equivalence score, landing suitability assessment or rover traversability certification.
- Earth uses Copernicus DEM GLO-30 DSM aggregated to about 925 m. This is a digital surface model, not bare-earth elevation.
- Mars uses MOLA MEGDR 64 pixels/degree around Nili Patera. Current observation coverage is only 50.53% (567 of 1,122 cells), with 87 complete 3×3 neighborhoods for terrain derivatives.
- The MOLA coverage limitation means Nili Patera descriptors are provisional and should be checked against another Mars DEM/product before any strong inference.
- Absolute elevation is not compared between the Copernicus Earth DSM and Mars areoid/topography vertical references.
- A roughly 925 m grid and approximately 2.8 km 3×3 local-relief footprint are too coarse for rover-scale hazards, wheel traction or field-scale obstacle assessment.
- The 30 km windows sample only the selected local areas, not the full Syrtis Major region or the whole Pakistan geological province.

## Earth observation
- Sentinel-2 true-colour previews support visual reconnaissance only. RGB imagery does not establish lithology, mineralogy, geochemistry, or in-situ sample properties.
- Scene-level cloud percentage is not a pixel-level cloud mask for the exact area of interest.
- Copernicus DEM is a DSM and can include vegetation, structures, snow/ice surface and other surface objects.
- Field mapping, georeferenced photos, rock/soil descriptions and independent geological review remain necessary.

## Climate
- NASA POWER is gridded climatology, not local field-station observations.
- T2M is 2-m air temperature, not surface or rock temperature.
- WS10M is not friction velocity, dust emission or dust deposition.
- PRECTOTCORR is precipitation, not water/ice resource abundance.
- ALLSKY_SFC_SW_DWN is Earth's weather-affected solar resource, not lunar illumination.
- NASA POWER climate data do not classify geology, mineralogy, terrain roughness, caves, ice or subsurface resources.

## Planetary transferability
- No Earth site reproduces lunar vacuum, reduced gravity, radiation or permanently shadowed-region conditions.
- Earth cannot reproduce the thin CO₂ Martian atmosphere, Martian dust electrostatics or reduced gravity.
- An Earth glacier is not a lunar permanently shadowed region and is not a substitute for Diviner/LOLA analysis.
- Raw lunar LOLA and Diviner rasters are not processed in this release.

## Institutional data
- EvK2CNR's Pakistan Glacier Inventory and glacial-lake work already exist; ANALOG-X does not claim their discovery or national remapping.
- NDMA, SUPARCO/DisasterWatch, NatCat and Space4Climate are recognized as existing institutional capabilities. No public bulk API/reuse licence is claimed for those data products.
- Local permits, protected-area rules, land access, safe field conditions and independent verification must be checked before real fieldwork.

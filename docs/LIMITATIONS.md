# Scientific and Operational Limitations

## Terrain comparison
- The Earth–Mars terrain product is a local profile comparison, not a geological-equivalence score, landing suitability assessment or rover traversability certification.
- Earth uses Copernicus DEM GLO-30 DSM aggregated to about 925 m. This is a digital surface model, not bare-earth elevation.
- Mars uses MOLA MEGDR 64 pixels/degree around Nili Patera. Current observation coverage is only 50.53% (567 of 1,122 cells), with 87 complete 3×3 neighborhoods for terrain derivatives.
- The MOLA coverage limitation means Nili Patera descriptors are provisional and should be checked against another Mars DEM/product before any strong inference.
- Absolute elevation is not compared between the Copernicus Earth DSM and Mars areoid/topography vertical references.
- A roughly 925 m grid and approximately 2.8 km 3×3 local-relief footprint are too coarse for rover-scale hazards, wheel traction or field-scale obstacle assessment.
- The 30 km windows sample only the selected local areas, not the full Syrtis Major region or the whole Pakistan geological province.
- A separate University of Arizona HiRISE stereo DTM for moving dunes at Nili Patera is catalogued at 1.01 m/pixel. A capped read of its embedded PDS label confirms that its geographic bounding box does not intersect the existing MOLA comparison AOI: the DTM begins east of the AOI's eastern boundary. It is an adjacent high-resolution reference, not a replacement or co-located extension of the current MOLA profile. The approximately 430 MB raster has not been downloaded or processed.

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
- Lunar LOLA 80 m GDR terrain is integrated for a 29.6 km Shackleton Rim window; the LDEM is interpolated and LDEC counts are separate observational support. LOLA alone does not provide illumination, PSR geometry or water-ice resource measurements.
- Separate 100 m LROC WAC historical illumination-frequency layers and Diviner PRP V2.0 model-derived thermal / ice-stability-depth summaries are processed for the Shackleton window. WAC data represent 2010–2011 observations, not mission-date forecasts; the ≤5% illumination threshold is a screening proxy, not a formal PSR boundary.
- Diviner PRP V2.0 covers 6,823 Shackleton-window triangles. Median annual-average temperature at 2 cm is 103.786 K and median annual-maximum surface temperature is 238.568 K. Ice-stability-depth QA remains limited: 2,812 valid values, 2,514 values censored beyond 2.8738 m and 1,497 invalid or unreadable records. These model-derived values do not establish ice abundance, concentration, thickness, purity, accessibility or reserves.
- The Shackleton coarse profile at 925 m has median/P90 slope 13.40°/30.94° and P90 local relief 1,391 m; the selected window is rugged and does not demonstrate a suitable base area.

## Institutional data
- EvK2CNR's Pakistan Glacier Inventory and glacial-lake work already exist; ANALOG-X does not claim their discovery or national remapping.
- NDMA, SUPARCO/DisasterWatch, NatCat and Space4Climate are recognized as existing institutional capabilities. No public bulk API/reuse licence is claimed for those data products.
- Local permits, protected-area rules, land access, safe field conditions and independent verification must be checked before real fieldwork.

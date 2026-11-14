# NASA Space Apps Project Submission — ANALOG-X

## Project title
ANALOG-X — Pakistan Analog Evidence Operations Atlas

## One-line summary
A Pakistan-first planetary analog evidence console that combines NASA climate snapshots, Sentinel-2 imagery, Copernicus DEM and Mars MOLA terrain descriptors, and institutional baselines to characterize candidate Earth field environments and expose what still needs validation before calling them useful Moon/Mars analogs.

## Project description
The 2026 challenge asks teams to use open Earth, Moon and Mars data from NASA and other space agencies to identify and characterize new terrestrial analogs for future bases or landing sites. Existing candidate environments are not all fully characterized. ANALOG-X responds by focusing on evidence readiness for two contrasting Pakistan case studies rather than presenting another universal similarity leaderboard.

The first study area is Koh-i-Sultan in Chagai, a Smithsonian-catalogued volcanic-field candidate. NASA POWER climatology is fetched for this coordinate and Sentinel-2 L2A scenes are discovered through Microsoft Planetary Computer. A true-colour scene preview is clipped to the study bounding box. Copernicus DEM GLO-30 DSM is processed over an approximately 30 km window and aggregated to about 925 m terrain support. The intended field workflow is volcanic outcrop reconnaissance, sample-context logging and satellite-to-ground validation. The product does not claim that Koh-i-Sultan is compositionally equivalent to Syrtis Major or a validated Mars analog.

The second study area is the Hispar Glacier/Karakoram region. NASA POWER data, Sentinel-2 L2A scene discovery/preview and Copernicus DEM terrain descriptors support a cryosphere image-interpretation and field-validation case study. EvK2CNR has already published a Pakistan glacier inventory of 13,032 glaciers covering 13,546.93 km² and a preliminary glacial-lake inventory. ANALOG-X credits this baseline rather than claiming to discover or remap Pakistan's glaciers.

For a Mars reference, the project processes MGS MOLA MEGDR 64 pixels/degree topography and observation counts around Nili Patera in the Syrtis Major quadrangle. It compares coarse slope and local-relief descriptors with the Earth DSM windows at approximately 925 m support. The selected Nili Patera window has 50.53% valid MOLA observed-cell coverage (567 of 1,122 cells) and 87 complete 3×3 neighborhoods. This limitation is displayed in the application and constrains interpretation. The comparison is a terrain profile, not a geological-equivalence, landing-safety or rover-mobility score.

The public console shows actual NASA POWER snapshots for eight locations; actual Sentinel-2 scene IDs, capture dates, MGRS tiles and true-colour previews for the two Pakistan study areas; a NASA EPIC full-disc Earth context image; Copernicus DSM and MOLA-derived terrain descriptors; official sources and explicit data integration states. It separates integrated data from metadata-only discovery, portals reviewed and planetary datasets that are linked but not yet processed.

## Project URL
https://usmanmughal96.github.io/analog-x/

## Demo URL
https://usmanmughal96.github.io/analog-x/demo.html

## Source repository
https://github.com/usmanmughal96/analog-x

## Data and methods
NASA POWER Climatology API (RE community) is queried server-side by a reproducible GitHub Actions pipeline for T2M, T2M_MAX, T2M_MIN, RH2M, WS10M, PRECTOTCORR and ALLSKY_SFC_SW_DWN. Original responses, monthly values, metrics, timestamps and source request URLs are committed as JSON. Eight site records are currently present.

Microsoft Planetary Computer's public STAC API is queried for Sentinel-2 L2A and Copernicus DEM GLO-30 products over Koh-i-Sultan and Hispar. Sentinel-2 COG assets are clipped into true-colour previews; Copernicus DSM tiles are mosaicked, reprojected and averaged to approximately 925 m. The MOLA 64 ppd topography and counts products are read using their separate PDS sample formats; cells with zero counts are excluded from reported terrain derivatives.

NASA DSCOVR/EPIC provides optional global Earth imagery via the public GSFC endpoint. It is not used for site-level analysis.

## Existing institutional work
SUPARCO, UN-SPIDER and NDMA already operate important disaster/remote-sensing systems and practices. EvK2CNR already published Pakistan glacier and glacial-lake inventory work. ANALOG-X does not seek to replace them. It links their work as baselines and records which products can be accessed and integrated under open-data terms. No public DisasterWatch or Space4Climate machine-readable data API is claimed in this release.

## Science integrity and limitations
No raw lunar LOLA or Diviner raster comparison is claimed in the current build. No geology or mineralogy is inferred from Sentinel-2 RGB images. No universal planetary similarity score is reported. Nili Patera MOLA observation coverage is limited, and the comparison is not rover-scale or a safety assessment. Local permits, field access, geology mapping and on-site measurements remain necessary. See docs/DATA_SOURCES.md, docs/AGENCY_DATA_AUDIT.md, docs/METHODOLOGY.md and docs/LIMITATIONS.md.

## AI-use disclosure
See docs/AI_DISCLOSURE.md. AI assistance was used for brainstorming, code support, documentation and presentation preparation. The team remains responsible for reviewing and validating scientific content.

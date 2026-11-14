# ANALOG-X: problem statement and differentiation

## Challenge-aligned problem statement

Planetary analog field campaigns need more than a list of visually similar landscapes. Before a team can use a terrestrial site to rehearse a specific lunar/Martian science or operations task, it needs to know whether the site is characterized by compatible, traceable evidence across imagery, terrain, climate and geology—and which critical measurements are still missing or incompatible in scale.

**ANALOG-X addresses the evidence-readiness gap:** it assembles open Earth-observation and environmental records for under-characterized candidate locations, links them to planetary reference products, records spatial/temporal support and provenance, and converts evidence gaps into a targeted field-validation plan. It deliberately does not turn unrelated data layers into an unvalidated single planetary-similarity percentage.

## Current Pakistan case studies

### Koh-i-Sultan / Chagai
A candidate volcanic field for rehearsing exposed volcanic-terrain reconnaissance, outcrop-context logging and remote-sensing-to-ground validation. The Smithsonian catalogue identifies Sultan as a volcanic field; its catalogue point is not a surveyed field boundary. Chagai regional geology and Sentinel-2 imagery provide context. No claim is made that its lithology matches Syrtis Major basalt or that it is a validated Mars analog.

### Hispar Glacier / Karakoram
A cryosphere field-operations case study for image interpretation, ice/debris boundary mapping and field-data validation. EvK2CNR already published a Pakistan-wide glacier inventory from Sentinel-2-based mapping (13,032 glaciers; 13,546.93 km²) and documents multitemporal change work and field validation. ANALOG-X therefore does not claim to discover or remap Pakistan's glaciers. It uses an existing institutional baseline and exposes what is and is not transferable to lunar polar exploration. An Earth glacier does not reproduce lunar permanently shadowed-region conditions, vacuum, reduced gravity or illumination cycles.

These two cases are contrasting test environments and should not be described as one universal analog.

## Why not simply build another site-ranking dashboard?

Public 2026 challenge submissions already include:
- ODYSSEY: mission-brief-to-experiments, Earth-site ranking and explicit breakdown of analog limitations.
- Earth Analog Explorer: topography-based terrain match, low-sun share, bare-ground share and top-3 rank stability for a fixed set of candidates.

ANALOG-X should not copy their core features or claim that no one has built a multi-source analog tool. Its differentiating contribution is a Pakistan-first, evidence-provenance and data-gap workflow that links:
- actual NASA POWER climatology records;
- Microsoft Planetary Computer Sentinel-2 L2A STAC results and clipped visual previews;
- EvK2CNR's existing glacier-inventory evidence;
- relevant NASA planetary product references;
- NDMA / SUPARCO / UN-SPIDER / Space4Climate workflow and portal status; and
- site-specific field validation tasks.

The product should report per-layer availability, units, resolution, date, source licence and evidence class. It should not create a composite analog score until Earth and planetary measurements have been harmonized to compatible spatial and temporal support and scientifically justified.

## What remains to prove

1. Validate Sentinel-2 quicklooks and spectral-index computations against scene-classification/cloud masks.
2. Add a defensible Earth DEM and quantify slope/roughness using verified site-scale tiles.
3. Retrieve and process the relevant Mars MOLA product and lunar LOLA/Diviner products; state their spatial support and limitations.
4. Add a primary-source geology map or field observations for Koh-i-Sultan before making mineralogical claims.
5. Confirm whether NDMA, Space4Climate, SACCS/SUPARCO and EvK2CNR expose downloadable data and reuse terms beyond their portal pages.
6. Have a geologist or planetary scientist review the selected experiments and transferability statements.

## Status vocabulary

- Integrated: data downloaded/queried, parsed, validated and referenced in the public build.
- Metadata discovered: catalogue or STAC metadata returned; scientific raster analysis may still be pending.
- Portal reviewed: official portal/page checked; no usable open API or redistributable data product is yet verified.
- Reference only: official data/product linked but not ingested or processed.
- Field validation required: remote sensing cannot establish the site-scale geological/operational claim alone.

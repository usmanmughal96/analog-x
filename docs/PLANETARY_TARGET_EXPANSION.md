# Planetary Target Expansion Registry

ANALOG-X currently has two data-backed target profiles in its global terrain-ranking pipeline: Shackleton Rim (LOLA) and Nili Patera (MOLA). A target registry now separates those active profiles from a curated ingestion queue.

## Lunar south-pole expansion

The registry includes NASA's updated 2024 Artemis III candidate-region set: Peak near Cabeus B, Haworth, Malapert Massif, Mons Mouton Plateau, Mons Mouton, Nobile Rim 1, Nobile Rim 2, de Gerlache Rim 2 and Slater Plain. NASA describes these as candidate regions assessed using science value, mission availability, terrain, communication and illumination constraints. They are not final landing-site selections and are not all represented by a local terrain profile in ANALOG-X.

Official source: https://www.nasa.gov/news-release/nasa-provides-update-on-artemis-iii-moon-landing-regions/

## Mars expansion queue

The registry also tracks Jezero Crater, Gale Crater, Eberswalde Crater, Mawrth Vallis, Arcadia Planitia and Valles Marineris as distinct research environments. These are target candidates for future ingestion, not active scored targets. The research context is a selection aid only; the exact mission question, region polygon and MOLA/HiRISE/CTX evidence must be curated before activation.

MOLA archive and product access: https://pds-geosciences.wustl.edu/missions/mgs/mola.html

## Activation gate

Each new target requires its own authoritative planetary DEM product and version, coordinate reference, region-of-interest geometry, valid-data mask, coverage report, terrain descriptors, source/quality checks and reproducibility hashes. A single median profile for Nili Patera or Shackleton must never be silently reused as the reference for a different crater, valley, plateau or landing region.

Current status is intentionally explicit: two active profiles; nine planned Artemis III lunar regions; six planned Mars environments. The global discovery engine continues to score only the two active profiles until the ingestion and validation gates are met.

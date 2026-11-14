# ANALOG-X

**Mission-Specific Planetary Analog Reconnaissance**  
NASA Space Apps Challenge 2026 · Team **X Æ A-Xii** · Participant: **Muhammad Usman Mughal**

## Public project links
- Project landing page: https://usmanmughal96.github.io/analog-x/
- Seven-slide browser demo: https://usmanmughal96.github.io/analog-x/demo.html
- Source repository: https://github.com/usmanmughal96/analog-x

> These Pages URLs are expected deployment addresses. Confirm that the GitHub Actions deployment has succeeded before using them in the NASA submission.

## Research question
Which aspects of the Koh-i-Sultan volcanic field in Chagai, Pakistan, may inform field-geology methods and robotic geological reconnaissance workflows for Martian volcanic terrain represented by the Syrtis Major MC-13 quadrangle?

## Scientific integrity
This is a source-grounded reconnaissance prototype, not a claim that Chagai is a complete Mars analog. It does not display a single planetary-equivalence percentage. Raw MOLA and NASADEM/SRTM rasters have not yet been processed in this public build; therefore no terrain statistics or numerical analog score are claimed. NASA GIBS is a visual browse service only. SUPARCO Space4Climate is a potential data source; no Chagai-specific product has been verified or ingested.

## Repository structure
- `index.html` — public project landing page.
- `demo.html` — seven-slide browser presentation; use arrow keys or Previous/Next.
- `docs/` — methodology, data provenance, limitations, AI-use disclosure, NASA submission copy and SUPARCO request draft.
- `science/` — reproducible MOLA and projected-DEM processing scripts.
- `app/` — app entry redirect.
- `presentation/` and `reports/` — pointers to PDF/PPTX deliverables in the complete submission package.

## Run the science scripts
Install dependencies:

```bash
pip install -r science/requirements.txt
```

From repository root:

```bash
python science/analyze_mola.py --out outputs/mola_syrtis_summary.json
python science/dem_metrics.py /path/to/projected_dem.tif --out outputs/koh_i_sultan_dem_metrics.json
```

The Earth DEM must have a verified projected CRS in metres. Do not compare fine Earth DEM statistics directly with coarse MOLA 4 px/degree data. See `docs/METHODOLOGY.md` and `docs/LIMITATIONS.md`.

## Data sources
NASA GIBS, NASA MOLA, NASADEM/SRTM, USGS Chagai regional geology, USGS Syrtis Major MC-13, Smithsonian Global Volcanism Program and SUPARCO Space4Climate. Dataset status and limitations are recorded in `docs/DATA_SOURCES.md`.

## AI-use disclosure
See `docs/AI_DISCLOSURE.md`. The team discloses AI-assisted brainstorming and development support. AI output is not treated as scientific evidence; claims and data must be independently validated.

## Licence
Original project code and text are MIT-licensed. Third-party datasets, maps and imagery retain their own provider terms.

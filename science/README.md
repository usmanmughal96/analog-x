# Scientific processing

Install dependencies with `pip install -r science/requirements.txt`.

From repository root, run:

```bash
python science/analyze_mola.py --out outputs/mola_syrtis_summary.json
python science/dem_metrics.py /path/to/projected_dem.tif --out outputs/koh_i_sultan_dem_metrics.json
```

The DEM must be projected in metres. Do not compare fine Earth DEM statistics directly with coarse MOLA 4 px/degree. See ../docs/METHODOLOGY.md and ../docs/LIMITATIONS.md.

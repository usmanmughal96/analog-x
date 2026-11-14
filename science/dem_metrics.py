#!/usr/bin/env python3
"""Compute transparent terrain descriptors from a projected metric GeoTIFF DEM."""
from __future__ import annotations
import argparse, json
from pathlib import Path
import numpy as np
import rasterio
from rasterio.warp import calculate_default_transform, reproject, Resampling
from scipy.ndimage import maximum_filter, minimum_filter

def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("raster", help="Input projected GeoTIFF DEM")
    p.add_argument("--out", default="outputs/dem_metrics.json")
    p.add_argument("--target-resolution-m", type=float, default=None)
    args = p.parse_args()
    path = Path(args.raster)
    with rasterio.open(path) as ds:
        if ds.count < 1: raise SystemExit("Raster contains no bands")
        arr = ds.read(1, masked=True).astype("float64")
        crs = ds.crs
        if crs is None: raise SystemExit("Input DEM has no CRS; assign/verify the correct CRS first")
        if args.target_resolution_m:
            if not crs.is_projected: raise SystemExit("Reproject to a metric CRS before resampling.")
            transform, width, height = calculate_default_transform(crs, crs, ds.width, ds.height, *ds.bounds, resolution=args.target_resolution_m)
            dest = np.full((height, width), np.nan, dtype="float64")
            reproject(source=arr.filled(np.nan), destination=dest, src_transform=ds.transform, src_crs=crs, dst_transform=transform, dst_crs=crs, resampling=Resampling.average)
            arr = np.ma.masked_invalid(dest); pixel_x, pixel_y = abs(transform.a), abs(transform.e)
        else: pixel_x, pixel_y = abs(ds.transform.a), abs(ds.transform.e)
        values = arr.compressed()
        if values.size < 9: raise SystemExit("Not enough valid cells")
        if not crs.is_projected: raise SystemExit("Slope calculation requires projected CRS in metres.")
        if (crs.linear_units or "").lower() not in {"metre","metres","meter","meters"}:
            raise SystemExit(f"Projected CRS units are {crs.linear_units!r}; use metres.")
        z = arr.filled(np.nan); gy, gx = np.gradient(z, pixel_y, pixel_x)
        slope = np.degrees(np.arctan(np.sqrt(gx*gx + gy*gy))); slope = slope[np.isfinite(slope)]
        valid = np.isfinite(z); zfill = np.where(valid, z, np.nanmedian(values))
        relief = maximum_filter(zfill, size=3) - minimum_filter(zfill, size=3); relief = relief[valid]
    result = {"input":str(path),"crs":str(crs),"pixel_size_crs_units":[float(pixel_x),float(pixel_y)],"valid_cells":int(values.size),
      "elevation_m":{"p10":float(np.percentile(values,10)),"median":float(np.median(values)),"p90":float(np.percentile(values,90))},
      "slope_deg":{"median":float(np.median(slope)),"p90":float(np.percentile(slope,90)),"p95":float(np.percentile(slope,95))},
      "3x3_local_relief_m":{"median":float(np.median(relief)),"p90":float(np.percentile(relief,90))},
      "method_note":"Descriptors depend on projection, resolution, resampling and valid-data mask. Do not compare with MOLA 4 px/degree unless Earth DEM is aggregated to comparable support. Not rover hazard certification."}
    out=Path(args.out); out.parent.mkdir(parents=True,exist_ok=True); out.write_text(json.dumps(result,indent=2)); print(json.dumps(result,indent=2))
if __name__=="__main__": main()

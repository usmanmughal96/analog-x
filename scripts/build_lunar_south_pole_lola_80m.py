#!/usr/bin/env python3
"""Process MIT-hosted NASA LRO LOLA south-polar 80 m DEM and count JP2s.

The JP2 labels define a polar stereographic grid (Moon ME, DE421). The LDEM is
an interpolated surface model: count=0 does not mean the elevation cell is
missing. Therefore elevation/slope statistics use LDEM nodata only; the
matching LDEC count grid is reported separately as observational support.
"""
from __future__ import annotations
import json,math,sys
from datetime import datetime,timezone
from pathlib import Path
import requests
import numpy as np
import rasterio
from rasterio.windows import Window, transform as window_transform
from rasterio.transform import from_origin
from rasterio.warp import reproject
from rasterio.enums import Resampling
from pyproj import CRS as PyCRS, Transformer
from scipy.ndimage import maximum_filter,minimum_filter
from PIL import Image

BASE="https://imbrium.mit.edu/DATA/LOLA_GDR/POLAR/JP2/"
FILES={
 "ldem":"LDEM_80S_80M.JP2",
 "ldem_label":"LDEM_80S_80M_JP2.LBL",
 "ldem_aux":"LDEM_80S_80M_AUX.XML",
 "ldec":"LDEC_80S_80M.JP2",
 "ldec_label":"LDEC_80S_80M_JP2.LBL",
 "ldec_aux":"LDEC_80S_80M_AUX.XML"
}
SITE={"name":"Shackleton Rim / lunar south pole","latitude_south_deg":-89.7668,
      "longitude_east_deg":188.13,"site_id":"R04 / Site04",
      "coordinate_source":"Lunar Surface Data Book R04/Site04"}
ROOT=Path(__file__).resolve().parents[1]
RAW=ROOT/"data"/"raw"/"lola_mit_80m"
OUT=ROOT/"data"/"moon"
SESSION=requests.Session()
SESSION.headers.update({"User-Agent":"ANALOG-X/1.0 NASA LOLA PDS archive processing"})
def now():
 return datetime.now(timezone.utc).replace(microsecond=0).isoformat()
def download(name):
 path=RAW/name
 if path.exists() and path.stat().st_size>0:return path
 path.parent.mkdir(parents=True,exist_ok=True)
 url=BASE+name
 with SESSION.get(url,stream=True,timeout=(30,180)) as r:
  r.raise_for_status()
  tmp=path.with_suffix(path.suffix+".part")
  with tmp.open("wb") as f:
   for chunk in r.iter_content(1024*1024):
    if chunk:f.write(chunk)
  tmp.replace(path)
 return path
def pds_number(text,key,default=None):
 import re
 m=re.search(r"(?im)^\s*"+re.escape(key)+r"\s*=\s*([-+0-9.Ee]+)",text)
 return float(m.group(1)) if m else default
def summary(x):
 x=np.asarray(x,dtype="float64")
 x=x[np.isfinite(x)]
 if x.size==0:return None
 return {"count":int(x.size),"min":float(x.min()),"p10":float(np.percentile(x,10)),
         "median":float(np.median(x)),"p90":float(np.percentile(x,90)),
         "p95":float(np.percentile(x,95)),"max":float(x.max())}
def surface_grid_relative_m(z,valid,pixel_m):
   values=np.asarray(z,dtype=np.float64)
   mask=np.asarray(valid,dtype=bool) & np.isfinite(values)
   if not mask.any(): return None
   baseline=float(np.median(values[mask]))
   rows=[]
   for row in range(values.shape[0]):
    rows.append([round(float(values[row,col]-baseline),2) if mask[row,col] else None for col in range(values.shape[1])])
   return {"units":"m","vertical_reference":"relative to median valid elevation within this local grid",
    "rows":int(values.shape[0]),"columns":int(values.shape[1]),
    "pixel_size_m":{"x":float(pixel_m),"y":float(pixel_m)},
    "valid_cell_count":int(mask.sum()),"total_cell_count":int(mask.size),"values":rows}


def main():
 OUT.mkdir(parents=True,exist_ok=True);RAW.mkdir(parents=True,exist_ok=True)
 paths={k:download(v) for k,v in FILES.items()}
 for k in ("ldem","ldec"):
  # GDAL PAM sidecar convention for the JP2 scale/nodata metadata.
  aux=RAW/FILES[k].replace(".JP2","_AUX.XML")
  dest=RAW/(FILES[k]+".aux.xml")
  if aux.exists():dest.write_bytes(aux.read_bytes())
 labels={k:paths[k+"_label"].read_text(encoding="latin-1",errors="replace") for k in ("ldem","ldec")}
 ds={}
 with rasterio.Env(GDAL_CACHEMAX=256,GDAL_DISABLE_READDIR_ON_OPEN="EMPTY_DIR"):
  ds["ldem"]=rasterio.open(paths["ldem"])
  ds["ldec"]=rasterio.open(paths["ldec"])
  dem=ds["ldem"];cnt=ds["ldec"]
  grid_equal=(dem.width==cnt.width and dem.height==cnt.height and dem.transform==cnt.transform and dem.crs==cnt.crs)
  # Require the product labels' dimensions and common grid to agree before comparison.
  if not grid_equal:
   raise RuntimeError("LOLA DEM and count JP2s do not share identical raster geometry: "
    +json.dumps({"dem":[dem.width,dem.height,str(dem.crs),str(dem.transform)],
                 "count":[cnt.width,cnt.height,str(cnt.crs),str(cnt.transform)]}))
  # This is a Moon-centred custom CRS, not Earth EPSG:4326. Transform
  # longitude/latitude in the DEM's own lunar geodetic CRS to its stereographic
  # map CRS so the target is not inadvertently interpreted on an Earth ellipsoid.
  moon_projected_crs=PyCRS.from_wkt(dem.crs.to_wkt())
  lunar_geographic=moon_projected_crs.geodetic_crs
  if lunar_geographic is None:
   raise RuntimeError("LOLA JP2 has no lunar geodetic base CRS")
  transformer=Transformer.from_crs(lunar_geographic,dem.crs,always_xy=True)
  x,y=transformer.transform(SITE["longitude_east_deg"],SITE["latitude_south_deg"])
  row,col=dem.index(x,y)
  if row<0 or col<0 or row>=dem.height or col>=dem.width:
   raise RuntimeError(f"Shackleton target maps outside LOLA 80 m grid: row={row}, col={col}")
  # 12 km half-width gives a 24 km x 24 km local base-area context.
  half_m=14800
  pixels=int(round(half_m/80))
  col_off=max(0,col-pixels)
  row_off=max(0,row-pixels)
  win_width=min(2*pixels,dem.width-col_off)
  win_height=min(2*pixels,dem.height-row_off)
  window=Window(col_off,row_off,win_width,win_height)
  if win_width<2*pixels or win_height<2*pixels:
   raise RuntimeError(f"Target is too close to product edge for a full 24 km window: {win_width}x{win_height} pixels")
  z_raw=dem.read(1,window=window,masked=True).astype("float64")
  n_raw=cnt.read(1,window=window,masked=True).astype("float64")
  z_raw=np.asarray(z_raw.filled(np.nan));n=np.asarray(n_raw.filled(np.nan))
  # PDS label: height is radius relative to 1,737,400 m, scaled by 0.5.
  z_scale=pds_number(labels["ldem"],"SCALING_FACTOR",0.5)
  z_offset=pds_number(labels["ldem"],"OFFSET",1737400.0)
  z=z_raw*z_scale+z_offset
  nodata_z=dem.nodata
  valid=np.isfinite(z)
  if nodata_z is not None:valid &= z_raw!=nodata_z
  # Convert radius to elevation relative to the reference lunar sphere.
  elev=z-z_offset
  elev[~valid]=np.nan
  count_valid=np.isfinite(n)
  count_positive=count_valid&(n>0)
  # Interpolated LDEM stays valid even where no laser footprint hit the pixel.
  elev_fill=np.where(valid,elev,np.nanmedian(elev[valid]))
  gy,gx=np.gradient(elev_fill,80.0,80.0)
  slope=np.degrees(np.arctan(np.hypot(gx,gy)))
  complete=minimum_filter(valid.astype(np.uint8),size=3,mode="constant",cval=0)==1
  relief=maximum_filter(elev_fill,size=3,mode="nearest")-minimum_filter(elev_fill,size=3,mode="nearest")
  slope_stats=summary(slope[complete])
  relief_stats=summary(relief[complete])
  valid_elev=elev[valid]
  count_vals=n[count_valid]
  observed=count_positive
  # Aggregate the native 80 m LOLA elevation grid to the same approximately
  # 925 m cell support used for the Earth/Mars profiles. The 370x370 native
  # pixel window spans 29.6 km; the 32x32 coarse grid spans the same footprint.
  coarse_res=925.0
  coarse_rows=32
  coarse_cols=32
  src_transform=window_transform(window,dem.transform)
  coarse_transform=from_origin(src_transform.c,src_transform.f,coarse_res,coarse_res)
  coarse_elev=np.full((coarse_rows,coarse_cols),np.nan,dtype=np.float32)
  reproject(
   source=elev.astype(np.float32),destination=coarse_elev,
   src_transform=src_transform,src_crs=dem.crs,
   dst_transform=coarse_transform,dst_crs=dem.crs,
   src_nodata=np.nan,dst_nodata=np.nan,
   resampling=Resampling.average,num_threads=2
  )
  coarse_valid=np.isfinite(coarse_elev)
  if coarse_valid.sum()<100:
   raise RuntimeError(f"Too few valid lunar cells after aggregation to {coarse_res} m")
  coarse_fill=np.where(coarse_valid,coarse_elev,np.nanmedian(coarse_elev[coarse_valid]))
  cy,cx=np.gradient(coarse_fill,coarse_res,coarse_res)
  coarse_slope=np.degrees(np.arctan(np.hypot(cx,cy)))
  coarse_complete=minimum_filter(coarse_valid.astype(np.uint8),size=3,mode="constant",cval=0)==1
  coarse_relief=maximum_filter(coarse_fill,size=3,mode="nearest")-minimum_filter(coarse_fill,size=3,mode="nearest")
  # Aggregate the positive-return mask separately. It is support metadata,
  # not an elevation nodata mask.
  return_fraction=np.zeros((coarse_rows,coarse_cols),dtype=np.float32)
  reproject(
   source=(n>0).astype(np.float32),destination=return_fraction,
   src_transform=src_transform,src_crs=dem.crs,
   dst_transform=coarse_transform,dst_crs=dem.crs,
   src_nodata=None,dst_nodata=0,
   resampling=Resampling.average,num_threads=2
  )
  coarse_support={
   "pixel_size_m":coarse_res,"rows":coarse_rows,"columns":coarse_cols,
   "window_extent_m":[coarse_cols*coarse_res,coarse_rows*coarse_res],
   "valid_elevation_cells":int(coarse_valid.sum()),
   "total_cells":int(coarse_valid.size),
   "elevation_coverage_percent":round(float(coarse_valid.mean()*100),3),
   "slope_deg":{
    "median":float(np.median(coarse_slope[coarse_complete])),
    "p90":float(np.percentile(coarse_slope[coarse_complete],90)),
    "p95":float(np.percentile(coarse_slope[coarse_complete],95)),
    "valid_3x3_neighbourhoods":int(coarse_complete.sum())
   },
   "3x3_local_relief_m_2775m_footprint":{
    "median":float(np.median(coarse_relief[coarse_complete])),
    "p90":float(np.percentile(coarse_relief[coarse_complete],90)),
    "p95":float(np.percentile(coarse_relief[coarse_complete],95))
   },
   "ldec_positive_return_support":{
    "mean_native_pixel_fraction_per_coarse_cell_percent":float(np.mean(return_fraction[coarse_valid])*100),
    "coarse_cells_with_any_positive_returns":int(np.sum(return_fraction>0)),
    "coarse_cells_total":int(return_fraction.size)
   }
  }
  # A small grayscale browse preview uses elevation only; no colour ramp is
  # assigned scientific meaning.
  lo,hi=np.percentile(valid_elev,[2,98])
  img=np.clip((elev_fill-lo)/max(hi-lo,1e-9),0,1)
  img[~valid]=0
  Image.fromarray((img*255).astype("uint8")).resize((512,512),Image.Resampling.BILINEAR).save(
   OUT/"shackleton_lola_80m_elevation_preview.png",optimize=True)
  result={
   "generated_at_utc":now(),"provider":"NASA LRO LOLA PDS GDR hosted by MIT Imbrium mirror",
   "product":"LDEM_80S_80M and LDEC_80S_80M",
   "source_urls":{k:BASE+v for k,v in FILES.items()},
   "site":SITE,
   "grid":{"width_px":dem.width,"height_px":dem.height,"crs":str(dem.crs),
    "transform":[dem.transform.a,dem.transform.b,dem.transform.c,dem.transform.d,dem.transform.e,dem.transform.f],
    "native_pixel_size_m":80,"product_latitude_extent_deg":[-90,-80],
    "target_raster_row_col":[int(row),int(col)],
    "window_pixel_size":[int(window.width),int(window.height)],
    "window_extent_m":[int(window.width*80),int(window.height*80)],
    "native_support_m":80,"coarse_comparison_support_m":925,
    "window_bounds":[float(window.col_off),float(window.row_off),float(window.col_off+window.width),float(window.row_off+window.height)],
    "dem_and_count_grid_aligned":grid_equal},
   "matched_coarse_support_approx_925m":coarse_support,
    "surface_grid_relative_m":surface_grid_relative_m(coarse_elev,coarse_valid,coarse_res),
   "terrain_metrics":{
    "elevation_relative_to_1737_4km_sphere_m":summary(valid_elev),
    "slope_deg_from_80m_dem":slope_stats,
    "3x3_local_relief_m_240m_footprint":relief_stats,
    "valid_interpolated_elevation_cells":int(valid.sum()),
    "total_window_cells":int(valid.size),
    "ldec_count_map":{
      "cells_with_positive_lola_returns":int(count_positive.sum()),
      "cells_with_valid_count_value":int(count_valid.sum()),
      "coverage_with_positive_returns_percent":round(float(count_positive.sum()/count_valid.sum()*100),2) if count_valid.any() else None,
      "mean_returns_per_valid_count_cell":float(np.mean(count_vals)) if count_vals.size else None,
      "median_returns_per_valid_count_cell":float(np.median(count_vals)) if count_vals.size else None,
      "p90_returns_per_valid_count_cell":float(np.percentile(count_vals,90)) if count_vals.size else None
    }
   },
   "method_note":"LDEM is an interpolated gridded surface model. Count=0 does not invalidate an interpolated DEM cell; the LDEC count map is reported separately as measurement support. Elevation is converted from radius by subtracting the 1,737,400 m reference radius after applying the 0.5 m/sample scaling factor. This is a terrain context product, not a shadow/illumination, water-ice, resource, landing-safety or rover-mobility assessment.",
   "limitations":["80 m polar stereographic DEM; not 5 m site DEM.","No Diviner illumination, annual temperature or water-ice permafrost depth has been integrated.","A separate illumination and terrain-safety study is required for a permanent base candidate."],
   "preview_path":"shackleton_lola_80m_elevation_preview.png"
  }
  (OUT/"shackleton_lola_80m.json").write_text(json.dumps(result,indent=2,allow_nan=False)+"\n",encoding="utf-8")
  print(json.dumps({"status":"success","grid":result["grid"],"terrain":result["terrain_metrics"]},indent=2),flush=True)
  for d in ds.values():d.close()
 return 0
if __name__=="__main__":
 raise SystemExit(main())

#!/usr/bin/env python3
"""Process NASA GSFC LOLA 5 m south-pole terrain products for Shackleton Rim.

Inputs are public Cloud-Optimized GeoTIFFs (LDEM, LDEC count map and LDSM
slope map) from PGDA product 78. Only the derived JSON and a browse PNG are
committed; the source raster assets are read through GDAL /vsicurl range reads.
"""
from __future__ import annotations
import json, sys
from datetime import datetime, timezone
from pathlib import Path
import numpy as np
import rasterio
from rasterio.enums import Resampling
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"data"/"moon"
BASE="https://pgda.gsfc.nasa.gov/data/LOLA_5mpp/Site04/"
FILES={
 "elevation":"Site04_final_adj_5mpp_surf.tif",
 "counts":"Site04_final_adj_5mpp_ldec.tif",
 "slope":"Site04_final_adj_5mpp_slp.tif"
}
SITE={
 "id":"Site04",
 "name":"Shackleton Rim",
 "latitude_south_deg":-89.7668,
 "longitude_east_deg":188.13,
 "source_coordinate_note":"Lunar Surface Data Book coordinate for R04/Site04. The DEM tile is a site-specific product; its pixel CRS is Moon south-polar stereographic (MOON_ME, DE421)."
}
session_env={
 "GDAL_DISABLE_READDIR_ON_OPEN":"EMPTY_DIR",
 "CPL_VSIL_CURL_ALLOWED_EXTENSIONS":".tif",
 "GDAL_HTTP_MAX_RETRY":"4",
 "GDAL_HTTP_RETRY_DELAY":"1",
 "GDAL_HTTP_TIMEOUT":"60",
 "GDAL_CACHEMAX":512
}

def utcnow():
 return datetime.now(timezone.utc).replace(microsecond=0).isoformat()

def stats(values):
 x=np.asarray(values,dtype=np.float64)
 x=x[np.isfinite(x)]
 if x.size==0:return None
 return {
  "count":int(x.size),
  "p10":float(np.percentile(x,10)),
  "median":float(np.median(x)),
  "p90":float(np.percentile(x,90)),
  "p95":float(np.percentile(x,95)),
  "min":float(np.min(x)),
  "max":float(np.max(x))
 }

def open_source(kind):
 url=BASE+FILES[kind]
 try:
  ds=rasterio.open("/vsicurl/"+url)
 except Exception as exc:
  raise RuntimeError(f"Cannot open public PGDA COG ({kind}): {exc}") from exc
 return ds,url

def make_preview(dem_path,slope_path,count_path,outpath):
 # Native grids are read as overviews for a fast, auditable browse layer.
 with rasterio.Env(**session_env):
  with rasterio.open("/vsicurl/"+dem_path) as dem, \
       rasterio.open("/vsicurl/"+slope_path) as slope, \
       rasterio.open("/vsicurl/"+count_path) as counts:
   target=(900,900)
   z=dem.read(1,out_shape=target,resampling=Resampling.average).astype("float32")
   s=slope.read(1,out_shape=target,resampling=Resampling.average).astype("float32")
   n=counts.read(1,out_shape=target,resampling=Resampling.average).astype("float32")
 valid=np.isfinite(z)&np.isfinite(s)&np.isfinite(n)&(n>0)
 if valid.sum()<10:raise RuntimeError("No valid sample pixels in the LOLA overview")
 zfill=np.where(valid,z,np.nanmedian(z[valid]))
 gy,gx=np.gradient(zfill,5.0*(dem.width/target[1]),5.0*(dem.height/target[0]))
 # Simple hillshade from the elevation overview. Scale uses the actual
 # downsampled pixel spacing reported by the source product.
 az=np.deg2rad(315.0);alt=np.deg2rad(40.0)
 slope_rad=np.arctan(np.hypot(gx,gy))
 aspect=np.arctan2(-gx,gy)
 shade=np.sin(alt)*np.cos(slope_rad)+np.cos(alt)*np.sin(slope_rad)*np.cos(az-aspect)
 shade=np.clip((shade+1)/2,0,1)
 shade[~valid]=0
 img=(shade*255).astype(np.uint8)
 outpath.parent.mkdir(parents=True,exist_ok=True)
 Image.fromarray(img,mode="L").save(outpath,optimize=True)

def main():
 OUT.mkdir(parents=True,exist_ok=True)
 ds={}
 urls={}
 try:
  with rasterio.Env(**session_env):
   for kind in FILES:
    ds[kind],urls[kind]=open_source(kind)
   dem,counts,slope=ds["elevation"],ds["counts"],ds["slope"]
   signatures={(d.width,d.height,d.crs,d.transform) for d in ds.values()}
   if len(signatures)!=1:
    raise RuntimeError("LOLA elevation, count and slope rasters do not share identical grid geometry")
   width,height=dem.width,dem.height
   if width<10 or height<10:raise RuntimeError("LOLA COG dimensions are implausibly small")
   # Read native rasters. The product is a site-sized 5 m map; the pipeline
   # verifies file metadata first and does not fetch unrelated global DEMs.
   z=dem.read(1,masked=True).astype("float64")
   n=counts.read(1,masked=True).astype("float64")
   sl=slope.read(1,masked=True).astype("float64")
   z=np.asarray(z.filled(np.nan))
   n=np.asarray(n.filled(np.nan))
   sl=np.asarray(sl.filled(np.nan))
   nodata_z=dem.nodata
   nodata_n=counts.nodata
   nodata_sl=slope.nodata
   valid=np.isfinite(z)&np.isfinite(n)&np.isfinite(sl)&(n>0)
   if nodata_z is not None:valid &= z!=nodata_z
   if nodata_n is not None:valid &= n!=nodata_n
   if nodata_sl is not None:valid &= sl!=nodata_sl
   if valid.sum()<1000:raise RuntimeError(f"Too few LOLA-observed pixels ({int(valid.sum())})")
   z_values=z[valid]
   slope_values=sl[valid]
   count_values=n[valid]
   # Local relief at a 15 m footprint (3x3 pixels). For this fine-resolution
   # panel, report only neighbourhoods where all nine cells have LOLA returns.
   from scipy.ndimage import maximum_filter,minimum_filter
   complete=minimum_filter(valid.astype(np.uint8),size=3,mode="constant",cval=0)==1
   zfill=np.where(valid,z,np.nanmedian(z_values))
   rel=maximum_filter(zfill,size=3,mode="nearest")-minimum_filter(zfill,size=3,mode="nearest")
   relief=rel[complete]
   if relief.size<100:raise RuntimeError("Too few complete 3x3 neighborhoods for local relief")
   result={
    "generated_at_utc":utcnow(),
    "provider":"NASA GSFC Planetary Geosciences Data Archive (PGDA), LRO LOLA",
    "product":"High-Resolution LOLA Topography for Lunar South Pole Sites (PGDA product 78)",
    "site":SITE,
    "source_products":{
      kind:{"filename":FILES[kind],"url":urls[kind],"crs":str(ds[kind].crs),
            "width_px":int(ds[kind].width),"height_px":int(ds[kind].height),
            "pixel_size_crs_units":[float(ds[kind].transform.a),float(ds[kind].transform.e)],
            "nodata":ds[kind].nodata,"dtype":ds[kind].dtypes[0]}
      for kind in FILES
    },
    "native_pixel_scale_m":5,
    "grid_coverage":{
      "valid_lola_return_pixels":int(valid.sum()),
      "total_pixels":int(valid.size),
      "valid_coverage_percent":round(100*float(valid.mean()),3),
      "complete_3x3_neighborhoods":int(relief.size),
      "mean_lola_returns_per_valid_pixel":float(np.mean(count_values)),
      "median_lola_returns_per_valid_pixel":float(np.median(count_values))
    },
    "terrain_metrics":{
      "elevation_m_moon_me_de421":stats(z_values),
      "slope_deg_source_lola_product":stats(slope_values),
      "3x3_local_relief_m_15m_footprint":stats(relief),
      "slope_fraction":{
        "under_5_deg_percent":float(np.mean(slope_values<5)*100),
        "under_10_deg_percent":float(np.mean(slope_values<10)*100),
        "over_20_deg_percent":float(np.mean(slope_values>20)*100)
      }
    },
    "preview_path":"shackleton_rim_lola_5m_hillshade.png",
    "interpretation":"High-resolution south-polar terrain context for a named Shackleton Rim candidate site. The DEM is interpolated surface elevation; LDEC count map is used as a measurement-support mask. These descriptors alone do not establish illumination, PSR status, water-ice abundance, landing suitability, rover traversability or engineering safety.",
    "citations":[
      "Barker et al. (2023), A New View of the Lunar South Pole from LOLA, Planetary Science Journal 4, 183, DOI 10.3847/PSJ/acf3e1.",
      "Barker et al. (2021), Improved LOLA Elevation Maps for South Pole Landing Sites: Error Estimates and Their Impact on Illumination Conditions, Planetary and Space Science 203, 105119."
    ]
   }
  # Render overview from source COGs while handles are still available.
  # A 900x900 average-resampled image is small enough for the public web app.
  dem_path,slope_path,count_path=(urls["elevation"],urls["slope"],urls["counts"])
  for d in ds.values():
   d.close()
  ds.clear()
  make_preview(dem_path,slope_path,count_path,OUT/"shackleton_rim_lola_5m_hillshade.png")
  (OUT/"shackleton_rim_lola.json").write_text(json.dumps(result,indent=2,allow_nan=False)+"\n",encoding="utf-8")
  print(json.dumps({"status":"success","dimensions":[width,height],"valid_percent":result["grid_coverage"]["valid_coverage_percent"],"slope_p50":result["terrain_metrics"]["slope_deg_source_lola_product"]["median"]},indent=2),flush=True)
  return 0
 except Exception as exc:
  print(f"LOLA south-pole processing failed: {exc}",file=sys.stderr,flush=True)
  err={"generated_at_utc":utcnow(),"provider":"NASA GSFC PGDA / LOLA","site":SITE,"status":"processing_failed","error":str(exc)}
  (OUT/"shackleton_rim_lola.json").write_text(json.dumps(err,indent=2)+"\n",encoding="utf-8")
  return 1
 finally:
  for d in ds.values():
   try:d.close()
   except Exception:pass

if __name__=="__main__":
 raise SystemExit(main())

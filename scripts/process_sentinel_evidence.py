#!/usr/bin/env python3
"""Build reproducible 20 m Sentinel-2 spectral-context screens for Pakistan sites.

Uses public Microsoft Planetary Computer STAC metadata and SAS signing. Outputs
are screening indicators, not mineralogical classification or glacier outlines.
"""
from __future__ import annotations
import json, sys, time
from datetime import datetime, timezone
from pathlib import Path
import requests
import numpy as np
import rasterio
from rasterio.windows import from_bounds, Window
from rasterio.warp import transform_bounds, reproject, Resampling
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
CATALOG_PATH=ROOT/"data"/"pakistan"/"public_scene_catalog.json"
OUT=ROOT/"data"/"pakistan"/"imagery"
STAC="https://planetarycomputer.microsoft.com/api/stac/v1/search"
SIGN="https://planetarycomputer.microsoft.com/api/sas/v1/sign"
COLLECTION="sentinel-2-l2a"

SITES={
 "koh_i_sultan":{
  "name":"Koh-i-Sultan / Chagai",
  "bbox":[62.70,29.00,62.90,29.20],
  "window":"2026-09-07T00:00:00Z/2026-09-10T23:59:59Z",
  "role":"Volcanic outcrop / arid terrain spectral-context screen",
  "interpretation":"Bare-surface, vegetation and SWIR contrast indicators can help target field observations. These bands do not identify minerals or prove Mars analog equivalence."
 },
 "hispar_glacier":{
  "name":"Hispar Glacier / Karakoram",
  "bbox":[75.12,36.02,75.34,36.22],
  "window":"2022-09-01T00:00:00Z/2022-10-01T23:59:59Z",
  "role":"Cryosphere / snow-ice and debris-context screen",
  "interpretation":"NDSI and Sentinel-2 Scene Classification Layer provide a screening view of snow/ice and cloud/shadow context, not a validated glacier boundary or mass-balance result."
 },
 "chagai_small_playas":{
  "name":"Chagai small salt playas near Nok Kundi",
  "bbox":[62.54,28.53,62.73,28.64],
  "window":"2024-01-01T00:00:00Z/2026-11-14T23:59:59Z",
  "role":"Evaporite / salt-playa and sedimentary-process screen",
  "interpretation":"Bare-surface and SWIR context can help plan field checks of salt-pan and sedimentary units. Spectral indices do not establish evaporite mineralogy, brine chemistry or Mars equivalence. This AOI is based on two historical NASA report coordinates and needs modern ground verification."
 },
 "hamun_i_mashkel":{
  "name":"Hamun-i-Mashkel playa / Kharan Basin",
  "bbox":[62.82,28.13,63.02,28.33],
  "window":"2024-01-01T00:00:00Z/2026-11-14T23:59:59Z",
  "role":"Closed-basin playa / intermittent-lake spectral-context screen",
  "interpretation":"Bare-surface, wetness and seasonal spectral context can inform playa process reconnaissance. NDMI/NDSI do not identify brines or minerals; a single Sentinel scene cannot characterize intermittent inundation."
 }
}

session=requests.Session()
session.headers.update({"User-Agent":"ANALOG-X/1.0 Sentinel-2 public COG processing","Accept":"application/json"})

def now():
 return datetime.now(timezone.utc).replace(microsecond=0).isoformat()

def polygon(b):
 x0,y0,x1,y1=b
 return {"type":"Polygon","coordinates":[[[x0,y0],[x1,y0],[x1,y1],[x0,y1],[x0,y0]]]}

def get_item(site):
 body={
  "collections":[COLLECTION],
  "intersects":polygon(site["bbox"]),
  "datetime":site["window"],
  "limit":100,
  "query":{"eo:cloud_cover":{"lt":30}}
 }
 r=session.post(STAC,json=body,timeout=(20,90))
 if r.status_code!=200:
  raise RuntimeError(f"Planetary Computer STAC HTTP {r.status_code}: {r.text[:1200]}")
 items=r.json().get("features",[])
 if not items:
  body.pop("query",None)
  r=session.post(STAC,json=body,timeout=(20,90))
  r.raise_for_status()
  items=r.json().get("features",[])
 if not items:
  raise RuntimeError("No Sentinel-2 L2A scenes found in the selected AOI/date window.")
 items.sort(key=lambda item:(
   item.get("properties",{}).get("eo:cloud_cover",9999),
   item.get("properties",{}).get("datetime","")
 ))
 return items[0]

SAS_TOKEN=None
SAS_EXPIRY=None

def sign_href(href):
 global SAS_TOKEN,SAS_EXPIRY
 if SAS_TOKEN is None:
  token_url="https://planetarycomputer.microsoft.com/api/sas/v1/token/"+COLLECTION
  last_error=None
  for attempt in range(5):
   r=session.get(token_url,timeout=(20,60))
   if r.status_code==429:
    try: wait=int(r.headers.get("Retry-After","20"))
    except ValueError: wait=20
    time.sleep(min(max(wait,5),90))
    continue
   if r.status_code!=200:
    last_error=f"HTTP {r.status_code}: {r.text[:800]}"
    time.sleep(2*(attempt+1))
    continue
   data=r.json()
   SAS_TOKEN=data.get("token")
   SAS_EXPIRY=data.get("msft:expiry")
   if not SAS_TOKEN:
    last_error="Planetary Computer SAS token response had no token"
    continue
   break
  if SAS_TOKEN is None:
   raise RuntimeError("Could not obtain Planetary Computer collection SAS token: "+str(last_error))
 separator="&" if "?" in href else "?"
 return href+separator+SAS_TOKEN,SAS_EXPIRY

def read_reference_band(href,bbox):
 with rasterio.open(href) as src:
  bounds=transform_bounds("EPSG:4326",src.crs,*bbox,densify_pts=21)
  win=from_bounds(*bounds,transform=src.transform)
  win=win.round_offsets().round_lengths()
  win=win.intersection(Window(0,0,src.width,src.height))
  if win.width<2 or win.height<2:
   raise RuntimeError("AOI does not intersect raster asset")
  arr=src.read(1,window=win)
  tr=src.window_transform(win)
  crs=src.crs
  nodata=src.nodata
  return arr.astype(np.float32),tr,crs,nodata

def read_on_grid(href,bbox,shape,dst_transform,dst_crs,resampling):
 with rasterio.open(href) as src:
  bounds=transform_bounds("EPSG:4326",src.crs,*bbox,densify_pts=21)
  win=from_bounds(*bounds,transform=src.transform)
  win=win.round_offsets().round_lengths()
  win=win.intersection(Window(0,0,src.width,src.height))
  if win.width<2 or win.height<2:
   raise RuntimeError("AOI does not intersect band asset")
  arr=src.read(1,window=win).astype(np.float32)
  if src.nodata is not None:
   arr[arr==src.nodata]=np.nan
  src_transform=src.window_transform(win)
  dst=np.full(shape,np.nan,dtype=np.float32)
  reproject(
   source=arr,destination=dst,
   src_transform=src_transform,src_crs=src.crs,
   dst_transform=dst_transform,dst_crs=dst_crs,
   resampling=resampling,
   src_nodata=np.nan,dst_nodata=np.nan
  )
  return dst

def ratio(a,b):
 den=a+b
 out=np.full(a.shape,np.nan,dtype=np.float32)
 good=np.isfinite(a)&np.isfinite(b)&(np.abs(den)>1e-6)
 out[good]=(a[good]-b[good])/den[good]
 return out

def safe_ratio(a,b):
 out=np.full(a.shape,np.nan,dtype=np.float32)
 good=np.isfinite(a)&np.isfinite(b)&(np.abs(b)>1e-6)
 out[good]=a[good]/b[good]
 return out

def stats(a):
 v=a[np.isfinite(a)]
 if v.size==0:
  return {"valid_pixels":0,"p02":None,"p25":None,"median":None,"p75":None,"p98":None}
 p=np.percentile(v,[2,25,50,75,98])
 return {"valid_pixels":int(v.size),"p02":float(p[0]),"p25":float(p[1]),"median":float(p[2]),"p75":float(p[3]),"p98":float(p[4])}

def stretch(a,mask):
 v=a[mask&np.isfinite(a)]
 if v.size==0:return np.zeros_like(a,dtype=np.uint8)
 lo,hi=np.percentile(v,[2,98])
 if hi<=lo:return np.zeros_like(a,dtype=np.uint8)
 x=np.clip((a-lo)/(hi-lo),0,1)
 x=np.where(np.isfinite(x),x,0)
 return (x*255).astype(np.uint8)

def save_rgb(path,r,g,b,mask):
 rgb=np.dstack([stretch(r,mask),stretch(g,mask),stretch(b,mask)])
 rgb[~mask]=0
 Image.fromarray(rgb,"RGB").save(path,optimize=True)

def save_index(path,a,mask):
 vals=a[mask&np.isfinite(a)]
 if vals.size==0:
  Image.fromarray(np.zeros((*a.shape,3),dtype=np.uint8),"RGB").save(path)
  return
 lo,hi=np.percentile(vals,[2,98])
 if hi<=lo: hi=lo+1e-6
 x=np.clip((a-lo)/(hi-lo),0,1)
 x=np.where(np.isfinite(x),x,0)
 stops=np.array([[19,38,46],[27,105,92],[130,164,103],[221,196,125]],dtype=np.float32)
 pos=x*3
 idx=np.clip(np.floor(pos).astype(int),0,2)
 frac=(pos-idx)[...,None]
 rgb=stops[idx]*(1-frac)+stops[idx+1]*frac
 rgb[~mask]=[0,0,0]
 Image.fromarray(np.clip(rgb,0,255).astype(np.uint8),"RGB").save(path,optimize=True)

def main():
 if not CATALOG_PATH.exists():
  raise RuntimeError("Public STAC catalogue missing; run fetch_public_evidence.py first.")
 OUT.mkdir(parents=True,exist_ok=True)
 results={}
 for site_id,site in SITES.items():
  print(f"[{site_id}] Search Sentinel-2 L2A",flush=True)
  item=get_item(site)
  assets=item.get("assets",{})
  required=["B02","B03","B04","B08","B11","B12","SCL"]
  missing=[x for x in required if x not in assets]
  if missing:
   raise RuntimeError(f"Scene missing required assets: {missing}")
  signed={}
  for name in required:
   signed[name],_=sign_href(assets[name]["href"])
   time.sleep(0.08)
  b11,transform,crs,nodata=read_reference_band(signed["B11"],site["bbox"])
  shape=b11.shape
  bands={"B11":b11}
  for name in ["B02","B03","B04","B08","B12"]:
   bands[name]=read_on_grid(signed[name],site["bbox"],shape,transform,crs,Resampling.bilinear)
  scl=read_on_grid(signed["SCL"],site["bbox"],shape,transform,crs,Resampling.nearest)
  refl={k:v/10000.0 for k,v in bands.items()}
  cloud_shadow_classes=np.isin(np.rint(scl).astype(np.int16),[0,1,3,8,9,10])
  base_valid=np.isfinite(refl["B11"])&np.isfinite(refl["B12"])&np.isfinite(refl["B04"])&np.isfinite(refl["B02"])&np.isfinite(refl["B08"])&np.isfinite(refl["B03"])
  base_valid &= ~cloud_shadow_classes
  ndvi=ratio(refl["B08"],refl["B04"])
  ndsi=ratio(refl["B03"],refl["B11"])
  bsi_num=(refl["B11"]+refl["B04"])-(refl["B08"]+refl["B02"])
  bsi_den=(refl["B11"]+refl["B04"])+(refl["B08"]+refl["B02"])
  bsi=np.full(shape,np.nan,dtype=np.float32)
  good=np.isfinite(bsi_num)&np.isfinite(bsi_den)&(np.abs(bsi_den)>1e-6)
  bsi[good]=bsi_num[good]/bsi_den[good]
  swir_ratio=safe_ratio(refl["B11"],refl["B12"])
  iron_proxy=safe_ratio(refl["B04"],refl["B02"])
  ndmi=ratio(refl["B08"],refl["B11"])
  index_arrays={"NDVI":ndvi,"NDSI":ndsi,"BSI":bsi,"SWIR1_SWIR2_ratio":swir_ratio,"Red_Blue_ratio":iron_proxy,"NDMI":ndmi}
  for k in index_arrays:
   index_arrays[k]=np.where(base_valid,index_arrays[k],np.nan)
  scl_valid=np.isfinite(scl)
  snow_class=(np.rint(scl).astype(np.int16)==11)&scl_valid
  ndsi_vals=ndsi[base_valid&np.isfinite(ndsi)]
  stats_out={k:stats(v) for k,v in index_arrays.items()}
  result={
   "schema_version":"1.0",
   "site":{"id":site_id,"name":site["name"],"bbox_wgs84":site["bbox"],"role":site["role"]},
   "scene":{
    "provider":"Copernicus Sentinel-2 L2A hosted on Microsoft Planetary Computer",
    "collection":COLLECTION,"item_id":item.get("id"),
    "datetime":item.get("properties",{}).get("datetime"),
    "platform":item.get("properties",{}).get("platform"),
    "mgrs_tile":item.get("properties",{}).get("s2:mgrs_tile"),
    "cloud_cover_percent":item.get("properties",{}).get("eo:cloud_cover"),
    "processing_baseline":item.get("properties",{}).get("s2:processing_baseline"),
    "stac_item_url":next((l.get("href") for l in item.get("links",[]) if l.get("rel")=="self"),None),
    "source_collection_url":"https://planetarycomputer.microsoft.com/api/stac/v1/collections/sentinel-2-l2a"
   },
   "processing":{
    "analysis_grid_m":20,"grid_crs":str(crs),"rows":int(shape[0]),"columns":int(shape[1]),
    "cloud_shadow_mask_scl_classes":[0,1,3,8,9,10],
    "masked_pixel_percent":round(float((1-base_valid.sum()/base_valid.size)*100),2),
    "valid_pixel_count":int(base_valid.sum()),
    "snow_ice_scl_class_11_percent_of_all_pixels":round(float(snow_class.sum()/scl_valid.sum()*100),2) if scl_valid.sum() else None,
    "ndsi_gt_0_4_percent_of_valid_pixels":round(float((ndsi_vals>0.4).sum()/ndsi_vals.size*100),2) if ndsi_vals.size else None,
    "note":"20 m common grid. 10 m bands were resampled to the B11 20 m grid. Indices are spectral screening descriptors, not mineral identifications, calibrated abundances or validated glacier boundaries."
   },
   "indices":stats_out,
   "interpretation_note":site["interpretation"],
   "attribution":"Contains modified Copernicus Sentinel data; Sentinel-2 L2A hosted by Microsoft Planetary Computer. See Copernicus data terms and collection metadata.",
   "generated_at_utc":now(),
   "assets":{"true_color_png":f"imagery/{site_id}_true_color.png","index_png":f"imagery/{site_id}_index_screen.png"}
  }
  save_rgb(OUT/f"{site_id}_true_color.png",refl["B04"],refl["B03"],refl["B02"],base_valid)
  screen=ndsi if site_id=="hispar_glacier" else bsi
  save_index(OUT/f"{site_id}_index_screen.png",screen,base_valid)
  (OUT/f"{site_id}_spectral_profile.json").write_text(json.dumps(result,indent=2,allow_nan=False)+"\n",encoding="utf-8")
  results[site_id]=result
  print(f"[{site_id}] OK scene={item.get('id')} valid_pixels={base_valid.sum()} grid={shape}",flush=True)
 index={"schema_version":"1.0","provider":"Microsoft Planetary Computer / Copernicus Sentinel-2 L2A",
        "generated_at_utc":now(),"site_count":len(results),"sites":results}
 (OUT/"index.json").write_text(json.dumps(index,indent=2,allow_nan=False)+"\n",encoding="utf-8")
 (OUT/"README.md").write_text(
  "# Sentinel-2 spectral-context screens\n\n"
  "Products generated by scripts/process_sentinel_evidence.py from Copernicus Sentinel-2 L2A scenes hosted by Microsoft Planetary Computer.\n\n"
  "- 20 m common analysis grid; 10 m bands were resampled to B11's 20 m support.\n"
  "- Koh-i-Sultan: BSI, NDVI, SWIR1/SWIR2 and red/blue reflectance ratios are spectral context only; not mineral identification.\n"
  "- Hispar Glacier: NDSI and SCL class-11 are screening descriptors; not a validated glacier outline or mass-balance estimate.\n"
  "- Clouds/shadows/no-data classes are masked. Scene time, tile, cloud metadata, CRS and valid-pixel counts are preserved in each profile.\n\n"
  "Contains modified Copernicus Sentinel data. See docs/DATA_SOURCES.md for source attribution and limitations.\n",encoding="utf-8")
 return 0

if __name__=="__main__":
 raise SystemExit(main())

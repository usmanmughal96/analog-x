#!/usr/bin/env python3
"""Create clipped RGB quicklooks from public Sentinel-2 L2A COGs.

Inputs:
  data/pakistan/public_scene_catalog.json

Outputs:
  data/pakistan/quicklooks/koh_i_sultan.png
  data/pakistan/quicklooks/hispar_glacier.png
  data/pakistan/quicklooks/index.json

Microsoft Planetary Computer's STAC endpoint is public. Data COG requests are
signed with the public collection SAS endpoint; no user account is required.
"""
from __future__ import annotations
import json, sys
from datetime import datetime, timezone
from pathlib import Path
import requests
import numpy as np
import rasterio
from rasterio.enums import Resampling
from rasterio.warp import transform_bounds
from rasterio.windows import from_bounds, Window
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
CATALOG=ROOT/"data"/"pakistan"/"public_scene_catalog.json"
OUT=ROOT/"data"/"pakistan"/"quicklooks"
TOKEN_URL="https://planetarycomputer.microsoft.com/api/sas/v1/token/sentinel-2-l2a"
SITES={
 "koh_i_sultan":{"bbox":[62.70,29.00,62.90,29.20]},
 "hispar_glacier":{"bbox":[75.12,36.02,75.34,36.22]},
 "chagai_small_playas":{"bbox":[62.54,28.53,62.73,28.64]},
 "hamun_i_mashkel":{"bbox":[62.82,28.13,63.02,28.33]}
}
session=requests.Session()
session.headers.update({"User-Agent":"ANALOG-X/1.0 public Sentinel-2 preview generator"})

def utcnow():
 return datetime.now(timezone.utc).replace(microsecond=0).isoformat()

def get_sas():
 r=session.get(TOKEN_URL,timeout=(20,60))
 r.raise_for_status()
 payload=r.json()
 token=payload.get("token")
 if not token:
  raise RuntimeError("Planetary Computer SAS token response contained no token")
 return token

def signed_href(href,token):
 return href+("&" if "?" in href else "?")+token.lstrip("?&")

def point_in_ring(lon,lat,ring):
 inside=False
 j=len(ring)-1
 for i in range(len(ring)):
  xi,yi=ring[i][0],ring[i][1]
  xj,yj=ring[j][0],ring[j][1]
  intersects=((yi>lat)!=(yj>lat)) and (lon < (xj-xi)*(lat-yi)/((yj-yi) or 1e-15)+xi)
  if intersects: inside=not inside
  j=i
 return inside

def covers_site(geometry,lon,lat):
 if not geometry:return False
 typ=geometry.get("type")
 coords=geometry.get("coordinates",[])
 if typ=="Polygon":
  if not coords or not point_in_ring(lon,lat,coords[0]):return False
  return not any(point_in_ring(lon,lat,ring) for ring in coords[1:])
 if typ=="MultiPolygon":
  return any(covers_site({"type":"Polygon","coordinates":poly},lon,lat) for poly in coords)
 return False

def scene_candidates(site_id,entry):
 searches=entry.get("scene_searches",[])
 recent=next((x for x in searches if x.get("window")=="recent_archive" and x.get("items")),None)
 if recent is None:
  recent=next((x for x in searches if x.get("items")),None)
 if recent is None:return []
 site=SITES[site_id]
 lon=(site["bbox"][0]+site["bbox"][2])/2
 lat=(site["bbox"][1]+site["bbox"][3])/2
 items=recent["items"]
 # Prefer a scene footprint covering the site centre. Among those choose low
 # cloud cover; if none covers, use the best scene intersecting the area.
 covered=[x for x in items if covers_site(x.get("geometry"),lon,lat)]
 choices=covered or items
 choices=sorted(choices,key=lambda x:(9999 if x.get("cloud_cover_percent") is None else x["cloud_cover_percent"]))
 return [(x,recent["window"]) for x in choices if x.get("assets",{}).get("visual",{}).get("href")]

def build_one(site_id,entry,token):
 candidates=scene_candidates(site_id,entry)
 if not candidates:
  raise RuntimeError("No Sentinel-2 scene with a true-colour visual asset found")
 site=SITES[site_id]
 bbox=site["bbox"]
 failures=[]
 for item,window_name in candidates[:5]:
  try:
   href=signed_href(item["assets"]["visual"]["href"],token)
   vsicurl="/vsicurl/"+href
   with rasterio.Env(
    GDAL_DISABLE_READDIR_ON_OPEN="EMPTY_DIR",
    CPL_VSIL_CURL_ALLOWED_EXTENSIONS=".tif",
    GDAL_HTTP_MAX_RETRY="3",
    GDAL_HTTP_RETRY_DELAY="1",
    GDAL_CACHEMAX=256
   ):
    with rasterio.open(vsicurl) as src:
     if src.count<3:
      raise RuntimeError(f"Expected RGB TCI bands; source has {src.count} bands")
     bounds=transform_bounds("EPSG:4326",src.crs,*bbox,densify_pts=21)
     win=from_bounds(*bounds,transform=src.transform)
     full=Window(0,0,src.width,src.height)
     win=win.intersection(full)
     if win.width<10 or win.height<10:
      raise RuntimeError("Candidate scene does not cover enough of the requested site window")
     arr=src.read(
      indexes=[1,2,3],
      window=win,
      out_shape=(3,768,768),
      resampling=Resampling.bilinear,
      boundless=False
     )
     # TCI is normally uint8; normalise only if provider uses another dtype.
     if arr.dtype!=np.uint8:
      vals=arr.astype("float32")
      for band in range(3):
       p2,p98=np.nanpercentile(vals[band],[2,98])
       vals[band]=np.clip((vals[band]-p2)/max(p98-p2,1e-6)*255,0,255)
      arr=vals.astype("uint8")
     rgb=np.moveaxis(arr,0,-1)
     # Keep no-data/black margins as provided: never paint or interpolate them.
     out=OUT/f"{site_id}.png"
     Image.fromarray(rgb,mode="RGB").save(out,optimize=True)
     metadata={
      "site_id":site_id,
      "scene_id":item.get("id"),
      "capture_datetime":item.get("datetime"),
      "cloud_cover_percent":item.get("cloud_cover_percent"),
      "mgrs_tile":item.get("mgrs_tile"),
      "platform":item.get("platform"),
      "collection":"sentinel-2-l2a",
      "window":window_name,
      "asset_type":"Sentinel-2 L2A true-colour visual COG",
      "preview_path":f"./{site_id}.png",
      "preview_dimensions_px":[rgb.shape[1],rgb.shape[0]],
      "requested_bbox_wgs84":bbox,
      "source_item":item.get("self"),
      "source_asset":item["assets"]["visual"]["href"],
      "license":"Copernicus Sentinel data terms; see STAC collection metadata",
      "generated_at_utc":utcnow()
     }
     return metadata
  except Exception as exc:
   failures.append({"scene_id":item.get("id"),"error":str(exc)})
 raise RuntimeError("All candidate scenes failed: "+json.dumps(failures[:5]))

def main():
 OUT.mkdir(parents=True,exist_ok=True)
 if not CATALOG.exists():raise SystemExit("Scene catalog not found. Run fetch_public_evidence.py first.")
 catalog=json.loads(CATALOG.read_text(encoding="utf-8"))
 token=get_sas()
 results={}
 for site_id,entry in catalog.get("planetary_computer",{}).get("sites",{}).items():
  if site_id not in SITES:continue
  try:
   results[site_id]=build_one(site_id,entry,token)
   print(f"[{site_id}] QUICKLOOK READY: {results[site_id]['scene_id']}",flush=True)
  except Exception as exc:
   results[site_id]={"status":"unavailable","error":str(exc),"generated_at_utc":utcnow()}
   print(f"[{site_id}] QUICKLOOK FAILED: {exc}",file=sys.stderr,flush=True)
 index={"generated_at_utc":utcnow(),"provider":"Microsoft Planetary Computer / Sentinel-2 L2A","results":results,
        "note":"RGB previews are clipped from Sentinel-2 L2A visual COGs. They are browse products, not geological classification or field validation."}
 (OUT/"index.json").write_text(json.dumps(index,indent=2)+"\n",encoding="utf-8")
 return 0 if any(x.get("preview_path") for x in results.values()) else 1

if __name__=="__main__":
 raise SystemExit(main())

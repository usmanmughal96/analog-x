#!/usr/bin/env python3
"""Enrich retained global terrain candidates with 2023 global land-cover context.

Source: Microsoft Planetary Computer io-lulc-annual-v02, a global 10 m annual
land-cover classification derived from Sentinel-2. The output is an
environmental-context screen for the bounded global candidate shortlist only;
it is not a field observation or a mineralogical/soil classification.
"""
from __future__ import annotations
import concurrent.futures
import json
import math
import sys
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import rasterio
import requests
from rasterio.enums import Resampling
from rasterio.transform import from_origin
from rasterio.warp import reproject, transform

ROOT=Path(__file__).resolve().parents[1]
GLOBAL_PATH=ROOT/"data/global_discovery/global_discovery.json"
OUT_PATH=ROOT/"data/global_discovery/global_landcover_enrichment.json"
STAC="https://planetarycomputer.microsoft.com/api/stac/v1"
COLLECTION="io-lulc-annual-v02"
YEAR_START="2023-01-01T00:00:00Z"
YEAR_END="2024-01-01T00:00:00Z"
TARGET_RES_M=30.0
HALF_WINDOW_M=2775.0
CLASSES={1:"water",2:"trees",4:"flooded_vegetation",5:"crops",7:"built_area",8:"bare_ground",9:"snow_ice",10:"clouds",11:"rangeland"}
THREAD_LOCAL=threading.local()


def utcnow()->str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def session()->requests.Session:
    if not hasattr(THREAD_LOCAL,"session"):
        s=requests.Session()
        s.headers.update({"User-Agent":"ANALOG-X/1.0 global land-cover candidate enrichment"})
        THREAD_LOCAL.session=s
    return THREAD_LOCAL.session


def local_crs(lat:float,lon:float)->str:
    if lat>=84:return "EPSG:3413"
    if lat<=-80:return "EPSG:3031"
    zone=max(1,min(60,int((lon+180)//6)+1))
    return f"EPSG:{32600+zone if lat>=0 else 32700+zone}"


def candidate_bbox(lat:float,lon:float)->list[float]:
    dlat=HALF_WINDOW_M/111320.0
    dlon=HALF_WINDOW_M/(111320.0*max(abs(math.cos(math.radians(lat))),0.015))
    return [max(-180,lon-dlon),max(-90,lat-dlat),min(180,lon+dlon),min(90,lat+dlat)]


def sign_href(href:str,token:str)->str:
    if not token:return href
    return href+("&" if "?" in href else "?")+token.lstrip("?&")


def find_items(bbox:list[float],sess:requests.Session)->list[dict[str,Any]]:
    response=sess.post(
        STAC+"/search",
        json={"collections":[COLLECTION],"bbox":bbox,"datetime":f"{YEAR_START}/{YEAR_END}","limit":100},
        timeout=(25,90),
    )
    response.raise_for_status()
    payload=response.json()
    return [item for item in payload.get("features",[]) if item.get("assets",{}).get("data",{}).get("href")]


def reproject_item(href:str,token:str,crs:str,left:float,top:float,width:int,height:int)->np.ndarray:
    target=np.zeros((height,width),dtype=np.uint8)
    signed=sign_href(href,token)
    with rasterio.Env(
        GDAL_DISABLE_READDIR_ON_OPEN="EMPTY_DIR",
        CPL_VSIL_CURL_ALLOWED_EXTENSIONS=".tif,.tiff",
        GDAL_HTTP_MAX_RETRY="3",
        GDAL_HTTP_RETRY_DELAY="2",
        GDAL_HTTP_TIMEOUT="90",
        GDAL_CACHEMAX=128,
    ):
        with rasterio.open("/vsicurl/"+signed) as src:
            if src.count<1:
                raise RuntimeError("Land-cover COG contains no data band")
            transform_dst=from_origin(left,top,TARGET_RES_M,TARGET_RES_M)
            temp=np.zeros((height,width),dtype=np.uint8)
            reproject(
                source=rasterio.band(src,1),
                destination=temp,
                src_transform=src.transform,
                src_crs=src.crs,
                src_nodata=0,
                dst_transform=transform_dst,
                dst_crs=crs,
                dst_nodata=0,
                resampling=Resampling.mode,
                init_dest_nodata=True,
                num_threads=2,
            )
            return temp


def enrich_one(candidate:dict[str,Any],token:str)->dict[str,Any]:
    lat=float(candidate["latitude"]);lon=float(candidate["longitude"])
    if abs(lat)>84:
        return {"state":"outside_sentinel2_landcover_coverage","limitation":"The 2023 Sentinel-2-derived 10 m land-cover layer is not assumed to cover this polar window; no class values are inferred.","valid_pixel_percent":0,"class_fractions_percent":{}}
    crs=local_crs(lat,lon)
    cx,cy=transform("EPSG:4326",crs,[lon],[lat])
    left=float(cx[0])-HALF_WINDOW_M
    top=float(cy[0])+HALF_WINDOW_M
    width=height=int(math.ceil((2*HALF_WINDOW_M)/TARGET_RES_M))
    bbox=candidate_bbox(lat,lon)
    sess=session()
    items=find_items(bbox,sess)
    if not items:
        return {"state":"unavailable","limitation":"No 2023 io-lulc-annual-v02 STAC data item intersected the candidate window.","valid_pixel_percent":0,"class_fractions_percent":{}}
    grid=np.zeros((height,width),dtype=np.uint8)
    used=[]
    errors=[]
    for item in items:
        href=item["assets"]["data"]["href"]
        try:
            tile=reproject_item(href,token,crs,left,top,width,height)
            fill=(grid==0)&(tile!=0)
            grid[fill]=tile[fill]
            if np.any(tile!=0):
                used.append({"item_id":item.get("id"),"datetime":item.get("properties",{}).get("datetime"),"asset_href":href,"license":item.get("properties",{}).get("license","CC-BY-4.0")})
        except Exception as exc:
            errors.append({"item_id":item.get("id"),"error":str(exc)[:400]})
    valid=grid!=0
    valid_count=int(valid.sum())
    total=int(grid.size)
    if valid_count==0:
        return {"state":"unavailable","valid_pixel_percent":0,"class_fractions_percent":{},"items_found":len(items),"item_errors":errors,"limitation":"STAC items were discovered but no classified pixels could be decoded for this window."}
    counts={int(value):int(count) for value,count in zip(*np.unique(grid[valid],return_counts=True))}
    class_fractions={CLASSES.get(code,f"class_{code}"):round(100*count/valid_count,3) for code,count in counts.items()}
    return {
        "state":"processed" if not errors else "partially_processed",
        "year":2023,
        "source_collection":COLLECTION,
        "native_product_resolution_m":10,
        "window_sampling_resolution_m":TARGET_RES_M,
        "window_footprint_km":round(2*HALF_WINDOW_M/1000,3),
        "valid_pixel_count":valid_count,
        "sampled_pixel_count":total,
        "valid_pixel_percent":round(100*valid_count/total,3),
        "class_fractions_percent":class_fractions,
        "items_used":used,
        "items_found":len(items),
        "item_errors":errors,
        "limitations":[
            "Land-cover classes are machine-learning predictions from annual Sentinel-2 composites, not field observations or detailed lithology/mineralogy.",
            "The source collection reports assessed average accuracy above 75%; accuracy varies by class, geography and conditions.",
            "Pixels are resampled by modal class to a 30 m local analysis grid; this does not create 30 m native source information.",
            "No-data pixels are excluded from class fractions and are reported separately.",
            "This enrichment is applied only to retained global terrain shortlist windows, not every global terrain window."
        ]
    }


def main()->None:
    if not GLOBAL_PATH.exists():
        raise SystemExit("Merged global discovery dataset is missing; run the global terrain scan first.")
    data=json.loads(GLOBAL_PATH.read_text(encoding="utf-8"))
    token_response=requests.get(f"https://planetarycomputer.microsoft.com/api/sas/v1/token/{COLLECTION}",timeout=(25,60))
    token_response.raise_for_status()
    token=token_response.json().get("token")
    if not token:raise SystemExit("Public Planetary Computer SAS endpoint returned no token.")
    unique={}
    for target in ("moon","mars"):
        for row in data.get("targets",{}).get(target,{}).get("candidate_windows",[]):
            unique[row["id"]]=row
    rows=list(unique.values())
    outputs={}
    failures=0
    processed=0
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        futures={pool.submit(enrich_one,row,token):row for row in rows}
        for index,future in enumerate(concurrent.futures.as_completed(futures),1):
            row=futures[future]
            try:
                result=future.result()
            except Exception as exc:
                failures+=1
                result={"state":"unavailable","valid_pixel_percent":0,"class_fractions_percent":{},"error":str(exc)[:700]}
            if result["state"] in ("processed","partially_processed"):processed+=1
            outputs[row["id"]]=result
            if index%50==0:
                print(f"Land-cover enrichment {index}/{len(rows)}; processed {processed}; unavailable/errors {failures}",flush=True)
    for target in ("moon","mars"):
        for row in data.get("targets",{}).get(target,{}).get("candidate_windows",[]):
            row["environmental_context"]=outputs.get(row["id"],{"state":"not_attempted"})
    state="processed" if processed==len(rows) and rows else ("partially_processed" if processed else "unavailable")
    summary={
        "schema_version":"1.0.0","project":"ANALOG-X Global Environment Enrichment",
        "generated_at_utc":utcnow(),"state":state,
        "source":{"provider":"Impact Observatory / Esri / Microsoft Planetary Computer","collection":COLLECTION,"dataset":"10m Annual Land Use Land Cover (9-class) V2","year":2023,"native_resolution_m":10,"license":"CC-BY-4.0","stac_url":STAC+"/collections/"+COLLECTION,"class_codes":CLASSES,"source_note":"Global Sentinel-2-derived annual land-cover classifications; provider reports assessed average accuracy above 75%."},
        "shortlist_candidate_windows_unique":len(rows),
        "processed_candidate_windows":processed,
        "unavailable_or_failed_candidate_windows":len(rows)-processed,
        "coverage_percent_of_shortlist":round(100*processed/max(len(rows),1),3),
        "method":"For each retained candidate window, query the 2023 global STAC collection, read intersecting classification COGs and reproject by modal class into a local 30 m grid covering the nominal 5.55 km window. Report class fractions among valid pixels and valid-pixel coverage.",
        "candidate_results":outputs,
        "limitations":[
            "This enrichment is limited to global terrain shortlist windows; it is not a full-world land-cover resampling or a second global candidate search.",
            "Land-cover predictions are a broad environmental descriptor, not lithology, soil chemistry, mineralogy, evaporite or brine identification.",
            "The source reports assessed average accuracy above 75%; class-specific accuracy and uncertainty vary.",
            "Annual 2023 context is a snapshot/composite and may not represent current seasonal or event conditions.",
            "The enrichment is derived from Sentinel-2; it is a distinct thematic product, not an independent sensor family from the Sentinel-2 source imagery.",
            "No physical field validation is implied."
        ]
    }
    OUT_PATH.parent.mkdir(parents=True,exist_ok=True)
    OUT_PATH.write_text(json.dumps(summary,indent=2)+"\n",encoding="utf-8")
    GLOBAL_PATH.write_text(json.dumps(data,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"state":state,"unique_candidates":len(rows),"processed":processed,"unavailable":len(rows)-processed,"coverage_pct":summary["coverage_percent_of_shortlist"],"output":str(OUT_PATH)},indent=2))


if __name__=="__main__":main()

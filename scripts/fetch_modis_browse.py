#!/usr/bin/env python3
"""Discover MOD11A2 8-day LST granules and download public browse quicklooks.

This is a browse-image evidence layer, not pixel-level LST extraction. MOD11A2
science arrays and QA layers remain a separate authenticated/asset-processing
step. The browse tiles are not clipped to the site AOI and must not be used as
quantitative site measurements.
"""
from __future__ import annotations
import json, re
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"data"/"nasa"
BROWSE=OUT/"modis_browse"
CMR="https://cmr.earthdata.nasa.gov/search/granules.json"
SITES={
 "chagai_small_playas":{"name":"Chagai small salt playas near Nok Kundi","bbox":"62.54,28.53,62.73,28.64"},
 "hamun_i_mashkel":{"name":"Hamun-i-Mashkel / Kharan Basin","bbox":"62.82,28.13,63.02,28.33"},
 "koh_i_sultan":{"name":"Koh-i-Sultan / Chagai","bbox":"62.65,28.95,62.95,29.25"},
 "hispar_glacier":{"name":"Hispar Glacier / Karakoram","bbox":"75.12,36.02,75.34,36.22"},
 "dallol":{"name":"Dallol / Danakil Depression","bbox":"40.15,14.15,40.45,14.35"},
 "atacama":{"name":"Atacama Desert","bbox":"-68.4,-23.7,-68.1,-23.3"},
 "mcmurdo":{"name":"McMurdo Dry Valleys","bbox":"161.6,-77.7,162.0,-77.3"},
 "haughton":{"name":"Haughton impact structure","bbox":"-89.9,75.25,-89.45,75.5"},
 "iceland":{"name":"Icelandic volcanic fields","bbox":"-22.5,63.75,-22.0,64.0"},
 "death":{"name":"Death Valley region","bbox":"-117.0,36.1,-116.6,36.4"},
}
s=requests.Session()
s.headers.update({"User-Agent":"ANALOG-X/1.1 MODIS browse discovery","Accept":"application/json"})
retry=Retry(total=3,connect=3,read=3,backoff_factor=1,status_forcelist=(429,500,502,503,504),allowed_methods=frozenset(["GET"]),respect_retry_after_header=True)
s.mount("https://",HTTPAdapter(max_retries=retry))
def main():
 OUT.mkdir(parents=True,exist_ok=True);BROWSE.mkdir(parents=True,exist_ok=True)
 results=[]
 for sid,site in SITES.items():
  params={"short_name":"MOD11A2","version":"061","bounding_box":site["bbox"],
          "temporal":"2025-11-01T00:00:00Z,2026-11-14T23:59:59Z",
          "page_size":5,"sort_key":"-start_date"}
  rec={"site_id":sid,"site":site,"status":"not_found","granules":[]}
  try:
   r=s.get(CMR,params=params,timeout=(20,90));r.raise_for_status()
   entries=r.json().get("feed",{}).get("entry",[])
   for entry in entries:
    browse=[]
    for link in entry.get("links",[]):
     href=link.get("href","")
     rel=link.get("rel","").lower()
     if href.startswith("https://") and "browse" in rel:
      browse.append(href)
    rec["granules"].append({"id":entry.get("id"),"producer_granule_id":entry.get("producer_granule_id"),
      "time_start":entry.get("time_start"),"time_end":entry.get("time_end"),
      "day_night_flag":entry.get("day_night_flag"),"browse_urls":browse})
   if entries:
    rec["status"]="metadata_found"
    first=rec["granules"][0]
    for j,url in enumerate(first["browse_urls"][:2]):
     name=re.sub(r"[^A-Za-z0-9_.-]","_",first.get("producer_granule_id") or first["id"])
     dest=BROWSE/(sid+"_"+str(j+1)+".jpg")
     try:
      rr=s.get(url,timeout=(20,90));rr.raise_for_status()
      if "image" not in rr.headers.get("Content-Type","").lower() and not url.lower().endswith((".jpg",".jpeg")):
       raise RuntimeError("Browse URL did not return an image content type")
      if len(rr.content)>15_000_000:raise RuntimeError("Browse image exceeded 15 MB safety limit")
      dest.write_bytes(rr.content)
      first.setdefault("downloaded_browse",[]).append({"path":str(dest.relative_to(ROOT)),"url":url,"bytes":len(rr.content)})
      rec["status"]="browse_downloaded"
     except Exception as exc:
      first.setdefault("browse_errors",[]).append(str(exc))
   print(sid,rec["status"],len(entries),flush=True)
  except Exception as exc:
   rec["status"]="query_error";rec["error"]=str(exc)
   print(sid,"ERROR",str(exc),flush=True)
  results.append(rec)
 out={"schema_version":"1.0","generated_at_utc":datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
  "provider":"NASA Earthdata CMR / MODIS Terra MOD11A2 V061",
  "product":"8-day land-surface temperature and emissivity, 1 km sinusoidal grid",
  "purpose":"Recent public browse-tile discovery for the curated Earth study sites.",
  "important_limitations":["Downloaded browse JPEGs are not clipped to the AOI and are not quantitative LST arrays.","Do not read temperatures from display colours or use browse images as calibrated measurement values.","The MOD11A2 science granules contain day/night LST, emissivity and QA layers; scaling, fill values and QA must be decoded before analysis.","CMR metadata discovery does not prove the science HDF file is anonymously downloadable; Earthdata Login may be required."],
  "site_count":len(results),"browse_download_count":sum(len(g.get("downloaded_browse",[])) for x in results for g in x["granules"]),
  "sites":results}
 (OUT/"modis_browse_index.json").write_text(json.dumps(out,indent=2,allow_nan=False)+"\n",encoding="utf-8")
 print(json.dumps({"output":"data/nasa/modis_browse_index.json","sites":len(results),"browse_download_count":out["browse_download_count"],"statuses":{x["site_id"]:x["status"] for x in results}},indent=2))
if __name__=="__main__":main()

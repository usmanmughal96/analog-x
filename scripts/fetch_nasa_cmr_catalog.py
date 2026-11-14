#!/usr/bin/env python3
"""Discover relevant NASA Earthdata collections and MODIS LST granules via CMR.

This pipeline uses NASA's public Common Metadata Repository (CMR) search API.
It does not download science granules or imply that discovery metadata itself is
a temperature measurement.
"""
from __future__ import annotations
import json,sys
from datetime import datetime,timezone
from pathlib import Path
from urllib.parse import urlparse
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"data"/"nasa"
CMR="https://cmr.earthdata.nasa.gov/search"
SITES={
 "koh_i_sultan":{"name":"Koh-i-Sultan / Chagai, Pakistan","bbox":"62.70,29.00,62.90,29.20"},
 "hispar_glacier":{"name":"Hispar Glacier / Karakoram, Pakistan","bbox":"75.12,36.02,75.34,36.22"}
}
COLLECTIONS=[
 {"short_name":"MOD11A2","version":"061","role":"Terra MODIS 8-day land-surface temperature and emissivity"},
 {"short_name":"MYD11A2","version":"061","role":"Aqua MODIS 8-day land-surface temperature and emissivity"},
 {"short_name":"MCD12Q1","version":"061","role":"Annual global land-cover type"},
 {"short_name":"M2T1NXAER","version":None,"role":"MERRA-2 hourly aerosol diagnostics, including dust-related fields"},
]
SESSION=requests.Session()
SESSION.headers.update({"User-Agent":"ANALOG-X/1.0 NASA CMR open metadata discovery","Accept":"application/json"})
retry=Retry(total=3,connect=3,read=3,backoff_factor=1,
 status_forcelist=(429,500,502,503,504),allowed_methods=frozenset(["GET"]),
 respect_retry_after_header=True)
SESSION.mount("https://",HTTPAdapter(max_retries=retry))

def utcnow():
 return datetime.now(timezone.utc).replace(microsecond=0).isoformat()

def request_json(path,params):
 url=CMR+"/"+path
 r=SESSION.get(url,params=params,timeout=(20,90))
 if r.status_code!=200:
  raise RuntimeError(f"CMR HTTP {r.status_code}: {r.text[:700]}")
 return r.json(),r.url

def safe_links(entry):
 out=[]
 for link in entry.get("links",[]):
  href=link.get("href")
  if not href:continue
  # keep only public metadata/browse/download links, never credentials or tokens
  rel=link.get("rel","")
  if any(x in rel.lower() for x in ["data#","browse#","metadata#","service#"]):
   out.append({"rel":rel,"title":link.get("title"),"href":href})
 return out[:12]

def collection_search(spec):
 params={"short_name":spec["short_name"],"page_size":10}
 if spec.get("version"):params["version"]=spec["version"]
 data,url=request_json("collections.json",params)
 entries=data.get("feed",{}).get("entry",[])
 results=[]
 for e in entries:
  results.append({
   "id":e.get("id"),"title":e.get("title"),"short_name":e.get("short_name"),
   "version_id":e.get("version_id"),"summary":e.get("summary"),
   "time_start":e.get("time_start"),"time_end":e.get("time_end"),
   "data_center":e.get("data_center"),"archive_center":e.get("archive_center"),
   "coordinate_system":e.get("coordinate_system"),"links":safe_links(e)
  })
 return {"query_url":url,"count":len(results),"collections":results,
         "status":"found" if results else "no matching collection"}

def granule_search(site_id,site):
 params={
  "short_name":"MOD11A2","version":"061","bounding_box":site["bbox"],
  "temporal":"2026-08-01T00:00:00Z,2026-11-14T23:59:59Z",
  "page_size":10,"sort_key":"-start_date"
 }
 data,url=request_json("granules.json",params)
 entries=data.get("feed",{}).get("entry",[])
 items=[]
 for e in entries:
  links=safe_links(e)
  items.append({
   "id":e.get("id"),"producer_granule_id":e.get("producer_granule_id"),
   "title":e.get("title"),"time_start":e.get("time_start"),
   "time_end":e.get("time_end"),"day_night_flag":e.get("day_night_flag"),
   "cloud_cover":e.get("cloud_cover"),"granule_size":e.get("granule_size"),
   "links":links
  })
 return {"query_url":url,"returned_count":len(items),"items":items,
         "status":"granules_found" if items else "no granules returned"}
 
def main():
 OUT.mkdir(parents=True,exist_ok=True)
 out={
  "generated_at_utc":utcnow(),
  "provider":"NASA Earthdata / Common Metadata Repository (CMR)",
  "api":"https://cmr.earthdata.nasa.gov/search",
  "access":"Public collection/granule metadata search; granule data access can require Earthdata Login depending on provider and endpoint.",
  "collections":{},
  "site_granules":{},
  "limitations":[
   "This is catalogue and granule discovery, not ingestion of MODIS measurements.",
   "MOD11A2 is an 8-day land-surface-temperature product; its scale factors, QA flags, day/night bands and fill values must be decoded before scientific use.",
   "Granule discovery alone does not prove that all science assets are anonymously downloadable."
  ]
 }
 failures=[]
 for spec in COLLECTIONS:
  try:
   item=collection_search(spec)
   item["role"]=spec["role"]
   out["collections"][spec["short_name"]]=item
   print(f"[COLLECTION] {spec['short_name']}: {item['count']} matches",flush=True)
  except Exception as exc:
   out["collections"][spec["short_name"]]={"status":"search_error","role":spec["role"],"error":str(exc)}
   failures.append(spec["short_name"])
 for site_id,site in SITES.items():
  try:
   r=granule_search(site_id,site)
   r["site"]=site
   out["site_granules"][site_id]=r
   print(f"[GRANULES] {site_id}: {r['returned_count']} MOD11A2 granules",flush=True)
  except Exception as exc:
   out["site_granules"][site_id]={"status":"search_error","site":site,"error":str(exc)}
   failures.append("granules:"+site_id)
 (OUT/"earthdata_cmr_catalog.json").write_text(json.dumps(out,indent=2,allow_nan=False)+"\n",encoding="utf-8")
 print(json.dumps({"collection_counts":{k:v.get("count") for k,v in out["collections"].items()},
  "site_granule_counts":{k:v.get("returned_count") for k,v in out["site_granules"].items()},
  "failures":failures},indent=2),flush=True)
 # A CMR outage should be visible, but it should not break unrelated data feeds.
 return 0

if __name__=="__main__":
 raise SystemExit(main())

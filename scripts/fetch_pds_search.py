#!/usr/bin/env python3
"""Discover relevant Moon/Mars PDS products through the public PDS Search API.

Metadata discovery is intentionally separated from binary ingestion. Product
records and their source links are stored with query provenance; this script
never implies that every product is directly downloadable or analysis-ready.
"""
from __future__ import annotations
import json
from datetime import datetime, timezone
from pathlib import Path
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"data"/"planetary"/"pds_search.json"
API="https://pds.nasa.gov/api/search/1/products"
QUERIES=[
 {"id":"mars_target","q":'(ref_lid_target eq "urn:nasa:pds:context:target:planet.mars")',"target":"Mars","instrument_filter":None,"purpose":"Search observational products explicitly associated with the Mars target identifier."},
 {"id":"mars_mola","q":'(ref_lid_target eq "urn:nasa:pds:context:target:planet.mars")',"target":"Mars","instrument_filter":"mola","purpose":"Filter Mars-target products for MOLA instrument metadata."},
 {"id":"mars_hirise","q":'(ref_lid_target eq "urn:nasa:pds:context:target:planet.mars")',"target":"Mars","instrument_filter":"hirise","purpose":"Filter Mars-target products for HiRISE instrument metadata."},
 {"id":"moon_target","q":'(ref_lid_target eq "urn:nasa:pds:context:target:satellite.moon")',"target":"Moon","instrument_filter":None,"purpose":"Search observational products explicitly associated with the Moon target identifier."},
 {"id":"moon_lola","q":'(ref_lid_target eq "urn:nasa:pds:context:target:satellite.moon")',"target":"Moon","instrument_filter":"lola","purpose":"Filter Moon-target products for LOLA instrument metadata."},
 {"id":"moon_diviner","q":'(ref_lid_target eq "urn:nasa:pds:context:target:satellite.moon")',"target":"Moon","instrument_filter":"diviner","purpose":"Filter Moon-target products for Diviner instrument metadata."},
]
s=requests.Session()
s.headers.update({"User-Agent":"ANALOG-X/1.1 PDS public search integration","Accept":"application/json"})
retry=Retry(total=3,connect=3,read=3,backoff_factor=1,status_forcelist=(429,500,502,503,504),allowed_methods=frozenset(["GET"]),respect_retry_after_header=True)
s.mount("https://",HTTPAdapter(max_retries=retry))
def main():
 OUT.parent.mkdir(parents=True,exist_ok=True)
 results=[]
 for q in QUERIES:
  params={"limit":100,"q":q["q"]}
  try:
   r=s.get(API,params=params,timeout=(20,90));r.raise_for_status()
   payload=r.json()
   # Keep the source response shape available; compact the UI-facing record list.
   products=payload.get("data",[]) if isinstance(payload,dict) else []
   if not products and isinstance(payload,dict):
    products=payload.get("results",[])
   relevant=[x for x in products[:100] if x.get("type") != "Product_Service"]
   if q.get("instrument_filter"):
    token=q["instrument_filter"].lower()
    relevant=[x for x in relevant if token in json.dumps(x.get("observing_system_components",[])).lower() or token in str(x.get("title","")).lower() or token in json.dumps(x.get("properties",{})).lower()]
   results.append({**q,"status":"results_returned" if relevant else "no_relevant_products_returned",
      "query_url":r.url,"returned_count":len(relevant),"raw_result_count":len(products),"products":relevant,
      "response_summary":payload.get("summary") if isinstance(payload,dict) else None})
   print(q["id"],"raw",len(products),"relevant",len(relevant),flush=True)
  except Exception as exc:
   detail = (exc.response.text[:1200] if isinstance(exc, requests.HTTPError) and exc.response is not None else str(exc))
   results.append({**q,"status":"query_error","query_url":None,"returned_count":0,"error":detail,"products":[]})
   print(q["id"],"ERROR",str(exc),flush=True)
 out={"schema_version":"1.0","generated_at_utc":datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
      "provider":"NASA Planetary Data System Search API","api":API,
      "access_note":"Public product metadata discovery. A result is not proof that a binary product is directly downloadable, calibrated, spatially complete or ready for scientific use.",
      "queries":results,"query_count":len(results),
      "results_returned":sum(x["returned_count"] for x in results),
      "limitations":["PDS Search API documentation warns that the registry is not fully populated; zero results do not prove the archive lacks data.","Review product labels, instrument calibration, coordinate system, units, spatial coverage, version and licence before processing.","Binary ingestion is a separate step; do not interpret metadata as measurements."]}
 OUT.write_text(json.dumps(out,indent=2,allow_nan=False)+"\n",encoding="utf-8")
 print(json.dumps({"output":str(OUT.relative_to(ROOT)),"results_returned":out["results_returned"],"query_statuses":{x["id"]:x["status"] for x in results}},indent=2))
if __name__=="__main__":main()

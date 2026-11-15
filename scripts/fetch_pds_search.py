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
API="https://pds.nasa.gov/api/search/1/classes/observational"
QUERIES=[
 {"id":"mars_target","q":'(ref_lid_target eq "urn:nasa:pds:context:target:planet.mars")',"target":"Mars","instrument_filter":None,"purpose":"Search observational products explicitly associated with the Mars target identifier."},
 {"id":"mars_mola","q":'(ref_lid_instrument eq "urn:nasa:pds:context:instrument:mgs.mola")',"target":"Mars","instrument_filter":None,"purpose":"Search PDS observational products linked to the MGS MOLA instrument."},
 {"id":"mars_hirise","q":'(ref_lid_instrument eq "urn:nasa:pds:context:instrument:hirise.mro")',"target":"Mars","instrument_filter":None,"purpose":"Search PDS observational products linked to the MRO HiRISE instrument."},
 {"id":"moon_target","q":'(ref_lid_target eq "urn:nasa:pds:context:target:satellite.moon")',"target":"Moon","instrument_filter":None,"purpose":"Search observational products explicitly associated with the Moon target identifier."},
 {"id":"moon_lola","q":'(ref_lid_instrument eq "urn:nasa:pds:context:instrument:lro.lola")',"target":"Moon","instrument_filter":None,"purpose":"Search PDS observational products linked to the LRO LOLA instrument."},
 {"id":"moon_diviner","q":'(ref_lid_instrument eq "urn:nasa:pds:context:instrument:lro.dlre")',"target":"Moon","instrument_filter":None,"purpose":"Search PDS observational products linked to the LRO Diviner instrument."},
]
s=requests.Session()
s.headers.update({"User-Agent":"ANALOG-X/1.1 PDS public search integration","Accept":"application/json"})
retry=Retry(total=3,connect=3,read=3,backoff_factor=1,status_forcelist=(429,500,502,503,504),allowed_methods=frozenset(["GET"]),respect_retry_after_header=True)
s.mount("https://",HTTPAdapter(max_retries=retry))
def compact_product(product):
 props=product.get("properties",{}) or {}
 def first(key):
  value=props.get(key)
  return value[0] if isinstance(value,list) and value else value
 metadata=product.get("metadata",{}) or {}
 return {
  "id":product.get("id"),"type":product.get("type"),"title":product.get("title"),
  "start_date_time":product.get("start_date_time"),"stop_date_time":product.get("stop_date_time"),
  "targets":product.get("targets",[])[:8],
  "observing_system_components":product.get("observing_system_components",[])[:8],
  "data_file_url":first("ops:Data_File_Info.ops:file_ref"),
  "data_file_name":first("ops:Data_File_Info.ops:file_name"),
  "label_url":metadata.get("label_url"),
  "instrument_refs":props.get("ref_lid_instrument",[])[:8] if isinstance(props.get("ref_lid_instrument",[]),list) else []
 }


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
   relevant=[x for x in products[:100] if x.get("type") == "Product_Observational" or x.get("product_class") == "observational"]
   if q.get("instrument_filter"):
    token=q["instrument_filter"].lower()
    relevant=[x for x in relevant if token in json.dumps(x.get("observing_system_components",[])).lower() or token in str(x.get("title","")).lower() or token in json.dumps(x.get("properties",{})).lower()]
   results.append({**q,"status":"results_returned" if relevant else "no_relevant_products_returned",
      "query_url":r.url,"returned_count":len(relevant),"raw_result_count":len(products),"products":[compact_product(x) for x in relevant],
      "response_summary":{"hits":(payload.get("summary") or {}).get("hits")} if isinstance(payload,dict) else None})
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

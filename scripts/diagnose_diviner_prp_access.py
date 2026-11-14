#!/usr/bin/env python3
"""Probe the PDS4 Diviner PRP V2 south-polar collection inventory and assets."""
from __future__ import annotations
import csv,json,sys
from datetime import datetime,timezone
from pathlib import Path
import requests

BASE="https://pds.nasa.gov/data/pds4/releases/geo/lro_diviner_derived1-20260918/"
FILES=[
 "bundle.xml",
 "collection_data_derived_prp.xml",
 "collection_data_derived_prp_inventory.csv",
 "readme.txt"
]
OLD_BASE="https://pds-geosciences.wustl.edu/lro/lro-l-dlre-4-rdr-v1/lrodlr_1001/data/prp/"
OLD_FILES=["DLRE_PRP_SOUTH.TAB","DLRE_PRP_SOUTH.LBL","DLRE_PRP_NORTH.TAB","DLRE_PRP_NORTH.LBL"]
def probe(session,url,read_text=False):
 out={"url":url}
 try:
  h=session.head(url,allow_redirects=True,timeout=(20,60))
  out.update({"head_status":h.status_code,"content_type":h.headers.get("Content-Type"),
   "content_length":h.headers.get("Content-Length"),"accept_ranges":h.headers.get("Accept-Ranges"),
   "final_url":h.url})
  if read_text:
   r=session.get(url,timeout=(20,90))
   out["get_status"]=r.status_code
   if r.status_code==200:
    out["text"]=r.text[:25000]
  else:
   r=session.get(url,headers={"Range":"bytes=0-1023"},timeout=(20,60))
   out.update({"range_status":r.status_code,"range_bytes":len(r.content),
     "content_range":r.headers.get("Content-Range")})
 except Exception as exc:
  out["error"]=repr(exc)
 return out
def main():
 s=requests.Session();s.headers.update({"User-Agent":"ANALOG-X/1.0 PDS product access diagnostic"})
 result={"generated_at_utc":datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
         "provider":"NASA PDS4 / LRO Diviner derived bundle",
         "base":BASE,"pds4":{},"pds3_alternative":{}}
 for fn in FILES:
  result["pds4"][fn]=probe(s,BASE+fn,read_text=fn.endswith(".xml") or fn.endswith(".txt") or fn.endswith(".csv"))
 for fn in OLD_FILES:
  result["pds3_alternative"][fn]=probe(s,OLD_BASE+fn,read_text=fn.endswith(".LBL"))
 outdir=Path("data/moon/diviner_prp_diagnostic");outdir.mkdir(parents=True,exist_ok=True)
 (outdir/"report.json").write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
 print(json.dumps({"pds4":{k:{kk:v.get(kk) for kk in ("head_status","content_length","get_status","range_status","error")} for k,v in result["pds4"].items()},
   "pds3":{k:{kk:v.get(kk) for kk in ("head_status","content_length","get_status","range_status","error")} for k,v in result["pds3_alternative"].items()}},indent=2),flush=True)
 return 0
if __name__=="__main__":raise SystemExit(main())

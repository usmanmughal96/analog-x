#!/usr/bin/env python3
"""Probe the PDS4 Diviner PRP V2 south-polar collection inventory and assets."""
from __future__ import annotations
import csv,json,re,sys
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
OLD_VOLUME_BASE="https://pds-geosciences.wustl.edu/lro/lro-l-dlre-4-rdr-v1/lrodlr_1001/"
PDS3_DATA_BASE=OLD_VOLUME_BASE+"data/prp/"
PDS3_LABEL_BASE=OLD_VOLUME_BASE+"label/"
PDS3_CATALOG_BASE=OLD_VOLUME_BASE+"catalog/"
PDS4_MIRROR_BASE="https://pds-geosciences.wustl.edu/lro/urn-nasa-pds-lro_diviner_derived1/"
PDS3_DATA_FILES=["DLRE_PRP_SOUTH.TAB","DLRE_PRP_SOUTH.LBL","DLRE_PRP_NORTH.TAB","DLRE_PRP_NORTH.LBL"]
PDS3_FORMAT_FILES=["DLRE_PRP.FMT"]
PDS3_CATALOG_FILES=["PRPDS.CAT"]
PDS4_PRODUCT_CANDIDATES=[
 "data_derived_prp/DLRE_PRP_SOUTH.xml",
 "data_derived_prp/dlre_prp_south.xml",
 "data_derived_prp/DLRE_PRP_SOUTH.TAB",
 "data_derived_prp/DLRE_PRP_NORTH.xml",
 "data_derived_prp/dlre_prp_north.xml"
]
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
   if url.upper().endswith(".FMT") or url.lower().endswith(".cat"):
    full=session.get(url,timeout=(20,90))
    out["format_get_status"]=full.status_code
    if full.status_code==200:out["text"]=full.text[:30000]
   if url.upper().endswith(".TAB"):
    out["range_text"]=r.text[:1024]
 except Exception as exc:
  out["error"]=repr(exc)
 return out
def main():
 s=requests.Session();s.headers.update({"User-Agent":"ANALOG-X/1.0 PDS product access diagnostic"})
 result={"generated_at_utc":datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
         "provider":"NASA PDS4 / LRO Diviner derived bundle",
         "base":BASE,"pds4":{},"pds3_alternative":{},"pds3_format_files":{},"pds3_catalog_files":{},"pds4_product_candidates":{}}
 for fn in FILES:
  result["pds4"][fn]=probe(s,BASE+fn,read_text=fn.endswith(".xml") or fn.endswith(".txt") or fn.endswith(".csv"))
 for fn in PDS3_DATA_FILES:
  result["pds3_alternative"][fn]=probe(s,PDS3_DATA_BASE+fn,read_text=fn.endswith(".LBL"))
 for fn in PDS3_FORMAT_FILES:
  result["pds3_format_files"][fn]=probe(s,PDS3_LABEL_BASE+fn,read_text=True)
 for fn in PDS3_CATALOG_FILES:
  result["pds3_catalog_files"][fn]=probe(s,PDS3_CATALOG_BASE+fn,read_text=True)
 # The PDS4 migration mirror can expose labels separately from the legacy volume.
 for fn in ["DLRE_PRP.FMT","PRPDS.CAT"]:
  directory="label/" if fn.endswith(".FMT") else "catalog/"
  result["pds3_format_files" if fn.endswith(".FMT") else "pds3_catalog_files"]["mirror/"+fn]=probe(s,PDS4_MIRROR_BASE+directory+fn,read_text=True)
 for path in PDS4_PRODUCT_CANDIDATES:
  result["pds4_product_candidates"][path]=probe(s,PDS4_MIRROR_BASE+path,read_text=path.lower().endswith(".xml"))
 fmt=result["pds3_format_files"].get("DLRE_PRP.FMT",{}).get("text") or result["pds3_format_files"].get("mirror/DLRE_PRP.FMT",{}).get("text") or ""
 columns=[]
 for block in re.findall(r"(?ims)^\s*OBJECT\s*=\s*COLUMN(.*?)^\s*END_OBJECT\s*=\s*COLUMN",fmt):
  def field(name):
   m=re.search(r"(?im)^\s*"+re.escape(name)+r"\s*=\s*(.+)$",block)
   return m.group(1).strip().strip('"') if m else None
  columns.append({"name":field("NAME"),"unit":field("UNIT"),"data_type":field("DATA_TYPE"),"format":field("FORMAT"),"missing_constant":field("MISSING_CONSTANT"),"description":field("DESCRIPTION")})
 result["format_columns"]=columns
 target_columns={x.get("name"):x for x in columns if x.get("name") in {"temp_avg","temp_max","ice_depth"}}
 result["interpretation_status"]="field units and missing-value definitions retrieved" if all(target_columns.get(k,{}).get("unit") and target_columns.get(k,{}).get("missing_constant") is not None for k in ("temp_avg","temp_max","ice_depth")) else "format metadata still incomplete; do not interpret numeric fields"
 outdir=Path("data/moon/diviner_prp_diagnostic");outdir.mkdir(parents=True,exist_ok=True)
 (outdir/"report.json").write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
 def summarize(group):
  return {k:{kk:v.get(kk) for kk in ("head_status","content_length","get_status","range_status","error")} for k,v in group.items()}
 print(json.dumps({"pds4":summarize(result["pds4"]),"pds3":summarize(result["pds3_alternative"]),
  "format":summarize(result["pds3_format_files"]),"catalog":summarize(result["pds3_catalog_files"]),
  "pds4_product_candidates":summarize(result["pds4_product_candidates"]),
  "format_columns":columns,"interpretation_status":result["interpretation_status"]},indent=2),flush=True)
 return 0
if __name__=="__main__":raise SystemExit(main())

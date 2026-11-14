#!/usr/bin/env python3
"""Test the MIT-hosted NASA LOLA south-polar 80 m JP2 DEM/count alternative.

This script only probes HEAD, byte-range access and the detached PDS labels.
It does not publish raster values until coordinate-system and grid alignment
are verified.
"""
from __future__ import annotations
import json,sys
from datetime import datetime,timezone
from pathlib import Path
import requests

BASE="https://imbrium.mit.edu/DATA/LOLA_GDR/POLAR/JP2/"
ASSETS={
 "ldem_jp2":"LDEM_80S_80M.JP2",
 "ldem_label":"LDEM_80S_80M_JP2.LBL",
 "ldem_aux":"LDEM_80S_80M_AUX.XML",
 "ldec_jp2":"LDEC_80S_80M.JP2",
 "ldec_label":"LDEC_80S_80M_JP2.LBL",
 "ldec_aux":"LDEC_80S_80M_AUX.XML"
}
def main():
 session=requests.Session()
 session.headers.update({"User-Agent":"ANALOG-X/1.0 NASA LOLA PDS access diagnostic"})
 result={"generated_at_utc":datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
         "provider":"NASA LRO LOLA PDS archive mirrored by MIT Imbrium",
         "base_url":BASE,"assets":{}}
 outdir=Path("data/moon/mit_lola_diagnostic");outdir.mkdir(parents=True,exist_ok=True)
 for key,name in ASSETS.items():
  url=BASE+name
  item={"url":url}
  try:
   h=session.head(url,allow_redirects=True,timeout=(15,45))
   item.update({"head_status":h.status_code,"content_type":h.headers.get("Content-Type"),
     "content_length":h.headers.get("Content-Length"),"accept_ranges":h.headers.get("Accept-Ranges"),
     "last_modified":h.headers.get("Last-Modified"),"final_url":h.url})
   if key.endswith("_label") or key.endswith("_aux"):
    r=session.get(url,timeout=(15,60))
    item["get_status"]=r.status_code
    if r.status_code==200:
     text=r.text[:20000]
     item["text_sample"]=text[:12000]
     (outdir/name).write_text(text,encoding="utf-8",errors="replace")
   else:
    r=session.get(url,headers={"Range":"bytes=0-1023"},timeout=(15,60))
    item.update({"range_status":r.status_code,"range_bytes":len(r.content),
      "content_range":r.headers.get("Content-Range"),"range_content_type":r.headers.get("Content-Type")})
  except Exception as exc:
   item["error"]=repr(exc)
  result["assets"][key]=item
  print(json.dumps({key:item},indent=2),flush=True)
 (outdir/"report.json").write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
 print("Diagnostic complete.",flush=True)
 return 0
if __name__=="__main__":
 raise SystemExit(main())

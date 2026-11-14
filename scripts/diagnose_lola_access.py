#!/usr/bin/env python3
"""Diagnose NASA PGDA Site04 LOLA 5 m COG range-read access.

Metadata and one small central pixel window are read only. This is a diagnostic
and does not create scientific terrain metrics.
"""
from __future__ import annotations
import json,sys
from datetime import datetime,timezone
from pathlib import Path
import rasterio
from rasterio.windows import Window

BASE="https://core2.gsfc.nasa.gov/PGDA/LOLA_5mpp/Site04/"
FILES={
 "elevation":"Site04_final_adj_5mpp_surf.tif",
 "counts":"Site04_final_adj_5mpp_ldec.tif",
 "slope":"Site04_final_adj_5mpp_slp.tif",
 "z_uncertainty":"Site04_final_adj_5mpp_toterr.tif",
 "slope_uncertainty":"Site04_final_adj_5mpp_slperr.tif"
}
ENV={
 "GDAL_DISABLE_READDIR_ON_OPEN":"EMPTY_DIR",
 "CPL_VSIL_CURL_ALLOWED_EXTENSIONS":".tif",
 "GDAL_HTTP_MAX_RETRY":"2",
 "GDAL_HTTP_RETRY_DELAY":"1",
 "GDAL_HTTP_TIMEOUT":"45",
 "GDAL_CACHEMAX":128
}
def main():
 out={"generated_at_utc":datetime.now(timezone.utc).replace(microsecond=0).isoformat(),"files":{}}
 with rasterio.Env(**ENV):
  for key,name in FILES.items():
   url=BASE+name
   rec={"url":url}
   try:
    with rasterio.open("/vsicurl/"+url) as ds:
     rec.update({"status":"opened","width":ds.width,"height":ds.height,"crs":str(ds.crs),
       "bounds":[ds.bounds.left,ds.bounds.bottom,ds.bounds.right,ds.bounds.top],
       "transform":[ds.transform.a,ds.transform.b,ds.transform.c,ds.transform.d,ds.transform.e,ds.transform.f],
       "dtype":ds.dtypes[0],"nodata":ds.nodata,"block_shapes":ds.block_shapes,
       "overviews":ds.overviews(1),"driver":ds.driver})
     # A very small window tests byte-range access independently of a full read.
     w=min(128,ds.width);h=min(128,ds.height)
     win=Window(max(0,(ds.width-w)//2),max(0,(ds.height-h)//2),w,h)
     try:
      a=ds.read(1,window=win,masked=True)
      rec["small_window"]={"status":"read","shape":[int(a.shape[0]),int(a.shape[1])],
        "valid_count":int(a.count()),"min":float(a.min()) if a.count() else None,
        "max":float(a.max()) if a.count() else None}
     except Exception as exc:
      rec["small_window"]={"status":"failed","error":repr(exc)}
   except Exception as exc:
    rec["status"]="open_failed";rec["error"]=repr(exc)
   out["files"][key]=rec
   print(json.dumps({key:rec},indent=2),flush=True)
 outdir=Path("data/moon");outdir.mkdir(parents=True,exist_ok=True)
 (outdir/"lola_access_diagnostic.json").write_text(json.dumps(out,indent=2)+"\n",encoding="utf-8")
 return 0
if __name__=="__main__":
 raise SystemExit(main())

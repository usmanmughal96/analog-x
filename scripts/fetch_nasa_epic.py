#!/usr/bin/env python3
"""Fetch latest NASA DSCOVR/EPIC natural-colour image.

The EPIC website's public API is used directly; unlike the api.nasa.gov mirror,
this current endpoint does not require an API key. NASA_API_KEY is kept as a
server-side environment variable for future api.nasa.gov endpoints that need
it, but this public EPIC feed does not consume it.
"""
from __future__ import annotations
import json
from datetime import datetime, timezone
from pathlib import Path
import requests

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"data"/"nasa"
API="https://epic.gsfc.nasa.gov/api/natural"

def utcnow():
 return datetime.now(timezone.utc).replace(microsecond=0).isoformat()

def main():
 OUT.mkdir(parents=True,exist_ok=True)
 try:
  r=requests.get(API,headers={"User-Agent":"ANALOG-X/1.0"},timeout=(20,90))
  r.raise_for_status()
  payload=r.json()
  if not isinstance(payload,list) or not payload:
   raise RuntimeError("EPIC API returned no natural-colour images")
  item=payload[-1]
  date=item.get("date","")
  date_str=date.split(" ")[0]
  parts=date_str.split("-")
  if len(parts)!=3:raise RuntimeError(f"Unexpected EPIC date format: {date!r}")
  image=item.get("image")
  if not image:raise RuntimeError("EPIC metadata had no image identifier")
  image_url=f"https://epic.gsfc.nasa.gov/archive/natural/{parts[0]}/{parts[1]}/{parts[2]}/png/{image}.png"
  image_response=requests.get(image_url,headers={"User-Agent":"ANALOG-X/1.0"},timeout=(20,120))
  image_response.raise_for_status()
  if not image_response.headers.get("Content-Type","").startswith("image/"):
   raise RuntimeError("EPIC archive response was not an image")
  image_path=OUT/"epic_latest.png"
  image_path.write_bytes(image_response.content)
  metadata={
   "provider":"NASA DSCOVR / EPIC",
   "product":"Natural-colour full-disk Earth image",
   "image_id":image,
   "date":date,
   "caption":item.get("caption"),
   "centroid_coordinates":item.get("centroid_coordinates"),
   "dscovr_j2000_position":item.get("dscovr_j2000_position"),
   "sun_j2000_position":item.get("sun_j2000_position"),
   "image_path":"./epic_latest.png",
   "image_url":image_url,
   "api_documentation":"https://epic.gsfc.nasa.gov/about/api",
   "fetched_at_utc":utcnow(),
   "authentication_mode":"Public EPIC endpoint; no NASA API key required",
   "note":"Global full-disk context imagery only; not used for site-scale analog metrics or surface interpretation."
  }
  (OUT/"epic_latest.json").write_text(json.dumps(metadata,indent=2)+"\n",encoding="utf-8")
  print(json.dumps({"status":"success","date":date,"image_id":image,"bytes":len(image_response.content)},indent=2),flush=True)
  return 0
 except Exception as exc:
  result={"provider":"NASA DSCOVR / EPIC","status":"unavailable","error":str(exc),"fetched_at_utc":utcnow(),
          "note":"EPIC is optional global context imagery. Core site analysis remains available from NASA POWER and Sentinel-2 records."}
  (OUT/"epic_latest.json").write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
  print(json.dumps(result,indent=2),flush=True)
  return 0

if __name__=="__main__":
 raise SystemExit(main())

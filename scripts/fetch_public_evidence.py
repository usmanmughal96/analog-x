#!/usr/bin/env python3
"""Discover public Sentinel-2 L2A scenes and EvK2CNR glacier metadata.

Metadata discovery only: this script does not download full Sentinel-2 raster
assets or redistribute third-party imagery. Planetary Computer STAC metadata is
public and anonymous; Azure data assets, when downloaded separately, need a
short-lived SAS URL from Microsoft's public token endpoint.
"""
from __future__ import annotations
import json
from datetime import datetime, timezone
from pathlib import Path
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"data"/"pakistan"
STAC="https://planetarycomputer.microsoft.com/api/stac/v1"
SEARCH=STAC+"/search"
EVK2_UUID="60565650-b68d-4db2-8873-53b94b4ed56b"
EVK2_RECORD=f"https://geoportal.mountaingenius.org/geonetwork/srv/api/records/{EVK2_UUID}"

SITES={
 "koh_i_sultan":{
   "name":"Koh-i-Sultan / Chagai",
   "country":"Pakistan",
   "latitude":29.1,"longitude":62.8,
   "bbox":[62.70,29.00,62.90,29.20],
   "role":"Volcanic outcrop mapping and sample-context workflow candidate",
   "coordinate_note":"Smithsonian GVP catalogue coordinate; not a surveyed field boundary."
 },
 "hispar_glacier":{
   "name":"Hispar Glacier / Hispar-Passu region",
   "country":"Pakistan",
   "latitude":36.10572,"longitude":75.23341,
   "bbox":[75.12,36.02,75.34,36.22],
   "role":"Cryosphere imaging, debris/ice boundary interpretation and sensor/sample-handling workflow candidate",
   "coordinate_note":"Approximate gazetteer reference point for scene discovery, not an official EvK2CNR glacier centroid or field-access point."
 }
}

session=requests.Session()
retry=Retry(total=3,connect=3,read=3,backoff_factor=1.0,
            status_forcelist=(429,500,502,503,504),
            allowed_methods=frozenset(["GET","POST"]),
            respect_retry_after_header=True)
session.mount("https://",HTTPAdapter(max_retries=retry))
session.headers.update({"User-Agent":"ANALOG-X/1.0 public geospatial metadata discovery","Accept":"application/geo+json, application/json"})

def now():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()

def stac_search(site,datetime_range,cloud_limit):
    body={
      "collections":["sentinel-2-l2a"],
      "bbox":site["bbox"],
      "datetime":datetime_range,
      "limit":25
    }
    if cloud_limit is not None:
      body["query"]={"eo:cloud_cover":{"lt":cloud_limit}}
    r=session.post(SEARCH,json=body,timeout=(20,90))
    if r.status_code!=200:
      raise RuntimeError(f"STAC HTTP {r.status_code}: {r.text[:1000]}")
    payload=r.json()
    if payload.get("type")!="FeatureCollection":
      raise RuntimeError("STAC response was not a GeoJSON FeatureCollection")
    return payload

def summarize_item(item):
    p=item.get("properties",{})
    assets=item.get("assets",{})
    chosen={}
    for key in ["visual","preview","thumbnail","B02","B03","B04","B08","B11","B12","SCL"]:
      if key in assets:
        a=assets[key]
        chosen[key]={
          "href":a.get("href"),
          "type":a.get("type"),
          "roles":a.get("roles",[]),
          "title":a.get("title")
        }
    return {
      "id":item.get("id"),
      "collection":item.get("collection"),
      "datetime":p.get("datetime") or p.get("start_datetime"),
      "platform":p.get("platform"),
      "instruments":p.get("instruments"),
      "mgrs_tile":p.get("s2:mgrs_tile"),
      "cloud_cover_percent":p.get("eo:cloud_cover"),
      "processing_baseline":p.get("s2:processing_baseline"),
      "geometry":item.get("geometry"),
      "assets":chosen,
      "self":next((x.get("href") for x in item.get("links",[]) if x.get("rel")=="self"),None)
    }

def get_scene_set(site_id,site):
    windows=[]
    if site_id=="hispar_glacier":
      windows.append(("inventory_reference_period","2022-07-31T00:00:00Z/2022-10-01T23:59:59Z"))
    windows.append(("recent_archive","2024-01-01T00:00:00Z/2026-11-14T23:59:59Z"))
    results=[]
    for label,window in windows:
      try:
        payload=stac_search(site,window,30)
        items=payload.get("features",[])
        used_filter=30
        if not items:
          payload=stac_search(site,window,None)
          items=payload.get("features",[])
          used_filter=None
        summaries=[summarize_item(x) for x in items]
        summaries.sort(key=lambda x:(
          9999 if x["cloud_cover_percent"] is None else x["cloud_cover_percent"],
          x["datetime"] or ""
        ))
        results.append({
          "window":label,
          "datetime_range":window,
          "cloud_filter_lt_percent":used_filter,
          "returned_count":len(summaries),
          "items":summaries[:12],
          "next_page_available":bool(payload.get("links") and any(l.get("rel")=="next" for l in payload["links"])),
          "status":"success" if summaries else "no scenes returned for this query"
        })
      except Exception as exc:
        results.append({"window":label,"datetime_range":window,"status":"error","error":str(exc),"items":[]})
    return results

def try_evk2():
    try:
      r=session.get(EVK2_RECORD,timeout=(20,60))
      if r.status_code!=200:
        return {"status":"metadata endpoint unavailable","http_status":r.status_code,"url":EVK2_RECORD,"note":r.text[:1000]}
      try:
        payload=r.json()
      except ValueError:
        return {"status":"metadata endpoint returned non-JSON","url":EVK2_RECORD,"sample":r.text[:1000]}
      return {"status":"metadata retrieved","url":EVK2_RECORD,"record":payload}
    except Exception as exc:
      return {"status":"request error","url":EVK2_RECORD,"error":str(exc)}

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    catalog={
      "generated_at_utc":now(),
      "planetary_computer":{
        "provider":"Microsoft Planetary Computer",
        "stac_api":STAC,
        "collection":"sentinel-2-l2a",
        "collection_url":STAC+"/collections/sentinel-2-l2a",
        "access":"STAC metadata is public and anonymous; COG assets may require SAS token from https://planetarycomputer.microsoft.com/api/sas/v1/token/sentinel-2-l2a",
        "license":"Copernicus Sentinel data terms; see collection metadata.",
        "sites":{}
      },
      "evk2cnr":{
        "provider":"EvK2CNR SHARE GeoNetwork",
        "inventory_title":"G&S Project - Pakistan Glacier Inventory v.1.0",
        "record_uuid":EVK2_UUID,
        "record":try_evk2(),
        "inventory_reference":"https://geoportal.mountaingenius.org/geonetwork/srv/search?keyword=Glaciers+inventory",
        "geoportal":"https://geoportal.mountaingenius.org/portal/",
        "inventory_publication":"https://www.undp.org/sites/g/files/zskgke326/files/2024-11/evk2cnr_the_new_inventory_of_13032_glaciers_in_pakistan.pdf",
        "documented_inventory":{"glacier_count":13032,"combined_area_km2":13546.93,"sentinel2_based":True,"version":"1.0"},
        "data_access_note":"The GeoNetwork catalogue lists four glacier-inventory records, one shapefile format, and two records marked downloadable. Confirm the individual record's access conditions and reuse licence before republishing geometry."
      }
    }
    for site_id,site in SITES.items():
      catalog["planetary_computer"]["sites"][site_id]={
        "site":site,
        "scene_searches":get_scene_set(site_id,site)
      }
    (OUT/"public_scene_catalog.json").write_text(json.dumps(catalog,indent=2,allow_nan=False)+"\n",encoding="utf-8")
    (OUT/"README.md").write_text(
      "# Pakistan analog evidence catalogue\n\n"
      "Generated by scripts/fetch_public_evidence.py.\n\n"
      "- Microsoft Planetary Computer: anonymous STAC search for Sentinel-2 L2A scene metadata. This is scene discovery, not raster ingestion.\n"
      "- EvK2CNR: metadata record fetch attempted for the Pakistan Glacier Inventory; product access and reuse terms are recorded separately.\n"
      "- Sentinel-2 assets require a short-lived SAS token for Azure data access; no account is required for public STAC metadata or token issuance.\n\n"
      "Do not treat scene metadata as mineralogy, field validation, or a planetary similarity score.\n",encoding="utf-8")
    print(json.dumps({
      "stac_sites":{k:[(x["window"],x.get("returned_count"),x["status"]) for x in v["scene_searches"]] for k,v in catalog["planetary_computer"]["sites"].items()},
      "evk2_status":catalog["evk2cnr"]["record"].get("status")
    },indent=2),flush=True)
    return 0

if __name__=="__main__":
    raise SystemExit(main())

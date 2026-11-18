#!/usr/bin/env python3
"""Enrich the retained global terrain shortlist with NASA POWER climatology.

This is a global-coordinate climate-context sample for selected candidates,
not a global climate raster and not an in-situ field observation.
"""
from __future__ import annotations
import concurrent.futures
import json
import math
import threading
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

ROOT=Path(__file__).resolve().parents[1]
GLOBAL=ROOT/"data/global_discovery/global_discovery.json"
OUT=ROOT/"data/global_discovery/global_power_enrichment.json"
BASE="https://power.larc.nasa.gov/api/temporal/climatology/point"
COMMUNITY="RE"
PARAMS=["T2M","T2M_MAX","T2M_MIN","RH2M","WS10M","PRECTOTCORR","ALLSKY_SFC_SW_DWN"]
MONTHS=["JAN","FEB","MAR","APR","MAY","JUN","JUL","AUG","SEP","OCT","NOV","DEC"]
LABELS={"T2M":"air_temperature_2m_c","T2M_MAX":"air_temperature_2m_max_c","T2M_MIN":"air_temperature_2m_min_c","RH2M":"relative_humidity_2m_pct","WS10M":"wind_speed_10m_m_s","PRECTOTCORR":"corrected_precipitation_mm_day","ALLSKY_SFC_SW_DWN":"all_sky_surface_shortwave_kwh_m2_day"}
THREAD=threading.local()
TOP_PER_TARGET=100
MAX_WORKERS=4


def utcnow()->str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def get_session()->requests.Session:
    if not hasattr(THREAD,"session"):
        s=requests.Session()
        retry=Retry(total=4,connect=4,read=4,backoff_factor=1.2,status_forcelist=(429,500,502,503,504),allowed_methods=frozenset(["GET"]),respect_retry_after_header=True)
        s.mount("https://",HTTPAdapter(max_retries=retry))
        s.headers.update({"User-Agent":"ANALOG-X/1.0 NASA POWER global candidate climatology","Accept":"application/json"})
        THREAD.session=s
    return THREAD.session


def clean(value:Any)->float|None:
    if not isinstance(value,(int,float)) or isinstance(value,bool):return None
    number=float(value)
    return number if math.isfinite(number) and number>-900 else None


def parse_payload(payload:dict[str,Any])->dict[str,Any]:
    block=payload.get("properties",{}).get("parameter",{})
    if not isinstance(block,dict) or not block:
        raise ValueError("NASA POWER returned no properties.parameter block")
    series={}
    for param in PARAMS:
        raw=block.get(param)
        if not isinstance(raw,dict):
            series[param]={"annual":None,"monthly":{m:None for m in MONTHS}}
            continue
        months={m:clean(raw.get(m)) for m in MONTHS}
        annual=clean(raw.get("ANN"))
        if annual is None:
            vals=[v for v in months.values() if v is not None]
            annual=sum(vals)/len(vals) if vals else None
        series[param]={"annual":annual,"monthly":months}
    if series["T2M"]["annual"] is None and not any(v is not None for v in series["T2M"]["monthly"].values()):
        raise ValueError("NASA POWER response contains no usable T2M climatology")
    monthly=[]
    for month in MONTHS:
        row={"month":month}
        for param in PARAMS:row[LABELS[param]]=series[param]["monthly"].get(month)
        tmax=row["air_temperature_2m_max_c"];tmin=row["air_temperature_2m_min_c"]
        row["diurnal_air_temperature_range_c"]=tmax-tmin if tmax is not None and tmin is not None else None
        monthly.append(row)
    precip=[(row["month"],row["corrected_precipitation_mm_day"]) for row in monthly if row["corrected_precipitation_mm_day"] is not None]
    dry_months=[m for m,v in sorted(precip,key=lambda item:(item[1],MONTHS.index(item[0])))[:3]]
    tvals=[row["air_temperature_2m_c"] for row in monthly if row["air_temperature_2m_c"] is not None]
    return {
        "annual_metrics":{LABELS[p]:series[p]["annual"] for p in PARAMS},
        "monthly":monthly,
        "derived": {
            "mean_diurnal_air_temperature_range_c":(
                sum(row["diurnal_air_temperature_range_c"] for row in monthly if row["diurnal_air_temperature_range_c"] is not None) /
                max(1,sum(row["diurnal_air_temperature_range_c"] is not None for row in monthly))
            ),
            "monthly_mean_air_temperature_span_c":max(tvals)-min(tvals) if tvals else None,
            "three_driest_climatology_months":dry_months
        }
    }


def fetch_one(candidate:dict[str,Any])->dict[str,Any]:
    lat=float(candidate["latitude"]);lon=float(candidate["longitude"])
    params={"parameters":",".join(PARAMS),"community":COMMUNITY,"longitude":lon,"latitude":lat,"format":"JSON"}
    sess=get_session()
    response=sess.get(BASE,params=params,timeout=(25,100))
    request_url=response.url
    if response.status_code!=200:
        raise RuntimeError(f"NASA POWER HTTP {response.status_code}: {response.text[:400]}")
    payload=response.json()
    parsed=parse_payload(payload)
    header=payload.get("header",{})
    return {
        "state":"processed",
        "coordinate":{"latitude":lat,"longitude":lon,"coordinate_status":"approximate DEM-window centre; not a field station"},
        "source":{
            "provider":"NASA Langley Research Center POWER",
            "product":"Climatology API / point",
            "community":COMMUNITY,
            "parameters":PARAMS,
            "request_url":request_url,
            "title":header.get("title"),
            "fetched_at_utc":utcnow(),
            "documentation":"https://power.larc.nasa.gov/docs/services/api/temporal/climatology/"
        },
        **parsed,
        "limitations":[
            "NASA POWER is gridded climatology, not a local weather-station observation or current forecast.",
            "T2M is 2 m air temperature, not rock or surface temperature.",
            "WS10M is wind speed at 10 m and does not estimate dust emission or deposition.",
            "PRECTOTCORR is precipitation and is not evidence of surface/subsurface water or ice resources.",
            "ALLSKY_SFC_SW_DWN is Earth atmospheric solar irradiance, not lunar illumination.",
            "Candidate coordinates are approximate centers derived from a resampled DEM tile and are not survey-grade field station locations."
        ]
    }


def main()->None:
    if not GLOBAL.exists():raise SystemExit("Global discovery merged dataset not found.")
    data=json.loads(GLOBAL.read_text(encoding="utf-8"))
    unique={}
    for target in ("moon","mars"):
        rows=data.get("targets",{}).get(target,{}).get("candidate_windows",[])
        for row in rows[:TOP_PER_TARGET]:
            unique[row["id"]]=row
    candidates=list(unique.values())
    results={}
    failures=0
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
        futures={pool.submit(fetch_one,row):row for row in candidates}
        for index,future in enumerate(concurrent.futures.as_completed(futures),1):
            row=futures[future]
            try:result=future.result()
            except Exception as exc:
                failures+=1
                result={"state":"unavailable","error":str(exc)[:700],"limitations":["No usable NASA POWER response was obtained for this coordinate; absence of a value is not zero."]}
            results[row["id"]]=result
            if index%20==0:print(f"NASA POWER global shortlist {index}/{len(candidates)} complete; failures={failures}",flush=True)
            time.sleep(0.03)
    for target in ("moon","mars"):
        for row in data.get("targets",{}).get(target,{}).get("candidate_windows",[]):
            if row["id"] in results:row["climate_context"]=results[row["id"]]
    processed=sum(1 for x in results.values() if x.get("state")=="processed")
    payload={
        "schema_version":"1.0.0","project":"ANALOG-X Global Climate Context",
        "generated_at_utc":utcnow(),
        "state":"processed" if processed==len(candidates) and candidates else ("partially_processed" if processed else "unavailable"),
        "source":{"provider":"NASA Langley Research Center POWER","product":"Global point Climatology API","community":COMMUNITY,"parameters":PARAMS,"documentation":"https://power.larc.nasa.gov/docs/services/api/temporal/climatology/"},
        "scope":{"unique_candidate_coordinates_attempted":len(candidates),"top_candidates_per_target":TOP_PER_TARGET,"unique_coordinates_processed":processed,"unavailable_or_failed":len(candidates)-processed,"coverage_percent":round(100*processed/max(1,len(candidates)),3),"coverage_note":"Enrichment is limited to the retained top-100-per-target terrain shortlist, deduplicated by candidate window ID; it is not a global climate raster or all-window climate scan."},
        "candidate_results":results,
        "interpretation":"Climate context is an independent environmental data family from Copernicus terrain, but NASA POWER gridded climatology is not local station ground truth and does not establish planetary environment equivalence."
    }
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(payload,indent=2)+"\n",encoding="utf-8")
    GLOBAL.write_text(json.dumps(data,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"state":payload["state"],**payload["scope"],"output":str(OUT)},indent=2))


if __name__=="__main__":main()

#!/usr/bin/env python3
"""Fetch NASA POWER climatology snapshots for ANALOG-X in GitHub Actions."""
from __future__ import annotations
import json, sys, time
from datetime import datetime, timezone
from pathlib import Path
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

ROOT=Path(__file__).resolve().parents[1]
SITES=json.loads((ROOT/"scripts"/"sites.json").read_text(encoding="utf-8"))
OUT=ROOT/"data"/"power"
BASE="https://power.larc.nasa.gov/api/temporal/climatology/point"
COMMUNITY="RE"
PARAMS=["T2M","T2M_MAX","T2M_MIN","RH2M","WS10M","PRECTOTCORR","ALLSKY_SFC_SW_DWN"]
MONTHS=["JAN","FEB","MAR","APR","MAY","JUN","JUL","AUG","SEP","OCT","NOV","DEC"]
SESSION=requests.Session()
retry=Retry(total=4,connect=4,read=4,backoff_factor=1.0,status_forcelist=(429,500,502,503,504),allowed_methods=frozenset(["GET"]),respect_retry_after_header=True)
SESSION.mount("https://",HTTPAdapter(max_retries=retry))
SESSION.headers.update({"User-Agent":"ANALOG-X/1.0 NASA Space Apps 2026","Accept":"application/json"})

def utcnow():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()

def request_params(lat,lon,params):
    q={"parameters":",".join(params),"community":COMMUNITY,"longitude":lon,"latitude":lat,"format":"JSON"}
    response=SESSION.get(BASE,params=q,timeout=(20,90))
    url=response.url
    if response.status_code!=200:
        return None,url,f"HTTP {response.status_code}: {response.text[:1200]}"
    try:
        payload=response.json()
    except ValueError:
        return None,url,"NASA POWER response was not JSON"
    messages=payload.get("messages") or []
    if messages:
        return None,url,"; ".join(map(str,messages))
    block=payload.get("properties",{}).get("parameter",{})
    if not isinstance(block,dict) or not block:
        return None,url,"No properties.parameter object in response"
    return payload,url,None

def clean(v):
    if not isinstance(v,(int,float)):
        return None
    v=float(v)
    if v!=v or abs(v)==float("inf") or v<=-900:
        return None
    return v

def get_series(payload,name):
    block=payload.get("properties",{}).get("parameter",{})
    p=block.get(name) if isinstance(block,dict) else None
    if not isinstance(p,dict):
        return None
    monthly={m:clean(p.get(m)) for m in MONTHS}
    annual=clean(p.get("ANN"))
    if annual is None:
        vals=[x for x in monthly.values() if x is not None]
        annual=sum(vals)/len(vals) if vals else None
    if annual is None and not any(x is not None for x in monthly.values()):
        return None
    return {"annual":annual,"monthly":monthly}

def fetch_site(site_id,site):
    lat,lon=float(site["latitude"]),float(site["longitude"])
    print(f"[{site_id}] NASA POWER {COMMUNITY} climatology at {lat}, {lon}",flush=True)
    payload,url,error=request_params(lat,lon,PARAMS)
    errors={}
    mode="one multi-parameter request"
    if payload is None:
        print(f"[{site_id}] bundle failed; parameter fallback: {error}",flush=True)
        block={}
        for param in PARAMS:
            one,one_url,one_error=request_params(lat,lon,[param])
            if one is not None:
                pb=one.get("properties",{}).get("parameter",{})
                if param in pb:
                    block[param]=pb[param]
                else:
                    errors[param]="Not present in response"
            else:
                errors[param]=one_error or "Unknown API error"
            time.sleep(0.12)
        if not block:
            raise RuntimeError(f"No usable NASA POWER parameters. Bundle error={error}; fallback errors={errors}")
        payload={"header":{"title":"NASA POWER Climatology API","community":COMMUNITY},"messages":[],"properties":{"parameter":block}}
        url=BASE
        mode="per-parameter fallback"
    series={p:get_series(payload,p) for p in PARAMS}
    missing=[p for p,v in series.items() if v is None]
    if series["T2M"] is None:
        raise RuntimeError(f"No valid T2M. Missing={missing}; errors={errors}")
    monthly=[]
    for m in MONTHS:
        row={"month":m}
        keys={"T2M":"temp","T2M_MAX":"tmax","T2M_MIN":"tmin","RH2M":"rh","WS10M":"wind","PRECTOTCORR":"precip","ALLSKY_SFC_SW_DWN":"solar"}
        for p,k in keys.items():
            row[k]=series[p]["monthly"].get(m) if series[p] else None
        row["diurnal_air_temp_range"]=row["tmax"]-row["tmin"] if row["tmax"] is not None and row["tmin"] is not None else None
        monthly.append(row)
    def annual(p):
        return series[p]["annual"] if series[p] else None
    tvals=[x["temp"] for x in monthly if x["temp"] is not None]
    dvals=[x["diurnal_air_temp_range"] for x in monthly if x["diurnal_air_temp_range"] is not None]
    product={
      "schema_version":"1.0",
      "site":{"id":site_id,"name":site["name"],"country":site["country"],"latitude":lat,"longitude":lon,"environment":site["environment"]},
      "source":{"provider":"NASA Langley Research Center POWER","product":"Climatology API / point","community":COMMUNITY,
                "parameters_requested":PARAMS,"request_url":url,"request_mode":mode,"fetched_at_utc":utcnow(),
                "documentation":"https://power.larc.nasa.gov/docs/services/api/temporal/climatology/",
                "community_documentation":"https://power.larc.nasa.gov/docs/methodology/communities/","parameter_errors":errors},
      "metrics":{"temp":annual("T2M"),"tmax":annual("T2M_MAX"),"tmin":annual("T2M_MIN"),"rh":annual("RH2M"),"wind":annual("WS10M"),
                 "precip":annual("PRECTOTCORR"),"solar":annual("ALLSKY_SFC_SW_DWN"),
                 "dailyRange":sum(dvals)/len(dvals) if dvals else None,
                 "seasonalSpan":max(tvals)-min(tvals) if len(tvals)>1 else None},
      "monthly":monthly,"missing_parameters":missing,"raw_power_response":payload,
      "quality":{"valid_parameter_count":len(PARAMS)-len(missing),"note":"Null means unavailable or missing. NASA POWER is gridded climatology, not a local weather station."}
    }
    if product["quality"]["valid_parameter_count"]<2:
        raise RuntimeError("Fewer than two valid parameters; refusing to publish a useless record.")
    return product

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    records,failures={},{}
    for site_id,site in SITES.items():
        try:
            product=fetch_site(site_id,site)
            (OUT/f"{site_id}.json").write_text(json.dumps(product,indent=2,allow_nan=False)+"\n",encoding="utf-8")
            records[site_id]={"file":f"{site_id}.json","site":product["site"],"fetched_at_utc":product["source"]["fetched_at_utc"],
              "valid_parameters":[p for p in PARAMS if p not in product["missing_parameters"]],
              "missing_parameters":product["missing_parameters"],"request_mode":product["source"]["request_mode"]}
            print(f"[{site_id}] SUCCESS {records[site_id]['valid_parameters']}",flush=True)
        except Exception as exc:
            failures[site_id]=str(exc)
            print(f"[{site_id}] FAILED {exc}",file=sys.stderr,flush=True)
    index={"schema_version":"1.0","provider":"NASA POWER Climatology API","community":COMMUNITY,"generated_at_utc":utcnow(),
           "record_count":len(records),"candidate_count":len(SITES),"records":records,"errors":failures}
    (OUT/"index.json").write_text(json.dumps(index,indent=2)+"\n",encoding="utf-8")
    (OUT/"README.md").write_text(
      "# NASA POWER snapshots\n\nServer-side snapshots fetched by the GitHub Actions workflow.\n"
      "The public app reads these same-origin JSON files rather than making a browser cross-origin NASA request.\n\n"
      "NASA POWER: https://power.larc.nasa.gov/\n"
      "API docs: https://power.larc.nasa.gov/docs/services/api/temporal/climatology/\n"
      "Community/parameter availability: https://power.larc.nasa.gov/docs/methodology/communities/\n\n"
      "Null values mean missing/unavailable. They are never converted into matches.\n",encoding="utf-8")
    print(f"Finished {len(records)}/{len(SITES)} site snapshots",flush=True)
    return 0 if records else 1

if __name__=="__main__":
    raise SystemExit(main())

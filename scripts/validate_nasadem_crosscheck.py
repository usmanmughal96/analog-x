#!/usr/bin/env python3
"""Cross-check selected Earth terrain profiles against NASADEM (SRTM-derived).

This is an independent-elevation-source comparison for overlapping NASADEM
coverage only. It is not field validation and does not prove analog identity.
"""
from __future__ import annotations
import json, math, re, sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import requests
import rasterio
from rasterio.transform import from_origin
from rasterio.warp import reproject, transform_bounds
from rasterio.enums import Resampling
from scipy.ndimage import maximum_filter, minimum_filter

ROOT=Path(__file__).resolve().parents[1]
CATALOG="https://planetarycomputer.microsoft.com/api/stac/v1"
TOKEN="https://planetarycomputer.microsoft.com/api/sas/v1/token/nasadem"
TARGET_RES=925.0
SIZE=32
session=requests.Session()
session.headers.update({"User-Agent":"ANALOG-X/1.0 NASADEM independent DEM cross-check"})


def now():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def crs_for(lat,lon):
    zone=max(1,min(60,int((lon+180)//6)+1))
    return f"EPSG:{32600+zone if lat>=0 else 32700+zone}"


def percentile(a,q):
    return float(np.nanpercentile(a,q))


def metrics(grid):
    z=np.asarray(grid,dtype=np.float32)
    valid=np.isfinite(z)
    slope=np.full(z.shape,np.nan,dtype=np.float32)
    gx=(z[1:-1,2:]-z[1:-1,:-2])/(2*TARGET_RES)
    gy=(z[2:,1:-1]-z[:-2,1:-1])/(2*TARGET_RES)
    ok=valid[1:-1,2:]&valid[1:-1,:-2]&valid[2:,1:-1]&valid[:-2,1:-1]
    core=np.degrees(np.arctan(np.hypot(gx,gy)))
    core[~ok]=np.nan
    slope[1:-1,1:-1]=core
    ok3=minimum_filter(valid.astype(np.uint8),size=3,mode="constant",cval=0)==1
    relief=maximum_filter(np.where(valid,z,-np.inf),size=3,mode="constant",cval=-np.inf)-minimum_filter(np.where(valid,z,np.inf),size=3,mode="constant",cval=np.inf)
    relief[~ok3]=np.nan
    sv=slope[np.isfinite(slope)]; rv=relief[np.isfinite(relief)]
    if len(sv)<30 or len(rv)<30:
        raise RuntimeError("Insufficient valid NASADEM terrain derivatives")
    return {
        "valid_cell_percent":100*float(valid.mean()),
        "median_slope_deg":percentile(sv,50),
        "p90_slope_deg":percentile(sv,90),
        "p90_local_relief_m":percentile(rv,90),
        "p95_slope_deg":percentile(sv,95),
        "slope_under_5_deg_pct":100*float(np.mean(sv<5)),
        "slope_over_20_deg_pct":100*float(np.mean(sv>20)),
        "elevation_iqr_m":percentile(z[valid],75)-percentile(z[valid],25),
    }


def choose_asset(item):
    assets=item.get("assets",{})
    for key in ("data","elevation","dem","NASADEM_HGT"):
        if key in assets and assets[key].get("href"):
            return assets[key]["href"]
    for asset in assets.values():
        href=asset.get("href","")
        roles=asset.get("roles",[])
        media=asset.get("type","")
        if href and ("data" in roles or "tiff" in media.lower() or href.lower().endswith((".tif",".tiff"))):
            return href
    return None


def process_site(site,token,earth_baseline):
    lat=float(site["latitude"]); lon=float(site["longitude"])
    if lat < -56 or lat > 60:
        return {"site_id":site["id"],"status":"outside_nasadem_coverage","coverage_note":"NASADEM SRTM-based global product covers approximately 56°S to 60°N; no cross-check attempted."}
    crs=crs_for(lat,lon)
    # A square 29.6 km study window matches the nominal 32 x 925 m terrain grid.
    center_x,center_y=rasterio.warp.transform("EPSG:4326",crs,[lon],[lat])
    left=center_x[0]-SIZE*TARGET_RES/2
    top=center_y[0]+SIZE*TARGET_RES/2
    dst_transform=from_origin(left,top,TARGET_RES,TARGET_RES)
    right=left+SIZE*TARGET_RES; bottom=top-SIZE*TARGET_RES
    bbox=transform_bounds(crs,"EPSG:4326",left,bottom,right,top,densify_pts=21)
    response=session.post(CATALOG+"/search",json={"collections":["nasadem"],"bbox":list(bbox),"limit":100},timeout=(30,120))
    response.raise_for_status()
    items=response.json().get("features",[])
    hrefs=[choose_asset(x) for x in items]
    hrefs=[x for x in hrefs if x]
    if not hrefs:
        raise RuntimeError(f"NASADEM STAC search returned {len(items)} items but no elevation COG asset")
    signed_token=token.lstrip("?&")
    grid=np.full((SIZE,SIZE),np.nan,dtype=np.float32)
    read_count=0
    with rasterio.Env(GDAL_DISABLE_READDIR_ON_OPEN="EMPTY_DIR",CPL_VSIL_CURL_ALLOWED_EXTENSIONS=".tif,.tiff",GDAL_HTTP_MAX_RETRY="3",GDAL_HTTP_TIMEOUT="90",GDAL_CACHEMAX=128):
        for href in hrefs:
            signed=href+("&" if "?" in href else "?")+signed_token
            try:
                with rasterio.open("/vsicurl/"+signed) as src:
                    reproject(
                        source=rasterio.band(src,1),destination=grid,
                        src_transform=src.transform,src_crs=src.crs,
                        src_nodata=src.nodata,dst_transform=dst_transform,
                        dst_crs=crs,dst_nodata=np.nan,
                        resampling=Resampling.average,init_dest_nodata=False,
                        num_threads=2
                    )
                read_count+=1
            except Exception:
                continue
    if read_count==0:
        raise RuntimeError("Could not read any NASADEM elevation COGs intersecting the candidate window")
    observed=float(np.isfinite(grid).mean())
    if observed<0.65:
        raise RuntimeError(f"Insufficient NASADEM valid coverage: {observed*100:.1f}%")
    derived=metrics(grid)
    baseline=earth_baseline["terrain_metrics"]
    cop={
        "median_slope_deg":baseline["slope_deg"]["median"],
        "p90_slope_deg":baseline["slope_deg"]["p90"],
        "p90_local_relief_m":baseline["3x3_local_relief_m"]["p90"]
    }
    diffs={k:round(derived[k]-cop[k],4) for k in cop}
    ratios={k:(round(100*(derived[k]-cop[k])/abs(cop[k]),2) if abs(cop[k])>1e-6 else None) for k in cop}
    return {
        "site_id":site["id"],"site_name":site["name"],"status":"processed",
        "source":{"provider":"NASA LP DAAC / NASADEM","collection":"NASADEM_HGT.001 / NASADEM STAC","doi":"10.5067/MEASURES/NASADEM/NASADEM_HGT.001","catalog_api":CATALOG,"spatial_coverage_note":"Approximately 56°S to 60°N; source pixels are 1 arc-second and include SRTM-based elevation with auxiliary void filling."},
        "stac_items_found":len(items),"elevation_assets_read":read_count,
        "analysis_support_m":TARGET_RES,"valid_cell_percent":round(derived["valid_cell_percent"],3),
        "nasadem_metrics":derived,"copernicus_glo30_metrics":cop,
        "nasadem_minus_copdem_absolute_difference":diffs,
        "relative_difference_percent":ratios,
        "interpretation":"Independent elevation-source cross-check for coarse terrain descriptors only. Copernicus DSM versus NASADEM surface model semantics differ; disagreement is diagnostic, not a correction or ground truth."
    }


def main():
    catalog=json.loads((ROOT/"data/agents/candidate_catalog.json").read_text(encoding="utf-8"))
    terrain=json.loads((ROOT/"data/terrain/terrain_comparison.json").read_text(encoding="utf-8"))
    try:
        token_response=session.get(TOKEN,timeout=(20,60)); token_response.raise_for_status()
        token=token_response.json().get("token")
        if not token: raise RuntimeError("NASADEM SAS token response did not contain token")
    except Exception as exc:
        raise SystemExit(f"Unable to obtain NASADEM public asset token: {exc}")
    results=[]
    aliases={"koh_i_sultan":"koh_i_sultan","hispar_glacier":"hispar_glacier","chagai_small_playas":"chagai_small_playas","hamun_i_mashkel":"hamun_i_mashkel"}
    for site in catalog.get("candidate_sites",[]):
        sid=site["id"]
        baseline=terrain.get("earth_sites",{}).get(sid)
        if not baseline or baseline.get("status")!="processed":
            results.append({"site_id":sid,"status":"no_processed_copdem_baseline"})
            continue
        try:
            row=process_site(site,token,baseline)
            results.append(row)
            print(f"[{sid}] {row['status']}",flush=True)
        except Exception as exc:
            results.append({"site_id":sid,"site_name":site.get("name"),"status":"unavailable","error":str(exc)[:700]})
            print(f"[{sid}] cross-check unavailable: {exc}",file=sys.stderr,flush=True)
    compared=[x for x in results if x.get("status")=="processed"]
    features=["median_slope_deg","p90_slope_deg","p90_local_relief_m"]
    concordance={}
    for feature in features:
        if len(compared)>=3:
            x=[r["copernicus_glo30_metrics"][feature] for r in compared]
            y=[r["nasadem_metrics"][feature] for r in compared]
            rankx=np.argsort(np.argsort(x)).astype(float)
            ranky=np.argsort(np.argsort(y)).astype(float)
            rho=float(np.corrcoef(rankx,ranky)[0,1]) if np.std(rankx)>0 and np.std(ranky)>0 else None
            concordance[feature]={"spearman_rank_correlation_approx":None if rho is None else round(rho,4),"n_sites":len(compared)}
        else:
            concordance[feature]={"spearman_rank_correlation_approx":None,"n_sites":len(compared),"note":"At least three matched sites are required."}
    output={
        "schema_version":"1.0.0","generated_at_utc":now(),"status":"processed" if compared else "unavailable",
        "purpose":"Independent-source elevation cross-check for matched Earth regional terrain profiles.",
        "source":"NASADEM (SRTM-derived) compared with Copernicus DEM GLO-30 DSM",
        "sites_attempted":len(results),"sites_crosschecked":len(compared),
        "rank_concordance":concordance,"site_results":results,
        "limitations":[
            "NASADEM has approximate coverage from 56°S to 60°N; high-latitude sites such as McMurdo, Haughton or Iceland may be outside its coverage.",
            "NASADEM uses SRTM with auxiliary void filling and is not a perfect independent ground survey.",
            "NASADEM and Copernicus GLO-30 have different acquisition sensors, processing and DSM/DEM semantics; compare coarse descriptors, not absolute elevation datums.",
            "This is independent raster-source checking, not in-situ field validation, geological validation or planetary analog validation.",
            "Rank correlation is only descriptive for this small, selected set and must not be presented as calibrated model accuracy."
        ]
    }
    path=ROOT/"data/validation/nasadem_crosscheck.json";path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(output,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"sites_attempted":len(results),"sites_crosschecked":len(compared),"output":str(path)},indent=2))


if __name__=="__main__":
    main()

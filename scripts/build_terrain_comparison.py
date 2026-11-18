#!/usr/bin/env python3
"""Build a matched coarse-scale Earth–Mars terrain evidence comparison.

Earth: Copernicus DEM GLO-30 COGs from Microsoft Planetary Computer.
Mars: MOLA MEGDR 64 pixels/degree topography + observation-count tile.
Earth DEM is averaged to the approximately 926 m MOLA support before slope and
local-relief statistics are computed. This is a terrain-profile comparison,
not geological equivalence, landing safety or a universal analog score.
"""
from __future__ import annotations
import json, math, re, sys, time
from datetime import datetime, timezone
from pathlib import Path
import requests
import numpy as np
import rasterio
from rasterio.merge import merge
from rasterio.warp import reproject, transform
from rasterio.transform import from_origin
from rasterio.enums import Resampling
from scipy.ndimage import maximum_filter, minimum_filter, minimum_filter1d
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
CATALOG=ROOT/"data"/"pakistan"/"public_scene_catalog.json"
OUT=ROOT/"data"/"terrain"
RAW=ROOT/"data"/"raw"/"mars"/"mola64"
PC_TOKEN="https://planetarycomputer.microsoft.com/api/sas/v1/token/cop-dem-glo-30"
MOLA_BASE="https://pds-geosciences.wustl.edu/mgs/mgs-m-mola-5-megdr-l3-v1/mgsl_300x/meg064"
MOLA_TOPO="megt90n000gb.img"
MOLA_COUNTS="megc90n000gb.img"
MOLA_LABELS=["megt90n000gb.lbl","megc90n000gb.lbl"]
MARS_RADIUS_M=3396190.0
MOLA_PPD=64
MOLA_ROWS=90*MOLA_PPD
MOLA_COLS=180*MOLA_PPD
MOLA_NODATA=-32768
WINDOW_HALF_M=15000.0
TARGET_RES_M=925.0
EARTH_FINE_RES_M=30.0
NILI={"name":"Nili Patera, Syrtis Major quadrangle, Mars","latitude":8.90,"longitude":67.00,
      "gazetteer":"https://planetarynames.wr.usgs.gov/Feature/4272",
      "themis":"https://themis.asu.edu/zoom-20260617a"}

session=requests.Session()
session.headers.update({"User-Agent":"ANALOG-X/1.0 reproducible terrain evidence pipeline"})

def utcnow():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()

def download(url: str, path: Path):
    if path.exists() and path.stat().st_size>0:
        return
    path.parent.mkdir(parents=True,exist_ok=True)
    print(f"Download: {url}",flush=True)
    with session.get(url,stream=True,timeout=(30,180)) as r:
        r.raise_for_status()
        temp=path.with_suffix(path.suffix+".part")
        with temp.open("wb") as f:
            for chunk in r.iter_content(chunk_size=1024*1024):
                if chunk:f.write(chunk)
        temp.replace(path)
    print(f"Saved {path.name}: {path.stat().st_size:,} bytes",flush=True)

def get_sas_token():
    r=session.get(PC_TOKEN,timeout=(20,60));r.raise_for_status()
    token=r.json().get("token")
    if not token:raise RuntimeError("Planetary Computer SAS endpoint returned no token")
    return token

def signed_href(href,token):
    return href+("&" if "?" in href else "?")+token.lstrip("?&")

def pds_label_value(text,key,default=None):
    m=re.search(r"(?im)^\s*"+re.escape(key)+r"\s*=\s*([^\r\n]+)",text)
    if not m:return default
    v=m.group(1).strip().strip('"')
    try:
        return float(v) if any(x in v.upper() for x in [".","E"]) else int(v)
    except ValueError:
        return v

def load_mola_tile():
    top_path=RAW/MOLA_TOPO
    cnt_path=RAW/MOLA_COUNTS
    top_lbl=RAW/MOLA_LABELS[0]
    cnt_lbl=RAW/MOLA_LABELS[1]
    for filename,path in [(MOLA_TOPO,top_path),(MOLA_COUNTS,cnt_path)]:
        download(f"{MOLA_BASE}/{filename}",path)
    for filename,path in [(MOLA_LABELS[0],top_lbl),(MOLA_LABELS[1],cnt_lbl)]:
        download(f"{MOLA_BASE}/{filename}",path)
    top_text=top_lbl.read_text(encoding="latin-1",errors="replace")
    cnt_text=cnt_lbl.read_text(encoding="latin-1",errors="replace")

    # MOLA MEGDR topography and counts are separate rasters and do not have
    # the same sample width: this 64 ppd tile uses 16-bit topography and
    # 8-bit observation counts. Respect each detached PDS label independently.
    top_rows=int(pds_label_value(top_text,"LINES",MOLA_ROWS))
    top_cols=int(pds_label_value(top_text,"LINE_SAMPLES",MOLA_COLS))
    top_bits=int(pds_label_value(top_text,"SAMPLE_BITS",16))
    top_type=str(pds_label_value(top_text,"SAMPLE_TYPE","MSB_INTEGER")).upper()

    count_rows=int(pds_label_value(cnt_text,"LINES",MOLA_ROWS))
    count_cols=int(pds_label_value(cnt_text,"LINE_SAMPLES",MOLA_COLS))
    count_bits=int(pds_label_value(cnt_text,"SAMPLE_BITS",8))
    count_type=str(pds_label_value(cnt_text,"SAMPLE_TYPE","UNSIGNED_INTEGER")).upper()

    if (top_rows,top_cols)!=(MOLA_ROWS,MOLA_COLS):
        raise RuntimeError(f"Unexpected MOLA topography layout: {top_rows}x{top_cols}")
    if (count_rows,count_cols)!=(MOLA_ROWS,MOLA_COLS):
        raise RuntimeError(f"Unexpected MOLA counts layout: {count_rows}x{count_cols}")
    if top_bits!=16 or "MSB" not in top_type:
        raise RuntimeError(f"Unexpected MOLA topography sample format: {top_bits} bits, {top_type}")
    if count_bits not in (8,16) or "UNSIGNED" not in count_type:
        raise RuntimeError(f"Unexpected MOLA counts sample format: {count_bits} bits, {count_type}")

    expected_top=top_rows*top_cols*(top_bits//8)
    expected_counts=count_rows*count_cols*(count_bits//8)
    if top_path.stat().st_size!=expected_top:
        raise RuntimeError(f"MOLA topography size {top_path.stat().st_size} != label-derived {expected_top}")
    if cnt_path.stat().st_size!=expected_counts:
        raise RuntimeError(f"MOLA counts size {cnt_path.stat().st_size} != label-derived {expected_counts}")

    scale=float(pds_label_value(top_text,"SCALING_FACTOR",1.0))
    offset=float(pds_label_value(top_text,"OFFSET",0.0))
    top=np.memmap(top_path,dtype=">i2",mode="r",shape=(top_rows,top_cols))
    count_dtype=">u1" if count_bits==8 else ">u2"
    counts=np.memmap(cnt_path,dtype=count_dtype,mode="r",shape=(count_rows,count_cols))
    return top,counts,{"rows":top_rows,"columns":top_cols,"topography_sample_bits":top_bits,
                       "topography_sample_type":top_type,"counts_sample_bits":count_bits,
                       "counts_sample_type":count_type,"scale_factor":scale,"offset":offset,
                       "pixels_per_degree":MOLA_PPD,"tile_latitude_range_deg":[0,90],
                       "tile_longitude_range_deg":[0,180],"topography_label":top_text[:1600],
                       "counts_label":cnt_text[:900]}

def crop_mola(lat,lon,half_width_m,top,counts,scale,offset):
    deg_per_m=180.0/(math.pi*MARS_RADIUS_M)
    lat_delta=half_width_m*deg_per_m
    lon_delta=half_width_m*deg_per_m/max(math.cos(math.radians(lat)),1e-6)
    north,south=lat+lat_delta,lat-lat_delta
    west,east=lon-lon_delta,lon+lon_delta
    r0=max(0,int(math.floor((90.0-north)*MOLA_PPD)))
    r1=min(MOLA_ROWS,int(math.ceil((90.0-south)*MOLA_PPD)))
    c0=max(0,int(math.floor(west*MOLA_PPD)))
    c1=min(MOLA_COLS,int(math.ceil(east*MOLA_PPD)))
    z=np.asarray(top[r0:r1,c0:c1],dtype=np.float64)*scale+offset
    n=np.asarray(counts[r0:r1,c0:c1],dtype=np.int32)
    valid=(n>0)&np.isfinite(z)&(z!=MOLA_NODATA)
    z[~valid]=np.nan
    dx=MARS_RADIUS_M*math.pi/180.0/MOLA_PPD*math.cos(math.radians(lat))
    dy=MARS_RADIUS_M*math.pi/180.0/MOLA_PPD
    return z,valid,{"window_lat_lon_deg":[south,west,north,east],"row_range":[r0,r1],"column_range":[c0,c1],
                    "pixel_spacing_x_m":dx,"pixel_spacing_y_m":dy,"cells":[int(z.shape[0]),int(z.shape[1])],
                    "observed_cells":int(valid.sum()),"total_cells":int(valid.size),
                    "valid_observation_coverage_percent":round(100*float(valid.mean()),2)}

def terrain_stats(z,valid,dx,dy):
    n_valid=int(valid.sum())
    if n_valid<50:raise RuntimeError(f"Insufficient valid cells for terrain statistics: {n_valid}")
    vals=z[valid]
    fill=float(np.nanmedian(vals))
    filled=np.where(valid,z,fill)
    gy,gx=np.gradient(filled,dy,dx)
    slope=np.degrees(np.arctan(np.hypot(gx,gy)))
    complete=minimum_filter(valid.astype(np.uint8),size=3,mode="constant",cval=0)==1
    s=slope[complete]
    local_range=maximum_filter(filled,size=3,mode="nearest")-minimum_filter(filled,size=3,mode="nearest")
    rel=local_range[complete]
    if s.size<20 or rel.size<20:raise RuntimeError("Too few complete neighbourhoods for slope/roughness stats")
    return {
      "valid_cell_count":n_valid,
      "complete_3x3_neighbourhood_count":int(s.size),
      "elevation_m_relative_to_product_datum":{
        "p10":float(np.percentile(vals,10)),"median":float(np.median(vals)),"p90":float(np.percentile(vals,90)),
        "range_p90_minus_p10":float(np.percentile(vals,90)-np.percentile(vals,10))},
      "slope_deg":{
        "median":float(np.median(s)),"p90":float(np.percentile(s,90)),"p95":float(np.percentile(s,95))},
      "3x3_local_relief_m":{
        "median":float(np.median(rel)),"p90":float(np.percentile(rel,90))},
      "slope_fraction":{
        "under_5_deg_percent":float(np.mean(s<5)*100),
        "under_10_deg_percent":float(np.mean(s<10)*100),
        "over_20_deg_percent":float(np.mean(s>20)*100)}
    }

def local_utm(lon,lat):
    zone=int((lon+180)//6)+1
    return f"EPSG:{32600+zone if lat>=0 else 32700+zone}"

def get_earth_dem(site_id,site,items,token):
    if not items:raise RuntimeError(f"No Copernicus DEM items in STAC catalog for {site_id}")
    lon,lat=float(site["longitude"]),float(site["latitude"])
    # Fixed 30 km square. The STAC search window is expanded to include
    # neighbouring 1-degree DEM tiles when the AOI crosses a tile edge.
    half=WINDOW_HALF_M
    lat_delta=half/110574.0
    lon_delta=half/(111320.0*math.cos(math.radians(lat)))
    bbox=[lon-lon_delta,lat-lat_delta,lon+lon_delta,lat+lat_delta]
    sources=[]; opened=[]
    try:
        for item in items:
            href=item.get("asset_href")
            if not href:continue
            signed=signed_href(href,token)
            with rasterio.Env(
              GDAL_DISABLE_READDIR_ON_OPEN="EMPTY_DIR",
              CPL_VSIL_CURL_ALLOWED_EXTENSIONS=".tif",
              GDAL_HTTP_MAX_RETRY="3",
              GDAL_HTTP_RETRY_DELAY="1",
              GDAL_CACHEMAX=256
            ):
              ds=rasterio.open("/vsicurl/"+signed)
            opened.append(ds)
            # Include only tiles intersecting the required geographic window.
            if ds.crs and ds.crs.to_epsg()==4326:
                b=ds.bounds
                if b.right < bbox[0] or b.left > bbox[2] or b.top < bbox[1] or b.bottom > bbox[3]:
                    continue
            sources.append(ds)
        if not sources:raise RuntimeError("No Copernicus DEM tile overlaps the terrain window")
        # Mosaic adjacent 1-degree COG tiles and crop to the AOI.
        mosaic,src_transform=merge(sources,bounds=tuple(bbox),res=sources[0].res,
                                   nodata=sources[0].nodata)
        src_crs=sources[0].crs
        src_nodata=sources[0].nodata
        east,north=transform("EPSG:4326",local_utm(lon,lat),[lon],[lat])
        centre_x,centre_y=float(east[0]),float(north[0])
        width=int(round((2*half)/TARGET_RES_M))
        height=width
        dst_transform=from_origin(centre_x-half,centre_y+half,TARGET_RES_M,TARGET_RES_M)
        dst=np.full((1,height,width),np.nan,dtype=np.float32)
        reproject(
          source=mosaic,destination=dst,
          src_transform=src_transform,src_crs=src_crs,
          dst_transform=dst_transform,dst_crs=local_utm(lon,lat),
          src_nodata=src_nodata,dst_nodata=np.nan,
          resampling=Resampling.average,num_threads=2
        )
        z=dst[0].astype(np.float64)
        valid=np.isfinite(z)
        # Source data can have numeric nodata values as well as GDAL nodata.
        if src_nodata is not None:valid &= z!=src_nodata
        z[~valid]=np.nan
        if valid.mean()<0.9:
            raise RuntimeError(f"Copernicus DEM valid coverage too low: {valid.mean()*100:.1f}%")
        stats=terrain_stats(z,valid,TARGET_RES_M,TARGET_RES_M)
        stats["coverage"]={"valid_percent":round(float(valid.mean()*100),2),"total_cells":int(valid.size)}
        meta={"collection":"cop-dem-glo-30","source_item_ids":[x.get("id") for x in items],
              "asset_hrefs":[x.get("asset_href") for x in items],
              "source_crs":str(src_crs),"analysis_crs":local_utm(lon,lat),
              "native_resolution_m_approx":30,"analysis_resolution_m":TARGET_RES_M,
              "window_size_m":[width*TARGET_RES_M,height*TARGET_RES_M],
              "centre_wgs84":[lon,lat],"dem_type":"Digital Surface Model (DSM)"}
        # Preserve a separate ~30 m Earth DSM diagnostic before the
        # common-support 925 m downsampling. This adds local roughness context
        # for Earth study areas only; it is never mixed into Moon/Mars scores.
        fine_diagnostics = {
          "status":"unavailable",
          "source":"Copernicus DEM GLO-30 DSM",
          "source_native_resolution_m_approx":30,
          "analysis_resolution_m":EARTH_FINE_RES_M,
          "role":"Earth-only higher-detail roughness context; not matched to planetary data and not rover-scale",
          "limitation":"A 30 m DSM still cannot resolve rover-scale obstacles, bearing strength or trafficability."
        }
        try:
            fine_width=int(round((2*half)/EARTH_FINE_RES_M))
            fine_transform=from_origin(centre_x-half,centre_y+half,EARTH_FINE_RES_M,EARTH_FINE_RES_M)
            fine_dst=np.full((1,fine_width,fine_width),np.nan,dtype=np.float32)
            reproject(
              source=mosaic,destination=fine_dst,
              src_transform=src_transform,src_crs=src_crs,
              dst_transform=fine_transform,dst_crs=local_utm(lon,lat),
              src_nodata=src_nodata,dst_nodata=np.nan,
              resampling=Resampling.average,num_threads=2
            )
            fine_z=fine_dst[0].astype(np.float64)
            fine_valid=np.isfinite(fine_z)
            if src_nodata is not None:
                fine_valid &= fine_z!=src_nodata
            fine_z[~fine_valid]=np.nan
            if fine_valid.mean()>=0.9:
                fine_diagnostics.update({
                  "status":"processed",
                  "grid_shape":[int(fine_z.shape[0]),int(fine_z.shape[1])],
                  "valid_cell_count":int(fine_valid.sum()),
                  "total_cell_count":int(fine_valid.size),
                  "coverage_percent":round(float(fine_valid.mean()*100),2),
                  "window_size_km":round(fine_width*EARTH_FINE_RES_M/1000,2),
                  "terrain_metrics":terrain_stats(fine_z,fine_valid,EARTH_FINE_RES_M,EARTH_FINE_RES_M),
                  "local_relief_footprint_m":round(3*EARTH_FINE_RES_M,1)
                })
            else:
                fine_diagnostics["coverage_percent"]=round(float(fine_valid.mean()*100),2)
                fine_diagnostics["limitation"]="Valid-data coverage below 90%; higher-detail diagnostics withheld."
        except Exception as fine_error:
            fine_diagnostics["error"]=str(fine_error)[:500]
        return z,valid,stats,meta,fine_diagnostics
    finally:
        for ds in opened:
            try:ds.close()
            except Exception:pass

def hillshade_png(z,valid,path):
    vals=z[valid]
    if vals.size==0:return
    p2,p98=np.percentile(vals,[2,98])
    norm=np.clip((z-p2)/max(p98-p2,1e-6),0,1)
    norm[~valid]=0
    im=(norm*255).astype(np.uint8)
    img=Image.fromarray(im,mode="L").resize((384,384),Image.Resampling.BILINEAR)
    path.parent.mkdir(parents=True,exist_ok=True);img.save(path,optimize=True)

def surface_grid_relative_m(z,valid,pixel_x_m,pixel_y_m):
    """Small DEM surface for 3D display, relative to the grid's median elevation."""
    values=np.asarray(z,dtype=np.float64)
    mask=np.asarray(valid,dtype=bool) & np.isfinite(values)
    if not mask.any():
        return None
    baseline=float(np.median(values[mask]))
    rows=[]
    for row in range(values.shape[0]):
        out=[]
        for col in range(values.shape[1]):
            out.append(round(float(values[row,col]-baseline),2) if mask[row,col] else None)
        rows.append(out)
    return {
      "units":"m","vertical_reference":"relative to median valid elevation within this local grid",
      "rows":int(values.shape[0]),"columns":int(values.shape[1]),
      "pixel_size_m":{"x":float(pixel_x_m),"y":float(pixel_y_m)},
      "valid_cell_count":int(mask.sum()),"total_cell_count":int(mask.size),
      "values":rows
    }


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    RAW.mkdir(parents=True,exist_ok=True)
    if not CATALOG.exists():raise SystemExit("Pakistan public scene catalog not found; run fetch_public_evidence.py first")
    catalog=json.loads(CATALOG.read_text(encoding="utf-8"))
    dem_sites=catalog.get("copernicus_dem",{}).get("sites",{})
    if not dem_sites:raise SystemExit("No Copernicus DEM metadata in catalog; refresh public evidence pipeline")
    token=get_sas_token()
    top,counts,label_info=load_mola_tile()
    scale=label_info["scale_factor"];offset=label_info["offset"]
    # MOLA topography tile is the 64 px/degree 90N-to-equator, 0E-to-180E map.
    earth_sites={
      "koh_i_sultan":{"name":"Koh-i-Sultan / Chagai, Pakistan","latitude":29.1,"longitude":62.8,"catalog_key":"koh_i_sultan"},
      "hispar_glacier":{"name":"Hispar Glacier / Karakoram, Pakistan","latitude":36.10572,"longitude":75.23341,"catalog_key":"hispar_glacier"},
      "chagai_small_playas":{"name":"Chagai small salt playas near Nok Kundi, Pakistan","latitude":28.583333,"longitude":62.633333,"catalog_key":"chagai_small_playas"},
      "hamun_i_mashkel":{"name":"Hamun-i-Mashkel playa / Kharan Basin, Pakistan","latitude":28.25,"longitude":62.91667,"catalog_key":"hamun_i_mashkel"},
      "dallol":{"name":"Dallol / Danakil Depression, Ethiopia","latitude":14.25,"longitude":40.30,"catalog_key":"dallol"},
      "atacama":{"name":"Atacama Desert, Chile","latitude":-23.50,"longitude":-68.25,"catalog_key":"atacama"},
      "mcmurdo":{"name":"McMurdo Dry Valleys, Antarctica","latitude":-77.50,"longitude":161.80,"catalog_key":"mcmurdo"},
      "haughton":{"name":"Haughton impact structure, Canada","latitude":75.375,"longitude":-89.675,"catalog_key":"haughton"},
      "iceland":{"name":"Icelandic volcanic fields, Iceland","latitude":63.875,"longitude":-22.25,"catalog_key":"iceland"},
      "death":{"name":"Death Valley region, United States","latitude":36.25,"longitude":-116.80,"catalog_key":"death"}
    }
    result={
      "generated_at_utc":utcnow(),
      "method":"Earth Copernicus DEM GLO-30 DSM averaged to 925 m across up to ten curated Earth analog/reference sites; Mars MOLA MEGDR 64 pixels/degree. Both use approximately 30 km square windows and terrain derivatives computed in metres.",
      "planetary_target":{"name":NILI["name"],"latitude":NILI["latitude"],"longitude":NILI["longitude"],
        "source_gazetteer":NILI["gazetteer"],"context_image":NILI["themis"],
        "dataset":"MGS MOLA MEGDR topography and counts 64 pixels/degree",
        "topography_source":f"{MOLA_BASE}/{MOLA_TOPO}","counts_source":f"{MOLA_BASE}/{MOLA_COUNTS}",
        "pixel_spacing_m":{"north_south":MARS_RADIUS_M*math.pi/180/MOLA_PPD,
          "east_west_at_target":MARS_RADIUS_M*math.pi/180/MOLA_PPD*math.cos(math.radians(NILI["latitude"]))}},
      "earth_sites":{},
      "comparison":{"status":"descriptors only","not_a_geological_equivalence_claim":True,
        "interpretation":"Compare slope and local-relief distributions at similar coarse spatial support. Do not compare absolute elevation across different vertical datums or Earth DSM and Mars areoid height. This is not a rover-safety or landing-suitability assessment.",
        "spatial_support_note":"MOLA 64 px/degree is approximately 0.93 km north-south and 0.91 km east-west near Nili Patera. Copernicus DEM GLO-30 is a DSM averaged to 0.925 km. The 30 km windows are a local terrain sample, not the entire Syrtis Major quadrangle."}
    }
    try:
      z,valid,meta_crop=crop_mola(NILI["latitude"],NILI["longitude"],WINDOW_HALF_M,top,counts,scale,offset)
      mars_stats=terrain_stats(z,valid,meta_crop["pixel_spacing_x_m"],meta_crop["pixel_spacing_y_m"])
      mars_stats["coverage"]={"valid_percent":meta_crop["valid_observation_coverage_percent"],"total_cells":meta_crop["total_cells"]}
      result["planetary_target"]["window"]=meta_crop
      result["planetary_target"]["terrain_metrics"]=mars_stats
      result["planetary_target"]["surface_grid_relative_m"]=surface_grid_relative_m(z,valid,meta_crop["pixel_spacing_x_m"],meta_crop["pixel_spacing_y_m"])
      hillshade_png(z,valid,OUT/"nili_patera_mola_hillshade.png")
      result["planetary_target"]["preview_path"]="nili_patera_mola_hillshade.png"
    except Exception as exc:
      result["planetary_target"]["status"]="processing_failed"
      result["planetary_target"]["error"]=str(exc)
      print(f"MOLA processing error: {exc}",file=sys.stderr,flush=True)

    for key,site in earth_sites.items():
      entry=dem_sites.get(key,{})
      items=entry.get("items",[])
      try:
        z,valid,stats,meta,fine_diagnostics=get_earth_dem(key,site,items,token)
        stats["window_half_width_m"]=WINDOW_HALF_M
        result["earth_sites"][key]={
          "site":site,"status":"processed","source":meta,"terrain_metrics":stats,
          "surface_grid_relative_m":surface_grid_relative_m(z,valid,meta["analysis_resolution_m"],meta["analysis_resolution_m"]),
          "native_30m_diagnostics":fine_diagnostics,
          "preview_path":f"{key}_copdem_hillshade.png"
        }
        hillshade_png(z,valid,OUT/f"{key}_copdem_hillshade.png")
        print(f"[{key}] Copernicus DEM terrain metrics ready",flush=True)
      except Exception as exc:
        result["earth_sites"][key]={"site":site,"status":"processing_failed","error":str(exc)}
        print(f"[{key}] Copernicus DEM processing failed: {exc}",file=sys.stderr,flush=True)

    result["mola_product_metadata"]={"label_summary":label_info,
      "source_product":"MGS MOLA MEGDR 64 pixels/degree","product_version":"PDS MEGDR final archive",
      "no_raw_raster_committed":True}
    (OUT/"terrain_comparison.json").write_text(json.dumps(result,indent=2,allow_nan=False)+"\n",encoding="utf-8")
    (OUT/"README.md").write_text(
      "# Matched-scale Earth–Mars terrain descriptors\n\n"
      "The terrain comparison pipeline uses Copernicus DEM GLO-30 DSM for up to ten curated Earth analog/reference sites and MOLA MEGDR 64 px/degree topography/counts around Nili Patera in Syrtis Major. "
      "The Earth DSM is aggregated to approximately the MOLA pixel scale before slope and 3x3 local-relief descriptors are computed for all candidate AOIs with tiles in the refreshed Copernicus STAC catalogue. "
      "This is a coarse terrain-profile comparison, not geological equivalence, rover traversability or landing safety.\n\n"
      "See terrain_comparison.json for values, spatial support, data provenance and limitations. Raw MOLA files are not committed.\n",encoding="utf-8")
    success=bool(result.get("planetary_target",{}).get("terrain_metrics")) and any(
      x.get("status")=="processed" for x in result.get("earth_sites",{}).values())
    return 0 if success else 1

if __name__=="__main__":
    raise SystemExit(main())

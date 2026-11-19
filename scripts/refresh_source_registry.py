#!/usr/bin/env python3
"""Refresh source registry states only from verified generated output records."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
REG=ROOT/"data/source_registry.json"
def read(path):
    p=ROOT/path
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None
def main():
    registry=json.loads(REG.read_text(encoding="utf-8"))
    lookup={x["id"]:x for x in registry["sources"]}
    global_data=read("data/global_discovery/global_discovery.json")
    if global_data:
        coverage=global_data.get("completion_contract",{}).get("tile_processing_coverage_pct",0)
        complete=global_data.get("status")=="complete"
        lookup["copernicus_glo90_global"]["state"]="processed" if complete else ("partially_processed" if coverage>0 else "planned")
        lookup["copernicus_glo90_global"]["coverage_pct_processed_tiles"]=coverage
    landcover=read("data/global_discovery/global_landcover_enrichment.json")
    if landcover:
        state=landcover.get("state","unavailable")
        lookup["io_lulc_global"]["state"]="processed" if state=="processed" else ("partially_processed" if landcover.get("processed_candidate_windows",0)>0 else "unavailable")
        lookup["io_lulc_global"]["coverage_pct_processed_candidates"]=landcover.get("coverage_percent_of_shortlist",0)
        lookup["io_lulc_global"]["candidate_windows_processed"]=landcover.get("processed_candidate_windows",0)
    power=read("data/global_discovery/global_power_enrichment.json")
    if power:
        pstate=power.get("state","unavailable")
        lookup["nasa_power_global"]["state"]="processed" if pstate=="processed" else ("partially_processed" if power.get("scope",{}).get("unique_coordinates_processed",0)>0 else "unavailable")
        lookup["nasa_power_global"]["coverage_pct_processed_candidates"]=power.get("scope",{}).get("coverage_percent",0)
        lookup["nasa_power_global"]["candidate_coordinates_processed"]=power.get("scope",{}).get("unique_coordinates_processed",0)
    cross=read("data/validation/nasadem_crosscheck.json")
    if cross:
        count=int(cross.get("sites_crosschecked",0))
        lookup["nasadem_independent_check"]["state"]="processed" if count>0 else "unavailable"
        lookup["nasadem_independent_check"]["sites_crosschecked"]=count
    lithology=read("data/global_discovery/global_lithology_enrichment.json")
    if lithology and "glim_global_candidate_context" in lookup:
        state=lithology.get("state","unavailable")
        lookup["glim_global_candidate_context"]["state"]=state if state in {"processed","partially_processed"} else "unavailable"
        scope=lithology.get("scope",{})
        lookup["glim_global_candidate_context"]["candidate_points_attempted"]=scope.get("unique_candidate_points_attempted",0)
        lookup["glim_global_candidate_context"]["candidate_points_with_features"]=scope.get("candidate_points_with_lithology_features",0)
        lookup["glim_global_candidate_context"]["query_success_coverage_percent"]=scope.get("query_success_coverage_percent",0)
    REG.write_text(json.dumps(registry,indent=2)+"\n",encoding="utf-8")
    print("Updated source register states from generated data.")
if __name__=="__main__":main()

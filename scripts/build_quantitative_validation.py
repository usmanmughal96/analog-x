#!/usr/bin/env python3
"""Build quantitative robustness diagnostics; never label them as model accuracy."""
import json, math
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
GLOBAL=ROOT/"data/global_discovery/global_discovery.json"
NASADEM=ROOT/"data/validation/nasadem_crosscheck.json"
OUT=ROOT/"data/validation/quantitative_validation.json"
def rank(values):
    order=np.argsort(np.argsort(values))
    return order.astype(float)
def spearman(a,b):
    if len(a)<3:return None
    ra,rb=rank(a),rank(b)
    if np.std(ra)==0 or np.std(rb)==0:return None
    return round(float(np.corrcoef(ra,rb)[0,1]),4)
def target_report(rows):
    if not rows:return {"status":"no_global_candidates"}
    core=[float(x["core_terrain_index"]) for x in rows]
    secondary=[float(x["secondary_diagnostic_index"]) for x in rows]
    core_order=np.argsort(core)[::-1]
    secondary_order=np.argsort(secondary)[::-1]
    rank_corr=spearman(core,secondary)
    report={"candidate_pool_size":len(rows),"core_vs_secondary_spearman":rank_corr,"top_25_overlap":len(set(core_order[:25])&set(secondary_order[:25])),"top_100_overlap":len(set(core_order[:100])&set(secondary_order[:100])),"metric_family_interpretation":"Agreement between two descriptor families from the same GLO-90 DEM. This is robustness analysis, not independent-data validation."}
    for n in (25,100,500):
        selected=[rows[i] for i in core_order[:min(n,len(rows))]]
        report[f"top_{n}_unique_source_tiles"]=len({x["tile_id"] for x in selected})
        report[f"top_{n}_occupied_10deg_cells"]=len({(int((x["latitude"]+90)//10),int((x["longitude"]+180)//10)) for x in selected})
    return report
def main():
    if not GLOBAL.exists():
        payload={"schema_version":"1.0.0","generated_at_utc":datetime.now(timezone.utc).isoformat(),"status":"awaiting_global_scan","note":"Run the global GLO-90 workflow to generate global candidate data."}
    else:
        data=json.loads(GLOBAL.read_text(encoding="utf-8"))
        payload={"schema_version":"1.0.0","generated_at_utc":datetime.now(timezone.utc).replace(microsecond=0).isoformat(),"status":"diagnostic_only","global_scan_status":data.get("status"),"global_tile_processing_coverage_pct":data.get("completion_contract",{}).get("tile_processing_coverage_pct"),"targets":{},"interpretation":"Metric-family robustness checks the consistency of alternative terrain descriptors from the same DEM. It is not an independent validation set, probability, calibrated accuracy or expert/field truth."}
        for target in ("moon","mars"):
            rows=data.get("targets",{}).get(target,{}).get("candidate_windows",[])
            payload["targets"][target]=target_report(rows)
    landcover_path=ROOT/"data/global_discovery/global_landcover_enrichment.json"
    if landcover_path.exists():
        landcover=json.loads(landcover_path.read_text(encoding="utf-8"))
        payload["global_land_cover_enrichment"]={
            "state":landcover.get("state"),
            "shortlist_candidate_windows_unique":landcover.get("shortlist_candidate_windows_unique",0),
            "processed_candidate_windows":landcover.get("processed_candidate_windows",0),
            "coverage_percent_of_shortlist":landcover.get("coverage_percent_of_shortlist",0),
            "source_collection":landcover.get("source",{}).get("collection"),
            "year":landcover.get("source",{}).get("year"),
            "interpretation":"Global land-cover class fractions for retained terrain shortlist windows only; not a geological, mineralogical or field-validation result."
        }
    else:
        payload["global_land_cover_enrichment"]={"state":"awaiting_enrichment"}
    if NASADEM.exists():
        validation=json.loads(NASADEM.read_text(encoding="utf-8"))
        payload["independent_dem_crosscheck"]={"state":validation.get("status"),"sites_crosschecked":validation.get("sites_crosschecked",0),"rank_concordance":validation.get("rank_concordance",{}),"source":"NASADEM SRTM-derived elevation compared with Copernicus GLO-30 at selected overlapping sites","limits":validation.get("limitations",[])}
    else:
        payload["independent_dem_crosscheck"]={"state":"awaiting_validation_run","note":"NASADEM source check is a separate data-source test and is not yet processed."}
    payload["ground_truth_validation"]={"state":"not_available","note":"No physical field observations are present in the repository. The field protocol and evidence validator do not substitute for field measurements."}
    payload["release_gate"]={"independent_source_check":"report only where NASADEM actually processed and site coverage is reported","field_validation":"requires georeferenced, instrumented observations and independent review","global_scan":"must have complete tile inventory coverage and zero unreported tile failures before calling complete"}
    OUT.parent.mkdir(parents=True,exist_ok=True);OUT.write_text(json.dumps(payload,indent=2)+"\n",encoding="utf-8")
    print(f"Wrote {OUT.relative_to(ROOT)} ({payload['status']})")
if __name__=="__main__":main()

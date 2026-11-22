#!/usr/bin/env python3
"""Safely attach the core-only release contract to an already complete global scan.

This does not rescan or alter candidate scores. It verifies schema, ordering,
rank permutations, IDs, finite coordinates/scores, inventory accounting and
then records the contract in the existing discovery artifact.
"""
import json, math, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
PATH=ROOT/"data/global_discovery/global_discovery.json"
def main():
    data=json.loads(PATH.read_text(encoding="utf-8"))
    if data.get("schema_version")!="1.1.0":
        raise SystemExit("Refusing release: expected schema 1.1.0")
    completion=data.get("completion_contract",{})
    expected=completion.get("shards_expected")
    received=completion.get("shards_received")
    inventory=completion.get("global_land_tile_inventory_total")
    assigned=completion.get("tiles_assigned_to_shards")
    processed=completion.get("tiles_processed")
    failures=completion.get("tile_failures")
    if not (data.get("status")=="complete" and expected==received==24 and assigned==inventory==processed and failures==0):
        raise SystemExit("Refusing release: global inventory/shard contract is incomplete")
    counts={}
    for target in ("moon","mars"):
        rows=data.get("targets",{}).get(target,{}).get("candidate_windows",[])
        if not rows: raise SystemExit(f"Refusing release: no {target} candidates")
        ids=[r.get("id") for r in rows]
        if any(not isinstance(x,str) or not x for x in ids) or len(ids)!=len(set(ids)):
            raise SystemExit(f"Refusing release: invalid or duplicate {target} candidate IDs")
        for row in rows:
            for key in ("core_terrain_index","secondary_diagnostic_index","latitude","longitude"):
                value=row.get(key)
                if isinstance(value,bool) or not isinstance(value,(int,float)) or not math.isfinite(value):
                    raise SystemExit(f"Refusing release: {target} {row.get('id')} invalid {key}")
            if not 0<=row["core_terrain_index"]<=100 or not 0<=row["secondary_diagnostic_index"]<=100:
                raise SystemExit(f"Refusing release: {target} score outside [0,100]")
            if not -90<=row["latitude"]<=90 or not -180<=row["longitude"]<=180:
                raise SystemExit(f"Refusing release: {target} invalid WGS84 coordinates")
        ordered=sorted(rows,key=lambda r:(-float(r["core_terrain_index"]),r["id"]))
        if ids != [r["id"] for r in ordered]:
            raise SystemExit(f"Refusing release: {target} rows not sorted by core score")
        if [r.get("shortlist_rank") for r in rows] != list(range(1,len(rows)+1)):
            raise SystemExit(f"Refusing release: {target} primary ranks not sequential")
        secondary=[r.get("secondary_rank_within_primary_shortlist") for r in rows]
        if sorted(secondary)!=list(range(1,len(rows)+1)):
            raise SystemExit(f"Refusing release: {target} secondary diagnostic ranks invalid")
        counts[target]=len(rows)
    data["ranking_contract"]={
        "schema_version":"1.1.0","ranking_ready":True,
        "primary_feature_family":"core",
        "primary_sort":["core_terrain_index descending","id ascending"],
        "secondary_role":"diagnostic_only","consensus_score":False,
        "candidate_rows_validated":True,
        "contract_repaired_without_rescan":True,
        "note":"The existing complete inventory and candidate rows passed the current core-only ordering and rank-integrity checks. This is ranking-file readiness, not independent analog accuracy or field validation."
    }
    PATH.write_text(json.dumps(data,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"ranking_ready":True,"candidate_counts":counts,"tiles_processed":processed,"tile_failures":failures}))
if __name__=="__main__": main()

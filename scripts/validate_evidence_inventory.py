#!/usr/bin/env python3
"""Check that data-source states and repository artifacts are not overstated."""
import json, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
REGISTRY=ROOT/"data/source_registry.json"
ALLOWED={"processed","browse_only","metadata_only","reference_only","planned","partially_processed","unavailable","withheld_pending_qa","field_observed_unreviewed","independently_reviewed"}
def main():
    payload=json.loads(REGISTRY.read_text(encoding="utf-8"))
    errors=[]; seen=set()
    for source in payload.get("sources",[]):
        sid=source.get("id")
        if not sid or sid in seen: errors.append(f"missing/duplicate source id: {sid}")
        seen.add(sid)
        state=source.get("state")
        if state not in ALLOWED: errors.append(f"{sid}: invalid state {state}")
        if not source.get("url"): errors.append(f"{sid}: source URL missing")
        if state=="processed" and not source.get("artifacts"): errors.append(f"{sid}: processed state needs artifact path")
        for artifact in source.get("artifacts",[]):
            target=ROOT/artifact
            if state=="processed" and not target.exists():
                errors.append(f"{sid}: processed artifact missing: {artifact}")
    field=json.loads((ROOT/"data/field_validation/observations.json").read_text(encoding="utf-8"))
    if not field.get("observations") and field.get("status")!="not_started":
        errors.append("empty field observation ledger must remain status=not_started")
    if errors:
        print("\n".join(errors),file=sys.stderr);raise SystemExit(1)
    print(f"Evidence register valid: {len(seen)} sources")
    counts={}
    for x in payload["sources"]: counts[x["state"]]=counts.get(x["state"],0)+1
    print("Evidence states:",json.dumps(counts,sort_keys=True))
if __name__=="__main__":main()

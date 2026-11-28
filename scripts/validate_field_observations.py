#!/usr/bin/env python3
"""Validate field observations without upgrading desk evidence to field truth."""
import json, math, sys
from datetime import datetime, timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/"data/field_validation/observations.json"
VALID={"not_assessed","desk_evidence_only","field_planned","field_observed_unreviewed","independently_reviewed","not_validated"}

def valid_utc_timestamp(value):
    """Accept an ISO 8601 timestamp with an explicit zero UTC offset."""
    if not isinstance(value, str) or not value.endswith("Z"):
        return False
    try:
        parsed = datetime.fromisoformat(value[:-1] + "+00:00")
        return parsed.tzinfo is not None and parsed.utcoffset() == timezone.utc.utcoffset(parsed)
    except (TypeError, ValueError):
        return False
def main():
    payload=json.loads(DATA.read_text(encoding="utf-8"))
    rows=payload.get("observations",[])
    errors=[]
    ids=set()
    for i,row in enumerate(rows):
        tag=f"observations[{i}]"
        oid=row.get("station_id")
        if not oid: errors.append(f"{tag}: station_id required")
        elif oid in ids: errors.append(f"{tag}: duplicate station_id {oid}")
        ids.add(oid)
        if row.get("review_status") not in VALID: errors.append(f"{tag}: invalid review_status")
        if row.get("review_status") in {"field_observed_unreviewed","independently_reviewed"}:
            for key in ("candidate_id","date_utc","observer_ids","latitude_wgs84","longitude_wgs84","coordinate_accuracy_m","coordinate_method","surface_description","photo_ids","instrument_ids","calibration_status","uncertainty_notes","permission_status","safety_observations"):
                if row.get(key) in (None,"",[]): errors.append(f"{tag}: field observation missing {key}")
            if not valid_utc_timestamp(row.get("date_utc")):
                errors.append(f"{tag}: date_utc must be an ISO 8601 UTC timestamp ending in Z; date-only values are insufficient")
        for key,low,high in (("latitude_wgs84",-90,90),("longitude_wgs84",-180,180),("relative_humidity_pct",0,100),("coordinate_accuracy_m",0,1e9)):
            value=row.get(key)
            if value is not None:
                try:
                    number=float(value)
                    if not math.isfinite(number) or not (low <= number <= high): errors.append(f"{tag}: {key} outside valid range")
                except (TypeError,ValueError):
                    errors.append(f"{tag}: {key} must be numeric")
        if row.get("review_status")=="independently_reviewed":
            if not row.get("independent_reviewer"): errors.append(f"{tag}: independent reviewer required")
            if not row.get("review_date_utc"): errors.append(f"{tag}: review date required")
            if not row.get("review_scope"): errors.append(f"{tag}: review scope required")
    if errors:
        print("\n".join(errors),file=sys.stderr); raise SystemExit(1)
    print(f"Field evidence ledger valid: {len(rows)} observations; independently reviewed: {sum(x.get('review_status')=='independently_reviewed' for x in rows)}")
    if not rows: print("STATUS: not_started — zero field observations. Do not claim physical ground validation.")
if __name__=="__main__":main()

#!/usr/bin/env python3
"""Add coarse GLiM lithology context to the retained global terrain shortlist.

The GLiM feature is a point-in-polygon context lookup at each candidate-window
centre. It is never used to rank candidates or interpreted as field-scale
geology, mineralogy, soil chemistry, regolith, or ground truth.
"""
from __future__ import annotations
import concurrent.futures
import json
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

ROOT = Path(__file__).resolve().parents[1]
GLOBAL = ROOT / "data/global_discovery/global_discovery.json"
OUT = ROOT / "data/global_discovery/global_lithology_enrichment.json"
LAYER = "https://services3.arcgis.com/txu3Aw836B0Ze9Ef/ArcGIS/rest/services/GLiM_Lithology_Simplified/FeatureServer/1"
TOP_PER_TARGET = 100
MAX_WORKERS = 4
THREAD = threading.local()


def utcnow() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def session() -> requests.Session:
    if not hasattr(THREAD, "session"):
        client = requests.Session()
        retry = Retry(
            total=4, connect=4, read=4, backoff_factor=1.0,
            status_forcelist=(429, 500, 502, 503, 504),
            allowed_methods=frozenset(["GET"]),
            respect_retry_after_header=True,
        )
        client.mount("https://", HTTPAdapter(max_retries=retry))
        client.headers.update({
            "User-Agent": "ANALOG-X/1.0 GLiM candidate geology context",
            "Accept": "application/json",
        })
        THREAD.session = client
    return THREAD.session


def shortlist_points(data: dict[str, Any], limit: int = TOP_PER_TARGET) -> list[dict[str, Any]]:
    """Deduplicate candidate centres across Moon and Mars target lists."""
    unique: dict[str, dict[str, Any]] = {}
    for target in ("moon", "mars"):
        rows = data.get("targets", {}).get(target, {}).get("candidate_windows", [])
        for row in rows[:limit]:
            cid = row.get("id")
            if not cid:
                continue
            item = unique.setdefault(cid, {
                "candidate_id": cid,
                "latitude": float(row["latitude"]),
                "longitude": float(row["longitude"]),
                "target_membership": [],
                "core_terrain_index_by_target": {},
            })
            item["target_membership"].append(target)
            item["core_terrain_index_by_target"][target] = row.get("core_terrain_index")
    return list(unique.values())


def parse_features(payload: dict[str, Any]) -> list[dict[str, Any]]:
    """Extract stable, attributable GLiM fields without inventing a class."""
    if payload.get("error"):
        raise RuntimeError(str(payload["error"]))
    output = []
    for feature in payload.get("features", []):
        attrs = feature.get("attributes") or {}
        output.append({
            "feature_id": attrs.get("OBJECTID"),
            "lithology_level_2_code": attrs.get("LithoL2"),
            "lithology_description": attrs.get("Lithology"),
            "lithology_level_1_code": attrs.get("Litho16"),
            "original_feature_id": attrs.get("ORIG_FID"),
        })
    return output


def lookup_one(candidate: dict[str, Any]) -> dict[str, Any]:
    params = {
        "f": "json",
        "where": "1=1",
        "geometry": json.dumps({
            "x": candidate["longitude"],
            "y": candidate["latitude"],
            "spatialReference": {"wkid": 4326},
        }, separators=(",", ":")),
        "geometryType": "esriGeometryPoint",
        "inSR": 4326,
        "spatialRel": "esriSpatialRelIntersects",
        "outFields": "OBJECTID,LithoL2,Lithology,Litho16,ORIG_FID",
        "returnGeometry": "false",
        "outSR": 4326,
    }
    response = session().get(LAYER + "/query", params=params, timeout=(20, 90))
    response.raise_for_status()
    features = parse_features(response.json())
    return {
        "state": "processed" if features else "no_feature_returned",
        "coordinate": {
            "latitude": candidate["latitude"],
            "longitude": candidate["longitude"],
            "status": "approximate GLO-90 window centre; not survey-grade",
        },
        "target_membership": candidate["target_membership"],
        "lithology_features": features,
        "feature_count": len(features),
        "source_query_url": response.url,
    }


def main() -> None:
    if not GLOBAL.exists():
        raise SystemExit("Global discovery merged dataset not found.")
    data = json.loads(GLOBAL.read_text(encoding="utf-8"))
    candidates = shortlist_points(data)
    results: dict[str, dict[str, Any]] = {}
    failures = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
        futures = {pool.submit(lookup_one, row): row for row in candidates}
        for future in concurrent.futures.as_completed(futures):
            row = futures[future]
            try:
                results[row["candidate_id"]] = future.result()
            except Exception as exc:
                failures.append({"candidate_id": row["candidate_id"], "error": str(exc)[:500]})
                results[row["candidate_id"]] = {
                    "state": "unavailable",
                    "coordinate": {"latitude": row["latitude"], "longitude": row["longitude"],
                                   "status": "approximate GLO-90 window centre; not survey-grade"},
                    "target_membership": row["target_membership"],
                    "lithology_features": [],
                    "error": str(exc)[:500],
                }

    successful_queries = len(candidates) - len(failures)
    classified = sum(x.get("state") == "processed" for x in results.values())
    no_feature = sum(x.get("state") == "no_feature_returned" for x in results.values())
    state = "processed" if not failures and classified == len(candidates) else (
        "partially_processed" if successful_queries or classified else "unavailable"
    )
    payload = {
        "schema_version": "1.0.0",
        "generated_at_utc": utcnow(),
        "state": state,
        "scope": {
            "top_candidates_per_target": TOP_PER_TARGET,
            "unique_candidate_points_attempted": len(candidates),
            "successful_point_queries": successful_queries,
            "candidate_points_with_lithology_features": classified,
            "successful_queries_without_returned_feature": no_feature,
            "failed_queries": len(failures),
            "query_success_coverage_percent": round(100 * successful_queries / max(1, len(candidates)), 3),
        },
        "source": {
            "provider": "GLiM / Global Lithological Map",
            "version": "GLiM v1.1 simplified ArcGIS FeatureServer layer",
            "layer": "GLiM_Level2_Pr_SimplifyPolyg (layer 1)",
            "service_url": LAYER,
            "doi": "10.1029/2012GC004370",
            "data_doi": "10.1594/PANGAEA.788537",
            "license": "CC BY 3.0 (PANGAEA gridded GLiM record; confirm terms for the served v1.1 derivative before redistribution)",
            "attribution": "Hartmann, J. and N. Moosdorf (2012), The new global lithological map database GLiM: A representation of rock properties at the Earth's surface, Geochemistry, Geophysics, Geosystems, 13, Q12004.",
            "metadata_last_edit_reported": "2026-08-17",
        },
        "method": {
            "operation": "Point-in-polygon lookup at approximate centre of each retained 5.55 km GLO-90 terrain window",
            "fields": ["LithoL2", "Lithology", "Litho16"],
            "role": "Contextual geology evidence only; excluded from all terrain ranking and scoring.",
        },
        "records": results,
        "failures": failures,
        "limitations": [
            "GLiM is a generalized compilation of regional geological maps; the paper reports an average mapping scale around 1:3,750,000 and the original database is assembled from many national/regional sources.",
            "The returned class is the polygon intersecting the approximate window centre, not an area-weighted lithology mixture across the full 5.55 km window.",
            "No local rock exposure, regolith, mineralogy, soil chemistry, alteration, geotechnical properties or field observations are measured.",
            "Boundary position, source-map scale, compilation and regional mapping coverage can affect the class returned at a point.",
            "This enrichment is applied only to the retained top-100-per-target shortlist, deduplicated by candidate ID; it is not a global lithology raster reprocessing of all 5.85 million terrain windows.",
            "A missing feature is reported as no_feature_returned; it is not converted into a lithology class.",
        ],
    }

    for target in ("moon", "mars"):
        for candidate in data.get("targets", {}).get(target, {}).get("candidate_windows", []):
            candidate["geology_context"] = results.get(candidate.get("id"), {
                "state": "outside_enrichment_shortlist",
                "lithology_features": [],
            })
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    GLOBAL.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"state": state, "scope": payload["scope"], "output": str(OUT)}, indent=2))


if __name__ == "__main__":
    main()

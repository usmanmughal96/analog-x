#!/usr/bin/env python3
"""Discover planetary archive metadata via ODE and USGS Astrogeology STAC.

Discovery only: this script does not download, decode, calibrate or process the
large source products. Every record retains its archive, query and metadata-only
boundary so catalogue hits cannot be mistaken for measurements.
"""
from __future__ import annotations

import json
import re
import sys
import time
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urljoin

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "planetary" / "archive_discovery.json"

ODE_API = "https://oderest.rsl.wustl.edu/live2/"
STAC_API = "https://stac.astrogeology.usgs.gov/api/"
NILI = {
    "name": "Nili Patera / Syrtis Major",
    "latitude_deg": 8.9,
    "longitude_east_deg": 67.0,
    "bbox_wsen": [66.7438569302, 8.6469409271, 67.2561430698, 9.1530590729],
    "bbox_note": "The existing approximately 30 km MOLA comparison window; discovery AOI only, not a surveyed route.",
}

# Exact archive dataset identifiers already used by ANALOG-X and/or official
# archive records. If ODE does not advertise a matching IIPT set, no guessed
# product-type request is sent.
ODE_TARGETS = [
    {
        "id": "mars_hirise_dtm_nili",
        "database": "mars",
        "target": "mars",
        "ihid": "mro",
        "instrument_tokens": ("hirise",),
        "dataset_id": "MRO-M-HIRISE-5-DTM-V1.0",
        "purpose": "Find stereo-derived HiRISE DTMs intersecting the Nili Patera comparison window.",
        "spatially_bounded": True,
    },
    {
        "id": "mars_mola_megdr_nili",
        "database": "mars",
        "target": "mars",
        "ihid": "mgs",
        "instrument_tokens": ("mola",),
        "dataset_id": "MGS-M-MOLA-5-MEGDR-L3-V1.0",
        "purpose": "Discover the MOLA MEGDR topography archive products corresponding to the regional Mars reference.",
        "spatially_bounded": False,
    },
    {
        "id": "moon_lola_reference",
        "database": "moon",
        "target": "moon",
        "ihid": "lro",
        "instrument_tokens": ("lola",),
        "dataset_id": "LRO-L-LOLA-5-GDR-V1.0",
        "purpose": "Discover LRO LOLA gridded reference products and archive metadata.",
        "spatially_bounded": False,
    },
    {
        "id": "moon_diviner_prp",
        "database": "moon",
        "target": "moon",
        "ihid": "lro",
        "instrument_tokens": ("diviner", "dlre"),
        "dataset_id": "LRO-L-DLRE-5-PRP-V2.0",
        "purpose": "Discover LRO Diviner Polar Resource Product metadata already used in the Shackleton thermal summary.",
        "spatially_bounded": False,
    },
]

SESSION = requests.Session()
SESSION.headers.update({
    "User-Agent": "ANALOG-X/1.2 (planetary archive metadata discovery; research prototype)",
    "Accept": "application/json",
})
RETRY = Retry(
    total=2,
    connect=2,
    read=2,
    backoff_factor=1,
    status_forcelist=(429, 500, 502, 503, 504),
    allowed_methods=frozenset(["GET", "POST"]),
    respect_retry_after_header=True,
)
SESSION.mount("https://", HTTPAdapter(max_retries=RETRY))


def xml_to_value(node: ET.Element) -> Any:
    children = list(node)
    if not children:
        return (node.text or "").strip()
    grouped: dict[str, list[Any]] = {}
    for child in children:
        grouped.setdefault(child.tag, []).append(xml_to_value(child))
    return {key: values[0] if len(values) == 1 else values for key, values in grouped.items()}


def response_payload(response: requests.Response) -> dict[str, Any]:
    response.raise_for_status()
    try:
        payload = response.json()
        if isinstance(payload, dict):
            return payload
        return {"_payload": payload}
    except ValueError:
        root = ET.fromstring(response.text)
        converted = xml_to_value(root)
        if isinstance(converted, dict):
            return converted
        return {root.tag: converted}


def unwrap_ode(payload: dict[str, Any]) -> dict[str, Any]:
    value = payload.get("ODEResults") or payload.get("oderesults") or payload
    return value if isinstance(value, dict) else {}


def get_ci(mapping: Any, *names: str) -> Any:
    if not isinstance(mapping, dict):
        return None
    lookup = {str(key).lower(): value for key, value in mapping.items()}
    for name in names:
        if name.lower() in lookup:
            return lookup[name.lower()]
    return None


def text_value(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, (dict, list)):
        return ""
    return str(value).strip()


def as_records(value: Any, preferred_key: str | None = None) -> list[dict[str, Any]]:
    if isinstance(value, list):
        return [item for item in value if isinstance(item, dict)]
    if isinstance(value, dict):
        if preferred_key:
            nested = get_ci(value, preferred_key)
            if nested is not None:
                return as_records(nested)
        return [value]
    return []


def extract_iipt_sets(payload: dict[str, Any]) -> list[dict[str, Any]]:
    root = unwrap_ode(payload)
    sets = get_ci(root, "IIPTSets")
    records = as_records(sets, "IIPTSet")
    if records:
        return records
    # Some service versions flatten the array one level higher.
    return as_records(get_ci(root, "IIPTSet"))


def extract_products(payload: dict[str, Any]) -> tuple[list[dict[str, Any]], int | None]:
    root = unwrap_ode(payload)
    products_container = get_ci(root, "Products")
    products = as_records(products_container, "Product")
    count_value = get_ci(root, "Count")
    count: int | None
    try:
        count = int(count_value) if count_value not in (None, "") else None
    except (TypeError, ValueError):
        count = None
    if not products and isinstance(products_container, list):
        products = [row for row in products_container if isinstance(row, dict)]
    return products, count


def _clean_iipt(row: dict[str, Any]) -> dict[str, Any]:
    keys = ("ODEMetaDB", "IHID", "HName", "IID", "IName", "PT", "PTName", "DataSetId", "NumberProducts", "MinObservationTime", "MaxObservationTime", "ValidFootprints")
    return {key: get_ci(row, key) for key in keys if get_ci(row, key) is not None}


def _clean_product(row: dict[str, Any]) -> dict[str, Any]:
    keys = (
        "ode_id", "pdsid", "ihid", "iid", "pt", "Label_product_type",
        "Data_Set_Id", "PDSVolume_id", "RelativePathToVol", "LabelFileName",
        "Product_creation_time", "Target_name", "Product_id", "Bundle_lid",
        "Collection_lid", "Product_lid", "Observation_id",
    )
    cleaned = {key: get_ci(row, key) for key in keys if get_ci(row, key) is not None}
    # Preserve source product file fields if the ODE version returns them.
    files = get_ci(row, "Product_files")
    if files is not None:
        cleaned["Product_files"] = files
    label = get_ci(row, "label")
    if label is not None:
        cleaned["label"] = label
    return cleaned


def _ode_get(params: dict[str, Any]) -> tuple[dict[str, Any], str]:
    response = SESSION.get(ODE_API, params=params, timeout=(20, 90))
    return response_payload(response), response.url


def _find_matching_iipt_sets(rows: list[dict[str, Any]], spec: dict[str, Any]) -> list[dict[str, Any]]:
    target_dataset = spec["dataset_id"].lower()
    tokens = tuple(token.lower() for token in spec["instrument_tokens"])
    matches = []
    for row in rows:
        clean = _clean_iipt(row)
        host = text_value(clean.get("IHID")).lower()
        instrument_id = text_value(clean.get("IID")).lower()
        instrument_name = text_value(clean.get("IName")).lower()
        dataset_id = text_value(clean.get("DataSetId")).lower()
        if host != spec["ihid"].lower():
            continue
        if not any(token in instrument_id or token in instrument_name for token in tokens):
            continue
        if target_dataset not in dataset_id:
            continue
        # Product type is obtained from the live archive's valid IIPT list,
        # never guessed from a display name.
        if not text_value(clean.get("PT")):
            continue
        matches.append(clean)
    return matches


def query_ode_dataset(spec: dict[str, Any]) -> dict[str, Any]:
    result: dict[str, Any] = {
        "id": spec["id"],
        "provider": "PDS Geosciences Node Orbital Data Explorer (ODE) REST API",
        "target": spec["target"],
        "instrument_host_id": spec["ihid"],
        "dataset_id": spec["dataset_id"],
        "purpose": spec["purpose"],
        "status": "query_error",
        "iipt_query_url": None,
        "query_url": None,
        "iipt_sets": [],
        "product_count": None,
        "products_returned": 0,
        "products": [],
        "spatial_filter": NILI["bbox_wsen"] if spec["spatially_bounded"] else None,
    }
    try:
        iipt_payload, iipt_url = _ode_get({
            "query": "iipt",
            "odemetadb": spec["database"],
            "output": "JSON",
        })
        result["iipt_query_url"] = iipt_url
        status = text_value(get_ci(unwrap_ode(iipt_payload), "Status"))
        if status and status.lower() not in {"success", "ok"}:
            raise RuntimeError(text_value(get_ci(unwrap_ode(iipt_payload), "Error")) or f"ODE IIPT status: {status}")
        all_sets = extract_iipt_sets(iipt_payload)
        matching_sets = _find_matching_iipt_sets(all_sets, spec)
        result["iipt_sets"] = matching_sets
        if not matching_sets:
            result["status"] = "no_matching_iipt_set"
            result["iipt_sets_for_instrument"] = [
                _clean_iipt(row) for row in all_sets
                if text_value(get_ci(row, "IHID")).lower() == spec["ihid"].lower()
                and any(token in text_value(get_ci(row, "IID")).lower() or token in text_value(get_ci(row, "IName")).lower() for token in spec["instrument_tokens"])
            ][:30]
            return result

        products: list[dict[str, Any]] = []
        total_count = 0
        query_urls = []
        for iipt in matching_sets[:5]:
            params: dict[str, Any] = {
                "query": "product",
                "target": spec["target"],
                "ihid": text_value(iipt.get("IHID")),
                "iid": text_value(iipt.get("IID")),
                "pt": text_value(iipt.get("PT")),
                "dsid": spec["dataset_id"],
                "results": "opm",
                "output": "JSON",
                "limit": 20,
                "order": "obd",
            }
            if spec["spatially_bounded"]:
                west, south, east, north = NILI["bbox_wsen"]
                params.update({
                    "westernlon": west,
                    "easternlon": east,
                    "minlat": south,
                    "maxlat": north,
                    "loc": "b",
                })
            query_payload, query_url = _ode_get(params)
            query_urls.append(query_url)
            root = unwrap_ode(query_payload)
            query_status = text_value(get_ci(root, "Status"))
            if query_status and query_status.lower() not in {"success", "ok"}:
                raise RuntimeError(text_value(get_ci(root, "Error")) or f"ODE product status: {query_status}")
            rows, count = extract_products(query_payload)
            if count is not None:
                total_count += count
            products.extend(_clean_product(row) for row in rows)

        result["query_url"] = query_urls[0] if len(query_urls) == 1 else query_urls
        result["product_count"] = total_count if total_count else (len(products) if products else 0)
        result["products"] = products[:100]
        result["products_returned"] = len(result["products"])
        result["status"] = "products_returned" if products else ("no_products_in_aoi" if spec["spatially_bounded"] else "no_products_returned")
        result["metadata_note"] = "ODE metadata only. Product files have not been downloaded, decoded or validated by this discovery step."
    except Exception as exc:
        result["error"] = str(exc)[:1200]
    return result


def query_stac_hirise_rdr() -> dict[str, Any]:
    """Discover HiRISE RDR image observations around Nili Patera, not DTMs."""
    base = {
        "id": "usgs_hirise_rdr_nili",
        "provider": "USGS Astrogeology Analysis Ready Data STAC API",
        "collection": "mro_hirise_uncontrolled_observations",
        "target": "Mars",
        "purpose": "Find HiRISE image observations intersecting Nili Patera; imagery metadata is not a terrain DTM.",
        "status": "query_error",
        "query_url": None,
        "matched": None,
        "items_returned": 0,
        "items": [],
    }
    try:
        west, south, east, north = NILI["bbox_wsen"]
        url = urljoin(STAC_API, "search")
        params = {
            "collections": base["collection"],
            "bbox": ",".join(str(v) for v in (west, south, east, north)),
            "limit": 20,
        }
        response = SESSION.get(url, params=params, timeout=(20, 90))
        base["query_url"] = response.url
        response.raise_for_status()
        payload = response.json()
        features = payload.get("features", []) if isinstance(payload, dict) else []
        features = features if isinstance(features, list) else []
        links = payload.get("links", []) if isinstance(payload, dict) else []
        number_matched = payload.get("context", {}).get("matched") if isinstance(payload.get("context"), dict) else payload.get("numberMatched")
        base["matched"] = number_matched
        base["items"] = [
            {
                "id": item.get("id"),
                "collection": item.get("collection"),
                "datetime": (item.get("properties") or {}).get("datetime"),
                "start_datetime": (item.get("properties") or {}).get("start_datetime"),
                "end_datetime": (item.get("properties") or {}).get("end_datetime"),
                "gsd": (item.get("properties") or {}).get("gsd"),
                "geometry": item.get("geometry"),
                "assets": {
                    key: {
                        "href": asset.get("href"),
                        "type": asset.get("type"),
                        "roles": asset.get("roles"),
                        "title": asset.get("title"),
                    }
                    for key, asset in (item.get("assets") or {}).items()
                    if isinstance(asset, dict)
                },
            }
            for item in features[:20] if isinstance(item, dict)
        ]
        base["items_returned"] = len(base["items"])
        base["status"] = "items_returned" if base["items"] else "no_items_in_aoi"
        base["next_page_available"] = any(
            isinstance(link, dict) and link.get("rel") == "next" for link in links
        )
        base["metadata_note"] = "HiRISE RDR imagery metadata only. This is not a stereo DTM and no image asset is downloaded here."
    except Exception as exc:
        base["error"] = str(exc)[:1200]
    return base


def main() -> None:
    results = [query_ode_dataset(spec) for spec in ODE_TARGETS]
    # Small pause between archive requests to avoid hammering the public API.
    time.sleep(0.5)
    stac_result = query_stac_hirise_rdr()
    output = {
        "schema_version": "1.0.0",
        "generated_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "purpose": "Fallback archive discovery for planetary products when the federated PDS Search API is unavailable.",
        "coverage": "Targeted metadata discovery for Nili Patera HiRISE DTM, regional MOLA MEGDR, lunar LOLA GDR, Diviner PRP and Nili-area HiRISE RDR observations.",
        "nili_patera_aoi": NILI,
        "ode": {
            "provider": "PDS Geosciences Node Orbital Data Explorer (ODE)",
            "api": ODE_API,
            "manual": "https://oderest.rsl.wustl.edu/ODE_REST_V2.1.6.pdf",
            "queries": results,
            "limitations": [
                "ODE product records are metadata; they are not processed science rasters.",
                "Product types are taken from the live ODE IIPT list; a missing IIPT set is recorded, not guessed.",
                "The HiRISE DTM query is spatially bounded to the existing Nili Patera MOLA comparison AOI.",
                "ODE query counts may refer to the full matching product set even when the metadata sample is limited to 20 records.",
            ],
        },
        "usgs_astrogeology_stac": stac_result,
        "interpretation": {
            "discovery_is_not_processing": True,
            "hires_rdr_is_not_dtm": True,
            "product_binary_downloaded": False,
            "rover_safety_assessed": False,
            "mission_suitability_certified": False,
        },
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(output, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps({
        "output": str(OUT.relative_to(ROOT)),
        "ode_statuses": {result["id"]: result["status"] for result in results},
        "stac_status": stac_result["status"],
        "ode_products_returned": sum(result["products_returned"] for result in results),
        "stac_items_returned": stac_result["items_returned"],
    }, indent=2))


if __name__ == "__main__":
    main()

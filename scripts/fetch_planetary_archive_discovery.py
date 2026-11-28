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

# ODE's Mars product-location filter can be center-based. The known HiRISE
# Nili dunes DTM is centred at 67.33 E, outside the original MOLA comparison
# window's eastern edge (67.256 E). This secondary discovery box includes that
# published center but does not redefine the original MOLA comparison AOI.
NILI_HIRISE_DTM_DISCOVERY_BBOX = [
    NILI["bbox_wsen"][0], NILI["bbox_wsen"][1], 67.42, NILI["bbox_wsen"][3]
]

KNOWN_NILI_HIRISE_DTM = {
    "id": "DTEEC_017762_1890_018039_1890_A01",
    "title": "Topography of Moving Dunes in Nili Patera",
    "provider": "University of Arizona HiRISE Operations Center / NASA-JPL-Caltech",
    "source_page_url": "https://www.uahirise.org/dtm/dtm.php?ID=ESP_017762_1890",
    "data_file_url": (
        "https://www.uahirise.org/PDS/DTM/ESP/ORB_017700_017799/"
        "ESP_017762_1890_ESP_018039_1890/"
        "DTEEC_017762_1890_018039_1890_A01.IMG"
    ),
    "reported_file_size_mb": 430,
    "center_latitude_deg": 8.781,
    "center_longitude_east_deg": 67.33,
    "map_scale_m_per_pixel": 1.01,
    "stereo_pair": ["ESP_017762_1890", "ESP_018039_1890"],
    "relative_path_to_volume": "dtm\\esp\\orb_017700_017799\\esp_017762_1890_esp_018039_1890\\",
    "core_mola_aoi_center_inside": False,
    "core_mola_aoi_footprint_intersection": "not_yet_verified_from_product_label",
    "status": "known_catalogued_reference",
    "metadata_boundary": (
        "The published center is outside the original MOLA comparison box. "
        "The enlarged ODE discovery box is only a catalogue search window; "
        "it does not prove that the DTM footprint overlaps the original AOI."
    ),
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
        "product_type_filter": "DTM",
        "purpose": "Find stereo-derived HiRISE DTMs around Nili Patera, including the published dune-DTM center just east of the original MOLA comparison box.",
        "spatially_bounded": True,
        "spatial_bbox": NILI_HIRISE_DTM_DISCOVERY_BBOX,
    },
    {
        "id": "mars_mola_megdr_nili",
        "database": "mars",
        "target": "mars",
        "ihid": "mgs",
        "instrument_tokens": ("mola",),
        "dataset_id": "mgs_mola_topography_derived-data_meg064",
        "product_type_filter": "MEGDR",
        "purpose": "Discover the MOLA MEGDR topography archive products corresponding to the regional Mars reference.",
        "spatially_bounded": False,
    },
    {
        "id": "moon_lola_reference",
        "database": "moon",
        "target": "moon",
        "ihid": "lro",
        "instrument_tokens": ("lola",),
        "dataset_id": "lro_lola_rdr-data_gridded",
        "product_type_filter": "GDRDEM",
        "purpose": "Discover LRO LOLA gridded reference products and archive metadata.",
        "spatially_bounded": False,
    },
    {
        "id": "moon_diviner_prp",
        "database": "moon",
        "target": "moon",
        "ihid": "lro",
        "instrument_tokens": ("diviner", "dlre"),
        "dataset_id": "lro_diviner_derived_prp",
        "product_type_filter": "PRP",
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
        # never guessed from a display name. A strict requested type prevents
        # selecting another product family from a shared PDS4 data-set bundle.
        product_type = text_value(clean.get("PT"))
        if not product_type:
            continue
        requested_type = text_value(spec.get("product_type_filter"))
        if requested_type and product_type.lower() != requested_type.lower():
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
        "spatial_filter": spec.get("spatial_bbox", NILI["bbox_wsen"]) if spec["spatially_bounded"] else None,
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
                west, south, east, north = spec.get("spatial_bbox", NILI["bbox_wsen"])
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


def parse_pds_label_text(text):
    """Parse scalar fields from a PDS3 label prefix without needing a PDS parser."""
    fields = {}
    terminated = False
    for line in text.splitlines():
        if line.strip().upper() == "END":
            terminated = True
            break
        if "=" not in line:
            continue
        key, raw = line.split("=", 1)
        key = key.strip().upper()
        value = raw.strip().strip('"').strip("'")
        if not key:
            continue
        fields[key + "_RAW"] = raw.strip()
        scalar = value.split()[0] if value else ""
        try:
            number = float(scalar)
            fields[key] = int(number) if number.is_integer() else number
        except (TypeError, ValueError):
            fields[key] = value
    fields["_LABEL_TERMINATED"] = terminated
    return fields


def _pds_number(fields, key):
    value = fields.get(key)
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        try:
            return float(value.split()[0])
        except (ValueError, IndexError):
            return None
    return None


def _core_aoi_intersection(bounds):
    west, south, east, north = NILI["bbox_wsen"]
    min_lat = bounds.get("min_lat")
    max_lat = bounds.get("max_lat")
    west_lon = bounds.get("west_lon")
    east_lon = bounds.get("east_lon")
    if None in (min_lat, max_lat, west_lon, east_lon):
        return None
    lat_ok = max_lat >= south and min_lat <= north
    if west_lon <= east_lon:
        lon_ok = east_lon >= west and west_lon <= east
    else:
        lon_ok = west_lon <= east or east_lon >= west
    return bool(lat_ok and lon_ok)


def build_known_dtm_reference(label_inspection):
    """Promote a verified PDS-label footprint result to the top-level record."""
    record = {
        **KNOWN_NILI_HIRISE_DTM,
        "pds_label_inspection": label_inspection,
    }
    intersection = label_inspection.get("core_mola_aoi_footprint_intersection")
    if isinstance(intersection, bool):
        record["core_mola_aoi_footprint_intersection"] = intersection
        if intersection:
            record["metadata_boundary"] = (
                "The complete PDS-label geographic bounding box intersects the original "
                "MOLA comparison AOI. This is a bbox result only, not evidence of terrain "
                "registration, scientific equivalence or rover suitability."
            )
        else:
            record["metadata_boundary"] = (
                "The complete PDS-label geographic bounding box does not intersect the "
                "original MOLA comparison AOI. Treat this DTM as an adjacent high-resolution "
                "dune-field reference, not as co-located MOLA terrain."
            )
    else:
        record["core_mola_aoi_footprint_intersection"] = "not_yet_verified_from_product_label"
        record["metadata_boundary"] = (
            "The PDS-label footprint intersection is unknown because a complete geographic "
            "bounding box was not available from the capped label inspection. Do not infer "
            "overlap from the published center or the wider discovery search box."
        )
    return record


def build_hirise_dtm_img_url(product):
    """Build a public HiRISE DTM IMG URL from trusted ODE volume metadata."""
    pdsid = text_value(get_ci(product, "pdsid")).upper()
    relative = text_value(get_ci(product, "RelativePathToVol"))
    dataset_id = text_value(get_ci(product, "Data_Set_Id"))
    instrument_host = text_value(get_ci(product, "ihid"))
    instrument_id = text_value(get_ci(product, "iid"))
    product_type = text_value(get_ci(product, "pt"))

    if dataset_id != "MRO-M-HIRISE-5-DTM-V1.0":
        raise ValueError("Product is not in the MRO HiRISE DTM data set")
    if instrument_host.lower() != "mro" or instrument_id.lower() != "hirise":
        raise ValueError("Product is not an MRO HiRISE observation")
    if product_type.upper() != "DTM":
        raise ValueError("Product type is not DTM")
    if not re.fullmatch(r"DTEE[CD]_\d{6}_\d{4}_\d{6}_\d{4}_A\d{2}", pdsid):
        raise ValueError("ODE pdsid is not a recognized HiRISE DTM product identifier")

    normalized = relative.replace("\\", "/").strip("/")
    parts = normalized.split("/") if normalized else []
    if len(parts) < 3 or [part.lower() for part in parts[:2]] != ["dtm", "esp"]:
        raise ValueError("ODE RelativePathToVol is not a HiRISE DTM volume path")
    directories = parts[2:]
    if any(
        not part
        or part in {".", ".."}
        or not re.fullmatch(r"[A-Za-z0-9_-]+", part)
        for part in directories
    ):
        raise ValueError("ODE RelativePathToVol contains unsafe path components")

    relative_directory = "/".join(part.upper() for part in directories)
    return (
        "https://www.uahirise.org/PDS/DTM/ESP/"
        + relative_directory
        + "/"
        + pdsid
        + ".IMG"
    )


def inspect_hirise_dtm_product_label(product, max_bytes=262144):
    """Inspect only a bounded embedded PDS3 label prefix; never fetch the full DTM."""
    pdsid = text_value(get_ci(product, "pdsid")).upper()
    result = {
        "pdsid": pdsid or None,
        "ode_id": get_ci(product, "ode_id"),
        "status": "not_checked",
        "source_url": None,
        "http_status": None,
        "content_range": None,
        "bytes_read": 0,
        "max_bytes": max_bytes,
        "label_terminated": False,
        "fields": {},
        "bounds": {},
        "core_mola_aoi_footprint_intersection": None,
        "limitations": [
            "Only a bounded byte-range prefix is requested; the full DTM raster is not downloaded.",
            "Footprint intersection is computed only when the embedded label provides all four geographic bounds.",
            "A geographic bounding-box intersection is not proof of raster co-registration, pixel-level coverage, rover safety or route suitability.",
        ],
    }
    response = None
    try:
        source_url = build_hirise_dtm_img_url(product)
        result["source_url"] = source_url
        response = SESSION.get(
            source_url,
            headers={
                "Range": "bytes=0-" + str(max_bytes - 1),
                "Accept-Encoding": "identity",
            },
            stream=True,
            timeout=(20, 60),
            allow_redirects=True,
        )
        result["http_status"] = response.status_code
        result["final_url"] = response.url
        result["content_range"] = response.headers.get("Content-Range")
        if response.status_code not in (200, 206):
            response.raise_for_status()

        body = bytearray()
        for chunk in response.iter_content(chunk_size=32768):
            if not chunk:
                continue
            body.extend(chunk[: max_bytes - len(body)])
            if len(body) >= max_bytes:
                break
        result["bytes_read"] = len(body)
        label = parse_pds_label_text(bytes(body).decode("ascii", errors="replace"))
        result["label_terminated"] = bool(label.get("_LABEL_TERMINATED"))
        keep = (
            "PDS_VERSION_ID", "PRODUCT_ID", "DATA_SET_ID",
            "PRODUCT_CREATION_TIME", "MAP_PROJECTION_TYPE", "MAP_SCALE",
            "MAP_RESOLUTION", "CENTER_LATITUDE", "CENTER_LONGITUDE",
            "MINIMUM_LATITUDE", "MAXIMUM_LATITUDE", "WESTERNMOST_LONGITUDE",
            "EASTERNMOST_LONGITUDE", "LINE_SAMPLES", "LINES", "SAMPLE_TYPE",
            "SAMPLE_BITS", "OFFSET", "SCALING_FACTOR", "MISSING_CONSTANT",
            "POSITIVE_LONGITUDE_DIRECTION", "A_AXIS_RADIUS", "C_AXIS_RADIUS",
        )
        result["fields"] = {key: label[key] for key in keep if key in label}
        if not result["label_terminated"]:
            result["status"] = "label_not_complete_within_range_cap"
            return result

        bounds = {
            "min_lat": _pds_number(label, "MINIMUM_LATITUDE"),
            "max_lat": _pds_number(label, "MAXIMUM_LATITUDE"),
            "west_lon": _pds_number(label, "WESTERNMOST_LONGITUDE"),
            "east_lon": _pds_number(label, "EASTERNMOST_LONGITUDE"),
        }
        result["bounds"] = bounds
        intersection = _core_aoi_intersection(bounds)
        result["core_mola_aoi_footprint_intersection"] = intersection
        if intersection is None:
            result["status"] = "label_read_but_geographic_bounds_incomplete"
        elif intersection:
            result["status"] = "label_verified_bounds_intersect_core_aoi"
        else:
            result["status"] = "label_verified_bounds_outside_core_aoi"
        return result
    except Exception as exc:
        result["status"] = "label_request_error"
        result["error"] = str(exc)[:1000]
        return result
    finally:
        if response is not None:
            response.close()


def inspect_hirise_dtm_products(products, max_bytes=262144, pause_seconds=0.25):
    """Inspect each unique ODE HiRISE DTM label with a bounded prefix request."""
    inspections = []
    seen = set()
    unique_products = []
    for product in products:
        pdsid = text_value(get_ci(product, "pdsid")).upper()
        if not pdsid or pdsid in seen:
            continue
        seen.add(pdsid)
        unique_products.append(product)

    for index, product in enumerate(unique_products):
        if index and pause_seconds > 0:
            time.sleep(pause_seconds)
        inspections.append(
            inspect_hirise_dtm_product_label(product, max_bytes=max_bytes)
        )
    return inspections


def inspect_known_hirise_dtm_label(max_bytes=262144):
    """Compatibility wrapper for the original Nili dunes DTM reference."""
    product = {
        "pdsid": KNOWN_NILI_HIRISE_DTM["id"],
        "ode_id": None,
        "ihid": "MRO",
        "iid": "HiRISE",
        "pt": "DTM",
        "Data_Set_Id": "MRO-M-HIRISE-5-DTM-V1.0",
        "RelativePathToVol": KNOWN_NILI_HIRISE_DTM["relative_path_to_volume"],
    }
    return inspect_hirise_dtm_product_label(product, max_bytes=max_bytes)


def main() -> None:
    results = [query_ode_dataset(spec) for spec in ODE_TARGETS]
    # Small pause between archive requests to avoid hammering the public API.
    time.sleep(0.5)
    stac_result = query_stac_hirise_rdr()

    hirise_query = next(
        (result for result in results if result.get("id") == "mars_hirise_dtm_nili"),
        {},
    )
    hirise_products = hirise_query.get("products", [])
    dtm_label_inspections = inspect_hirise_dtm_products(hirise_products)

    inspection_by_id = {
        inspection.get("pdsid"): inspection
        for inspection in dtm_label_inspections
        if inspection.get("pdsid")
    }
    known_dtm_inspection = inspection_by_id.get(KNOWN_NILI_HIRISE_DTM["id"])
    if known_dtm_inspection is None:
        # Preserve an explicit unknown/error state if ODE omits the known
        # catalogue record; do not infer its footprint from its center.
        known_dtm_inspection = inspect_known_hirise_dtm_label()
        dtm_label_inspections.append(known_dtm_inspection)

    known_dtm_reference = build_known_dtm_reference(known_dtm_inspection)
    reference_titles = {
        "DTEED_013582_1895_020940_1895_A01": "Mound on Nili Patera floor",
        "DTEEC_017762_1890_018039_1890_A01": "Topography of Moving Dunes in Nili Patera",
        "DTEEC_043779_1890_043423_1890_A01": "Nili Patera stereo DTM",
        "DTEEC_050438_1890_051071_1890_A01": "Nili Patera monitoring DTM",
    }
    label_inspection_references = []
    for product in hirise_products:
        pdsid = text_value(get_ci(product, "pdsid")).upper()
        if not pdsid:
            continue
        inspection = inspection_by_id.get(pdsid)
        if inspection is None:
            continue
        intersection = inspection.get("core_mola_aoi_footprint_intersection")
        if intersection is True:
            boundary = (
                "The complete PDS-label bounding box intersects the original MOLA "
                "comparison AOI. This is only a footprint-screening result; it does "
                "not establish pixel coverage, raster co-registration or science readiness."
            )
        elif intersection is False:
            boundary = (
                "The complete PDS-label bounding box does not intersect the original "
                "MOLA comparison AOI. Keep this DTM as a separate adjacent reference."
            )
        else:
            boundary = (
                "Footprint relation to the original MOLA comparison AOI is unknown; "
                "the label did not provide a complete, verified geographic bounding box."
            )
        label_inspection_references.append({
            "pdsid": pdsid,
            "ode_id": get_ci(product, "ode_id"),
            "title": reference_titles.get(pdsid, pdsid),
            "data_file_url": inspection.get("source_url"),
            "relative_path_to_volume": get_ci(product, "RelativePathToVol"),
            "reported_file_size_mb": 430 if pdsid == KNOWN_NILI_HIRISE_DTM["id"] else None,
            "label_inspection": inspection,
            "core_mola_aoi_footprint_intersection": intersection if isinstance(intersection, bool) else "unknown",
            "metadata_boundary": boundary,
        })

    intersecting_dtm_ids = [
        row["pdsid"] for row in label_inspection_references
        if row["core_mola_aoi_footprint_intersection"] is True
    ]
    outside_dtm_ids = [
        row["pdsid"] for row in label_inspection_references
        if row["core_mola_aoi_footprint_intersection"] is False
    ]
    unknown_dtm_ids = [
        row["pdsid"] for row in label_inspection_references
        if row["core_mola_aoi_footprint_intersection"] == "unknown"
    ]
    labels_terminated = sum(
        row["label_inspection"].get("label_terminated") is True
        for row in label_inspection_references
    )
    labels_with_verified_bounds = sum(
        row["core_mola_aoi_footprint_intersection"] in (True, False)
        for row in label_inspection_references
    )

    output = {
        "schema_version": "1.1.0",
        "generated_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "purpose": "Fallback archive discovery for planetary products when the federated PDS Search API is unavailable.",
        "coverage": "Targeted metadata discovery for Nili Patera HiRISE DTM products, regional MOLA MEGDR, lunar LOLA GDR, Diviner PRP and Nili-area HiRISE RDR observations. Every returned HiRISE DTM has an independent capped PDS-label footprint inspection.",
        "nili_patera_aoi": NILI,
        "known_nili_hirise_dtm_reference": known_dtm_reference,
        "nili_hirise_dtm_references": label_inspection_references,
        "nili_hirise_dtm_footprint_summary": {
            "ode_dtm_products_returned": len(hirise_products),
            "unique_dtm_label_inspection_attempts": len(dtm_label_inspections),
            "terminated_labels_read": labels_terminated,
            "labels_with_verified_geographic_bounds": labels_with_verified_bounds,
            "bbox_intersecting_core_mola_aoi": intersecting_dtm_ids,
            "bbox_outside_core_mola_aoi": outside_dtm_ids,
            "bbox_intersection_unknown": unknown_dtm_ids,
            "interpretation": (
                "PDS-label bounding boxes are a footprint triage step only. Even a "
                "bounding-box intersection does not establish pixel-level coverage, "
                "horizontal/vertical registration, compatible vertical datum, raster "
                "quality or readiness for quantitative terrain analysis."
            ),
        },
        "nili_hirise_dtm_discovery_bbox_wsen": NILI_HIRISE_DTM_DISCOVERY_BBOX,
        "ode": {
            "provider": "PDS Geosciences Node Orbital Data Explorer (ODE)",
            "api": ODE_API,
            "manual": "https://oderest.rsl.wustl.edu/ODE_REST_V2.1.6.pdf",
            "queries": results,
            "limitations": [
                "ODE product records are metadata; they are not processed science rasters.",
                "Product types are taken from the live ODE IIPT list; a missing IIPT set is recorded, not guessed.",
                "The primary MOLA comparison AOI remains unchanged. The separate HiRISE DTM discovery box is expanded eastward to include Nili Patera DTM catalogue records whose reported centers may be east of the core AOI.",
                "Every returned HiRISE DTM is inspected using only a capped prefix of its embedded PDS3 label. The full DTM .IMG rasters are not downloaded.",
                "A label bbox intersection is necessary for a possible co-located raster but is not sufficient to prove it; pixel coverage and coordinate registration must be checked before processing.",
                "ODE query counts may refer to the full matching product set even when the metadata sample is limited to 20 records.",
            ],
        },
        "usgs_astrogeology_stac": stac_result,
        "interpretation": {
            "discovery_is_not_processing": True,
            "hires_rdr_is_not_dtm": True,
            "product_binary_downloaded": False,
            "full_dtm_raster_downloaded": False,
            "dtm_label_prefix_inspected": labels_terminated > 0,
            "dtm_labels_attempted": len(dtm_label_inspections),
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
        "hirise_dtm_labels_attempted": len(dtm_label_inspections),
        "hirise_dtm_labels_terminated": labels_terminated,
        "hirise_dtm_bbox_intersections": intersecting_dtm_ids,
        "hirise_dtm_bbox_outside": outside_dtm_ids,
        "hirise_dtm_bbox_unknown": unknown_dtm_ids,
    }, indent=2))




if __name__ == "__main__":
    main()

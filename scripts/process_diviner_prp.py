#!/usr/bin/env python3
"""Stream NASA Diviner south-polar PRP and summarize the Shackleton Rim window.

The full 604.8 MB source table is streamed and not committed. Only the small
reproducible AOI summary JSON is written to the repository.
"""
from __future__ import annotations

import csv
import json
import math
import re
import statistics
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

import requests
import xml.etree.ElementTree as ET

BASE = "https://pds-geosciences.wustl.edu/lro/urn-nasa-pds-lro_diviner_derived1/"
LABEL_URL = BASE + "data_derived_prp/dlre_prp_south.xml"
PDS3_LABEL_URL = "https://pds-geosciences.wustl.edu/lro/lro-l-dlre-4-rdr-v1/lrodlr_1001/data/prp/DLRE_PRP_SOUTH.LBL"
TAB_CANDIDATES = [
    BASE + "data_derived_prp/dlre_prp_south.tab",
    BASE + "data_derived_prp/DLRE_PRP_SOUTH.TAB",
]
OUTPUT = Path("data/moon/shackleton_diviner_prp.json")

# Shackleton Rim R04 / Site04 reference used by the existing ANALOG-X LOLA AOI.
CENTER_LAT_DEG = -89.7668
CENTER_LON_EAST_DEG = 188.13
AOI_SIDE_KM = 29.6
MOON_RADIUS_KM = 1737.4
INVALID_ICE_DEPTH = -999.0
EXPECTED_RECORDS = 2_880_000


def parse_pds3_table_layout(label_text: str) -> dict:
    """Read the fixed-width table layout from the authoritative PDS3 product label."""
    def integer(scope: str, key: str) -> int:
        match = re.search(rf"(?im)^\s*{re.escape(key)}\s*=\s*(\d+)", scope)
        if not match:
            raise RuntimeError(f"PDS3 Diviner label is missing {key}")
        return int(match.group(1))

    header_match = re.search(
        r"(?is)OBJECT\s*=\s*HEADER(.*?)END_OBJECT\s*=\s*HEADER", label_text
    )
    table_match = re.search(
        r"(?is)OBJECT\s*=\s*TABLE(.*?)END_OBJECT\s*=\s*TABLE", label_text
    )
    if not header_match or not table_match:
        raise RuntimeError("PDS3 Diviner label must define HEADER and TABLE objects")

    record_bytes = integer(label_text, "RECORD_BYTES")
    file_records = integer(label_text, "FILE_RECORDS")
    header_bytes = integer(header_match.group(1), "BYTES")
    row_bytes = integer(table_match.group(1), "ROW_BYTES")
    rows = integer(table_match.group(1), "ROWS")
    columns = integer(table_match.group(1), "COLUMNS")

    if rows != file_records:
        raise RuntimeError(f"PDS3 table row count disagrees with FILE_RECORDS: {rows} != {file_records}")
    if row_bytes != record_bytes:
        raise RuntimeError(f"PDS3 ROW_BYTES ({row_bytes}) disagrees with RECORD_BYTES ({record_bytes})")
    if header_bytes <= 0 or row_bytes <= 0 or columns <= 0:
        raise RuntimeError("PDS3 Diviner table layout contains non-positive dimensions")
    return {
        "records": rows,
        "record_length_bytes": row_bytes,
        "header_offset_bytes": header_bytes,
        "columns": columns,
        "declared_file_bytes": header_bytes + rows * row_bytes,
    }


def fetch_product_label(session: requests.Session) -> tuple[dict, str]:
    response = session.get(LABEL_URL, timeout=(20, 120))
    response.raise_for_status()
    root = ET.fromstring(response.content)
    ns = {"pds": "http://pds.nasa.gov/pds4/pds/v1"}

    table = root.find(".//pds:Table_Character", ns)
    if table is None:
        raise RuntimeError("Diviner PDS4 label has no Table_Character section")
    pds4_records = int(table.findtext("pds:records", default="0", namespaces=ns))
    pds4_record_length = int(table.findtext(".//pds:record_length", default="0", namespaces=ns))
    file_name = root.findtext(".//pds:File/pds:file_name", default="", namespaces=ns)

    # The PDS4 label omits this legacy ASCII table's fixed record length.
    # Use the linked PDS3 label for exact byte layout and retain PDS4 field metadata.
    layout_response = session.get(PDS3_LABEL_URL, timeout=(20, 120))
    layout_response.raise_for_status()
    layout = parse_pds3_table_layout(layout_response.text)
    records = layout["records"]
    record_length = layout["record_length_bytes"]
    if pds4_records not in (0, records):
        raise RuntimeError(f"PDS4/PDS3 record counts disagree: {pds4_records} != {records}")
    if pds4_record_length not in (0, record_length):
        raise RuntimeError(f"PDS4/PDS3 record lengths disagree: {pds4_record_length} != {record_length}")
    if records != EXPECTED_RECORDS or record_length != 210 or layout["columns"] != 15:
        raise RuntimeError(f"Unexpected Diviner source table structure: {layout}")

    fields = {}
    for field in root.findall(".//pds:Field_Character", ns):
        name = field.findtext("pds:name", default="", namespaces=ns).strip()
        if not name:
            continue
        invalid = field.findtext(".//pds:invalid_constant", default=None, namespaces=ns)
        fields[name] = {
            "field_number": int(field.findtext("pds:field_number", default="0", namespaces=ns) or 0),
            "start_byte": int(field.findtext("pds:field_location", default="0", namespaces=ns) or 0),
            "field_length_bytes": int(field.findtext("pds:field_length", default="0", namespaces=ns) or 0),
            "unit": field.findtext("pds:unit", default=None, namespaces=ns),
            "description": " ".join((field.findtext("pds:description", default="", namespaces=ns) or "").split()),
            "invalid_constant": float(invalid) if invalid is not None else None,
        }

    required = {"tri_clon", "tri_clat", "temp_avg", "temp_max", "ice_depth"}
    missing = sorted(required - set(fields))
    if missing:
        raise RuntimeError(f"Diviner label missing fields: {missing}")
    if fields["temp_avg"]["unit"] != "Kelvin" or fields["temp_max"]["unit"] != "Kelvin":
        raise RuntimeError("Unexpected Diviner temperature units; refusing to process")
    if fields["ice_depth"]["unit"] != "meter":
        raise RuntimeError("Unexpected Diviner ice_depth units; refusing to process")
    if fields["ice_depth"]["invalid_constant"] != INVALID_ICE_DEPTH:
        raise RuntimeError("Unexpected Diviner ice_depth invalid constant; refusing to process")
    return {
        "pds4_product_title": root.findtext(".//pds:title", default="LRO Diviner South Polar Resource Product", namespaces=ns),
        "logical_identifier": root.findtext(".//pds:logical_identifier", default=None, namespaces=ns),
        "version_id": root.findtext(".//pds:version_id", default=None, namespaces=ns),
        "file_name": file_name,
        "records": records,
        "record_length_bytes": record_length,
        "header_offset_bytes": layout["header_offset_bytes"],
        "declared_file_bytes": layout["declared_file_bytes"],
        "pds3_layout_columns": layout["columns"],
        "source_layout_label_url": layout_response.url,
        "fields": fields,
        "source_label_url": LABEL_URL,
        "dataset_doi": "10.17189/1520650",
        "bundle_doi": "10.17189/wj0s-w188",
    }, response.url


def angular_distance_and_bearing(lat_deg: float, lon_deg: float) -> tuple[float, float]:
    """Return central angle (rad) and initial bearing from the AOI centre."""
    lat1 = math.radians(CENTER_LAT_DEG)
    lat2 = math.radians(lat_deg)
    delta_lon_deg = (lon_deg - CENTER_LON_EAST_DEG + 180.0) % 360.0 - 180.0
    delta_lon = math.radians(delta_lon_deg)
    dlat = lat2 - lat1
    a = math.sin(dlat / 2.0) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(delta_lon / 2.0) ** 2
    a = min(1.0, max(0.0, a))
    central = 2.0 * math.asin(math.sqrt(a))
    bearing = math.atan2(
        math.sin(delta_lon) * math.cos(lat2),
        math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(delta_lon),
    )
    return central, bearing


def local_aeqd_km(lat_deg: float, lon_deg: float) -> tuple[float, float]:
    """Azimuthal-equidistant local east/north coordinates in lunar km."""
    central, bearing = angular_distance_and_bearing(lat_deg, lon_deg)
    distance = MOON_RADIUS_KM * central
    return distance * math.sin(bearing), distance * math.cos(bearing)


def parse_number(row: dict, key: str) -> float | None:
    raw = row.get(key)
    if raw is None:
        return None
    try:
        value = float(raw.strip())
    except (TypeError, ValueError):
        return None
    return value if math.isfinite(value) else None


def percentile(values: list[float], p: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    pos = (len(ordered) - 1) * p
    lo = math.floor(pos)
    hi = math.ceil(pos)
    if lo == hi:
        return ordered[lo]
    return ordered[lo] * (hi - pos) + ordered[hi] * (pos - lo)


def summarize(values: list[float], unit: str, description: str) -> dict:
    return {
        "count": len(values),
        "unit": unit,
        "description": description,
        "minimum": min(values) if values else None,
        "p10": percentile(values, 0.10),
        "median": statistics.median(values) if values else None,
        "mean": statistics.fmean(values) if values else None,
        "p90": percentile(values, 0.90),
        "maximum": max(values) if values else None,
    }


def select_source_table(session: requests.Session) -> tuple[str, int | None]:
    failures = []
    for url in TAB_CANDIDATES:
        try:
            response = session.head(url, allow_redirects=True, timeout=(20, 90))
            if response.status_code == 200:
                length = response.headers.get("Content-Length")
                return response.url, int(length) if length and length.isdigit() else None
            failures.append({"url": url, "status": response.status_code})
        except requests.RequestException as exc:
            failures.append({"url": url, "error": str(exc)})
    raise RuntimeError(f"Could not locate Diviner south-polar TAB file: {failures}")


def process_table(session: requests.Session, url: str, expected_bytes: int | None, label: dict) -> dict:
    started = time.monotonic()
    declared_bytes = label["header_offset_bytes"] + label["records"] * label["record_length_bytes"]
    if label.get("declared_file_bytes", declared_bytes) != declared_bytes:
        raise RuntimeError("PDS3 Diviner label contains inconsistent declared byte count")
    if expected_bytes is not None and expected_bytes != declared_bytes:
        raise RuntimeError(f"Diviner table size disagrees with PDS3 label: {expected_bytes} != {declared_bytes}")
    response = session.get(url, stream=True, timeout=(30, 180))
    response.raise_for_status()
    response.raw.decode_content = True
    actual_length = response.headers.get("Content-Length")
    if expected_bytes and actual_length and int(actual_length) != expected_bytes:
        raise RuntimeError(f"Unexpected Diviner table length: expected {expected_bytes}, got {actual_length}")

    half = AOI_SIDE_KM / 2.0
    temp_avg: list[float] = []
    temp_max: list[float] = []
    ice_depth: list[float] = []
    surface_stable = 0
    invalid_ice = 0
    candidate_rows = 0
    selected_rows = 0
    all_rows = 0
    min_x = min_y = float("inf")
    max_x = max_y = float("-inf")
    header_fields = None

    def decoded_lines() -> Iterable[str]:
        for raw in response.iter_lines(chunk_size=1024 * 1024, decode_unicode=False):
            if raw:
                yield raw.decode("ascii", errors="replace")

    reader = csv.reader(decoded_lines(), delimiter=",")
    for row in reader:
        if not row:
            continue
        if header_fields is None:
            header_fields = [x.strip() for x in row]
            continue
        all_rows += 1
        if len(row) < 15:
            continue
        values = dict(zip(header_fields, row))
        lat = parse_number(values, "tri_clat")
        lon = parse_number(values, "tri_clon")
        if lat is None or lon is None or lat > -80.0 or lat < -90.0:
            continue
        candidate_rows += 1
        east, north = local_aeqd_km(lat, lon)
        if abs(east) > half or abs(north) > half:
            continue
        selected_rows += 1
        min_x, max_x = min(min_x, east), max(max_x, east)
        min_y, max_y = min(min_y, north), max(max_y, north)

        avg = parse_number(values, "temp_avg")
        maximum = parse_number(values, "temp_max")
        depth = parse_number(values, "ice_depth")
        if avg is not None and avg > 0:
            temp_avg.append(avg)
        if maximum is not None and maximum > 0:
            temp_max.append(maximum)
        if depth is None or depth == INVALID_ICE_DEPTH:
            invalid_ice += 1
        else:
            ice_depth.append(depth)
            if abs(depth) < 1e-9:
                surface_stable += 1

        if all_rows % 500_000 == 0:
            print(
                f"Processed {all_rows:,}/{label['records']:,} records; "
                f"{selected_rows:,} AOI triangles selected",
                flush=True,
            )

    response.close()
    if all_rows != label["records"]:
        raise RuntimeError(f"Processed {all_rows:,} rows; PDS4 label declares {label['records']:,}")
    if not selected_rows or not temp_avg or not temp_max:
        raise RuntimeError("No usable Diviner records found in the Shackleton Rim AOI")

    valid_ice = len(ice_depth)
    return {
        "table_url": url,
        "table_content_length_bytes": int(actual_length) if actual_length and actual_length.isdigit() else expected_bytes,
        "declared_records": label["records"],
        "processed_records": all_rows,
        "south_polar_candidate_records": candidate_rows,
        "aoi_triangle_records": selected_rows,
        "aoi_extent_local_aeqd_km": {
            "east_min": min_x, "east_max": max_x, "north_min": min_y, "north_max": max_y,
            "nominal_side_km": AOI_SIDE_KM,
        },
        "temperature_average_at_2cm_K": summarize(
            temp_avg, "K", label["fields"]["temp_avg"]["description"]
        ),
        "temperature_average_at_2cm_C": summarize(
            [x - 273.15 for x in temp_avg], "°C",
            "Converted from the PDS temperature-average field in kelvin; not a surface temperature.",
        ),
        "annual_maximum_surface_temperature_K": summarize(
            temp_max, "K", label["fields"]["temp_max"]["description"]
        ),
        "annual_maximum_surface_temperature_C": summarize(
            [x - 273.15 for x in temp_max], "°C",
            "Converted from the PDS annual maximum surface temperature field in kelvin.",
        ),
        "ice_depth_model": {
            **summarize(
                ice_depth, "m", label["fields"]["ice_depth"]["description"]
            ),
            "valid_count": valid_ice,
            "invalid_censored_count": invalid_ice,
            "invalid_censored_fraction_of_aoi": invalid_ice / selected_rows if selected_rows else None,
            "surface_stable_count": surface_stable,
            "surface_stable_fraction_of_valid": surface_stable / valid_ice if valid_ice else None,
            "surface_stable_fraction_of_all_aoi_triangles": surface_stable / selected_rows if selected_rows else None,
            "invalid_constant": INVALID_ICE_DEPTH,
            "interpretation": (
                "A value of 0 means the thermal model indicates water ice would be stable "
                "against sublimation at the surface under the product's stated criterion "
                "(1 kg m-2 per billion years). It is not a direct ice detection, abundance, "
                "thickness, accessibility or resource-reserve measurement. Values reported "
                "as -999 are censored because the calculated depth exceeds 2.8738 m."
            ),
        },
        "processing_seconds": round(time.monotonic() - started, 1),
    }


def main() -> int:
    session = requests.Session()
    session.headers.update({"User-Agent": "ANALOG-X/1.2 (NASA PDS Diviner PRP AOI processor)"})
    label, _ = fetch_product_label(session)
    source_url, byte_count = select_source_table(session)
    stats = process_table(session, source_url, byte_count, label)
    result = {
        "schema_version": "1.0",
        "generated_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "provider": "NASA Lunar Reconnaissance Orbiter / Diviner Lunar Radiometer Experiment",
        "product": label,
        "aoi": {
            "name": "Shackleton Rim / R04 Site04 comparison window",
            "center_latitude_planetocentric_deg": CENTER_LAT_DEG,
            "center_longitude_positive_east_deg": CENTER_LON_EAST_DEG,
            "shape": "29.6 km × 29.6 km square",
            "projection_method": (
                "Each Diviner triangle centroid is converted to local east/north coordinates "
                "using a spherical azimuthal-equidistant calculation on the 1737.4 km lunar "
                "reference sphere; rows with |east| and |north| ≤ 14.8 km are selected."
            ),
            "geometry_note": (
                "This is an analyst-defined comparison window centered on the existing LOLA "
                "Shackleton R04 point, not a NASA-designated landing/base boundary."
            ),
        },
        "source_semantics": {
            "temp_avg": label["fields"]["temp_avg"],
            "temp_max": label["fields"]["temp_max"],
            "ice_depth": label["fields"]["ice_depth"],
            "product_context": (
                "PRP V2.0 is derived from thermal-model fits to Diviner observations from the "
                "first year of LRO mapping orbit; it is a model-based polar resource product."
            ),
        },
        "results": stats,
        "limitations": [
            "These are model-derived values from the Diviner PRP V2.0 product, not in-situ ice measurements.",
            "The product is based on first-year mapping-orbit observations and its thermal-model assumptions; it is not a live forecast.",
            "ice_depth -999 values mean the modeled depth exceeds 2.8738 m under the product criterion; they are censored, not zero.",
            "A surface-stable classification is not proof of exposed, accessible, concentrated or mineable ice.",
            "The AOI is a 29.6 km square comparison window, not a surveyed landing ellipse, habitat footprint or rover traverse plan.",
            "Illumination, long-duration power, communications, slope hazards, local geology, radiation and access are separate site-selection dimensions.",
        ],
        "citations": [
            {"title": "NASA PDS Diviner Polar Resource Product V2.0", "url": "https://ode.rsl.wustl.edu/MArs/pagehelp/Content/Missions_Instruments/Lunar%20Reconnaissance%20Orbiter%20%28LRO%29/DIVINER/PRP.htm"},
            {"title": "Paige et al. 2010, Diviner observations of the lunar regolith", "url": "https://doi.org/10.1126/science.1187726"},
            {"title": "NASA PDS4 Diviner derived bundle", "url": "https://pds.nasa.gov/data/pds4/releases/geo/lro_diviner_derived1-20260918/"},
        ],
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps({
        "output": str(OUTPUT),
        "aoi_triangle_records": stats["aoi_triangle_records"],
        "temperature_avg_K": stats["temperature_average_at_2cm_K"]["median"],
        "temperature_max_K": stats["annual_maximum_surface_temperature_K"]["median"],
        "ice_depth_m": stats["ice_depth_model"]["median"],
        "surface_stable_fraction_valid": stats["ice_depth_model"]["surface_stable_fraction_of_valid"],
    }, indent=2), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Build an auditable Shackleton Rim Diviner + LROC polar illumination evidence profile.

The script streams the 605 MB Diviner table and retains only rows in the project's
29.6 km x 29.6 km Shackleton study window. It never stores the full table.
"""
from __future__ import annotations

import json
import math
import statistics
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

import numpy as np
import requests
import rasterio
from PIL import Image
from pyproj import CRS, Transformer
from rasterio.windows import from_bounds

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "data" / "moon"
DIAG_DIR = OUT_DIR / "diviner_prp_diagnostic"
PROFILE_PATH = OUT_DIR / "shackleton_polar_evidence.json"
PREVIEW_PATH = OUT_DIR / "shackleton_wac_illumination_twi.png"

DIVINER_URL = (
    "https://pds-geosciences.wustl.edu/lro/urn-nasa-pds-lro_diviner_derived1/"
    "data_derived_prp/DLRE_PRP_SOUTH.TAB"
)
DIVINER_XML_URL = (
    "https://pds-geosciences.wustl.edu/lro/urn-nasa-pds-lro_diviner_derived1/"
    "data_derived_prp/DLRE_PRP_SOUTH.xml"
)
WAC_PRODUCTS = {
    "time_weighted": (
        "https://pds.lroc.im-ldi.com/data/LRO-L-LROC-5-RDR-V1.0/"
        "LROLRC_2001/EXTRAS/BROWSE/WAC_POLE/WAC_POLE_ILL_TWI_SOUTH/"
        "WAC_POLE_ILL_TWI_SOUTH_100M.TIF"
    ),
    "percentage_based": (
        "https://pds.lroc.im-ldi.com/data/LRO-L-LROC-5-RDR-V1.0/"
        "LROLRC_2001/EXTRAS/BROWSE/WAC_POLE/WAC_POLE_ILL_PCT_SOUTH/"
        "WAC_POLE_ILL_PCT_SOUTH_100M.TIF"
    ),
}
WAC_LABELS = {
    "time_weighted": WAC_PRODUCTS["time_weighted"].replace(".TIF", ".LBL"),
    "percentage_based": WAC_PRODUCTS["percentage_based"].replace(".TIF", ".LBL"),
}

# Existing project Shackleton Rim LRO LOLA study window.
CENTER_LAT_DEG = -89.7668
CENTER_LON_EAST_DEG = 188.13
WINDOW_KM = 29.6
HALF_WINDOW_KM = WINDOW_KM / 2.0
MOON_RADIUS_KM = 1737.4
EXPECTED_DIVINER_BYTES = 604_800_210
EXPECTED_DIVINER_ROWS = 2_880_000
DIVINER_RECORD_BYTES = 210
DIVINER_DATA_START_BYTE = 210

# PDS4 product label field positions are 1-based. iter_lines removes CRLF.
FIELDS = {
    "longitude_deg_east": (127, 15),
    "latitude_planetocentric_deg": (144, 15),
    "temp_avg_k": (178, 8),
    "temp_max_k": (188, 8),
    "ice_depth_m": (198, 11),
}
INVALID_ICE_DEPTH = -999.0
ICE_DEPTH_THRESHOLD_M = 2.8738

SESSION = requests.Session()
SESSION.headers.update({
    "User-Agent": "ANALOG-X/1.2 (open planetary data research; contact via GitHub repository)"
})


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def parse_float(raw: bytes) -> float | None:
    try:
        value = float(raw.decode("ascii").strip())
        return value if math.isfinite(value) else None
    except (ValueError, UnicodeDecodeError):
        return None


def field_value(row: bytes, name: str) -> float | None:
    start, length = FIELDS[name]
    return parse_float(row[start - 1:start - 1 + length])


def wrapped_lon_delta(lon_deg: float, lon0_deg: float) -> float:
    return (lon_deg - lon0_deg + 180.0) % 360.0 - 180.0


def local_offsets_km(lat_deg: float, lon_deg: float) -> tuple[float, float]:
    """Spherical azimuthal-equidistant offsets from the Shackleton AOI centre."""
    phi0 = math.radians(CENTER_LAT_DEG)
    phi = math.radians(lat_deg)
    dlon = math.radians(wrapped_lon_delta(lon_deg, CENTER_LON_EAST_DEG))
    cos_c = (
        math.sin(phi0) * math.sin(phi)
        + math.cos(phi0) * math.cos(phi) * math.cos(dlon)
    )
    c = math.acos(max(-1.0, min(1.0, cos_c)))
    sin_c = math.sin(c)
    k = c / sin_c if abs(sin_c) > 1e-12 else 1.0
    east = MOON_RADIUS_KM * k * math.cos(phi) * math.sin(dlon)
    north = MOON_RADIUS_KM * k * (
        math.cos(phi0) * math.sin(phi)
        - math.sin(phi0) * math.cos(phi) * math.cos(dlon)
    )
    return east, north


def distribution(values: Iterable[float]) -> dict:
    vals = [float(x) for x in values if math.isfinite(float(x))]
    if not vals:
        return {"count": 0}
    ordered = sorted(vals)

    def percentile(p: float) -> float:
        if len(ordered) == 1:
            return ordered[0]
        pos = (len(ordered) - 1) * p / 100.0
        lo, hi = math.floor(pos), math.ceil(pos)
        if lo == hi:
            return ordered[lo]
        return ordered[lo] * (hi - pos) + ordered[hi] * (pos - lo)

    return {
        "count": len(vals),
        "min": ordered[0],
        "p10": percentile(10),
        "median": statistics.median(ordered),
        "mean": statistics.fmean(ordered),
        "p90": percentile(90),
        "max": ordered[-1],
    }


def download_text(url: str) -> str:
    response = SESSION.get(url, timeout=(30, 120))
    response.raise_for_status()
    return response.text


def process_diviner() -> dict:
    """Stream the full south-polar PRP and summarize the project AOI."""
    response = SESSION.get(DIVINER_URL, stream=True, timeout=(45, 300))
    response.raise_for_status()
    content_length = int(response.headers.get("Content-Length", "0") or 0)
    if content_length and content_length != EXPECTED_DIVINER_BYTES:
        raise RuntimeError(
            f"Unexpected Diviner byte length: {content_length}; "
            f"expected {EXPECTED_DIVINER_BYTES}"
        )

    temp_avg: list[float] = []
    temp_max: list[float] = []
    ice_depth: list[float] = []
    ice_surface_stable = 0
    ice_modelled_depth = 0
    ice_beyond_model_limit = 0
    invalid_rows = 0
    rows_seen = 0
    selected_rows = 0
    min_east = min_north = float("inf")
    max_east = max_north = float("-inf")

    # iter_lines strips record delimiters; first 210-byte header is not a data row.
    for line in response.iter_lines(chunk_size=1024 * 1024, decode_unicode=False):
        if not line:
            continue
        if line.lstrip().startswith(b"tri1_x"):
            continue
        if len(line) < 208:
            invalid_rows += 1
            continue

        rows_seen += 1
        lon = field_value(line, "longitude_deg_east")
        lat = field_value(line, "latitude_planetocentric_deg")
        if lon is None or lat is None:
            invalid_rows += 1
            continue

        east, north = local_offsets_km(lat, lon)
        if abs(east) > HALF_WINDOW_KM or abs(north) > HALF_WINDOW_KM:
            continue

        selected_rows += 1
        min_east, max_east = min(min_east, east), max(max_east, east)
        min_north, max_north = min(min_north, north), max(max_north, north)

        t_avg = field_value(line, "temp_avg_k")
        t_max = field_value(line, "temp_max_k")
        depth = field_value(line, "ice_depth_m")
        if t_avg is not None and t_avg > 0:
            temp_avg.append(t_avg)
        if t_max is not None and t_max > 0:
            temp_max.append(t_max)
        if depth is None:
            continue
        if math.isclose(depth, INVALID_ICE_DEPTH, abs_tol=1e-6):
            # PDS label explains this as calculated depth > 2.8738 m.
            ice_beyond_model_limit += 1
        elif depth >= 0:
            ice_depth.append(depth)
            if math.isclose(depth, 0.0, abs_tol=1e-8):
                ice_surface_stable += 1
            else:
                ice_modelled_depth += 1

    response.close()

    if selected_rows < 20:
        raise RuntimeError(
            f"Only {selected_rows} Diviner triangles fell inside the Shackleton AOI; "
            "check the product coordinates, longitude convention and record offsets."
        )
    if rows_seen < EXPECTED_DIVINER_ROWS * 0.98:
        raise RuntimeError(
            f"Diviner stream was incomplete: {rows_seen:,} rows seen; "
            f"expected approximately {EXPECTED_DIVINER_ROWS:,}"
        )

    avg_k = distribution(temp_avg)
    max_k = distribution(temp_max)
    avg_c = {k: (v if k == "count" else v - 273.15) for k, v in avg_k.items()}
    max_c = {k: (v if k == "count" else v - 273.15) for k, v in max_k.items()}

    return {
        "status": "processed",
        "provider": "NASA LRO Diviner Polar Resource Product (PRP) V2.0",
        "dataset_id": "LRO-L-DLRE-5-PRP-V2.0",
        "doi": "10.17189/1520650",
        "product_doi": "10.17189/wj0s-w188",
        "product_file": "DLRE_PRP_SOUTH.TAB",
        "source_url": DIVINER_URL,
        "label_url": DIVINER_XML_URL,
        "model_observation_period": "First year of LRO mapping observations (2010–2011)",
        "release_date": "2018-03-15",
        "processing_level": "NASA Level 4 / CODMAC Level 5, model-derived",
        "aoi": {
            "name": "Shackleton Rim / ANALOG-X local lunar study window",
            "center_latitude_planetocentric_deg": CENTER_LAT_DEG,
            "center_longitude_east_deg": CENTER_LON_EAST_DEG,
            "shape": "29.6 km × 29.6 km local tangent-plane square",
            "selected_triangle_count": selected_rows,
            "selected_extent_east_km": [min_east, max_east],
            "selected_extent_north_km": [min_north, max_north],
        },
        "table_integrity": {
            "content_length_bytes": content_length or EXPECTED_DIVINER_BYTES,
            "expected_content_length_bytes": EXPECTED_DIVINER_BYTES,
            "expected_data_rows": EXPECTED_DIVINER_ROWS,
            "data_rows_seen": rows_seen,
            "invalid_rows": invalid_rows,
            "record_length_bytes_including_CRLF": DIVINER_RECORD_BYTES,
            "data_start_byte": DIVINER_DATA_START_BYTE,
            "coordinate_fields": "Planetocentric latitude; east longitude; degrees",
        },
        "annual_average_temperature_2cm_below_surface": {
            "unit": "K",
            "kelvin": avg_k,
            "celsius": avg_c,
            "interpretation": "Modelled annual average at 2 cm depth, not a real-time or current surface forecast.",
        },
        "annual_maximum_surface_temperature": {
            "unit": "K",
            "kelvin": max_k,
            "celsius": max_c,
            "interpretation": "Modelled annual maximum at the surface.",
        },
        "water_ice_permafrost_stability_depth": {
            "unit": "m",
            "valid_depth_distribution": distribution(ice_depth),
            "zero_depth_surface_stable_count": ice_surface_stable,
            "positive_depth_to_stability_count": ice_modelled_depth,
            "beyond_2_8738m_censored_count": ice_beyond_model_limit,
            "selected_triangle_count": selected_rows,
            "invalid_or_unreadable_count": selected_rows - len(ice_depth) - ice_beyond_model_limit,
            "meaning": (
                "Model-calculated depth at which water ice would sublimate at "
                "1 kg m−2 per billion years. A value of 0 m means the model "
                "indicates surface stability. The product reports -999 when "
                "the calculated depth exceeds 2.8738 m. This is not a direct "
                "detection, concentration, thickness, accessibility or reserve estimate."
            ),
        },
        "field_metadata": {
            "temp_avg": {"unit": "Kelvin", "start_byte": 178, "bytes": 8, "depth": "2 cm below surface"},
            "temp_max": {"unit": "Kelvin", "start_byte": 188, "bytes": 8, "depth": "surface"},
            "ice_depth": {
                "unit": "meter", "start_byte": 198, "bytes": 11,
                "invalid_constant": -999,
                "invalid_constant_semantics": "calculated depth exceeds 2.8738 m",
            },
        },
        "limitations": [
            "PRP values are model-derived from the first year of mapping observations, not a current operational weather or resource survey.",
            "The mesh uses Kaguya-derived triangular elevation elements, not the same spatial grid or vertical model as the project's LOLA DEM.",
            "The result does not establish ice concentration, mass, purity, mineability, accessibility, or resource reserves.",
            "Temperature/ice-depth statistics are thermal-resource context, not an official landing-site or habitat-safety assessment.",
        ],
    }


def parse_illumination_label(text: str) -> dict:
    out = {}
    import re
    for key in ("CORE_NULL", "CORE_VALID_MINIMUM", "CORE_VALID_MAXIMUM", "CORE_MULTIPLIER", "CORE_BASE"):
        m = re.search(r"(?im)^\s*" + key + r"\s*=\s*([^\r\n]+)", text)
        if m:
            out[key.lower()] = m.group(1).strip().strip('"')
    return out


def summarize_illumination(name: str, url: str, window_values: np.ma.MaskedArray, tags: dict, label_url: str) -> dict:
    values = np.asarray(window_values.filled(np.nan), dtype=float)
    mask = np.ma.getmaskarray(window_values) | ~np.isfinite(values)
    null_value = tags.get("nodata")
    if null_value is None:
        null_value = tags.get("core_null")
    if null_value is not None:
        try:
            mask |= np.isclose(values, float(null_value))
        except (TypeError, ValueError):
            pass
    values = values[~mask]
    # LROC defines the byte raster as an illumination percentage (0–100).
    # Values >100 are fill/reserved codes, not an alternate 0–255 percentage scale.
    values = values[(values >= 0) & (values <= 100)]
    if values.size == 0:
        raise RuntimeError(f"No valid illumination pixels in Shackleton window for {name}")

    pct = lambda threshold, op: float(np.mean(op(values, threshold)) * 100.0)
    return {
        "status": "processed",
        "product": name,
        "provider": "NASA LRO Camera (LROC) WAC",
        "resolution_m_per_pixel": 100,
        "source_url": url,
        "product_reference": label_url,
        "valid_pixel_count": int(values.size),
        "illumination_percent": {
            "min": float(np.min(values)),
            "p10": float(np.percentile(values, 10)),
            "median": float(np.median(values)),
            "mean": float(np.mean(values)),
            "p90": float(np.percentile(values, 90)),
            "max": float(np.max(values)),
            "pixels_below_1_percent_area_fraction": pct(1.0, np.less),
            "pixels_at_or_below_5_percent_area_fraction": pct(5.0, np.less_equal),
            "pixels_at_or_above_50_percent_area_fraction": pct(50.0, np.greater_equal),
            "pixels_at_or_above_70_percent_area_fraction": pct(70.0, np.greater_equal),
        },
        "aoi": {
            "center_latitude_deg": CENTER_LAT_DEG,
            "center_longitude_east_deg": CENTER_LON_EAST_DEG,
            "shape": "29.6 km × 29.6 km projected window",
        },
        "scale_interpretation": "Native product byte values interpreted as percentage (0–100); fill values above 100 excluded.",
        "limitations": [
            "WAC product is based on one lunar year of observations from 15 Feb 2010 to 5 Feb 2011, with supplementary observations/interpolation.",
            "It is a historical observational illumination-frequency product, not a current or future mission ephemeris simulation.",
            "Near-zero illumination values inside permanently shadowed terrain can be non-zero due to scattered-light and image-noise artefacts.",
            "The low-illumination fraction is a screening proxy, not a formal PSR polygon or regulatory landing-site determination.",
        ],
    }


def process_wac_product(name: str, url: str) -> tuple[dict, np.ndarray]:
    # The 100 m browse GeoTIFF carries the embedded map projection and nodata.
    product_reference = "https://data.lroc.im-ldi.com/lroc/view_rdr_product/" + (
        "WAC_POLE_ILL_TWI_SOUTH_100M" if name == "time_weighted" else "WAC_POLE_ILL_PCT_SOUTH_100M"
    )
    response = SESSION.get(url, stream=True, timeout=(30, 180))
    response.raise_for_status()
    temp_path = DIAG_DIR / f"{name}.tif"
    temp_path.parent.mkdir(parents=True, exist_ok=True)
    with temp_path.open("wb") as fh:
        for chunk in response.iter_content(chunk_size=1024 * 1024):
            if chunk:
                fh.write(chunk)
    response.close()

    with rasterio.open(temp_path) as ds:
        if ds.crs is None:
            raise RuntimeError(f"{name} WAC GeoTIFF has no CRS; refusing to guess projection.")
        # This raster uses a Moon-centred polar stereographic CRS. Do not
        # transform Earth WGS84 coordinates into a lunar CRS: PROJ correctly
        # rejects the Earth/Moon celestial-body mismatch. Re-express the known
        # planetocentric coordinate on the same spherical lunar datum instead.
        moon_radius_m = MOON_RADIUS_KM * 1000.0
        moon_geographic = CRS.from_proj4(
            f"+proj=longlat +a={moon_radius_m} +b={moon_radius_m} +no_defs +type=crs"
        )
        transformer = Transformer.from_crs(moon_geographic, ds.crs, always_xy=True)
        center_lon = CENTER_LON_EAST_DEG if CENTER_LON_EAST_DEG <= 180 else CENTER_LON_EAST_DEG - 360
        cx, cy = transformer.transform(center_lon, CENTER_LAT_DEG)
        print(
            f"{name} WAC CRS={ds.crs.to_string()} / {ds.crs.to_proj4()} bounds={ds.bounds} resolution={ds.res} center_px=({cx:.2f},{cy:.2f})",
            flush=True,
        )
        half_m = HALF_WINDOW_KM * 1000.0
        window = from_bounds(cx - half_m, cy - half_m, cx + half_m, cy + half_m, transform=ds.transform)
        data = ds.read(1, window=window, boundless=True, masked=True)
        tags = dict(ds.tags())
        summary = summarize_illumination(name, url, data, tags, product_reference)
        summary["raster"] = {
            "crs": str(ds.crs),
            "native_bounds": [float(x) for x in ds.bounds],
            "native_resolution": [float(x) for x in ds.res],
            "window_shape_rows_cols": [int(data.shape[0]), int(data.shape[1])],
            "window_center_projected_m": [float(cx), float(cy)],
            "nodata": ds.nodata,
        }
        preview = data.filled(np.nan).astype(float)
        return summary, preview


def main() -> None:
    DIAG_DIR.mkdir(parents=True, exist_ok=True)
    print("Streaming NASA Diviner south-polar resource product…", flush=True)
    diviner = process_diviner()
    print(
        "Diviner AOI triangles: "
        f"{diviner['aoi']['selected_triangle_count']:,}; "
        f"ice-depth classes: zero={diviner['water_ice_permafrost_stability_depth']['zero_depth_surface_stable_count']:,}, "
        f"positive={diviner['water_ice_permafrost_stability_depth']['positive_depth_to_stability_count']:,}, "
        f"beyond-limit={diviner['water_ice_permafrost_stability_depth']['beyond_2_8738m_censored_count']:,}",
        flush=True,
    )

    illumination = {}
    previews = {}
    for name, url in WAC_PRODUCTS.items():
        print(f"Processing LROC WAC {name} illumination raster…", flush=True)
        illumination[name], previews[name] = process_wac_product(name, url)
        print(
            f"{name}: median={illumination[name]['illumination_percent']['median']:.2f}% "
            f"mean={illumination[name]['illumination_percent']['mean']:.2f}%",
            flush=True,
        )

    make_preview(previews["time_weighted"])
    result = {
        "schema_version": "1.0",
        "generated_at_utc": utc_now(),
        "site": {
            "name": "Shackleton Rim / Lunar South Pole",
            "center_latitude_planetocentric_deg": CENTER_LAT_DEG,
            "center_longitude_east_deg": CENTER_LON_EAST_DEG,
            "study_window_km": WINDOW_KM,
        },
        "diviner_polar_resource_product": diviner,
        "lroc_wac_illumination": illumination,
        "low_illumination_proxy_definition": {
            "threshold": "<=5% observed illumination frequency",
            "warning": "This is not a formal PSR polygon. Official PSR maps and current ephemeris modelling must be consulted for mission engineering.",
        },
        "integrated_products": [
            "LOLA 80 m south-polar elevation / return-count profile (already in project)",
            "Diviner PRP V2.0 annual average and maximum temperature / modelled water-ice stability depth",
            "LROC WAC 100 m time-weighted south-pole illumination percentage",
            "LROC WAC 100 m unweighted south-pole illumination percentage for sensitivity comparison",
        ],
        "scientific_boundary": [
            "These are historical data products with different epochs and resolutions.",
            "Diviner PRP is a thermal-model product based on the first year of mapping observations.",
            "WAC illumination percentages are based on 2010–2011 imaging; they are not a 2026–2030 ephemeris forecast.",
            "The local terrain support window is 29.6 km square; it does not validate a specific lander footprint.",
            "Ice stability depth does not equal a direct measurement of ice abundance, concentration, thickness or extractability.",
            "LOLA DEM interpolation and measurement count support remain separate quality dimensions.",
        ],
    }
    PROFILE_PATH.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "profile": str(PROFILE_PATH.relative_to(ROOT)),
        "preview": str(PREVIEW_PATH.relative_to(ROOT)),
        "diviner_triangles": diviner["aoi"]["selected_triangle_count"],
        "wac_time_weighted_median_percent": illumination["time_weighted"]["illumination_percent"]["median"],
        "wac_unweighted_median_percent": illumination["percentage_based"]["illumination_percent"]["median"],
    }, indent=2), flush=True)


if __name__ == "__main__":
    main()

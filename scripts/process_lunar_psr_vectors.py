#!/usr/bin/env python3
"""Download NASA PGDA LOLA south-polar PSR vectors and test the Shackleton AOI.

Only a compact, reproducible summary is committed. Raw shapefile sidecars are
downloaded to a temporary directory on the CI runner and are not added to Git.
"""
from __future__ import annotations

import hashlib
import json
import math
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests
import shapefile
from pyproj import CRS, Transformer
from requests.adapters import HTTPAdapter
from shapely.geometry import Point, box, mapping, shape
from shapely.ops import transform as transform_geometry
from urllib3.util.retry import Retry

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "data" / "moon" / "lola_psr_site_overlap.json"
BASE_URL = "https://pgda.gsfc.nasa.gov/data/LOLA_20mpp/LPSR_80S_20MPP_ADJ_1km2"
SIDECARS = (".SHP", ".SHX", ".DBF", ".PRJ")
MAX_BYTES = {".SHP": 30_000_000, ".SHX": 1_000_000, ".DBF": 2_000_000, ".PRJ": 20_000}
SITE = {
    "name": "Shackleton Rim / Lunar South Pole",
    "latitude_planetocentric_deg": -89.7668,
    "longitude_east_deg": 188.13,
    "study_window_km": 29.6,
}
LUNAR_RADIUS_M = 1_737_400.0
AREA_THRESHOLD_KM2 = 1.0
NEARBY_REPORT_RADIUS_KM = 50.0

SESSION = requests.Session()
SESSION.headers.update({
    "User-Agent": "ANALOG-X/1.2 (NASA PGDA lunar PSR vector processing; research prototype)",
    "Accept": "*/*",
})
RETRY = Retry(
    total=4,
    connect=4,
    read=4,
    backoff_factor=1,
    status_forcelist=(429, 500, 502, 503, 504),
    allowed_methods=frozenset(["GET"]),
    respect_retry_after_header=True,
)
SESSION.mount("https://", HTTPAdapter(max_retries=RETRY))


def download_sidecar(extension: str, destination: Path) -> dict[str, Any]:
    """Stream and checksum one bounded-size PGDA shapefile component."""
    extension = extension.upper()
    if extension not in SIDECARS:
        raise ValueError(f"Unsupported shapefile sidecar: {extension}")
    url = BASE_URL + extension
    response = SESSION.get(url, stream=True, timeout=(20, 120))
    response.raise_for_status()
    digest = hashlib.sha256()
    total = 0
    try:
        with destination.open("wb") as output:
            for chunk in response.iter_content(chunk_size=1024 * 1024):
                if not chunk:
                    continue
                total += len(chunk)
                if total > MAX_BYTES[extension]:
                    raise ValueError(f"{extension} download exceeded size guard")
                digest.update(chunk)
                output.write(chunk)
    finally:
        response.close()
    if total < 20:
        raise ValueError(f"{extension} download is unexpectedly small ({total} bytes)")
    if extension == ".PRJ" and total > MAX_BYTES[".PRJ"]:
        raise ValueError("Projection file exceeded size guard")
    return {
        "file": "LPSR_80S_20MPP_ADJ_1km2" + extension,
        "url": url,
        "bytes": total,
        "sha256": digest.hexdigest(),
    }


def make_lunar_geographic_crs() -> CRS:
    """Planetocentric lon/lat on the lunar reference sphere used by PGDA."""
    return CRS.from_proj4(
        f"+proj=longlat +R={LUNAR_RADIUS_M:.1f} +no_defs +type=crs"
    )


def parse_projection(prj_path: Path) -> CRS:
    text = prj_path.read_text(encoding="utf-8").strip()
    if not text:
        raise ValueError("PGDA PRJ file is empty")
    crs = CRS.from_wkt(text)
    if not crs.is_projected:
        raise ValueError("PGDA PSR shapefile CRS is not projected")
    projection_name = (crs.coordinate_operation.method_name or "").lower()
    if "stereographic" not in projection_name:
        raise ValueError(f"Unexpected PSR projection: {crs.coordinate_operation.method_name}")
    radius = crs.ellipsoid.semi_major_metre
    if not math.isclose(radius, LUNAR_RADIUS_M, rel_tol=0, abs_tol=1.0):
        raise ValueError(f"Unexpected lunar reference radius in PRJ: {radius}")
    return crs


def build_study_aoi(target_crs: CRS):
    """Project the site centre and construct its declared 29.6 km square."""
    source_crs = make_lunar_geographic_crs()
    forward = Transformer.from_crs(source_crs, target_crs, always_xy=True)
    inverse = Transformer.from_crs(target_crs, source_crs, always_xy=True)
    center_x, center_y = forward.transform(
        SITE["longitude_east_deg"], SITE["latitude_planetocentric_deg"]
    )
    if not all(math.isfinite(v) for v in (center_x, center_y)):
        raise ValueError("Projected Shackleton centre is not finite")
    half_width_m = SITE["study_window_km"] * 500.0
    aoi = box(
        center_x - half_width_m,
        center_y - half_width_m,
        center_x + half_width_m,
        center_y + half_width_m,
    )
    return aoi, (center_x, center_y), forward, inverse


def _first_attr(record: dict[str, Any], *names: str):
    by_lower = {str(k).lower(): v for k, v in record.items()}
    for name in names:
        if name.lower() in by_lower:
            return by_lower[name.lower()]
    return None


def _number(value):
    if value in (None, ""):
        return None
    try:
        result = float(value)
        return result if math.isfinite(result) else None
    except (TypeError, ValueError):
        return None


def _relative_geometry_coordinates(geometry, center_x: float, center_y: float):
    """Return clipped geometry as kilometres relative to the site centre."""
    def shift(x, y, z=None):
        xx = (x - center_x) / 1000.0
        yy = (y - center_y) / 1000.0
        return (xx, yy) if z is None else (xx, yy, z)
    shifted = transform_geometry(shift, geometry)
    return mapping(shifted)


def analyze_psr_features(
    features: list[tuple[dict[str, Any], Any]],
    aoi,
    site_center: tuple[float, float],
    inverse_transformer: Transformer,
    *,
    nearby_radius_km: float = NEARBY_REPORT_RADIUS_KM,
) -> dict[str, Any]:
    """Calculate exact projected-plane bbox/polygon intersections and distances."""
    center_point = Point(*site_center)
    rows = []
    invalid_count = 0
    repaired_count = 0

    for index, (attributes, geometry) in enumerate(features):
        if geometry is None or geometry.is_empty:
            invalid_count += 1
            continue
        original_valid = geometry.is_valid
        if not original_valid:
            geometry = geometry.buffer(0)
            repaired_count += 1
        if geometry.is_empty:
            invalid_count += 1
            continue

        distance_m = float(geometry.distance(aoi))
        distance_to_center_m = float(geometry.distance(center_point))
        intersects = bool(geometry.intersects(aoi))
        clipped = geometry.intersection(aoi) if intersects else None
        overlap_area_km2 = (
            float(clipped.area) / 1_000_000.0
            if clipped is not None and not clipped.is_empty
            else 0.0
        )
        centroid = geometry.centroid
        centroid_lon, centroid_lat = inverse_transformer.transform(centroid.x, centroid.y)

        psr_id = _first_attr(attributes, "PSR_ID", "ID", "OBJECTID", "FID")
        if psr_id is None:
            psr_id = f"feature-{index + 1}"
        area_km2 = _number(_first_attr(attributes, "AREA", "AREA_KM2", "AREA_SQKM"))
        if area_km2 is None:
            area_km2 = float(geometry.area) / 1_000_000.0

        row = {
            "psr_id": str(psr_id),
            "area_km2": round(area_km2, 4),
            "geometry_area_km2": round(float(geometry.area) / 1_000_000.0, 4),
            "centroid_latitude_planetocentric_deg": round(float(centroid_lat), 6),
            "centroid_longitude_east_deg": round(float(centroid_lon) % 360.0, 6),
            "distance_from_aoi_boundary_km": round(distance_m / 1000.0, 6),
            "distance_from_site_center_km": round(distance_to_center_m / 1000.0, 6),
            "intersects_study_window": intersects,
            "overlap_area_km2": round(overlap_area_km2, 6),
            "geometry_repaired_for_analysis": not original_valid,
        }
        if intersects and clipped is not None and not clipped.is_empty:
            row["clipped_geometry_site_relative_km"] = _relative_geometry_coordinates(
                clipped, site_center[0], site_center[1]
            )
        if distance_m <= nearby_radius_km * 1000.0:
            rows.append(row)

    rows.sort(
        key=lambda row: (
            not row["intersects_study_window"],
            row["distance_from_aoi_boundary_km"],
            row["psr_id"],
        )
    )
    intersecting = [row for row in rows if row["intersects_study_window"]]
    return {
        "feature_count_in_source": len(features),
        "invalid_or_empty_geometry_count": invalid_count,
        "geometry_repair_count": repaired_count,
        "intersecting_polygon_count_within_source": sum(
            1 for _, geometry in features
            if geometry is not None and not geometry.is_empty
            and geometry.intersects(aoi)
        ),
        "positive_area_overlap_count_within_source": sum(
            1 for row in intersecting if row["overlap_area_km2"] > 0
        ),
        "overlap_area_total_km2": round(
            sum(row["overlap_area_km2"] for row in intersecting), 6
        ),
        "intersecting_psrs": intersecting,
        "nearest_psrs_within_radius": rows[:20],
        "nearest_boundary_distance_km": (
            rows[0]["distance_from_aoi_boundary_km"] if rows else None
        ),
        "nearby_radius_km": nearby_radius_km,
    }


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="analogx-lola-psr-") as temporary:
        directory = Path(temporary)
        downloads = [
            download_sidecar(extension, directory / ("psr" + extension))
            for extension in SIDECARS
        ]
        target_crs = parse_projection(directory / "psr.PRJ")
        aoi, center, _, inverse = build_study_aoi(target_crs)

        reader = shapefile.Reader(
            shp=str(directory / "psr.SHP"),
            shx=str(directory / "psr.SHX"),
            dbf=str(directory / "psr.DBF"),
            encoding="latin1",
        )
        fields = [item[0] for item in reader.fields[1:]]
        features = []
        for shape_record in reader.iterShapeRecords():
            record = shape_record.record.as_dict()
            geom = shape(shape_record.shape.__geo_interface__)
            features.append((record, geom))
        reader.close()

        analysis = analyze_psr_features(features, aoi, center, inverse)
        center_lon_back, center_lat_back = inverse.transform(*center)
        output = {
            "schema_version": "1.0.0",
            "generated_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
            "status": (
                "mapped_psr_intersects_study_window"
                if analysis["intersecting_polygon_count_within_source"]
                else "no_source_psr_intersects_study_window"
            ),
            "site": SITE,
            "study_window": {
                "shape": "29.6 km × 29.6 km square",
                "center_projected_m": [round(center[0], 3), round(center[1], 3)],
                "bounds_projected_m": [round(v, 3) for v in aoi.bounds],
                "center_round_trip_latitude_deg": round(center_lat_back, 8),
                "center_round_trip_longitude_east_deg": round(center_lon_back % 360.0, 8),
                "area_km2": round(aoi.area / 1_000_000.0, 6),
            },
            "source": {
                "provider": "NASA GSFC Planetary Geodesy Data Archive / LOLA",
                "product": "LPSR_80S_20MPP_ADJ_1km2",
                "url": "https://pgda.gsfc.nasa.gov/products/90",
                "data_doi": "https://doi.org/10.60903/gsfcpgda-lola-spole",
                "paper_doi": "https://doi.org/10.3847/PSJ/acf3e1",
                "catalogue_area_threshold_km2": AREA_THRESHOLD_KM2,
                "catalogue_population_reported": 1531,
                "coverage": "80°S to 90°S; south-polar LOLA-derived PSR polygons larger than 1 km²",
                "native_grid_spacing_m": 20,
                "limitation": "20 m is the source grid spacing, not a guarantee of 20 m boundary accuracy.",
                "sidecars": downloads,
                "attribute_fields": fields,
                "crs_wkt": target_crs.to_wkt(),
                "crs_name": target_crs.name,
                "semi_major_radius_m": target_crs.ellipsoid.semi_major_metre,
            },
            "method": {
                "intersection": "Shapely polygon intersection in the exact south-polar stereographic CRS declared by the downloaded PGDA PRJ file.",
                "aoi": "Square centred on the stated planetocentric Shackleton coordinate, projected from a lunar spherical lon/lat CRS and sized to the existing 29.6 km study window.",
                "distance": "Minimum planar geometry-to-AOI distance in the shapefile's projected metre coordinates.",
                "geometry_output": "Only clipped portions of PSRs intersecting the AOI are retained, expressed in kilometres relative to the site centre.",
            },
            "analysis": analysis,
            "interpretation": [
                "A mapped LOLA PSR polygon is evidence of a modeled permanently shadowed terrain region at the source product's support; it is not an ice detection.",
                "The 1 km² product omits smaller mapped PSRs and covers only 80°S to the pole.",
                "Intersection does not establish current mission-date illumination, ice abundance, accessibility, thickness, purity or reserves.",
                "A bounding-box or polygon intersection does not establish rover trafficability, landing safety or operational suitability.",
                "Historical Diviner and WAC products remain separate measurements with separate dates and methods.",
            ],
        }

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(output, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps({
        "output": str(OUTPUT.relative_to(ROOT)),
        "status": output["status"],
        "source_features": analysis["feature_count_in_source"],
        "intersecting_polygons": analysis["intersecting_polygon_count_within_source"],
        "positive_area_intersections": analysis["positive_area_overlap_count_within_source"],
        "overlap_area_km2": analysis["overlap_area_total_km2"],
        "nearest_boundary_km": analysis["nearest_boundary_distance_km"],
        "sidecars": [{k:v for k,v in row.items() if k!="url"} for row in downloads],
    }, indent=2))


if __name__ == "__main__":
    main()

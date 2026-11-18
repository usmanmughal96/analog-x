#!/usr/bin/env python3
"""Global, tile-inventory-driven candidate scan using public Copernicus DEM GLO-90.

This computes 5.55 km terrain windows globally from 90 m DSM COGs by reading
each 1x1-degree land tile and resampling it into a local metric CRS at ~925 m.
It is a terrain-only screening system. It cannot establish geology, mineralogy,
trafficability, resource access, landing safety, or full planetary analogy.
"""
from __future__ import annotations

import argparse
import json
import math
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import requests
import rasterio
from rasterio.enums import Resampling
from rasterio.transform import from_origin
from rasterio.warp import calculate_default_transform, reproject, transform_bounds, transform as transform_xy
from scipy.ndimage import maximum_filter, minimum_filter

ROOT = Path(__file__).resolve().parents[1]
TILE_LIST_URL = "https://copernicus-dem-90m.s3.amazonaws.com/tileList.txt"
TILE_BASE = "https://copernicus-dem-90m.s3.eu-central-1.amazonaws.com"
TILE_PATTERN = re.compile(r"Copernicus_DSM_COG_30_([NS])(\d{2})_00_([EW])(\d{3})_00_DEM")
WINDOW = 6
CELL_M = 925.0
MIN_VALID = math.ceil(WINDOW * WINDOW * 0.70)
MIN_DERIVATIVES = 15
SHARDS = 24
TOP_PER_SHARD = 2500
RANDOM_SEED = 20261118
OUT = ROOT / "data/global_discovery/shards"

SESSION = requests.Session()
SESSION.headers.update({"User-Agent": "ANALOG-X/1.0 global terrain discovery; public Copernicus DEM"})
TILELIST_CACHE = ROOT / "data/raw/global_discovery/tileList.txt"


def utcnow() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def parse_tile_id(raw: str) -> dict[str, Any] | None:
    match = TILE_PATTERN.search(raw)
    if not match:
        return None
    lat = int(match.group(2)) * (1 if match.group(1) == "N" else -1)
    lon = int(match.group(4)) * (1 if match.group(3) == "E" else -1)
    if lat < -90 or lat > 89 or lon < -180 or lon > 179:
        return None
    tile_id = match.group(0)
    return {"tile_id": tile_id, "south": lat, "west": lon, "north": lat + 1, "east": lon + 1}


def tile_inventory(refresh: bool = False) -> list[dict[str, Any]]:
    if refresh or not TILELIST_CACHE.exists():
        TILELIST_CACHE.parent.mkdir(parents=True, exist_ok=True)
        response = SESSION.get(TILE_LIST_URL, timeout=(30, 120))
        response.raise_for_status()
        TILELIST_CACHE.write_bytes(response.content)
    text = TILELIST_CACHE.read_text(encoding="utf-8", errors="replace")
    tiles: dict[str, dict[str, Any]] = {}
    for line in text.splitlines():
        tile = parse_tile_id(line)
        if tile:
            tiles[tile["tile_id"]] = tile
    if not tiles:
        raise RuntimeError("No Copernicus GLO-90 tile identifiers parsed from tileList.txt")
    return sorted(tiles.values(), key=lambda item: (item["west"], item["south"], item["tile_id"]))


def partition_for_lon(lon: int, shard_count: int = SHARDS) -> int:
    return min(shard_count - 1, max(0, int((lon + 180) // (360 / shard_count))))


def local_metric_crs(lat: float, lon: float) -> str:
    if lat >= 84:
        return "EPSG:3413"
    if lat <= -80:
        return "EPSG:3031"
    zone = max(1, min(60, int((lon + 180) // 6) + 1))
    return f"EPSG:{32600 + zone if lat >= 0 else 32700 + zone}"


def tile_asset_url(tile_id: str) -> str:
    return f"{TILE_BASE}/{tile_id}/{tile_id}.tif"


def read_metric_tile(tile: dict[str, Any], asset_url: str) -> tuple[np.ndarray, tuple[float, float, float, float], str]:
    lat = (tile["south"] + tile["north"]) / 2
    lon = (tile["west"] + tile["east"]) / 2
    dst_crs = local_metric_crs(lat, lon)
    bounds = transform_bounds("EPSG:4326", dst_crs, tile["west"], tile["south"], tile["east"], tile["north"], densify_pts=21)
    left, bottom, right, top = bounds
    width = max(1, int(math.ceil((right - left) / CELL_M)))
    height = max(1, int(math.ceil((top - bottom) / CELL_M)))
    destination = np.full((height, width), np.nan, dtype=np.float32)
    transform_dst = from_origin(left, top, CELL_M, CELL_M)
    with rasterio.Env(
        GDAL_DISABLE_READDIR_ON_OPEN="EMPTY_DIR",
        CPL_VSIL_CURL_ALLOWED_EXTENSIONS=".tif,.TIF",
        GDAL_HTTP_MAX_RETRY="4",
        GDAL_HTTP_RETRY_DELAY="2",
        GDAL_HTTP_TIMEOUT="90",
        GDAL_CACHEMAX=128,
    ):
        with rasterio.open("/vsicurl/" + asset_url) as source:
            if source.crs is None:
                raise RuntimeError("Global DEM COG has no CRS")
            reproject(
                source=rasterio.band(source, 1),
                destination=destination,
                src_transform=source.transform,
                src_crs=source.crs,
                src_nodata=source.nodata,
                dst_transform=transform_dst,
                dst_crs=dst_crs,
                dst_nodata=np.nan,
                resampling=Resampling.average,
                num_threads=2,
            )
    return destination, (left, bottom, right, top), dst_crs


def percentile(values: np.ndarray, q: float) -> float:
    return float(np.nanpercentile(values, q))


def derive_metric_arrays(z: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    valid = np.isfinite(z)
    slope = np.full(z.shape, np.nan, dtype=np.float32)
    if z.shape[0] >= 3 and z.shape[1] >= 3:
        gx = (z[1:-1, 2:] - z[1:-1, :-2]) / (2 * CELL_M)
        gy = (z[2:, 1:-1] - z[:-2, 1:-1]) / (2 * CELL_M)
        neighbour_ok = (
            valid[1:-1, 2:] & valid[1:-1, :-2] &
            valid[2:, 1:-1] & valid[:-2, 1:-1]
        )
        core = np.degrees(np.arctan(np.hypot(gx, gy)))
        core[~neighbour_ok] = np.nan
        slope[1:-1, 1:-1] = core
    valid3 = minimum_filter(valid.astype(np.uint8), size=3, mode="constant", cval=0) == 1
    high = maximum_filter(np.where(valid, z, -np.inf), size=3, mode="constant", cval=-np.inf)
    low = minimum_filter(np.where(valid, z, np.inf), size=3, mode="constant", cval=np.inf)
    relief = (high - low).astype(np.float32)
    relief[~valid3] = np.nan
    return slope, relief


def window_metrics(z: np.ndarray, slope: np.ndarray, relief: np.ndarray, r: int, c: int) -> dict[str, float] | None:
    patch = z[r:r + WINDOW, c:c + WINDOW]
    slope_patch = slope[r:r + WINDOW, c:c + WINDOW]
    relief_patch = relief[r:r + WINDOW, c:c + WINDOW]
    valid_cells = np.isfinite(patch).sum()
    slopes = slope_patch[np.isfinite(slope_patch)]
    reliefs = relief_patch[np.isfinite(relief_patch)]
    if valid_cells < MIN_VALID or len(slopes) < MIN_DERIVATIVES or len(reliefs) < MIN_DERIVATIVES:
        return None
    vals = patch[np.isfinite(patch)].astype(float)
    # Detrend the window with a least-squares plane; this is a separate
    # roughness diagnostic and is not included in the legacy three-feature index.
    yy, xx = np.mgrid[0:WINDOW, 0:WINDOW]
    mask = np.isfinite(patch)
    design = np.column_stack([np.ones(mask.sum()), xx[mask], yy[mask]])
    coeff, *_ = np.linalg.lstsq(design, patch[mask].astype(float), rcond=None)
    residual = patch[mask].astype(float) - design @ coeff
    return {
        "median_slope_deg": percentile(slopes, 50),
        "p90_slope_deg": percentile(slopes, 90),
        "p95_slope_deg": percentile(slopes, 95),
        "p90_local_relief_m": percentile(reliefs, 90),
        "elevation_iqr_m": percentile(vals, 75) - percentile(vals, 25),
        "detrended_roughness_rms_m": float(np.sqrt(np.mean(residual ** 2))),
        "slope_under_5_deg_pct": 100.0 * float(np.mean(slopes < 5)),
        "slope_over_20_deg_pct": 100.0 * float(np.mean(slopes > 20)),
        "valid_cell_pct": 100.0 * float(valid_cells) / (WINDOW * WINDOW),
    }


def grid_windows(surface: dict[str, Any], stride: int = 1) -> list[dict[str, float]]:
    grid = surface.get("values")
    if not isinstance(grid, list) or not grid:
        return []
    z = np.array([[np.nan if v is None else float(v) for v in row] for row in grid], dtype=np.float32)
    slope, relief = derive_metric_arrays(z)
    results = []
    for r in range(0, z.shape[0] - WINDOW + 1, stride):
        for c in range(0, z.shape[1] - WINDOW + 1, stride):
            m = window_metrics(z, slope, relief, r, c)
            if m:
                results.append(m)
    return results


def iqr(values: list[float]) -> float:
    return float(np.percentile(values, 75) - np.percentile(values, 25))


def build_reference_profiles() -> dict[str, Any]:
    terrain = json.loads((ROOT / "data/terrain/terrain_comparison.json").read_text(encoding="utf-8"))
    moon = json.loads((ROOT / "data/moon/shackleton_lola_80m.json").read_text(encoding="utf-8"))
    earth = []
    for site_id, site in terrain.get("earth_sites", {}).items():
        profile = site.get("surface_grid_relative_m")
        if profile:
            earth.extend(grid_windows(profile, stride=1))
    mars_profile = terrain["planetary_target"]["surface_grid_relative_m"]
    moon_profile = moon["surface_grid_relative_m"]
    mars = grid_windows(mars_profile, stride=1)
    lunar = grid_windows(moon_profile, stride=1)
    feature_a = ["median_slope_deg", "p90_slope_deg", "p90_local_relief_m"]
    feature_b = ["p95_slope_deg", "elevation_iqr_m", "detrended_roughness_rms_m"]
    iqr_a = {key: max(1e-6, iqr([v[key] for v in earth])) for key in feature_a}
    iqr_b = {key: max(1e-6, iqr([v[key] for v in earth])) for key in feature_b}
    def median_profile(rows: list[dict[str, float]]) -> dict[str, float]:
        if not rows:
            raise RuntimeError("Planetary reference profile has no valid 5.55 km windows")
        return {key: float(np.median([row[key] for row in rows])) for key in feature_a + feature_b}
    feature_families = {
        "core": feature_a,
        "secondary": feature_b,
        "secondary_note": "Alternative diagnostic feature family from the same DEM grids; it tests metric-family robustness, not independent-source accuracy."
    }
    return {
        "moon": {"name": "Shackleton Rim / lunar south pole", "profile": median_profile(lunar), "valid_reference_windows": len(lunar), "feature_families": feature_families},
        "mars": {"name": "Nili Patera / Mars", "profile": median_profile(mars), "valid_reference_windows": len(mars), "feature_families": feature_families},
        "earth_iqr": {**iqr_a, **iqr_b},
        "earth_reference_windows": len(earth),
        "feature_families": feature_families
    }


def score_candidate(metrics: dict[str, float], reference: dict[str, Any], scales: dict[str, float]) -> tuple[float, float, float]:
    profiles = reference["profile"]
    core_keys = reference["feature_families"]["core"]
    secondary_keys = reference["feature_families"]["secondary"]
    d_core = np.mean([abs(metrics[k] - profiles[k]) / scales[k] for k in core_keys])
    d_secondary = np.mean([abs(metrics[k] - profiles[k]) / scales[k] for k in secondary_keys])
    core = 100 * math.exp(-float(d_core))
    secondary = 100 * math.exp(-float(d_secondary))
    consensus = (core + secondary) / 2
    return round(core, 4), round(secondary, 4), round(consensus, 4)


def tile_candidate_windows(tile: dict[str, Any], shard: int, refs: dict[str, Any]) -> tuple[dict[str, list[dict[str, Any]]], dict[str, Any]]:
    url = tile_asset_url(tile["tile_id"])
    z, bounds, crs = read_metric_tile(tile, url)
    slope, relief = derive_metric_arrays(z)
    candidates = {"moon": [], "mars": []}
    windows_evaluated = 0
    lat_c = (tile["south"] + tile["north"]) / 2
    lon_c = (tile["west"] + tile["east"]) / 2
    for r in range(0, z.shape[0] - WINDOW + 1, WINDOW):
        for c in range(0, z.shape[1] - WINDOW + 1, WINDOW):
            metrics = window_metrics(z, slope, relief, r, c)
            if not metrics:
                continue
            windows_evaluated += 1
            x = bounds[0] + (c + WINDOW / 2) * CELL_M
            y = bounds[3] - (r + WINDOW / 2) * CELL_M
            lon, lat = transform_xy(crs, "EPSG:4326", [x], [y])
            lat0, lon0 = float(lat[0]), float(lon[0])
            if not (-90 <= lat0 <= 90 and -180 <= lon0 <= 180):
                continue
            for target in ("moon", "mars"):
                core, secondary, consensus = score_candidate(metrics, refs[target], refs["earth_iqr"])
                candidates[target].append({
                    "id": f"{tile['tile_id']}_r{r}_c{c}",
                    "tile_id": tile["tile_id"],
                    "latitude": round(lat0, 5),
                    "longitude": round(lon0, 5),
                    "window_footprint_km": round(WINDOW * CELL_M / 1000, 3),
                    "analysis_support_m": CELL_M,
                    "crs": crs,
                    "core_terrain_index": core,
                    "secondary_diagnostic_index": secondary,
                    "consensus_index": consensus,
                    "terrain": metrics,
                    "metric_family_score_agreement": round(100 * (1 - abs(core - secondary) / 100), 2),
                    "source": {
                        "provider": "Copernicus DEM GLO-90",
                        "collection": "COP-DEM_GLO-90-DGED",
                        "asset_url": url,
                        "asset_status": "processed_on_demand",
                        "resolution_native_m_approx": 90,
                        "product_type": "DSM",
                    },
                    "interpretation": "Global terrain-screening lead only; not a geological analog, field validation, resource assessment, rover-safety or landing-suitability result."
                })
    summary = {
        "tile_id": tile["tile_id"], "south": tile["south"], "west": tile["west"],
        "width_cells": int(z.shape[1]), "height_cells": int(z.shape[0]),
        "valid_cell_pct": round(100 * float(np.isfinite(z).mean()), 3),
        "windows_evaluated": windows_evaluated, "crs": crs,
    }
    return candidates, summary


def select_diverse(rows: list[dict[str, Any]], limit: int, max_per_tile: int = 4) -> list[dict[str, Any]]:
    rows = sorted(rows, key=lambda x: (-x["consensus_index"], -x["metric_family_score_agreement"], x["id"]))
    out, counts = [], {}
    for item in rows:
        tile_id = item["tile_id"]
        if counts.get(tile_id, 0) >= max_per_tile:
            continue
        counts[tile_id] = counts.get(tile_id, 0) + 1
        out.append(item)
        if len(out) >= limit:
            break
    for i, item in enumerate(out, 1):
        item["global_sample_rank"] = i
    return out


def run(args: argparse.Namespace) -> None:
    tiles = tile_inventory(refresh=args.refresh_tile_list)
    selected = [tile for tile in tiles if partition_for_lon(tile["west"], args.shards) == args.shard]
    if args.max_tiles:
        selected = selected[:args.max_tiles]
    refs = build_reference_profiles()
    result_rows = {"moon": [], "mars": []}
    processed, failures, empty, windows = 0, [], 0, 0
    started = time.time()
    for index, tile in enumerate(selected, 1):
        try:
            candidates, summary = tile_candidate_windows(tile, args.shard, refs)
            processed += 1
            windows += summary["windows_evaluated"]
            if summary["windows_evaluated"] == 0:
                empty += 1
            for target in ("moon", "mars"):
                result_rows[target].extend(candidates[target])
            if index % 25 == 0:
                print(f"shard {args.shard:02d}: {index}/{len(selected)} tiles; {processed} processed; {windows:,} windows; elapsed {int(time.time()-started)}s", flush=True)
        except Exception as exc:
            failures.append({"tile_id": tile["tile_id"], "error": str(exc)[:500]})
            if len(failures) % 25 == 0:
                print(f"shard {args.shard:02d}: {len(failures)} tile failures", file=sys.stderr, flush=True)
    OUT.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema_version": "1.0.0",
        "project": "ANALOG-X Global Discovery",
        "generated_at_utc": utcnow(),
        "shard": args.shard, "shard_count": args.shards,
        "scope": "All inventoried Copernicus GLO-90 one-degree land tiles assigned to this longitude shard, unless --max-tiles is used.",
        "tile_inventory_url": TILE_LIST_URL,
        "tile_inventory_total": len(tiles),
        "tiles_assigned": len(selected),
        "tiles_processed": processed,
        "tiles_without_valid_windows": empty,
        "tile_failures": failures,
        "candidate_windows_evaluated": windows,
        "target_reference_profiles": refs,
        "targets": {
            target: {"candidate_windows": select_diverse(result_rows[target], TOP_PER_SHARD, max_per_tile=8)}
            for target in ("moon", "mars")
        },
        "elapsed_seconds": round(time.time() - started, 2),
        "is_smoke_test": bool(args.max_tiles),
        "notes": [
            "GLO-90 is used for worldwide terrain coverage; current regional GLO-30 is kept as a separate finer-resolution reference layer.",
            "Candidate windows are non-overlapping 6x6 cells at nominal 925 m support and are screened only where sufficient valid DEM data exist.",
            "Core index reproduces the three-feature terrain-distance concept; the secondary feature family adds P95 slope, elevation IQR and detrended roughness.",
            "Core and secondary indexes are alternative terrain descriptors from the same Copernicus GLO-90 DEM. Their agreement is not independent-source validation or statistical confidence.",
            "Copernicus DEM is a DSM; vegetation, buildings, snow/ice and other surface objects may contribute to elevation."
        ]
    }
    path = OUT / f"global-shard-{args.shard:02d}.json"
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "shard": args.shard, "tile_inventory_total": len(tiles),
        "tiles_assigned": len(selected), "tiles_processed": processed,
        "failures": len(failures), "windows": windows, "output": str(path)
    }, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--shard", type=int, required=True)
    parser.add_argument("--shards", type=int, default=SHARDS)
    parser.add_argument("--max-tiles", type=int, default=0, help="Smoke-test limiter; do not use for a complete global release.")
    parser.add_argument("--refresh-tile-list", action="store_true")
    args = parser.parse_args()
    if not 0 <= args.shard < args.shards:
        raise SystemExit("--shard must be in [0, shards)")
    run(args)


if __name__ == "__main__":
    main()

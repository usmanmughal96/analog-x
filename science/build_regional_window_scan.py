#!/usr/bin/env python3
"""Build an evidence-bounded, matched-support regional terrain-window scan.

This scans 5.55 km windows inside ANALOG-X's ten existing 30 km Earth DEM
study areas. It is not a global Earth scan and does not classify geology,
resource abundance, landing safety, or rover trafficability.

Only the standard library is required.
"""
from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
TERRAIN_PATH = ROOT / "data/terrain/terrain_comparison.json"
MOON_PATH = ROOT / "data/moon/shackleton_lola_80m.json"
CATALOG_PATH = ROOT / "data/agents/candidate_catalog.json"
OUT_PATH = ROOT / "data/analog_benchmark/regional_window_scan.json"

FEATURES = ("median_slope_deg", "p90_slope_deg", "p90_local_relief_m")
WINDOW_CELLS = 6
MIN_VALID_CELLS = math.ceil(WINDOW_CELLS * WINDOW_CELLS * 0.70)
MIN_DERIVATIVE_SAMPLES = 15
SENSITIVITY_DRAWS = 500
RANDOM_SEED = 20261118
MAX_RESULTS = 30
MAX_PER_PARENT_SITE = 4
MIN_RESULT_SEPARATION_KM = 6.0


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(path)
    return json.loads(path.read_text(encoding="utf-8"))


def percentile(values: list[float], probability: float) -> float:
    """Linear-interpolated percentile, matching NumPy's default method."""
    if not values:
        raise ValueError("Cannot calculate percentile of an empty list")
    ordered = sorted(float(value) for value in values)
    position = (len(ordered) - 1) * probability
    lower = math.floor(position)
    upper = math.ceil(position)
    fraction = position - lower
    return ordered[lower] * (1 - fraction) + ordered[upper] * fraction


def is_valid(value: Any) -> bool:
    return isinstance(value, (int, float)) and math.isfinite(float(value))


def derive_windows(
    surface: dict[str, Any],
    *,
    site_id: str,
    site: dict[str, Any] | None = None,
    center_wgs84: list[float] | None = None,
) -> list[dict[str, Any]]:
    """Derive window metrics from a locally median-relative elevation grid."""
    grid = surface.get("values")
    if not isinstance(grid, list) or not grid or not isinstance(grid[0], list):
        raise ValueError(f"{site_id}: surface grid is missing or malformed")

    rows = len(grid)
    columns = len(grid[0])
    if any(not isinstance(row, list) or len(row) != columns for row in grid):
        raise ValueError(f"{site_id}: surface grid is not rectangular")

    z = [
        [float(value) if is_valid(value) else math.nan for value in row]
        for row in grid
    ]
    spacing = surface.get("pixel_size_m") or {}
    dx = float(spacing.get("x", 925.0))
    dy = float(spacing.get("y", 925.0))
    if dx <= 0 or dy <= 0:
        raise ValueError(f"{site_id}: invalid raster pixel spacing")

    def valid(row: int, column: int) -> bool:
        return (
            0 <= row < rows
            and 0 <= column < columns
            and math.isfinite(z[row][column])
        )

    slope: list[list[float | None]] = [
        [None for _ in range(columns)] for _ in range(rows)
    ]
    relief: list[list[float | None]] = [
        [None for _ in range(columns)] for _ in range(rows)
    ]

    # Central differences are calculated only where all four neighbours exist.
    for row in range(1, rows - 1):
        for column in range(1, columns - 1):
            if (
                valid(row, column - 1)
                and valid(row, column + 1)
                and valid(row - 1, column)
                and valid(row + 1, column)
            ):
                gx = (z[row][column + 1] - z[row][column - 1]) / (2 * dx)
                gy = (z[row + 1][column] - z[row - 1][column]) / (2 * dy)
                slope[row][column] = math.degrees(math.atan(math.hypot(gx, gy)))

            neighbourhood: list[float] = []
            complete = True
            for rr in range(row - 1, row + 2):
                for cc in range(column - 1, column + 2):
                    if not valid(rr, cc):
                        complete = False
                        break
                    neighbourhood.append(z[rr][cc])
                if not complete:
                    break
            if complete:
                relief[row][column] = max(neighbourhood) - min(neighbourhood)

    candidates: list[dict[str, Any]] = []
    for start_row in range(rows - WINDOW_CELLS + 1):
        for start_column in range(columns - WINDOW_CELLS + 1):
            valid_cells = 0
            slopes: list[float] = []
            local_relief: list[float] = []

            for row in range(start_row, start_row + WINDOW_CELLS):
                for column in range(start_column, start_column + WINDOW_CELLS):
                    if valid(row, column):
                        valid_cells += 1
                    slope_value = slope[row][column]
                    relief_value = relief[row][column]
                    if slope_value is not None:
                        slopes.append(slope_value)
                    if relief_value is not None:
                        local_relief.append(relief_value)

            if (
                valid_cells < MIN_VALID_CELLS
                or len(slopes) < MIN_DERIVATIVE_SAMPLES
                or len(local_relief) < MIN_DERIVATIVE_SAMPLES
            ):
                continue

            row_center = start_row + (WINDOW_CELLS - 1) / 2
            column_center = start_column + (WINDOW_CELLS - 1) / 2
            latitude = longitude = None
            if center_wgs84:
                center_lon, center_lat = map(float, center_wgs84)
                latitude = center_lat + (
                    ((rows - 1) / 2 - row_center) * dy / 111_320.0
                )
                longitude = center_lon + (
                    (column_center - (columns - 1) / 2)
                    * dx
                    / (111_320.0 * math.cos(math.radians(center_lat)))
                )

            name = (site or {}).get("name", site_id)
            candidates.append(
                {
                    "id": f"{site_id}_r{start_row}_c{start_column}",
                    "site_id": site_id,
                    "name": name,
                    "country": (site or {}).get("country", "Planetary"),
                    "latitude": latitude,
                    "longitude": longitude,
                    "row": start_row,
                    "column": start_column,
                    "valid_cell_percent": 100 * valid_cells / (WINDOW_CELLS**2),
                    "terrain": {
                        "median_slope_deg": percentile(slopes, 0.50),
                        "p90_slope_deg": percentile(slopes, 0.90),
                        "p90_local_relief_m": percentile(local_relief, 0.90),
                    },
                    "analysis_resolution_m": (dx + dy) / 2,
                    "window_cells": WINDOW_CELLS,
                    "window_footprint_km": WINDOW_CELLS * (dx + dy) / 2 / 1000,
                    "environment_tags": (site or {}).get("environment_tags", []),
                    "mission_targets": (site or {}).get("mission_targets", []),
                    "source_references": (site or {}).get("source_references", []),
                }
            )
    return candidates


class XorShift32:
    """Small deterministic RNG so local and CI builds generate identical draws."""

    def __init__(self, seed: int):
        self.state = seed & 0xFFFFFFFF or 0xA341316C

    def random(self) -> float:
        value = self.state
        value ^= (value << 13) & 0xFFFFFFFF
        value ^= value >> 17
        value ^= (value << 5) & 0xFFFFFFFF
        self.state = value & 0xFFFFFFFF
        return self.state / 4294967296.0


def iqr(values: list[float]) -> float:
    return percentile(values, 0.75) - percentile(values, 0.25)


def haversine_km(a: dict[str, Any], b: dict[str, Any]) -> float:
    if None in (a.get("latitude"), a.get("longitude"), b.get("latitude"), b.get("longitude")):
        return math.inf
    radius = 6371.0088
    lat1, lat2 = math.radians(a["latitude"]), math.radians(b["latitude"])
    dlat = lat2 - lat1
    dlon = math.radians(b["longitude"] - a["longitude"])
    h = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    return 2 * radius * math.asin(math.sqrt(min(1.0, h)))


def add_scores(
    earth_windows: list[dict[str, Any]],
    site_windows: dict[str, list[dict[str, Any]]],
    target_windows: list[dict[str, Any]],
    target_id: str,
    target_source: str,
    target_coverage: str,
) -> dict[str, Any]:
    if not earth_windows or not target_windows:
        raise RuntimeError(f"{target_id}: no valid windows available for comparison")

    target_profile = {
        feature: percentile(
            [window["terrain"][feature] for window in target_windows], 0.50
        )
        for feature in FEATURES
    }
    scales = {
        feature: iqr([window["terrain"][feature] for window in earth_windows])
        for feature in FEATURES
    }
    scales = {key: (value if value > 0 else 1.0) for key, value in scales.items()}

    ranked: list[dict[str, Any]] = []
    for window in earth_windows:
        components = {}
        normalized_distance = 0.0
        for feature in FEATURES:
            gap = abs(window["terrain"][feature] - target_profile[feature])
            components[feature] = 100 * math.exp(-gap / scales[feature])
            normalized_distance += gap / scales[feature] / len(FEATURES)
        ranked.append(
            {
                **window,
                "components": components,
                "distance": normalized_distance,
                "score": 100 * math.exp(-normalized_distance),
            }
        )

    ranked.sort(key=lambda item: (-item["score"], item["id"]))
    for index, window in enumerate(ranked, start=1):
        window["global_rank"] = index

    # Sensitivity is calculated within each parent 30 km region. Overlapping
    # windows are dependent, so this is explicitly not a confidence interval.
    rng = XorShift32(RANDOM_SEED + (11 if target_id == "moon" else 19))
    stability = {window["id"]: 0 for window in earth_windows}
    for _ in range(SENSITIVITY_DRAWS):
        weights = [-math.log(max(rng.random(), 1e-12)) for _ in FEATURES]
        weight_sum = sum(weights)
        weights = [weight / weight_sum for weight in weights]
        for site_id, windows in site_windows.items():
            draw_scores = []
            for window in windows:
                distance = sum(
                    weights[index]
                    * abs(window["terrain"][feature] - target_profile[feature])
                    / scales[feature]
                    for index, feature in enumerate(FEATURES)
                )
                draw_scores.append((distance, window["id"]))
            draw_scores.sort(key=lambda item: (item[0], item[1]))
            threshold = math.ceil(len(draw_scores) * 0.10)
            for _, window_id in draw_scores[:threshold]:
                stability[window_id] += 1

    for window in ranked:
        window["top_decile_stability_pct"] = (
            100 * stability[window["id"]] / SENSITIVITY_DRAWS
        )

    # Select globally high-ranked local windows, while reducing duplicate
    # overlapping pins and limiting each parent region to four entries.
    selected: list[dict[str, Any]] = []
    counts: dict[str, int] = {}
    for window in ranked:
        if len(selected) >= MAX_RESULTS:
            break
        site_id = window["site_id"]
        if counts.get(site_id, 0) >= MAX_PER_PARENT_SITE:
            continue
        if any(
            haversine_km(window, previous) < MIN_RESULT_SEPARATION_KM
            for previous in selected
        ):
            continue
        selected.append(window)
        counts[site_id] = counts.get(site_id, 0) + 1

    def rounded_candidate(window: dict[str, Any]) -> dict[str, Any]:
        return {
            "id": window["id"],
            "site_id": window["site_id"],
            "name": window["name"],
            "country": window["country"],
            "latitude": round(window["latitude"], 5),
            "longitude": round(window["longitude"], 5),
            "row": window["row"],
            "column": window["column"],
            "global_rank": window["global_rank"],
            "score": round(window["score"], 2),
            "top_decile_stability_pct": round(
                window["top_decile_stability_pct"], 2
            ),
            "terrain": {
                feature: round(window["terrain"][feature], 3)
                for feature in FEATURES
            },
            "components": {
                feature: round(window["components"][feature], 2)
                for feature in FEATURES
            },
            "valid_cell_percent": round(window["valid_cell_percent"], 2),
            "window_footprint_km": round(window["window_footprint_km"], 3),
            "environment_tags": window["environment_tags"],
            "mission_targets": window["mission_targets"],
            "source_references": window["source_references"],
        }

    moon_or_mars = "Shackleton Rim / lunar south pole" if target_id == "moon" else "Nili Patera / Mars"
    return {
        "target": {
            "id": target_id,
            "name": moon_or_mars,
            "source": target_source,
            "source_coverage": target_coverage,
            "valid_target_windows": len(target_windows),
            "typical_5_55km_window_profile": {
                feature: round(value, 3) for feature, value in target_profile.items()
            },
        },
        "scan": {
            "earth_windows_scanned": len(earth_windows),
            "parent_earth_regions": len(site_windows),
            "window_cells": WINDOW_CELLS,
            "window_footprint_km": 5.55,
            "analysis_resolution_m": 925,
            "valid_window_rule": (
                f"At least {MIN_VALID_CELLS}/{WINDOW_CELLS**2} valid elevation cells "
                f"and {MIN_DERIVATIVE_SAMPLES} valid slope and relief samples"
            ),
            "weight_sensitivity_draws": SENSITIVITY_DRAWS,
            "stability_definition": (
                "Percentage of random Dirichlet(1,1,1) feature-weight draws for which "
                "this window ranked in the top decile of its own 30 km parent region. "
                "Rank sensitivity only—not analog probability or statistical confidence."
            ),
            "default_weights": {feature: 1 / len(FEATURES) for feature in FEATURES},
            "earth_iqr_scales": {
                feature: round(value, 3) for feature, value in scales.items()
            },
            "selection_rule": (
                f"Up to {MAX_RESULTS} windows, max {MAX_PER_PARENT_SITE} per parent region, "
                f"at least {MIN_RESULT_SEPARATION_KM:.1f} km apart"
            ),
        },
        "candidate_windows": [rounded_candidate(window) for window in selected],
        "global_top_30_unfiltered": [rounded_candidate(window) for window in ranked[:30]],
    }


def build() -> dict[str, Any]:
    terrain = read_json(TERRAIN_PATH)
    moon = read_json(MOON_PATH)
    catalog = read_json(CATALOG_PATH)
    sites = {site["id"]: site for site in catalog.get("candidate_sites", [])}

    earth_windows: list[dict[str, Any]] = []
    site_windows: dict[str, list[dict[str, Any]]] = {}
    for site_id, data in terrain.get("earth_sites", {}).items():
        if data.get("status") != "processed" or not data.get("surface_grid_relative_m"):
            continue
        site = sites.get(site_id, {"name": site_id, "country": "Unknown"})
        center = data.get("source", {}).get("centre_wgs84")
        windows = derive_windows(
            data["surface_grid_relative_m"],
            site_id=site_id,
            site=site,
            center_wgs84=center,
        )
        if windows:
            site_windows[site_id] = windows
            earth_windows.extend(windows)

    if len(site_windows) != 10:
        raise RuntimeError(
            f"Expected ten processed Earth DEM regions; found {len(site_windows)}"
        )

    moon_windows = derive_windows(
        moon["surface_grid_relative_m"], site_id="moon", site=None
    )
    mars_windows = derive_windows(
        terrain["planetary_target"]["surface_grid_relative_m"],
        site_id="mars",
        site=None,
    )
    if len(moon_windows) == 0 or len(mars_windows) == 0:
        raise RuntimeError("No valid local windows in one or more planetary targets")

    mars_coverage = terrain.get("planetary_target", {}).get("window", {}).get(
        "valid_observation_coverage_percent"
    )
    moon_support = moon.get("matched_coarse_support_approx_925m", {}).get(
        "ldec_positive_return_support", {}
    )
    result = {
        "schema_version": "1.0",
        "engine": "ANALOG-X Regional Terrain Window Discovery & Robustness Engine",
        "generated_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "scientific_contract": {
            "unit_of_analysis": (
                "5.55 km × 5.55 km regional terrain windows sampled inside ten "
                "pre-selected 30 km Earth study/reference areas"
            ),
            "not_global_search": True,
            "score_interpretation": (
                "Exploratory terrain-only proximity index using equal-weight, "
                "IQR-normalized absolute gaps in median slope, P90 slope and P90 "
                "3×3 local relief. It is not a probability, geological match, "
                "mission score or landing-suitability assessment."
            ),
            "scale_limit": (
                "Earth inputs are Copernicus DEM GLO-30 DSM resampled to ~925 m; "
                "the Moon input is 80 m LOLA aggregated to ~925 m; Mars uses "
                "~925 m MOLA. The 5.55 km windows retain ~925 m spatial support."
            ),
            "window_overlap": (
                "Sliding windows overlap and are spatially dependent. Weight "
                "sensitivity is not a statistical confidence interval."
            ),
            "candidate_limit": (
                "Results identify candidate sub-windows within the ten existing "
                "study regions only. They are not a whole-Earth scan or newly "
                "validated geological analog discoveries."
            ),
            "physical_nontransferability": [
                "Earth gravity and atmosphere differ from the Moon and Mars.",
                "Terrain similarity does not measure lithology, mineralogy, regolith strength, dust, water or radiation.",
                "No rover-scale trafficability, landing safety, resource access or base suitability is inferred.",
            ],
            "inspiration_and_method_note": (
                "The transparent IQR-normalized terrain-distance and stability "
                "ideas were independently implemented after reviewing public "
                "NASA Space Apps examples from Team Shoemaker and Earth Analog "
                "Explorer. No competitor source code is copied into this engine."
            ),
        },
        "inputs": {
            "earth": "data/terrain/terrain_comparison.json",
            "moon": "data/moon/shackleton_lola_80m.json",
            "catalog": "data/agents/candidate_catalog.json",
            "earth_region_count": len(site_windows),
            "earth_window_count": len(earth_windows),
            "earth_window_count_by_region": {
                site_id: len(windows) for site_id, windows in site_windows.items()
            },
            "moon_window_count": len(moon_windows),
            "mars_window_count": len(mars_windows),
            "moon_ldec_mean_native_support_percent": moon_support.get(
                "mean_native_pixel_fraction_per_coarse_cell_percent"
            ),
            "mars_parent_grid_observed_coverage_percent": mars_coverage,
            "mars_parent_grid_complete_3x3_neighbourhoods": terrain.get(
                "planetary_target", {}
            ).get("terrain_metrics", {}).get("complete_3x3_neighbourhood_count"),
        },
        "targets": {
            "moon": add_scores(
                earth_windows,
                site_windows,
                moon_windows,
                "moon",
                "NASA LRO LOLA PDS GDR LDEM_80S_80M aggregated to ~925 m",
                "32×32 interpolated elevation grid; LDEC reports "
                f"{moon_support.get('mean_native_pixel_fraction_per_coarse_cell_percent', 'unknown')}% "
                "mean native-pixel return support per coarse cell",
            ),
            "mars": add_scores(
                earth_windows,
                site_windows,
                mars_windows,
                "mars",
                "NASA MGS MOLA MEGDR 64 pixels/degree",
                f"{mars_coverage}% observed-cell coverage in the parent 30 km grid; "
                f"{terrain.get('planetary_target', {}).get('terrain_metrics', {}).get('complete_3x3_neighbourhood_count')} "
                "complete 3×3 neighborhoods. Only local windows meeting the explicit validity threshold are ranked.",
            ),
        },
    }

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(
        json.dumps(result, indent=2, allow_nan=False) + "\n", encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "output": str(OUT_PATH.relative_to(ROOT)),
                "earth_regions": len(site_windows),
                "earth_windows": len(earth_windows),
                "moon_windows": len(moon_windows),
                "mars_windows": len(mars_windows),
                "moon_candidates": len(result["targets"]["moon"]["candidate_windows"]),
                "mars_candidates": len(result["targets"]["mars"]["candidate_windows"]),
            },
            indent=2,
        )
    )
    return result


if __name__ == "__main__":
    build()

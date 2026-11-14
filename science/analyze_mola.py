#!/usr/bin/env python3
"""Summarize NASA MOLA MEGDR global topography for a Mars region."""
from __future__ import annotations
import argparse, json, urllib.request
from pathlib import Path
import numpy as np

BASE = "https://pds-geosciences.wustl.edu/mgs/mgs-m-mola-5-megdr-l3-v1/mgsl_300x/meg004"
FILES = {"topography": ("MEGT90N000CB.IMG", ">i2"), "counts": ("MEGC90N000CB.IMG", ">i2")}
SHAPE = (720, 1440)

def get_file(kind: str, directory: Path) -> Path:
    filename, _ = FILES[kind]
    target = directory / filename
    target.parent.mkdir(parents=True, exist_ok=True)
    if not target.exists():
        url = f"{BASE}/{filename}"
        print(f"Downloading {url}")
        urllib.request.urlretrieve(url, target)
    return target

def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--out", default="outputs/mola_syrtis_summary.json")
    p.add_argument("--data-dir", default="data/raw/mars")
    p.add_argument("--west", type=float, default=45.0)
    p.add_argument("--east", type=float, default=90.0)
    p.add_argument("--south", type=float, default=0.0)
    p.add_argument("--north", type=float, default=30.0)
    args = p.parse_args()
    data_dir = Path(args.data_dir)
    topo_path, count_path = get_file("topography", data_dir), get_file("counts", data_dir)
    topo = np.fromfile(topo_path, dtype=FILES["topography"][1])
    counts = np.fromfile(count_path, dtype=FILES["counts"][1])
    if topo.size != SHAPE[0] * SHAPE[1] or counts.size != topo.size:
        raise SystemExit("Unexpected MOLA file size; check product/version and labels.")
    topo = topo.reshape(SHAPE).astype(np.float64)
    counts = counts.reshape(SHAPE).astype(np.int32)
    row_centres = 90.0 - (np.arange(SHAPE[0]) + 0.5) / 4.0
    r0 = np.where(row_centres <= args.north)[0][0]
    r1 = np.where(row_centres >= args.south)[0][-1] + 1
    c0, c1 = max(0, int(np.floor(args.west * 4))), min(SHAPE[1], int(np.ceil(args.east * 4)))
    z, n = topo[r0:r1, c0:c1], counts[r0:r1, c0:c1]
    valid = (n > 0) & np.isfinite(z) & (z != -32768)
    values = z[valid]
    result = {
        "dataset": "MGS MOLA MEGDR global topography, 4 pixels/degree",
        "product_id": "MEGT90N000CB.IMG", "instrument": "Mars Orbiter Laser Altimeter (MOLA)",
        "region": {"west_east_longitude_deg": [args.west, args.east], "south_north_latitude_deg": [args.south, args.north]},
        "grid": {"pixels_per_degree": 4, "approx_equatorial_pixel_scale_km": 14.818, "rows": int(r1-r0), "columns": int(c1-c0)},
        "valid_observation_coverage_percent": round(float(valid.sum()/valid.size*100), 2) if valid.size else 0.0,
        "observed_cells": int(valid.sum()), "total_cells": int(valid.size),
        "topography_m": None if values.size == 0 else {"median": float(np.median(values)), "mean": float(np.mean(values)), "p10": float(np.percentile(values,10)), "p90": float(np.percentile(values,90)), "min": float(np.min(values)), "max": float(np.max(values))},
        "caveat": "Regional context only; not rover-scale hazard data. Do not directly compare with 30 m Earth DEM slope statistics. Counts exclude interpolated/no-observation cells.",
        "source_url": f"{BASE}/megt90n000cb.img", "label_url": f"{BASE}/megt90n000cb.lbl", "counts_url": f"{BASE}/megc90n000cb.img"
    }
    out = Path(args.out); out.parent.mkdir(parents=True, exist_ok=True); out.write_text(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()

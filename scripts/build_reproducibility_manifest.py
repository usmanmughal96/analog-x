#!/usr/bin/env python3
"""Build a deterministic SHA-256 inventory for ANALOG-X science assets.

The manifest inventories files present in the repository. It does not certify
scientific validity, data licensing, or external source completeness.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INCLUDE_DIRS = ("data", "science", "scripts", "docs")
OUTPUT = ROOT / "data/provenance/reproducibility_manifest.json"
EXCLUDE_PARTS = {".git", "__pycache__", ".pytest_cache"}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def git_value(*args: str) -> str | None:
    try:
        return subprocess.check_output(
            ["git", *args], cwd=ROOT, text=True, stderr=subprocess.DEVNULL
        ).strip() or None
    except (OSError, subprocess.CalledProcessError):
        return None


def classify(path: Path) -> str:
    rel = path.relative_to(ROOT).as_posix().lower()
    if "quicklook" in rel or rel.endswith((".jpg", ".jpeg", ".webp")):
        return "browse_only"
    if "cmr" in rel or "pds_search" in rel or "catalog" in rel:
        return "metadata_only"
    if rel.startswith(("data/terrain/", "data/power/", "data/moon/")):
        return "processed"
    if rel.startswith("data/"):
        return "source_or_derived_unclassified"
    return "method_or_documentation"


def main() -> None:
    records = []
    for directory in INCLUDE_DIRS:
        base = ROOT / directory
        if not base.exists():
            continue
        for path in sorted(base.rglob("*")):
            if not path.is_file() or any(part in EXCLUDE_PARTS for part in path.parts):
                continue
            if path == OUTPUT:
                continue
            records.append({
                "path": path.relative_to(ROOT).as_posix(),
                "size_bytes": path.stat().st_size,
                "sha256": sha256(path),
                "evidence_class": classify(path),
            })
    payload = {
        "schema_version": "1.0.0",
        "project": "ANALOG-X",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "repository_commit": git_value("rev-parse", "HEAD"),
        "working_tree": "dirty" if git_value("status", "--porcelain") else "clean",
        "inventory_scope": list(INCLUDE_DIRS),
        "file_count": len(records),
        "records": records,
        "limitations": [
            "File hashes establish byte-level identity, not scientific validity.",
            "Evidence classes are conservative path-based hints and require source-specific review.",
            "External source URLs, licences, acquisition periods and processing parameters must be recorded in product-level provenance.",
            "A catalogue record or browse image is not a decoded quantitative science dataset."
        ],
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {OUTPUT.relative_to(ROOT)} with {len(records)} hashed files")


if __name__ == "__main__":
    main()

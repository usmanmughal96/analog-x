#!/usr/bin/env python3
"""Build a provenance-aware SHA-256 inventory of ANALOG-X science assets."""
from __future__ import annotations
import hashlib, importlib.metadata, json, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
INCLUDE_DIRS=("data","science","scripts","docs",".github","tests","assets","agent-worker","backend")
ROOT_FILES=("README.md","index.html","demo.html","discovery.html","global-discovery.html","field-validation.html","transferability.html","service-worker.js","manifest.webmanifest","package.json","package-lock.json")
OUTPUT=ROOT/"data/provenance/reproducibility_manifest.json"
EXCLUDE_PARTS={".git","__pycache__",".pytest_cache"}
# The quantitative report consumes this manifest's hash and inventory count.
# Excluding the report prevents a circular dependency and lets it reference
# the manifest generated in the same workflow run.
EXCLUDE_FILES={
    "data/provenance/reproducibility_manifest.json",
    "data/validation/quantitative_validation.json",
}
def include_in_manifest(path: Path) -> bool:
    return path.relative_to(ROOT).as_posix() not in EXCLUDE_FILES
def sha256(path):
    h=hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda:f.read(1024*1024),b""):h.update(chunk)
    return h.hexdigest()
def git_value(*args):
    try:return subprocess.check_output(["git",*args],cwd=ROOT,text=True,stderr=subprocess.DEVNULL).strip() or None
    except (OSError,subprocess.CalledProcessError):return None
def classify(path):
    rel=path.relative_to(ROOT).as_posix().lower()
    if "quicklook" in rel or rel.endswith((".jpg",".jpeg",".webp",".png")) and "preview" in rel:return "browse_only"
    if "cmr" in rel or "pds_search" in rel or "catalog" in rel:return "metadata_only"
    if rel.startswith(("data/terrain/","data/power/","data/moon/","data/transferability/","data/validation/")):return "processed_or_derived"
    if rel.startswith("data/global_discovery/"):return "global_discovery_output"
    if rel.startswith("data/field_validation/"):return "field_evidence_ledger"
    if rel.startswith("data/"):return "data_or_analysis_asset_requires_registry_context"
    return "method_or_documentation"
def package_version(name):
    try:return importlib.metadata.version(name)
    except importlib.metadata.PackageNotFoundError:return None
def main():
    registry_path=ROOT/"data/source_registry.json"
    registry=json.loads(registry_path.read_text(encoding="utf-8")) if registry_path.exists() else {"sources":[]}
    source_context=[]
    for source in registry.get("sources",[]):
        source_context.append({
            "id":source.get("id"),"state":source.get("state"),"provider":source.get("provider"),
            "name":source.get("name"),"url":source.get("url"),"doi_or_identifier":source.get("doi_or_identifier"),
            "artifacts":source.get("artifacts",[]),"limitations":source.get("limitations",[])
        })
    records=[]
    for relative in ROOT_FILES:
        path=ROOT/relative
        if path.is_file() and include_in_manifest(path):
            records.append({"path":relative,"size_bytes":path.stat().st_size,"sha256":sha256(path),"evidence_class_hint":classify(path)})
    for directory in INCLUDE_DIRS:
        base=ROOT/directory
        if not base.exists():continue
        for path in sorted(base.rglob("*")):
            if not path.is_file() or any(part in EXCLUDE_PARTS for part in path.parts) or not include_in_manifest(path):continue
            records.append({"path":path.relative_to(ROOT).as_posix(),"size_bytes":path.stat().st_size,"sha256":sha256(path),"evidence_class_hint":classify(path)})
    payload={
        "schema_version":"2.0.0","project":"ANALOG-X","generated_at_utc":datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "repository_commit_before_manifest_commit":git_value("rev-parse","HEAD"),
        "working_tree_before_manifest_write":"dirty" if git_value("status","--porcelain") else "clean",
        "generator":"scripts/build_reproducibility_manifest.py",
        "python_version":sys.version.split()[0],
        "runtime_packages":{name:package_version(name) for name in ("numpy","rasterio","scipy","requests","Pillow")},
        "inventory_scope":{"directories":list(INCLUDE_DIRS),"root_files":[x for x in ROOT_FILES if (ROOT/x).is_file()]},"file_count":len(records),
        "source_registry_sha256":sha256(registry_path) if registry_path.exists() else None,
        "source_registry_records":source_context,"records":records,
        "limitations":[
            "SHA-256 establishes byte-level identity, not scientific validity or source authenticity.",
            "The repository commit is recorded before the manifest file itself is written and committed; the manifest cannot hash its own final committed bytes.",
            "The inventory includes core source-code, UI, tests, workflows, generated data and research documentation.",
            "Source context is copied from the versioned source registry. Each generated product must still retain acquisition date, item/granule IDs, licence, exact parameters, coordinate reference system and processing logs where available.",
            "Path-based evidence-class hints are not a substitute for the source registry's explicit per-product state.",
            "Catalogue metadata and browse images are not equivalent to downloaded, decoded quantitative science arrays."
        ]
    }
    OUTPUT.parent.mkdir(parents=True,exist_ok=True)
    OUTPUT.write_text(json.dumps(payload,indent=2)+"\n",encoding="utf-8")
    print(f"Wrote {OUTPUT.relative_to(ROOT)} with {len(records)} hashed repository files and {len(source_context)} source records")
if __name__=="__main__":main()

#!/usr/bin/env python3
"""Discover Moon/Mars observational-product metadata through NASA PDS Search.

This is metadata discovery only. It does not download or process product binaries,
and it never treats registry metadata as calibration, coverage or science evidence.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "planetary" / "pds_search.json"
API = "https://pds.mcp.nasa.gov/api/search/1/products"
QUERY_LIMIT = 25
OBSERVATIONAL_CLASS = "Product_Observational"

MARS = "urn:nasa:pds:context:target:planet.mars"
MOON = "urn:nasa:pds:context:target:satellite.earth.moon"
MOLA = "urn:nasa:pds:context:instrument:mgs.mola"
HIRISE = "urn:nasa:pds:context:instrument:hirise.mro"
LOLA = "urn:nasa:pds:context:instrument:lro.lola"
DIVINER = "urn:nasa:pds:context:instrument:lro.dlre"

QUERIES = [
    {
        "id": "mars_target",
        "q": f'(product_class eq "{OBSERVATIONAL_CLASS}" and ref_lid_target eq "{MARS}")',
        "target": "Mars",
        "instrument_filter": None,
        "target_filter": "planet.mars",
        "purpose": "Discover PDS observational products whose target metadata references Mars.",
    },
    {
        "id": "mars_mola",
        "q": f'(product_class eq "{OBSERVATIONAL_CLASS}" and ref_lid_instrument eq "{MOLA}" and ref_lid_target eq "{MARS}")',
        "target": "Mars",
        "instrument_filter": "mgs.mola",
        "target_filter": "planet.mars",
        "purpose": "Search Mars-target observational products from the MGS MOLA instrument.",
    },
    {
        "id": "mars_hirise",
        "q": f'(product_class eq "{OBSERVATIONAL_CLASS}" and ref_lid_instrument eq "{HIRISE}" and ref_lid_target eq "{MARS}")',
        "target": "Mars",
        "instrument_filter": "hirise.mro",
        "target_filter": "planet.mars",
        "purpose": "Search Mars-target observational products from the MRO HiRISE instrument.",
    },
    {
        "id": "moon_target",
        "q": f'(product_class eq "{OBSERVATIONAL_CLASS}" and ref_lid_target eq "{MOON}")',
        "target": "Moon",
        "instrument_filter": None,
        "target_filter": "satellite.earth.moon",
        "purpose": "Discover PDS observational products whose target metadata references the Moon.",
    },
    {
        "id": "moon_lola",
        "q": f'(product_class eq "{OBSERVATIONAL_CLASS}" and ref_lid_instrument eq "{LOLA}" and ref_lid_target eq "{MOON}")',
        "target": "Moon",
        "instrument_filter": "lro.lola",
        "target_filter": "satellite.earth.moon",
        "purpose": "Search Moon-target observational products from the LRO LOLA instrument.",
    },
    {
        "id": "moon_diviner",
        "q": f'(product_class eq "{OBSERVATIONAL_CLASS}" and ref_lid_instrument eq "{DIVINER}" and ref_lid_target eq "{MOON}")',
        "target": "Moon",
        "instrument_filter": "lro.dlre",
        "target_filter": "satellite.earth.moon",
        "purpose": "Search Moon-target observational products from the LRO Diviner instrument.",
    },
]

SESSION = requests.Session()
SESSION.headers.update(
    {
        "User-Agent": "ANALOG-X/1.2 (NASA PDS metadata discovery; research prototype)",
        "Accept": "application/json",
    }
)
RETRY = Retry(
    total=2,
    connect=2,
    read=2,
    backoff_factor=0.75,
    status_forcelist=(429, 500, 502, 503, 504),
    allowed_methods=frozenset(["GET"]),
    respect_retry_after_header=True,
)
SESSION.mount("https://", HTTPAdapter(max_retries=RETRY))


def _value(product: dict[str, Any], key: str) -> Any:
    """Read a PDS field from flat API records or a nested properties map."""
    value = product.get(key)
    if value is not None:
        return value
    properties = product.get("properties")
    if isinstance(properties, dict):
        return properties.get(key)
    return None


def _first_value(product: dict[str, Any], *keys: str) -> Any:
    for key in keys:
        value = _value(product, key)
        if isinstance(value, list):
            if value:
                return value[0]
        elif value is not None:
            return value
    return None


def _as_list(value: Any, limit: int = 8) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value[:limit]
    return [value]


def is_observational_product(product: dict[str, Any]) -> bool:
    """Trust the server-side class filter if the response omits product_class."""
    product_class = _first_value(product, "product_class", "type")
    if product_class is None:
        return True
    normalized = str(product_class).strip().lower()
    return normalized in {
        "product_observational",
        "observational",
        "observationals",
    }


def compact_product(product: dict[str, Any]) -> dict[str, Any]:
    """Normalize flat PDS Search records while retaining source references."""
    metadata = product.get("metadata")
    if not isinstance(metadata, dict):
        metadata = {}
    targets = _as_list(_value(product, "ref_lid_target") or product.get("targets"))
    instruments = _as_list(
        _value(product, "ref_lid_instrument") or product.get("instrument_refs")
    )
    components = _as_list(product.get("observing_system_components"))
    return {
        "id": _first_value(product, "lidvid", "id", "lid"),
        "type": _first_value(product, "product_class", "type"),
        "title": _first_value(product, "title"),
        "start_date_time": _first_value(
            product,
            "start_date_time",
            "pds:Time_Coordinates.pds:start_date_time",
        ),
        "stop_date_time": _first_value(
            product,
            "stop_date_time",
            "pds:Time_Coordinates.pds:stop_date_time",
        ),
        "targets": targets,
        "observing_system_components": components,
        "instrument_refs": instruments,
        "data_file_url": _first_value(
            product,
            "ops:Data_File_Info.ops:file_ref",
            "data_file_url",
            "file_ref_url",
        ),
        "data_file_name": _first_value(
            product,
            "ops:Data_File_Info.ops:file_name",
            "data_file_name",
            "file_name",
        ),
        "label_url": _first_value(
            product,
            "ops:Label_File_Info.ops:file_ref",
            "label_url",
        )
        or metadata.get("label_url"),
    }


def extract_products(payload: Any) -> list[dict[str, Any]]:
    """Read the PDS data array with a conservative legacy fallback."""
    if not isinstance(payload, dict):
        return []
    products = payload.get("data")
    if products is None:
        products = payload.get("results")
    if not isinstance(products, list):
        return []
    return [item for item in products if isinstance(item, dict)]


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    results = []

    for query in QUERIES:
        params = {"limit": QUERY_LIMIT, "q": query["q"]}
        # Record the exact request before dispatch so RetryError/connection
        # failures still leave an inspectable query URL in the evidence ledger.
        prepared = requests.Request("GET", API, params=params).prepare()
        response_url = prepared.url
        try:
            response = SESSION.get(API, params=params, timeout=(12, 45))
            response_url = response.url
            response.raise_for_status()
            payload = response.json()
            products = extract_products(payload)
            # Target and instrument constraints are applied server-side. Do not
            # discard records merely because optional response fields are absent.
            relevant = [
                product for product in products if is_observational_product(product)
            ]
            summary = payload.get("summary") if isinstance(payload, dict) else None
            hits = summary.get("hits") if isinstance(summary, dict) else None
            results.append(
                {
                    **query,
                    "status": "results_returned" if relevant else "no_relevant_products_returned",
                    "query_url": response_url,
                    "returned_count": len(relevant),
                    "raw_result_count": len(products),
                    "products": [compact_product(product) for product in relevant],
                    "response_summary": {"hits": hits},
                }
            )
            print(
                query["id"],
                "raw",
                len(products),
                "observational",
                len(relevant),
                "hits",
                hits,
                flush=True,
            )
        except Exception as exc:
            response = getattr(exc, "response", None)
            if response is not None:
                response_url = getattr(response, "url", response_url)
                detail = (
                    response.text[:1200]
                    if getattr(response, "text", None)
                    else str(exc)
                )
            else:
                detail = str(exc)
            results.append(
                {
                    **query,
                    "status": "query_error",
                    "query_url": response_url,
                    "returned_count": 0,
                    "raw_result_count": 0,
                    "error": detail,
                    "products": [],
                }
            )
            print(query["id"], "ERROR", detail[:300], flush=True)

    output = {
        "schema_version": "1.1",
        "generated_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "provider": "NASA Planetary Data System Search API",
        "api": API,
        "query_class": OBSERVATIONAL_CLASS,
        "documentation": "https://nasa-pds.github.io/pds-api/guides/search.html",
        "access_note": (
            "Public product metadata discovery. A result is not proof that a binary "
            "product is directly downloadable, calibrated, spatially complete or "
            "ready for scientific use."
        ),
        "queries": results,
        "query_count": len(results),
        "query_limit_per_search": QUERY_LIMIT,
        "results_returned": sum(item["returned_count"] for item in results),
        "query_error_count": sum(item["status"] == "query_error" for item in results),
        "empty_query_count": sum(item["status"] == "no_relevant_products_returned" for item in results),
        "unique_product_count": len(
            {
                product.get("id")
                for query in results
                for product in query.get("products", [])
                if product.get("id")
            }
        ),
        "limitations": [
            "PDS documentation warns that the registry is not fully populated; zero results do not prove the archive lacks data.",
            "The search result is metadata only. Review product labels, calibration, coordinate system, units, spatial coverage, version and licence before processing.",
            "Binary ingestion is a separate step; do not interpret metadata as measurements.",
        ],
    }
    OUT.write_text(json.dumps(output, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "output": str(OUT.relative_to(ROOT)),
                "results_returned": output["results_returned"],
                "query_statuses": {
                    item["id"]: item["status"] for item in results
                },
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Build ANALOG-X Analog Transferability & Failure Analysis (ATFA).

This is a transparent experiment-selection engine, not a planetary similarity
percentage. It links documented site tasks to field experiments, records the
available evidence layers, and states what cannot be transferred to another
world. All classifications are explicit expert-authored rules; they are not
trained probabilities or NASA-certified ratings.
"""
from __future__ import annotations
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "transferability" / "transferability.json"

# Transferability refers to the experiment/process, never to whole-site equivalence.
# Each statement is intentionally bounded and paired with a failure condition.
TRACKS = {
    "terrain_mobility": {
        "label": "Terrain & mobility rehearsal",
        "what_transfers": "DEM processing, slope/relief interpretation, route-planning workflows and sensor-fusion procedures can be rehearsed on terrestrial terrain.",
        "breaks": "Earth gravity, atmosphere, soil cohesion, vegetation, hydrology and vehicle dynamics differ; 925 m terrain cells cannot resolve rover-scale hazards.",
        "next_measurement": "Acquire metre-to-centimetre DEM/LiDAR, grain-size and bearing-strength observations; validate traverses with an instrumented rover.",
    },
    "spectral_ground_truth": {
        "label": "Orbital-to-ground spectral validation",
        "what_transfers": "Scene selection, atmospheric/cloud screening, spectral-index QA, field spectroscopy and orbital-to-ground provenance workflows.",
        "breaks": "Earth vegetation, water, atmosphere and biological coatings alter spectra; Sentinel-2 bands are not a substitute for lunar/Martian instrument response or mineral identification.",
        "next_measurement": "Collect calibrated field spectra and XRD/XRF/FTIR samples, then compare with the relevant planetary instrument response functions.",
    },
    "evaporite_processes": {
        "label": "Evaporite / playa process science",
        "what_transfers": "Basin mapping, sediment facies logging, salt-crust morphology, desiccation structures and repeat-observation methods.",
        "breaks": "Earth liquid water, rainfall, groundwater, biology and atmospheric pressure create processes absent or different on the Moon and many Martian settings.",
        "next_measurement": "Map facies and stratigraphy; collect mineralogical samples, electrical conductivity, shallow cores and repeat wet/dry observations.",
    },
    "cryosphere_remote_sensing": {
        "label": "Ice / cold-region remote sensing",
        "what_transfers": "Debris-versus-ice mapping, thermal/optical sensor calibration, cold equipment trials and field logistics in difficult terrain.",
        "breaks": "Terrestrial glacier ice is not equivalent to lunar permanently shadowed regolith ice; pressure, sublimation, gravity and radiation differ.",
        "next_measurement": "Pair thermal imagery with ground temperature strings, snow/ice pits, dielectric measurements and independently validated ice/debris boundaries.",
    },
    "volcanic_morphology": {
        "label": "Volcanic / lava morphology",
        "what_transfers": "Lava-flow morphology mapping, roughness characterization, tube/cave reconnaissance and orbital-to-ground geologic mapping methods.",
        "breaks": "Earth weathering, vegetation, atmosphere, gravity and composition differ; andesite or altered tuff must not be called basaltic equivalence.",
        "next_measurement": "Map flow units and clast sizes; obtain petrography, XRF/XRD and high-resolution terrain/cave surveys.",
    },
    "dust_processes": {
        "label": "Dust / aeolian instrument testing",
        "what_transfers": "Wind-sensor deployment, particle collection, surface-change monitoring, dust-camera calibration and threshold-measurement procedures.",
        "breaks": "Earth air density, humidity, grain charging, gravity and wind stress differ substantially; 10 m wind speed is not dust flux or saltation threshold.",
        "next_measurement": "Measure particle-size distribution, threshold friction velocity, vertical dust flux, humidity and surface crust strength using a calibrated field station.",
    },
    "impact_geology": {
        "label": "Impact-structure field geology",
        "what_transfers": "Crater morphology mapping, ejecta/fault documentation, breccia logging and impact-geology field protocols.",
        "breaks": "Terrestrial erosion, water, atmosphere and gravity modify crater preservation; terrestrial target rocks differ from lunar regolith and impact melt.",
        "next_measurement": "Map ejecta and structural relations at high resolution; sample impactites and compare petrography/geochemistry.",
    },
    "biosignature_contamination_control": {
        "label": "Biosignature / contamination-control rehearsal",
        "what_transfers": "Field blank design, contamination-controlled sampling, instrument cleaning, chain-of-custody, extremophile habitat mapping and laboratory assay workflows can be rehearsed in terrestrial extreme environments.",
        "breaks": "Earth biology, oxygen, liquid water, organic background and terrestrial contamination differ fundamentally; finding Earth extremophiles does not demonstrate extraterrestrial life or validate a Mars biosignature.",
        "next_measurement": "Run contamination-controlled transects with field blanks, replicate samples, metagenomic or targeted assays, mineral-organic co-location and independent laboratory validation.",
    },
    "human_robotic_ops": {
        "label": "Human / robotic field operations",
        "what_transfers": "Remote team coordination, navigation interfaces, sampling workflows, communications procedures, logistics and human-factors evaluation.",
        "breaks": "No Earth field site reproduces EVA suits, vacuum, radiation, reduced gravity, lunar dust electrostatics or Mars atmospheric constraints.",
        "next_measurement": "Run a controlled mission simulation with timed tasks, comms latency, equipment failure injection and documented operator workload.",
    },
}

SITE_RULES = {
    "chagai_small_playas": {
        "tracks": {
            "evaporite_processes": ("moderate", "Historic NASA report identifies two small salt-surfaced playas; modern site-specific facies and mineralogy remain unverified."),
            "spectral_ground_truth": ("limited", "A 20 m Sentinel-2 spectral-context profile exists; it is not mineral identification or brine detection."),
            "terrain_mobility": ("limited", "Coarse ~925 m Copernicus DSM profile exists; it cannot resolve crust strength or rover-scale hazards."),
            "human_robotic_ops": ("moderate", "Remote arid field sampling and provenance workflows are rehearsable; mission environmental conditions are not."),
        },
        "priority": "Test whether mapped salt-crust facies and spectral anomalies can be tied to independently sampled mineralogy.",
    },
    "hamun_i_mashkel": {
        "tracks": {
            "evaporite_processes": ("moderate", "Intermittent playa/closed-basin process lead; hydrological boundaries and modern facies need validation."),
            "spectral_ground_truth": ("limited", "A narrow Sentinel-2 strip supplies screening context, not basin-wide mineral or water evidence."),
            "terrain_mobility": ("limited", "Coarse regional terrain is processed; surface bearing strength and seasonal access are unknown."),
            "human_robotic_ops": ("moderate", "Remote basin reconnaissance and sampling logistics are useful rehearsal activities."),
        },
        "priority": "Acquire multi-season imagery and field sediment/mineral samples to test inundation-drying facies.",
    },
    "koh_i_sultan": {
        "tracks": {
            "volcanic_morphology": ("moderate", "USGS mapping documents agglomerate, tuff and andesitic lava; this is not a basalt-composition match."),
            "spectral_ground_truth": ("limited", "Sentinel-2 scenes and terrain context support mapping workflows; no validated alteration/mineral map is integrated."),
            "terrain_mobility": ("limited", "Coarse DSM supports regional morphology only, not vehicle-scale traversability."),
            "human_robotic_ops": ("moderate", "Remote volcanic field mapping and instrument deployment are rehearsable."),
        },
        "priority": "Ground-truth mapped volcanic units with petrography and spectroscopy before proposing compositional analogies.",
    },
    "hispar_glacier": {
        "tracks": {
            "cryosphere_remote_sensing": ("moderate", "Glacier/debris interpretation and cold-region sensor methods are relevant; the national glacier inventory is prior work, not a new ANALOG-X discovery."),
            "terrain_mobility": ("limited", "Coarse terrain profile is useful for regional context only; crevasses and local hazards are unresolved."),
            "spectral_ground_truth": ("limited", "Sentinel-2 context can rehearse snow/ice screening but requires field validation and seasonal controls."),
            "human_robotic_ops": ("moderate", "High-altitude remote field logistics and equipment endurance are testable."),
        },
        "priority": "Validate debris/ice classification with field transects and temperature measurements; do not equate glacier ice with lunar PSR ice.",
    },
    "dallol": {
        "tracks": {
            "evaporite_processes": ("moderate", "Saline hydrothermal and evaporite settings offer process/mapping methods; Earth hydrology and biology are major differences."),
            "volcanic_morphology": ("limited", "Hydrothermal/volcanic context is relevant to mapping methods, not a direct lunar lava analogue."),
            "spectral_ground_truth": ("limited", "Spectral workflows can be rehearsed, but no site-specific ANALOG-X mineral classification is integrated."),
            "human_robotic_ops": ("limited", "Extreme-environment operations are relevant but access, safety and corrosive chemistry need specialist controls."),
        },
        "priority": "Use published geochemistry and safe, permitted field observations to distinguish hydrothermal salts from remote-sensing look-alikes.",
    },
    "atacama": {
        "tracks": {
            "dust_processes": ("limited", "Arid dust/surface monitoring is relevant; wind climatology alone does not quantify dust emission."),
            "evaporite_processes": ("moderate", "Salt-flat and hyperarid mapping methods can support selected Martian sedimentary questions."),
            "spectral_ground_truth": ("limited", "Useful setting for orbital-to-ground validation; no new site-specific spectral classification is asserted."),
            "human_robotic_ops": ("moderate", "Hyperarid remote field operations and instrument deployment are rehearsable."),
        },
        "priority": "Measure particle flux and grain-size thresholds alongside repeated surface imagery.",
    },
    "mcmurdo": {
        "tracks": {
            "cryosphere_remote_sensing": ("moderate", "Cold-desert field methods, ice/debris mapping and sensor endurance are useful process analogues."),
            "dust_processes": ("limited", "Dry-cold wind processes can be studied, but atmospheric density and particle transport differ."),
            "human_robotic_ops": ("moderate", "Logistics, cold-weather equipment and remote operations are rehearsable."),
        },
        "priority": "Pair surface energy-balance observations with validated ground temperature and sublimation measurements.",
    },
    "haughton": {
        "tracks": {
            "impact_geology": ("moderate", "Impact-structure mapping and polar field methods are relevant; terrestrial erosion and target geology differ."),
            "cryosphere_remote_sensing": ("limited", "Permafrost/polar context supports cold-region methods, not direct lunar ice equivalence."),
            "terrain_mobility": ("limited", "Regional terrain methods are transferable only where suitable high-resolution data exist."),
            "human_robotic_ops": ("moderate", "Remote polar field logistics and sampling workflows are useful rehearsals."),
        },
        "priority": "Tie impact breccia/ejecta mapping to high-resolution topography and laboratory sample characterization.",
    },
    "iceland": {
        "tracks": {
            "volcanic_morphology": ("moderate", "Basaltic lava morphology and volcanic mapping methods are useful; Earth weathering and atmosphere remain different."),
            "terrain_mobility": ("limited", "Lava roughness workflows can be tested, but local metre-scale data are required."),
            "human_robotic_ops": ("moderate", "Instrument deployment and robotic mapping over lava fields are rehearsable."),
        },
        "priority": "Compare mapped lava-flow textures and roughness with planetary image-derived units using matched spatial support.",
    },
    "death": {
        "tracks": {
            "evaporite_processes": ("limited", "Salt-flat/alluvial basin mapping can test sedimentary workflows; hydrologic history differs."),
            "dust_processes": ("limited", "Arid wind and surface monitoring methods are testable, but no dust flux measurement is integrated."),
            "terrain_mobility": ("limited", "Regional alluvial-fan terrain is useful for mapping methods, not rover safety."),
            "human_robotic_ops": ("moderate", "Arid field logistics and sampling protocols can be rehearsed."),
        },
        "priority": "Measure grain-size, crust strength and repeat surface change on a precisely mapped fan/salt-pan transect.",
    },
}

ALIASES = {
    "koh_i_sultan": "koh",
    "hispar_glacier": "hispar_glacier",
    "chagai_small_playas": "chagai_small_playas",
    "hamun_i_mashkel": "hamun_i_mashkel",
    "dallol": "dallol",
    "atacama": "atacama",
    "mcmurdo": "mcmurdo",
    "haughton": "haughton",
    "iceland": "iceland",
    "death": "death",
}

def read_json(path: Path, required=True):
    if not path.exists():
        if required:
            raise FileNotFoundError(path)
        return {}
    return json.loads(path.read_text(encoding="utf-8"))

def evidence_for(site_id, site, power, terrain, catalog):
    power_key = ALIASES.get(site_id, site_id)
    p = power.get("records", {}).get(power_key)
    terrain_key = site_id
    t = terrain.get("earth_sites", {}).get(terrain_key)
    status = site.get("evidence_status", {})
    return {
        "nasa_power": {
            "status": "processed" if p and not p.get("missing_parameters") else "missing_or_incomplete",
            "source": "NASA POWER Climatology API",
            "parameters": p.get("valid_parameters", []) if p else [],
            "fetched_at_utc": p.get("fetched_at_utc") if p else None,
            "limitation": "Gridded climatology; not a local weather station, surface temperature, dust flux or resource measurement.",
        },
        "terrain": {
            "status": t.get("status", "not_integrated") if t else "not_integrated",
            "source": t.get("source", {}).get("collection") if t else None,
            "metrics": t.get("terrain_metrics") if t else None,
            "analysis_support_m": t.get("source", {}).get("analysis_resolution_m") if t else None,
            "surface_grid_relative_m": t.get("surface_grid_relative_m") if t else None,
            "limitation": "Where available, ~925 m regional descriptors cannot establish rover-scale trafficability or landing safety.",
        },
        "sentinel2": {
            "status": "context_available" if status.get("sentinel2", "").startswith("Integrated") else "not_integrated",
            "statement": status.get("sentinel2", "No site-specific Sentinel-2 processing is recorded in the candidate dossier."),
            "limitation": "Spectral indices and RGB previews are screening context, not mineral identification or ground truth.",
        },
        "site_dossier": {
            "status": "documented" if site.get("source_references") else "limited",
            "discovery_tier": site.get("discovery_tier", "established_reference"),
            "candidate_status": site.get("candidate_status", "reference"),
            "sources": site.get("source_references", []),
        },
    }

def build():
    catalog = read_json(ROOT / "data/agents/candidate_catalog.json")
    power = read_json(ROOT / "data/power/index.json")
    terrain = read_json(ROOT / "data/terrain/terrain_comparison.json")
    moon = read_json(ROOT / "data/moon/shackleton_lola_80m.json", required=False)
    sites = catalog.get("candidate_sites", [])
    dossiers = []
    for site in sites:
        sid = site["id"]
        rule = SITE_RULES.get(sid, {"tracks": {}, "priority": "No site-specific experiment rule has been authored; evidence review required."})
        tests = []
        for track_id, (level, rationale) in rule["tracks"].items():
            track = TRACKS[track_id]
            tests.append({
                "track_id": track_id,
                "track": track["label"],
                "transferability": level,
                "why_this_site": rationale,
                "what_can_be_rehearsed": track["what_transfers"],
                "analogy_breaks": track["breaks"],
                "next_measurement": track["next_measurement"],
            })
        dossier = {
            "id": sid, "name": site["name"], "country": site.get("country"),
            "region": site.get("region"), "latitude": site.get("latitude"),
            "longitude": site.get("longitude"), "bbox_wgs84": site.get("study_bbox_wgs84"),
            "discovery_tier": site.get("discovery_tier", "established_reference"),
            "candidate_status": site.get("candidate_status", "reference"),
            "mission_targets": site.get("mission_targets", []),
            "environment_tags": site.get("environment_tags", []),
            "hypothesis": site.get("hypothesis", ""),
            "priority_experiment": rule["priority"],
            "tests": tests,
            "evidence": evidence_for(sid, site, power, terrain, catalog),
            "source_references": site.get("source_references", []),
            "site_non_transferable": site.get("non_transferable", []),
        }
        dossiers.append(dossier)

    target = {
        "moon": {
            "name": "Shackleton Rim / lunar south pole",
            "latitude": -89.7668, "longitude": 188.13,
            "source": "NASA LRO LOLA PDS GDR LDEM_80S_80M / LDEC_80S_80M",
            "terrain": moon.get("matched_coarse_support_approx_925m"),
            "terrain_surface": moon.get("surface_grid_relative_m"),
            "thermal": {
                "status": "Diviner PRP V2.0 site summary is available in the existing project, but ice-depth interpretation remains withheld pending QA.",
                "limitation": "Do not infer accessible ice or PSR status from terrain or temperature alone.",
            },
            "known_unreproducible": ["vacuum", "one-sixth Earth gravity", "radiation environment", "electrostatic lunar dust", "true permanently shadowed illumination regime"],
        },
        "mars": {
            "name": "Nili Patera / Syrtis Major, Mars",
            "latitude": 8.9, "longitude": 67.0,
            "source": "MGS MOLA MEGDR 64 pixels/degree",
            "terrain": terrain.get("planetary_target", {}).get("terrain_metrics"),
            "terrain_surface": terrain.get("planetary_target", {}).get("surface_grid_relative_m"),
            "coverage_percent": terrain.get("planetary_target", {}).get("window", {}).get("valid_observation_coverage_percent"),
            "known_unreproducible": ["thin CO2 atmosphere", "lower gravity", "radiation environment", "planetary dust electrostatics", "Martian regolith chemistry"],
        },
    }
    out = {
        "schema_version": "1.0",
        "engine": "ANALOG-X Analog Transferability & Failure Analysis (ATFA)",
        "generated_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "scientific_contract": {
            "unit_of_analysis": "A named field experiment or process, not whole-site resemblance.",
            "classification": "Rule-based qualitative transferability classes authored in science/build_transferability.py; not probabilities, not a universal similarity score, not NASA certification.",
            "classes": {
                "moderate": "A bounded Earth process or field method is useful to rehearse; planetary environmental transfer remains limited.",
                "limited": "Only a subset of the method/process transfers, or important site-specific evidence is missing.",
                "high": "Reserved for cases with strong direct evidence and independent validation; none is assigned automatically in this release.",
            },
            "global_limitations": ["Earth cannot reproduce lunar vacuum, reduced gravity or planetary radiation.", "Earth cannot reproduce Mars atmospheric pressure/composition or gravity.", "A coarse DEM or gridded climate product is not a landing, trafficability, ice-access or resource certification.", "Candidate leads require independent ground truth and domain-scientist review."],
        },
        "planetary_targets": target,
        "experiment_tracks": TRACKS,
        "site_count": len(dossiers),
        "sites": dossiers,
        "interpretation": "Use this report to choose a field experiment and identify its failure conditions. Do not rank entire planets or sites by a single percentage.",
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps({
        "output": str(OUT.relative_to(ROOT)),
        "site_count": len(dossiers),
        "test_cards": sum(len(s["tests"]) for s in dossiers),
        "sites_with_nasa_power": sum(s["evidence"]["nasa_power"]["status"] == "processed" for s in dossiers),
        "sites_with_processed_terrain": sum(s["evidence"]["terrain"]["status"] == "processed" for s in dossiers),
        "moon_reference_present": bool(target["moon"]["terrain"]),
        "mars_reference_present": bool(target["mars"]["terrain"]),
    }, indent=2))

if __name__ == "__main__":
    build()

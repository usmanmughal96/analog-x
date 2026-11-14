const MODEL = "@cf/openai/gpt-oss-20b";
const DEFAULT_DATA_BASE = "https://usmanmughal96.github.io/analog-x";
const MAX_PROMPT = 800;
const MAX_CANDIDATES = 5;

const TOOL_DEFINITIONS = [
  {
    name: "get_candidate_inventory",
    description: "Return the curated ANALOG-X Earth analog candidate inventory, mission tags, evidence status and primary references. Use this before recommending locations.",
    parameters: {
      type: "object",
      properties: {
        mission_target: { type: "string", enum: ["Moon", "Mars", "Both"] },
        discovery_tier: { type: "string", enum: ["all", "under_characterized_candidate", "established_reference"] }
      },
      required: ["mission_target"]
    }
  },
  {
    name: "compare_terrain_profiles",
    description: "Compare available Earth site terrain descriptors with the selected Moon/Mars reference. Returns measured median slope, P90 slope and P90 3x3 local relief, absolute differences, support and coverage. Never infer safety.",
    parameters: {
      type: "object",
      properties: {
        mission_target: { type: "string", enum: ["Moon", "Mars"] },
        candidate_ids: { type: "array", items: { type: "string" } }
      },
      required: ["mission_target"]
    }
  },
  {
    name: "derive_campaign_windows",
    description: "Read NASA POWER monthly climatology for an Earth candidate and derive three lowest-precipitation months with temperature, wind and solar context. These are climatological planning signals, not forecasts.",
    parameters: {
      type: "object",
      properties: { site_id: { type: "string" } },
      required: ["site_id"]
    }
  },
  {
    name: "scout_earth_coordinate",
    description: "Search a user-supplied Earth coordinate and radius against the NASA POWER Climatology API, Microsoft Planetary Computer Sentinel-2 L2A STAC archive and Copernicus DEM GLO-30 STAC catalogue. Returns measured climate context, scene discovery metadata and DEM tile availability. This is a screening scan, not mineral identification or field validation.",
    parameters: {
      type: "object",
      properties: {
        latitude: { type: "number", description: "WGS84 latitude, -89.9 to 89.9 degrees." },
        longitude: { type: "number", description: "WGS84 longitude, -180 to 180 degrees." },
        radius_km: { type: "number", description: "Study-window radius, 1 to 50 km." },
        mission_target: { type: "string", enum: ["Moon", "Mars", "Both"] }
      },
      required: ["latitude", "longitude", "radius_km"]
    }
  },
  {
    name: "read_surface_evidence",
    description: "Read Sentinel-2 L2A spectral-context statistics and source metadata for an Earth candidate. Indices are screening descriptors, not mineral identification or validated ice boundaries.",
    parameters: {
      type: "object",
      properties: { site_id: { type: "string" } },
      required: ["site_id"]
    }
  }
];

const POWER_FILE = {
  koh_i_sultan: "koh",
  koh: "koh",
  hispar_glacier: "hispar_glacier",
  chagai_small_playas: "chagai_small_playas",
  hamun_i_mashkel: "hamun_i_mashkel"
};

function jsonResponse(payload, status, headers = {}) {
  return new Response(JSON.stringify(payload), {
    status,
    headers: { "content-type": "application/json; charset=utf-8", ...headers }
  });
}

function allowedOrigin(origin, env) {
  const configured = (env.ALLOWED_ORIGINS || "https://usmanmughal96.github.io")
    .split(",").map(x => x.trim()).filter(Boolean);
  return configured.includes(origin) || origin === "http://localhost:5500" || origin === "http://127.0.0.1:5500";
}

function corsHeaders(origin, env) {
  const ok = allowedOrigin(origin, env);
  return {
    "access-control-allow-origin": ok ? origin : "null",
    "access-control-allow-methods": "GET, POST, OPTIONS",
    "access-control-allow-headers": "Content-Type",
    "access-control-max-age": "86400",
    "vary": "Origin"
  };
}

async function fetchJson(base, path) {
  const url = base.replace(/\/$/, "") + path;
  const response = await fetch(url, {
    headers: { "Accept": "application/json", "User-Agent": "ANALOG-X-Agent/1.0" },
    cf: { cacheTtl: 1800, cacheEverything: true }
  });
  if (!response.ok) throw new Error("Evidence fetch failed (" + response.status + "): " + path);
  return response.json();
}

function powerFileFor(siteId) {
  return POWER_FILE[siteId] || siteId;
}

async function loadContext(env, candidateIds) {
  const base = env.DATA_BASE_URL || DEFAULT_DATA_BASE;
  const [catalog, powerIndex, terrain, lunar, imagery] = await Promise.all([
    fetchJson(base, "/data/agents/candidate_catalog.json"),
    fetchJson(base, "/data/power/index.json"),
    fetchJson(base, "/data/terrain/terrain_comparison.json"),
    fetchJson(base, "/data/moon/shackleton_lola_80m.json"),
    fetchJson(base, "/data/pakistan/imagery/index.json")
  ]);
  const unique = [...new Set(candidateIds)].slice(0, MAX_CANDIDATES);
  const powers = {};
  await Promise.all(unique.map(async id => {
    const file = powerFileFor(id);
    try { powers[id] = await fetchJson(base, "/data/power/" + file + ".json"); }
    catch { powers[id] = null; }
  }));
  return { base, catalog, powerIndex, terrain, lunar, imagery, powers };
}

function candidateMap(context) {
  return Object.fromEntries((context.catalog.candidate_sites || []).map(x => [x.id, x]));
}

function targetTerrain(context, missionTarget) {
  if (missionTarget === "Moon") {
    const m = context.lunar?.matched_coarse_support_approx_925m;
    if (!m?.slope_deg || !m?.["3x3_local_relief_m_2775m_footprint"]) return null;
    return {
      name: context.lunar.site?.name || "Shackleton Rim / Moon",
      median_slope_deg: m.slope_deg.median,
      p90_slope_deg: m.slope_deg.p90,
      p90_local_relief_m: m["3x3_local_relief_m_2775m_footprint"].p90,
      support_m: m.pixel_size_m,
      coverage_percent: m.elevation_coverage_percent,
      return_support_percent: m.ldec_positive_return_support?.mean_native_pixel_fraction_per_coarse_cell_percent,
      source: "NASA LRO LOLA PDS GDR, LDEM_80S_80M; 80 m native grid aggregated to approximately 925 m"
    };
  }
  const m = context.terrain?.planetary_target?.terrain_metrics;
  if (!m?.slope_deg || !m?.["3x3_local_relief_m"]) return null;
  return {
    name: context.terrain.planetary_target.name || "Nili Patera / Mars",
    median_slope_deg: m.slope_deg.median,
    p90_slope_deg: m.slope_deg.p90,
    p90_local_relief_m: m["3x3_local_relief_m"].p90,
    support_m: context.terrain.planetary_target.pixel_spacing_m,
    coverage_percent: m.coverage?.valid_percent,
    complete_3x3_neighbourhoods: m.complete_3x3_neighbourhood_count,
    source: "MGS MOLA MEGDR 64 pixels/degree topography and observation counts"
  };
}

function terrainForSite(context, siteId) {
  const r = context.terrain?.earth_sites?.[siteId];
  if (!r || r.status !== "processed" || !r.terrain_metrics) return null;
  const m = r.terrain_metrics;
  return {
    name: r.site?.name || siteId,
    median_slope_deg: m.slope_deg?.median,
    p90_slope_deg: m.slope_deg?.p90,
    p90_local_relief_m: m["3x3_local_relief_m"]?.p90,
    support_m: 925,
    coverage_percent: m.coverage?.valid_percent,
    valid_cells: m.valid_cell_count,
    source: r.source?.collection || "Copernicus DEM GLO-30 DSM",
    caveat: "Earth DSM aggregated to approximately 925 m; not a rover-scale roughness or traversability assessment."
  };
}

function compareTerrain(context, missionTarget, candidateIds) {
  const target = targetTerrain(context, missionTarget);
  if (!target) return { status: "planetary terrain reference unavailable", mission_target: missionTarget };
  const sites = candidateIds.map(id => ({ id, profile: terrainForSite(context, id) })).filter(x => x.profile);
  return {
    status: "dimension-by-dimension regional descriptor comparison",
    mission_target: missionTarget,
    planetary_reference: target,
    earth_sites: sites.map(({id, profile}) => {
      const delta = {
        median_slope_deg: Math.abs(profile.median_slope_deg - target.median_slope_deg),
        p90_slope_deg: Math.abs(profile.p90_slope_deg - target.p90_slope_deg),
        p90_local_relief_m: Math.abs(profile.p90_local_relief_m - target.p90_local_relief_m)
      };
      const dims = Object.keys(delta);
      return { id, ...profile, absolute_differences: delta, closer_dimensions: dims.filter(k =>
        sites.every(other => other.id === id || !other.profile[k] || delta[k] <= Math.abs(other.profile[k] - target[k]))
      ) };
    }),
    limitations: [
      "The Nili Patera MOLA window has only 50.53% observed cells and 87 complete 3x3 neighborhoods.",
      "Lunar LOLA is interpolated; its return-count grid reports measurement support, not illumination or ice.",
      "Earth Copernicus DSM, Mars MOLA and Moon LOLA have different physical contexts even when aggregated to similar nominal support.",
      "No result here establishes geology, surface strength, rover safety, landing suitability, or resource prospectivity."
    ]
  };
}

function campaignFor(context, siteId) {
  const p = context.powers[siteId];
  if (!p?.monthly?.length) return { site_id: siteId, status: "NASA POWER snapshot unavailable" };
  const monthly = p.monthly.filter(x => Number.isFinite(x.precip));
  const driest = [...monthly].sort((a,b) => a.precip - b.precip).slice(0,3).map(x => ({
    month: x.month, precipitation_mm_day: x.precip, mean_air_temperature_c: x.temp,
    wind_10m_ms: x.wind, solar_kwh_m2_day: x.solar
  }));
  const source = p.source || {};
  return {
    site_id: siteId, site: p.site, source: "NASA POWER Climatology API",
    fetched_at_utc: source.fetched_at_utc || null,
    variables: ["T2M", "PRECTOTCORR", "WS10M", "ALLSKY_SFC_SW_DWN"],
    driest_climatological_months: driest,
    interpretation: "Long-term gridded climatology only. Not a weather forecast, access guarantee, station observation, surface temperature, dust flux or water resource measurement."
  };
}

function surfaceFor(context, siteId) {
  const profile = context.imagery?.sites?.[siteId] || null;
  const candidate = candidateMap(context)[siteId] || null;
  if (!profile) return {
    site_id: siteId, status: "no processed Sentinel-2 spectral profile in the current release",
    candidate_context: candidate?.hypothesis || null,
    caveat: "Do not infer mineralogy or surface chemistry from a missing profile."
  };
  return {
    site_id: siteId,
    scene: profile.scene,
    processing: profile.processing,
    indices: Object.fromEntries(Object.entries(profile.indices || {}).map(([k,v]) => [k, {
      median: v.median, p02: v.p02, p98: v.p98, valid_pixels: v.valid_pixels
    }])),
    interpretation_note: profile.interpretation_note,
    caveat: "Spectral indices are screening descriptors only; no mineral identification, calibrated abundance, brine chemistry or validated glacier outline."
  };
}

function inventoryFor(context, missionTarget, tier = "all") {
  const candidates = context.catalog.candidate_sites || [];
  return candidates.filter(x =>
    (missionTarget === "Both" || (x.mission_targets || []).includes(missionTarget)) &&
    (tier === "all" || x.discovery_tier === tier)
  ).map(x => ({
    id: x.id, name: x.name, country: x.country, region: x.region,
    coordinates: [x.latitude, x.longitude], discovery_tier: x.discovery_tier,
    candidate_status: x.candidate_status, environment_tags: x.environment_tags,
    rehearsal_tasks: x.rehearsal_tasks, hypothesis: x.hypothesis,
    evidence_status: x.evidence_status, sources: x.source_references || [],
    limitations: x.non_transferable || []
  }));
}

function specialistReports(context, missionTarget, candidateIds) {
  const chosen = candidateIds.length ? candidateIds : ["chagai_small_playas","hamun_i_mashkel","koh_i_sultan","hispar_glacier"];
  return [
    {
      agent: "TERRAIN MORPHOLOGY ANALYST",
      status: "local deterministic analysis",
      result: compareTerrain(context, missionTarget, chosen)
    },
    {
      agent: "CLIMATE & CAMPAIGN PLANNER",
      status: "local deterministic analysis",
      result: chosen.map(id => campaignFor(context, id))
    },
    {
      agent: "SURFACE / PROCESS ANALYST",
      status: "local deterministic analysis",
      result: chosen.map(id => surfaceFor(context, id))
    },
    {
      agent: "EVIDENCE INTEGRITY OFFICER",
      status: "local deterministic analysis",
      result: chosen.map(id => {
        const candidate = candidateMap(context)[id];
        const power = context.powers[id];
        const spectral = context.imagery?.sites?.[id];
        const terrain = context.terrain?.earth_sites?.[id];
        return {
          site_id: id, name: candidate?.name || id,
          evidence_available: {
            candidate_record: !!candidate, nasa_power: !!power,
            sentinel2_spectral_profile: !!spectral,
            copernicus_terrain: terrain?.status === "processed",
            source_references: !!candidate?.source_references?.length
          },
          decision_state: candidate?.candidate_status || "unregistered",
          outstanding: [
            ...(!power ? ["NASA POWER climate snapshot"] : []),
            ...(!spectral ? ["Sentinel-2 spectral-context profile"] : []),
            ...(terrain?.status !== "processed" ? ["Matched-scale Copernicus terrain profile"] : []),
            "Site-specific field validation and specialist review"
          ]
        };
      })
    }
  ];
}


const PLANETARY_COMPUTER_STAC = "https://planetarycomputer.microsoft.com/api/stac/v1/search";
const NASA_POWER_CLIMATOLOGY = "https://power.larc.nasa.gov/api/temporal/climatology/point";

function validateScoutInput(input) {
  const latitude = Number(input?.latitude);
  const longitude = Number(input?.longitude);
  const radiusKm = Number(input?.radius_km ?? 10);
  if (!Number.isFinite(latitude) || latitude < -89.9 || latitude > 89.9) {
    throw new Error("Latitude must be between -89.9 and 89.9 degrees.");
  }
  if (!Number.isFinite(longitude) || longitude < -180 || longitude > 180) {
    throw new Error("Longitude must be between -180 and 180 degrees.");
  }
  if (!Number.isFinite(radiusKm) || radiusKm < 1 || radiusKm > 50) {
    throw new Error("Study radius must be between 1 and 50 km.");
  }
  return { latitude, longitude, radius_km: radiusKm };
}

function scoutBbox({ latitude, longitude, radius_km }) {
  const latDelta = radius_km / 110.574;
  const cosLat = Math.max(0.05, Math.cos(latitude * Math.PI / 180));
  const lonDelta = Math.min(180, radius_km / (111.320 * cosLat));
  const south = Math.max(-89.9, latitude - latDelta);
  const north = Math.min(89.9, latitude + latDelta);
  const west = Math.max(-180, longitude - lonDelta);
  const east = Math.min(180, longitude + lonDelta);
  return [west, south, east, north];
}

async function fetchPowerClimatology(latitude, longitude) {
  const url = new URL(NASA_POWER_CLIMATOLOGY);
  url.searchParams.set("parameters", "T2M,T2M_MAX,T2M_MIN,RH2M,WS10M,PRECTOTCORR,ALLSKY_SFC_SW_DWN");
  url.searchParams.set("community", "RE");
  url.searchParams.set("longitude", longitude.toFixed(5));
  url.searchParams.set("latitude", latitude.toFixed(5));
  url.searchParams.set("format", "JSON");
  const response = await fetch(url.toString(), { headers: { "Accept": "application/json" } });
  if (!response.ok) throw new Error("NASA POWER returned HTTP " + response.status);
  const payload = await response.json();
  const block = payload?.properties?.parameter;
  if (!block || typeof block !== "object" || !block.T2M) {
    throw new Error("NASA POWER returned no usable climatology parameter block.");
  }
  const months = ["JAN","FEB","MAR","APR","MAY","JUN","JUL","AUG","SEP","OCT","NOV","DEC"];
  const monthly = months.map(month => ({
    month,
    temperature_c: Number.isFinite(block.T2M?.[month]) ? block.T2M[month] : null,
    max_temperature_c: Number.isFinite(block.T2M_MAX?.[month]) ? block.T2M_MAX[month] : null,
    min_temperature_c: Number.isFinite(block.T2M_MIN?.[month]) ? block.T2M_MIN[month] : null,
    relative_humidity_percent: Number.isFinite(block.RH2M?.[month]) ? block.RH2M[month] : null,
    wind_10m_ms: Number.isFinite(block.WS10M?.[month]) ? block.WS10M[month] : null,
    precipitation_mm_day: Number.isFinite(block.PRECTOTCORR?.[month]) ? block.PRECTOTCORR[month] : null,
    solar_kwh_m2_day: Number.isFinite(block.ALLSKY_SFC_SW_DWN?.[month]) ? block.ALLSKY_SFC_SW_DWN[month] : null
  }));
  const driest = monthly.filter(x => Number.isFinite(x.precipitation_mm_day))
    .slice().sort((a,b) => a.precipitation_mm_day - b.precipitation_mm_day).slice(0,3);
  const annual = key => Number.isFinite(block[key]?.ANN) ? block[key].ANN : null;
  return {
    provider: "NASA POWER Climatology API",
    endpoint: url.toString(),
    community: "RE",
    fetched_at_utc: new Date().toISOString(),
    annual: {
      mean_air_temperature_c: annual("T2M"),
      mean_relative_humidity_percent: annual("RH2M"),
      mean_wind_10m_ms: annual("WS10M"),
      mean_precipitation_mm_day: annual("PRECTOTCORR"),
      mean_all_sky_solar_kwh_m2_day: annual("ALLSKY_SFC_SW_DWN")
    },
    driest_climatological_months: driest,
    monthly,
    interpretation: "Long-term gridded climatology; not a station record, forecast, rock/surface temperature, dust flux or accessible water/ice measurement."
  };
}

async function postStacSearch(collection, bbox, datetime) {
  const response = await fetch(PLANETARY_COMPUTER_STAC, {
    method: "POST",
    headers: { "Content-Type": "application/json", "Accept": "application/geo+json, application/json" },
    body: JSON.stringify({
      collections: [collection],
      bbox,
      ...(datetime ? { datetime } : {}),
      limit: 50
    })
  });
  if (!response.ok) throw new Error("Planetary Computer STAC " + collection + " returned HTTP " + response.status);
  return response.json();
}

async function scoutEarthCoordinate(input) {
  const point = validateScoutInput(input);
  const bbox = scoutBbox(point);
  const end = new Date();
  const start = new Date(end.getTime() - 24 * 30 * 24 * 60 * 60 * 1000);
  const datetime = start.toISOString() + "/" + end.toISOString();
  const results = await Promise.allSettled([
    fetchPowerClimatology(point.latitude, point.longitude),
    postStacSearch("sentinel-2-l2a", bbox, datetime),
    postStacSearch("cop-dem-glo-30", bbox, null)
  ]);
  const [powerResult, sentinelResult, demResult] = results;
  const sentinel = sentinelResult.status === "fulfilled" ? sentinelResult.value : null;
  const dem = demResult.status === "fulfilled" ? demResult.value : null;
  const features = Array.isArray(sentinel?.features) ? sentinel.features : [];
  const scenes = features.map(item => {
    const props = item.properties || {};
    return {
      id: item.id,
      datetime: props.datetime || null,
      platform: props.platform || props["constellation"] || null,
      cloud_cover_percent: Number.isFinite(props["eo:cloud_cover"]) ? props["eo:cloud_cover"] : null,
      mgrs_tile: props["s2:mgrs_tile"] || props["mgrs:utm_zone"] || null,
      item_url: item.links?.find(link => link.rel === "self")?.href || null,
      collection: item.collection || "sentinel-2-l2a"
    };
  });
  const best = scenes.slice().sort((a,b) => {
    const av = Number.isFinite(a.cloud_cover_percent) ? a.cloud_cover_percent : 999;
    const bv = Number.isFinite(b.cloud_cover_percent) ? b.cloud_cover_percent : 999;
    return av - bv || String(b.datetime || "").localeCompare(String(a.datetime || ""));
  }).slice(0,5);
  const demFeatures = Array.isArray(dem?.features) ? dem.features : [];
  return {
    status: "screening scan complete",
    coordinate: { latitude: point.latitude, longitude: point.longitude, crs: "WGS84" },
    study_window: { radius_km: point.radius_km, bbox_wgs84: bbox, construction: "Approximate rectangular search window from the user-supplied radius; not a site boundary." },
    generated_at_utc: new Date().toISOString(),
    evidence: {
      nasa_power: powerResult.status === "fulfilled"
        ? { status: "integrated response", data: powerResult.value }
        : { status: "unavailable", error: String(powerResult.reason?.message || powerResult.reason) },
      sentinel_2_l2a: sentinel
        ? {
            status: "catalogue metadata discovered",
            collection: "sentinel-2-l2a",
            time_window_utc: datetime,
            returned_items: features.length,
            number_matched: sentinel.numberMatched ?? sentinel.context?.matched ?? null,
            best_scene_candidates: best,
            source: "Microsoft Planetary Computer public STAC API",
            limits: "Catalogue metadata only. A scene cloud percentage is not an AOI cloud mask. No mineral classification, validated ice boundary or spectral change analysis is performed by this scout."
          }
        : { status: "unavailable", error: String(sentinelResult.reason?.message || sentinelResult.reason) },
      copernicus_dem: dem
        ? {
            status: "catalogue metadata discovered",
            collection: "cop-dem-glo-30",
            returned_items: demFeatures.length,
            number_matched: dem.numberMatched ?? dem.context?.matched ?? null,
            tiles: demFeatures.slice(0,12).map(item => ({
              id: item.id,
              bbox: item.bbox || null,
              gsd_m: item.properties?.gsd ?? null,
              epsg: item.properties?.["proj:epsg"] ?? null
            })),
            source: "Microsoft Planetary Computer / Copernicus DEM GLO-30",
            limits: "DEM catalogue discovery only. No raster has been downloaded, mosaicked or analysed for this coordinate by the scout."
          }
        : { status: "unavailable", error: String(demResult.reason?.message || demResult.reason) }
    },
    next_measurements: [
      "Inspect the best Sentinel-2 scenes with AOI-specific cloud/shadow masks and compare multiple acquisition dates.",
      "Retrieve and process Copernicus DEM or a higher-resolution local DEM; report support, nodata coverage and terrain uncertainty.",
      "Obtain primary-source geology and material evidence before assigning mineralogy or resource prospectivity.",
      "Plan field validation, instrument checks, access permissions and local safety review."
    ],
    decision_boundary: "This is a coordinate-level open-data discovery scan, not an analog designation, similarity probability, field-access guarantee or mission safety assessment."
  };
}

async function executeTool(name, args, context, missionTarget, candidateIds, env) {
  switch (name) {
    case "get_candidate_inventory":
      return inventoryFor(context, args.mission_target || missionTarget, args.discovery_tier || "all");
    case "compare_terrain_profiles":
      return compareTerrain(context, args.mission_target || missionTarget, args.candidate_ids || candidateIds);
    case "derive_campaign_windows":
      return campaignFor(context, args.site_id);
    case "read_surface_evidence":
      return surfaceFor(context, args.site_id);
    case "scout_earth_coordinate":
      return scoutEarthCoordinate(args);
    default:
      throw new Error("Tool not allow-listed: " + name);
  }
}

function extractToolCalls(result) {
  return result?.tool_calls ||
    result?.response?.tool_calls ||
    result?.choices?.[0]?.message?.tool_calls ||
    [];
}

function extractText(result) {
  const value = result?.response ?? result?.result?.response ??
    result?.choices?.[0]?.message?.content ?? result?.output_text ?? "";
  return typeof value === "string" ? value : JSON.stringify(value);
}

function parseToolArgs(call) {
  const value = call?.arguments ?? call?.function?.arguments ?? {};
  if (typeof value === "string") {
    try { return JSON.parse(value); } catch { return {}; }
  }
  return value && typeof value === "object" ? value : {};
}

async function runMissionAgent(env, body, context, candidateIds, agents) {
  const system = [
    "You are ANALOG-X Mission Director, a careful planetary field-science decision agent.",
    "The user is asking: " + body.question,
    "Mission target: " + body.mission_target + ". Experiment: " + body.objective + ".",
    "You have four specialist reports (terrain morphology, climate campaign, surface/process, evidence integrity).",
    "You may call the provided tools to inspect raw evidence. Use tools before reaching a recommendation.",
    "If the user supplies a new Earth coordinate, call scout_earth_coordinate before assessing it. Never invent coordinates; request them only when the task lacks a supplied location.",
    "Only use numerical evidence returned by tools or specialist reports. Preserve units, dates, spatial support and coverage.",
    "Separate measurement, inference and hypothesis. Never invent a source, measurement or site property.",
    "Do not call Earth/Moon/Mars locations identical. Do not claim a candidate is newly discovered or validated unless the evidence explicitly supports it.",
    "State the strongest candidate for the chosen experiment, runner-up if appropriate, evidence for/against, data gaps, and the next field measurement.",
    "Do not infer mineralogy from Sentinel indices, brine from reflectance, ice accessibility from NDSI, dust flux from wind speed, or safety from terrain statistics.",
    "Return concise Markdown with sections: DECISION, WHY THE EVIDENCE SUPPORTS IT, WHAT BREAKS THE ANALOGY, CONFIDENCE / GAPS, NEXT ACTIONS."
  ].join("\n");
  const compactAgents = agents.map(x => ({ agent: x.agent, result: x.result }));
  const messages = [
    { role: "system", content: system },
    { role: "user", content: JSON.stringify({
      question: body.question, mission_target: body.mission_target,
      objective: body.objective, selected_candidates: candidateIds,
      specialist_evidence: compactAgents
    }) }
  ];
  let finalText = "";
  const trace = [];
  for (let round = 0; round < 3; round++) {
    const response = await env.AI.run(MODEL, {
      messages, tools: TOOL_DEFINITIONS, max_tokens: round === 2 ? 950 : 450,
      temperature: 0.15
    });
    const calls = extractToolCalls(response);
    if (!calls.length) { finalText = extractText(response); break; }
    messages.push({ role: "assistant", content: JSON.stringify(calls) });
    for (const call of calls.slice(0, 3)) {
      const name = call.name || call.function?.name;
      const args = parseToolArgs(call);
      const result = await executeTool(name, args, context, body.mission_target, candidateIds, env);
      trace.push({ tool: name, arguments: args, result });
      messages.push({ role: "tool", content: JSON.stringify({ name, result }) });
    }
  }
  if (!finalText) {
    const response = await env.AI.run(MODEL, { messages, max_tokens: 950, temperature: 0.15 });
    finalText = extractText(response);
  }
  return { analysis: finalText, tool_trace: trace };
}

export default {
  async fetch(request, env) {
    const origin = request.headers.get("Origin") || "";
    const cors = corsHeaders(origin, env);
    if (request.method === "OPTIONS") {
      if (!allowedOrigin(origin, env)) return new Response(null, { status: 403 });
      return new Response(null, { status: 204, headers: cors });
    }
    const url = new URL(request.url);
    if (!allowedOrigin(origin, env)) return jsonResponse({ error: "Origin not allowed" }, 403, cors);
    if (request.method === "GET" && url.pathname === "/health") {
      return jsonResponse({
        ok: !!env.AI, service: "ANALOG-X Agent API", model: MODEL,
        free_tier_note: "Cloudflare Workers AI Free allocation is limited to 10,000 Neurons/day; requests may be throttled or fail when the account quota is exhausted.",
        data_base_url: env.DATA_BASE_URL || DEFAULT_DATA_BASE,
        ai_enabled: !!env.AI,
        scout_enabled: true,
        capabilities: ["global coordinate scout", "NASA POWER live climatology", "Sentinel-2 L2A STAC discovery", "Copernicus DEM STAC discovery", "multi-agent evidence analysis", "function calling", "candidate inventory", "Earth-Moon-Mars terrain comparison"],
        version: "1.1.0"
      }, 200, cors);
    }
    if (request.method !== "POST" || !["/analyze", "/scout"].includes(url.pathname)) {
      return jsonResponse({ error: "Use GET /health, POST /scout or POST /analyze" }, 404, cors);
    }
    const clientIp = request.headers.get("CF-Connecting-IP") || "anonymous";
    if (env.MISSION_RATE_LIMIT) {
      const limit = await env.MISSION_RATE_LIMIT.limit({ key: clientIp, delta: 1 });
      if (!limit.success) return jsonResponse({ error: "Rate limit reached. Please retry in a minute." }, 429, cors);
    }
    const length = Number(request.headers.get("Content-Length") || 0);
    if (length > 12000) return jsonResponse({ error: "Request is too large." }, 413, cors);
    let body;
    try { body = await request.json(); }
    catch { return jsonResponse({ error: "Request body must be valid JSON." }, 400, cors); }
    if (url.pathname === "/scout") {
      try {
        const scout = await scoutEarthCoordinate(body);
        return jsonResponse({ ok: true, scout }, 200, cors);
      } catch (error) {
        return jsonResponse({ ok: false, error: String(error?.message || error) }, 400, cors);
      }
    }
    const question = String(body.question || "").trim();
    const missionTarget = ["Moon","Mars","Both"].includes(body.mission_target) ? body.mission_target : "Mars";
    const objective = String(body.objective || "mission-specific field rehearsal").slice(0, 180);
    if (question.length < 8 || question.length > MAX_PROMPT) {
      return jsonResponse({ error: "Question must contain 8–800 characters." }, 400, cors);
    }
    if (!env.AI) return jsonResponse({ ok: false, error: "Workers AI binding is not enabled. The /scout data endpoint is available independently; connect AI in the Cloudflare Worker to run the Mission Director." }, 503, cors);
    try {
      const catalog = await fetchJson(env.DATA_BASE_URL || DEFAULT_DATA_BASE, "/data/agents/candidate_catalog.json");
      const validIds = new Set((catalog.candidate_sites || []).map(x => x.id));
      const requested = Array.isArray(body.candidate_ids) ? body.candidate_ids : [];
      const candidateIds = requested.filter(x => typeof x === "string" && validIds.has(x)).slice(0, MAX_CANDIDATES);
      const selection = candidateIds.length ? candidateIds : ["chagai_small_playas","hamun_i_mashkel","koh_i_sultan","hispar_glacier"];
      const context = await loadContext(env, selection);
      const agents = specialistReports(context, missionTarget, selection);
      const modelResult = await runMissionAgent(env, {
        question, mission_target: missionTarget, objective
      }, context, selection, agents);
      return jsonResponse({
        ok: true, mode: "cloudflare-workers-ai",
        model: MODEL, mission_target: missionTarget, objective,
        question, candidates: selection, agents, ...modelResult,
        data_generated_at_utc: {
          power: context.powerIndex.generated_at_utc,
          terrain: context.terrain.generated_at_utc,
          imagery: context.imagery.generated_at_utc
        },
        disclaimer: "Decision support for research planning only. Not a landing-site certification, safety plan, mineral identification or validated analog designation."
      }, 200, cors);
    } catch (error) {
      return jsonResponse({
        ok: false, error: "Agent execution failed. Evidence remains available in local mode.",
        detail: String(error?.message || error).slice(0, 500),
        model: MODEL
      }, 503, cors);
    }
  }
};

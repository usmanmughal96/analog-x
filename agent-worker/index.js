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

async function executeTool(name, args, context, missionTarget, candidateIds) {
  switch (name) {
    case "get_candidate_inventory":
      return inventoryFor(context, args.mission_target || missionTarget, args.discovery_tier || "all");
    case "compare_terrain_profiles":
      return compareTerrain(context, args.mission_target || missionTarget, args.candidate_ids || candidateIds);
    case "derive_campaign_windows":
      return campaignFor(context, args.site_id);
    case "read_surface_evidence":
      return surfaceFor(context, args.site_id);
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
      const result = await executeTool(name, args, context, body.mission_target, candidateIds);
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
        capabilities: ["multi-agent evidence analysis", "function calling", "NASA POWER campaign windows", "Sentinel-2 spectral context", "Earth-Moon-Mars terrain comparison"],
        version: "1.0.0"
      }, 200, cors);
    }
    if (request.method !== "POST" || url.pathname !== "/analyze") {
      return jsonResponse({ error: "Use GET /health or POST /analyze" }, 404, cors);
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
    const question = String(body.question || "").trim();
    const missionTarget = ["Moon","Mars","Both"].includes(body.mission_target) ? body.mission_target : "Mars";
    const objective = String(body.objective || "mission-specific field rehearsal").slice(0, 180);
    if (question.length < 8 || question.length > MAX_PROMPT) {
      return jsonResponse({ error: "Question must contain 8–800 characters." }, 400, cors);
    }
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

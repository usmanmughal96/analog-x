import assert from "node:assert/strict";
import { readFileSync } from "node:fs";

const read = (path) => readFileSync(path, "utf8");
const html = read("index.html");
const appJs = read("assets/analogx-labs.js");
const workerJs = read("agent-worker/index.js");
const catalog = JSON.parse(read("data/agents/candidate_catalog.json"));
const power = JSON.parse(read("data/power/index.json"));
const terrain = JSON.parse(read("data/terrain/terrain_comparison.json"));
const lunar = JSON.parse(read("data/moon/shackleton_lola_80m.json"));
const diviner = JSON.parse(read("data/moon/diviner_prp_diagnostic/report.json"));
const lunarPolar = JSON.parse(read("data/moon/shackleton_polar_evidence.json"));

const ids = [...html.matchAll(/\bid=["']([^"']+)["']/g)].map((m) => m[1]);
const duplicates = ids.filter((id, i) => ids.indexOf(id) !== i);
assert.equal(duplicates.length, 0, "HTML contains duplicate element IDs");

for (const id of [
  "discoveryLab", "coordinateScout", "agentBay", "axAgentCandidates",
  "axAgentRunLocal", "axAgentRunCloud", "axGameXp", "axGameProgressBar",
  "axScoutRun", "axGameToDirector", "missionLab"
]) assert(ids.includes(id), `Missing required UI element: ${id}`);

assert(html.includes("./assets/analogx-labs.js"), "Main app does not load its agent/atlas code");
assert(html.includes("./assets/analogx-labs.css"), "Main app does not load the interactive UI styles");
assert(appJs.includes("function relevanceProfile"), "Mission-specific task profiles missing");
assert(appJs.includes("function localAnalysisWithTerrain"), "Offline decision engine missing");
assert(appJs.includes("function syncCandidateSelection"), "Candidate selectors are not wired together");
assert(appJs.includes("function formatAgentMarkdown"), "Safe Mission Director Markdown renderer missing");
assert(appJs.includes("function saveGameProgress"), "Field School progress persistence missing");
assert(appJs.includes("MISSION 04 / TERRAIN DATA QUALITY"), "Terrain quality training challenge missing");
assert(appJs.includes('runLocal();'), "Field School handoff to the local Mission Director missing");


const sites = catalog.candidate_sites || [];
assert(sites.length >= 10, "Expected the ten curated Earth candidate/reference seeds");
const siteIds = new Set(sites.map((site) => site.id));
assert.equal(siteIds.size, sites.length, "Candidate IDs must be unique");
for (const site of sites) {
  assert(site.id && site.name, "Every candidate needs an ID and name");
  assert(Number.isFinite(site.latitude) && Number.isFinite(site.longitude), `Missing WGS84 coordinate: ${site.id}`);
  assert(Array.isArray(site.mission_targets), `Missing mission target tags: ${site.id}`);
  assert(Array.isArray(site.environment_tags), `Missing environment tags: ${site.id}`);
  assert(Array.isArray(site.rehearsal_tasks), `Missing documented rehearsal tasks: ${site.id}`);
  assert(Array.isArray(site.source_references) && site.source_references.length > 0, `Candidate lacks a source reference: ${site.id}`);
}

assert.equal(power.record_count, Object.keys(power.records || {}).length, "NASA POWER index count does not match records");
assert(power.record_count >= sites.length, "NASA POWER does not cover all catalogue seeds");
const powerAliases = { koh_i_sultan: "koh" };
for (const id of siteIds) {
  const powerId = powerAliases[id] || id;
  assert(power.records[powerId], `NASA POWER record missing for ${id} (expected key: ${powerId})`);
}
assert(appJs.includes('koh_i_sultan:"koh"'), "Legacy Koh-i-Sultan POWER alias must remain explicit in the app");

const pakistanSites = ["koh_i_sultan", "hispar_glacier", "chagai_small_playas", "hamun_i_mashkel"];
for (const id of pakistanSites) {
  assert.equal(terrain.earth_sites?.[id]?.status, "processed", `Terrain profile is not processed: ${id}`);
  assert.equal(terrain.earth_sites[id].terrain_metrics?.coverage?.valid_percent, 100, `Unexpected Earth DEM valid-cell coverage: ${id}`);
}
assert(terrain.planetary_target?.terrain_metrics?.coverage?.valid_percent < 100, "MOLA coverage caveat unexpectedly disappeared");
assert(lunar.matched_coarse_support_approx_925m?.slope_deg, "Matched-support lunar LOLA terrain metrics missing");
assert(lunar.matched_coarse_support_approx_925m?.ldec_positive_return_support, "LOLA return-support summary missing");

assert(workerJs.includes('@cf/openai/gpt-oss-20b'), "Open-weight Mission Director model missing");
assert(workerJs.includes('missionTarget === "Both"'), "Worker does not return separate Moon/Mars comparisons");
assert(workerJs.includes('evidence_mode'), "Worker does not accept strict/exploratory evidence policy");
assert(workerJs.includes('function executeTool'), "Allow-listed tool executor missing");
assert(workerJs.includes("function parseLeakedToolCalls"), "gpt-oss raw JSON tool-call recovery missing");
assert(workerJs.includes("ALLOWED_TOOL_NAMES.has(name)"), "Tool-call recovery is not allow-list constrained");
for (const toolName of ["get_candidate_inventory", "compare_terrain_profiles", "derive_campaign_windows", "scout_earth_coordinate", "read_surface_evidence"]) {
  assert(workerJs.includes(`name: "${toolName}"`), `Agent tool missing: ${toolName}`);
}
const southPrp = diviner.pds3_alternative?.["DLRE_PRP_SOUTH.TAB"];
assert.equal(southPrp?.range_status, 206, "Diviner south-polar table range probe missing");
assert.equal(String(southPrp?.content_length), "604800210", "Unexpected Diviner south-polar table size");
assert(read("docs/DECISION_ENGINE.md").includes("Strict evidence policy"), "Decision method documentation missing");



// Global discovery, evidence-registry and reproducibility release contracts.

assert(read("scripts/enrich_global_landcover.py").includes("io-lulc-annual-v02"), "Global land-cover enrichment source missing");
assert(read("scripts/enrich_global_power.py").includes("temporal/climatology/point"), "Global NASA POWER enrichment missing");
assert(read(".github/workflows/global-environment-enrichment.yml").includes("enrich_global_power.py"), "NASA POWER enrichment is not chained to global shortlist workflow");

assert(read(".github/workflows/global-environment-enrichment.yml").includes("workflow_run"), "Global land-cover enrichment must be chained to the global scan release");
assert(read("docs/COMPETITIVE_CAPABILITY_RESPONSE.md").includes("TwinWorlds"), "Competitor capability mapping missing");

const pdsSearchScript = read("scripts/fetch_pds_search.py");
assert(pdsSearchScript.includes("/api/search/1/products"), "PDS discovery must use the documented all-products endpoint");
assert(!pdsSearchScript.includes("/classes/observational"), "PDS discovery must not use the invalid singular observational class endpoint");
assert(pdsSearchScript.includes("product_class eq") && pdsSearchScript.includes("ref_lid_target eq") && pdsSearchScript.includes("ref_lid_instrument eq"), "PDS queries must retain target, instrument and product-class constraints");
assert(pdsSearchScript.includes("def extract_products") && pdsSearchScript.includes('payload.get("data")'), "PDS discovery must parse the documented flat data response");
assert(read("tests/test_pds_search_api.py").includes("test_accepts_flat_observational_product"), "PDS flat-response regression tests are missing");

const archiveDiscoveryScript = read("scripts/fetch_planetary_archive_discovery.py");
assert(archiveDiscoveryScript.includes("https://oderest.rsl.wustl.edu/live2/"), "ODE REST fallback endpoint is missing");
assert(archiveDiscoveryScript.includes('"query": "iipt"') && archiveDiscoveryScript.includes('"query": "product"'), "ODE discovery must dynamically inspect valid instrument/product-type sets before product queries");
assert(archiveDiscoveryScript.includes("MRO-M-HIRISE-5-DTM-V1.0") && archiveDiscoveryScript.includes("NILI[\"bbox_wsen\"]"), "HiRISE DTM lookup must be scoped to the known Nili Patera study window");
assert(archiveDiscoveryScript.includes("mro_hirise_uncontrolled_observations") && archiveDiscoveryScript.includes("not a stereo DTM"), "USGS HiRISE RDR metadata must remain distinct from DTM evidence");
assert(read("tests/test_planetary_archive_discovery.py").includes("test_matching_requires_exact_host_instrument_and_dataset"), "ODE IIPT selection regression tests are missing");

assert(html.includes('href="./field-validation.html"'), "Main portal is missing Field Validation Kit CTA");
assert(read("field-validation.html").includes("actual observations collected"), "Field capture must explicitly distinguish field observations from desk research");
assert(read("service-worker.js").includes('"./field-validation.html"'), "Offline application cache must include Field Validation Kit");

const globalPage = read("global-discovery.html");
const globalBuilder = read("scripts/build_global_discovery.py");
const globalMerger = read("scripts/merge_global_discovery.py");
const sourceRegistry = JSON.parse(read("data/source_registry.json"));
const fieldLedger = JSON.parse(read("data/field_validation/observations.json"));
const fieldProtocol = JSON.parse(read("science/field_validation_protocol.json"));
assert(html.includes('href="./global-discovery.html"'), "Main portal is missing the Global Discovery Engine CTA");
assert(html.includes('class="global-featured"'), "Main portal is missing persistent Global Discovery Engine link");
assert(globalPage.includes("data/global_discovery/global_discovery.json"), "Global discovery page does not load the merged global dataset");
assert(globalPage.includes("complete" ) && globalPage.includes("partial"), "Global discovery page must distinguish complete from partial scans");
assert(globalBuilder.includes("Copernicus DEM GLO-90"), "Global discovery builder must declare GLO-90 source");
assert(globalBuilder.includes("--shard") && globalMerger.includes("EXPECTED_SHARDS = 24") && globalMerger.includes("Expected exactly") && globalMerger.includes("Shard set is incomplete"), "Global discovery shard/merge release contract missing");
assert(read(".github/workflows/global-discovery.yml").includes("matrix:"), "Global discovery workflow matrix missing");
assert(read("docs/COMPETITIVE_CAPABILITY_RESPONSE.md").includes("Earth Analog Explorer"), "Capability benchmark note missing");
assert(fieldProtocol.stations && fieldProtocol.validation_states.includes("independently_reviewed"), "Field observation protocol incomplete");
const fieldValidationHtml = read("field-validation.html");
assert(fieldValidationHtml.includes('type="datetime-local"') && fieldValidationHtml.includes('date_utc:toUtcIso(val("date"))') && fieldValidationHtml.includes('measurement_time_utc:toUtcIso(val("date"))'), "Field kit must capture station and measurement UTC timestamps");
assert(fieldValidationHtml.includes("ISO 8601 UTC date-time ending in Z"), "Field kit must validate UTC timestamp format");
assert(fieldProtocol.stations[0].date_utc_format?.includes("ISO 8601 UTC timestamp ending in Z") && fieldProtocol.stations[0].measurement_time_utc_format?.includes("ISO 8601 UTC timestamp ending in Z"), "Field protocol must specify station and measurement UTC timestamp formats");
assert(read("scripts/validate_field_observations.py").includes('("date_utc", "measurement_time_utc")'), "Repository validator must require station and measurement timestamps");
assert(read("tests/test_field_observation_timestamps.py").includes("test_rejects_date_only_value"), "Date-only rejection regression test is missing");
assert.equal(fieldLedger.status, "not_started", "Empty field ledger must remain not_started");
assert.equal((fieldLedger.observations || []).length, 0, "No unverified field observations may be silently inserted");
const registryStates = new Map(sourceRegistry.sources.map((s) => [s.id, s.state]));
assert.equal(registryStates.get("sentinel2_rgb"), "browse_only", "RGB Sentinel-2 quicklooks must remain browse-only");
assert.equal(registryStates.get("nasa_cmr_modis_merra"), "metadata_only", "CMR entries must remain metadata-only until science arrays are processed");
assert.equal(registryStates.get("nasa_pds_search"), "metadata_only", "PDS product discovery must remain metadata-only until products are independently inspected and processed");
assert.equal(registryStates.get("pds_geosciences_ode"), "metadata_only", "ODE metadata must not be represented as processed science");
assert.equal(registryStates.get("usgs_astrogeology_hirise_stac"), "metadata_only", "USGS HiRISE STAC records must remain metadata-only");
assert(sourceRegistry.sources.find((source) => source.id === "pds_geosciences_ode")?.artifacts?.includes("data/planetary/archive_discovery.json"), "ODE archive discovery artifact must be registered");
assert(sourceRegistry.sources.find((source) => source.id === "nasa_pds_search")?.artifacts?.includes("data/planetary/pds_search.json"), "PDS search artifact must be registered in the evidence inventory");
assert.equal(registryStates.get("suparco_space4climate"), "reference_only", "SUPARCO institutional links must remain reference-only");
assert(["planned", "partially_processed", "processed"].includes(registryStates.get("copernicus_glo90_global")), "GLO-90 state must reflect actual global run progress");
assert(["planned", "partially_processed", "processed", "unavailable"].includes(registryStates.get("io_lulc_global")), "Global land-cover evidence state must be explicit");
assert(["planned", "partially_processed", "processed", "unavailable"].includes(registryStates.get("nasa_power_global")), "Global NASA POWER evidence state must be explicit");
assert(read("scripts/build_reproducibility_manifest.py").includes("sha256"), "SHA-256 manifest generator missing");
assert(read("scripts/validate_evidence_inventory.py").includes("processed state needs artifact path"), "Evidence state integrity validator missing");
assert(read("docs/COMPETITIVE_CAPABILITY_RESPONSE.md").includes("not independent-data validation"), "Competitive methods note must state independent validation limits");


const readinessHtml = read("mission-readiness.html");
const reviewHtml = read("independent-review.html");
const operationalDoc = read("docs/OPERATIONAL_READINESS_AND_VALIDATION.md");
const reviewerGuide = read("docs/INDEPENDENT_REVIEWER_GUIDE.md");
const validationReport = JSON.parse(read("data/validation/quantitative_validation.json"));
const blindPacket = JSON.parse(read("data/validation/independent_analog_review_packet.json"));
assert(readinessHtml.includes("operational suitability not established"), "Mission readiness page must state the current rover-suitability boundary");
assert(readinessHtml.includes("50.53%") && readinessHtml.includes("9.154%"), "Mission readiness page must preserve MOLA and LOLA coverage caveats");
const divinerPolar = lunarPolar.diviner_polar_resource_product || {};
const wacPolar = lunarPolar.lroc_wac_illumination || {};
assert.equal(divinerPolar.status, "processed", "Historical Diviner polar resource summary must remain processed");
assert.equal(divinerPolar.aoi?.selected_triangle_count, 6823, "Unexpected Diviner Shackleton AOI triangle count");
assert.equal(wacPolar.time_weighted?.resolution_m_per_pixel, 100, "Expected 100 m time-weighted WAC illumination product");
assert.equal(wacPolar.percentage_based?.resolution_m_per_pixel, 100, "Expected 100 m percentage-based WAC illumination product");
assert(wacPolar.time_weighted?.illumination_percent?.pixels_at_or_below_5_percent_area_fraction > 60, "WAC low-illumination proxy summary missing");
assert(readinessHtml.includes("renderLunarPolar") && readinessHtml.includes("lunarPolarMetrics"), "Mission readiness dashboard must display the processed lunar environment evidence");
assert(readinessHtml.includes("not a formal PSR polygon"), "Dashboard must distinguish low-illumination screening from formal PSR geometry");
assert(!readinessHtml.includes("The product does not establish illumination"), "Dashboard must not hide the separately processed historical illumination evidence");
assert(operationalDoc.includes("**LROC WAC, 100 m:** historical") && operationalDoc.includes("103.786 K"), "Operational readiness documentation must describe the historical lunar evidence and limits");
assert(read("README.md").includes("Evidence snapshot — 28 November 2026") && read("README.md").includes("NASA LROC WAC"), "README must use the current evidence date and disclose historical WAC evidence");
assert(read("service-worker.js").includes('CACHE_VERSION="analogx-offline-v9"'), "Offline cache version must be refreshed after field timestamp changes and lunar evidence updates");
assert(reviewHtml.includes("independent_of_analogx_score") && reviewHtml.includes("Export review JSON"), "Blind reviewer desk is missing provenance/export safeguards");
assert(!reviewHtml.includes("core_terrain_index") && !reviewHtml.includes("candidate_id"), "Reviewer interface must not expose candidate scores or IDs");
for (const source of [readinessHtml, reviewHtml]) {
  const match = source.match(/<script>([\s\S]*?)<\/script>/);
  assert(match, "New evidence module is missing its inline application script");
  new Function(match[1]);
}
assert(blindPacket.cases.length === 96, "Blind review packet must retain 96 cases");
assert(blindPacket.cases.every((row) => !row.independent_review?.label), "No reviewer labels may be fabricated");
assert.equal((validationReport.independent_analog_label_validation?.targets?.moon?.n_total || 0), 0, "Moon expert labels must remain absent until returned");
assert.equal((validationReport.independent_analog_label_validation?.targets?.mars?.n_total || 0), 0, "Mars expert labels must remain absent until returned");
assert.equal(fieldLedger.status, "not_started", "Field observations must remain not_started until real records are supplied");
assert.equal((fieldLedger.observations || []).length, 0, "No physical field observations may be fabricated");
assert(operationalDoc.includes("Do not convert generic slope thresholds"), "Operational evidence policy must prohibit unsupported safety claims");
assert(reviewerGuide.includes("This is an invitation template"), "Reviewer guide must not imply experts were contacted");
assert(idxIncludesReadiness(read("index.html")), "Main portal must expose the mission readiness workbench");
assert(read("service-worker.js").includes("./independent-review.html") && read("service-worker.js").includes("./mission-readiness.html"), "Offline cache must include new validation modules");
function idxIncludesReadiness(source) {
  return source.includes("./mission-readiness.html");
}

// Generated-data publishers share one queued lock and always rebuild from the latest main.
// This prevents stale push-event SHAs and parallel publishers from racing on shared evidence files.
const publisherWorkflowPaths = [
  ".github/workflows/build-lunar-lola-80m.yml",
  ".github/workflows/build-lunar-reference.yml",
  ".github/workflows/build-lunar-resource-profile.yml",
  ".github/workflows/build-provenance-manifest.yml",
  ".github/workflows/build-terrain-comparison.yml",
  ".github/workflows/build-transferability.yml",
  ".github/workflows/diagnose-diviner-prp.yml",
  ".github/workflows/diagnose-lola-access.yml",
  ".github/workflows/diagnose-lola-mit.yml",
  ".github/workflows/fetch-nasa-cmr.yml",
  ".github/workflows/fetch-nasa-power.yml",
  ".github/workflows/fetch-public-evidence.yml",
  ".github/workflows/global-discovery.yml",
  ".github/workflows/global-environment-enrichment.yml",
  ".github/workflows/global-ranking-release.yml",
  ".github/workflows/process-sentinel-evidence.yml"
];
for (const workflowPath of publisherWorkflowPaths) {
  const workflow = read(workflowPath);
  assert(
    workflow.includes("analogx-repository-data-publish"),
    `Generated-data publisher is missing the shared concurrency group: ${workflowPath}`
  );
  assert(
    workflow.includes("queue: max") && workflow.includes("cancel-in-progress: false"),
    `Generated-data publisher must queue all runs without cancelling the active publisher: ${workflowPath}`
  );
  assert(
    workflow.includes("ref: main"),
    `Generated-data publisher must check out the current main branch before building: ${workflowPath}`
  );
}

console.log("ANALOG-X validation passed:");
console.log(`- ${sites.length} candidate records and ${power.record_count} NASA POWER snapshots`);
console.log("- Four Pakistan terrain profiles plus Mars MOLA and lunar LOLA inputs");
console.log("- Unique UI IDs, Agent Bay controls, Field School, and decision-engine code");
console.log("- Cloud Agent model binding, target-specific comparisons and evidence-policy wiring");

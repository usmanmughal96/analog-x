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
assert(read("docs/DECISION_ENGINE.md").includes("Strict evidence policy"), "Decision method documentation missing");

console.log("ANALOG-X validation passed:");
console.log(`- ${sites.length} candidate records and ${power.record_count} NASA POWER snapshots`);
console.log("- Four Pakistan terrain profiles plus Mars MOLA and lunar LOLA inputs");
console.log("- Unique UI IDs, Agent Bay controls, Field School, and decision-engine code");
console.log("- Cloud Agent model binding, target-specific comparisons and evidence-policy wiring");

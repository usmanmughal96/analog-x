(function(){
"use strict";
const $=id=>document.getElementById(id);
const esc=s=>String(s??"").replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
const POWER_FILE={koh_i_sultan:"koh",koh:"koh",hispar_glacier:"hispar_glacier"};
const state={catalog:null,powerIndex:null,terrain:null,imagery:null,powers:{},selected:"chagai_small_playas",map:null,markers:{},endpoint:"",connected:false,brief:null,game:0,answered:false};
const scenarios=[
 {target:"Mars",objective:"playa",title:"MISSION 01 / MARS EVAPORITE RECONNAISSANCE",question:"A Mars team wants to rehearse mapping dry playa surfaces, possible evaporite accumulations and sediment transport. Which Pakistan field lead should be investigated first?",options:[["chagai_small_playas","Chagai small salt playas near Nok Kundi"],["hispar_glacier","Hispar Glacier / Karakoram"],["koh_i_sultan","Koh-i-Sultan volcanic field"],["hamun_i_mashkel","Hamun-i-Mashkel playa"]],correct:"chagai_small_playas",why:"The NASA 1974 report identifies two small salt-surfaced playas near Nok Kundi and discusses possible evaporite/brine context. This is a historical lead, not modern proof of mineralogy or brine. Hamun-i-Mashkel is a broader basin-scale comparator. Both need field verification."},
 {target:"Mars",objective:"volcanic",title:"MISSION 02 / MARS VOLCANIC FIELD MAPPING",question:"Which Pakistan site has mapped volcanic units that can support rehearsal of outcrop logging and orbital-to-ground field mapping?",options:[["koh_i_sultan","Koh-i-Sultan / Chagai"],["hamun_i_mashkel","Hamun-i-Mashkel playa"],["hispar_glacier","Hispar Glacier"],["chagai_small_playas","Chagai small salt playas"]],correct:"koh_i_sultan",why:"USGS maps Koh-i-Sultan as agglomerate, tuff and andesitic lava. That supports volcanic-process rehearsal, but it is not a basaltic composition match to Syrtis Major. Ground samples and site-scale mineral mapping are still missing."},
 {target:"Moon",objective:"cryosphere",title:"MISSION 03 / LUNAR POLAR OPERATIONS",question:"Which Earth site can help rehearse snow/ice image interpretation, debris-boundary observation and cold-region sensor workflows—without pretending to reproduce a lunar permanently shadowed region?",options:[["hispar_glacier","Hispar Glacier / Karakoram"],["chagai_small_playas","Chagai salt playas"],["dallol","Dallol / Danakil"],["koh_i_sultan","Koh-i-Sultan / Chagai"]],correct:"hispar_glacier",why:"Hispar is useful for terrestrial cryosphere observation and remote field workflows. A glacier does not reproduce lunar vacuum, gravity, radiation, illumination cycles or PSR ice stability."}
];
let currentSites=[];
function json(path){return fetch(path,{cache:"no-store"}).then(r=>{if(!r.ok)throw Error(path+" HTTP "+r.status);return r.json();});}
function pill(el,text,cls){el.textContent=text;el.className="statuspill "+(cls||"");}
function idPower(id){return POWER_FILE[id]||id;}
function selectedIds(){return [...document.querySelectorAll("[data-ax-site]:checked")].map(x=>x.value).slice(0,5);}
function findSite(id){return state.catalog?.candidate_sites?.find(x=>x.id===id);}
async function load(){
 try{
  const [c,p,t,i]=await Promise.all([json("./data/agents/candidate_catalog.json"),json("./data/power/index.json"),json("./data/terrain/terrain_comparison.json"),json("./data/pakistan/imagery/index.json")]);
  state.catalog=c;state.powerIndex=p;state.terrain=t;state.imagery=i;
  await Promise.all(c.candidate_sites.map(async s=>{try{state.powers[s.id]=await json("./data/power/"+idPower(s.id)+".json");}catch{state.powers[s.id]=null;}}));
  pill($("axDiscoveryStatus"),c.candidate_sites.length+" CANDIDATE SEEDS","blue");
  render();renderAgentChoices();renderGame();
  const saved=localStorage.getItem("analogx_agent_endpoint")||"";
  if(saved){$("axAgentEndpoint").value=saved;await testEndpoint(false);}
 }catch(e){pill($("axDiscoveryStatus"),"CANDIDATE DATA OFFLINE","gold");$("axCards").textContent=e.message;}
}
function layers(id){
 const s=findSite(id),p=state.powers[id],i=state.imagery?.sites?.[id],t=state.terrain?.earth_sites?.[id];
 return {site:s,power:!!p,spectral:!!i,terrain:t?.status==="processed",reference:!!s?.source_references?.length,terrainRecord:t,spectralRecord:i,powerRecord:p};
}
function render(){
 const mission=$("axMissionFilter").value,tier=$("axTierFilter").value,q=$("axSearch").value.trim().toLowerCase();
 currentSites=state.catalog.candidate_sites.filter(s=>(mission==="Both"||(s.mission_targets||[]).includes(mission))&&(tier==="all"||s.discovery_tier===tier)&&(!q||[s.name,s.country,s.region,...(s.environment_tags||[])].join(" ").toLowerCase().includes(q)));
 $("axMapCount").textContent=currentSites.length+" / "+state.catalog.candidate_sites.length+" sites";
 $("axCards").innerHTML=currentSites.map(s=>{
  const e=layers(s.id),lead=s.discovery_tier==="under_characterized_candidate";
  return "<article class='axCard "+(state.selected===s.id?"selected":"")+"' data-ax-card='"+esc(s.id)+"'><div class='axCardTop'><h4>"+esc(s.name)+"</h4><span class='statuspill "+(lead?"gold":"gray")+"'>"+(lead?"RESEARCH LEAD":"REFERENCE")+"</span></div><p>"+esc(s.region||s.country)+" · "+esc((s.environment_tags||[]).slice(0,3).join(" / "))+"</p><div class='axPills'><span class='axPill'>"+esc(s.candidate_status||"candidate")+"</span><span class='axPill'>"+esc((s.mission_targets||[]).join(" + "))+"</span></div><div class='axEvidence'><span>Climate "+(e.power?"✓":"—")+"</span><span>Sentinel "+(e.spectral?"✓":"—")+"</span><span>Terrain "+(e.terrain?"✓":"—")+"</span><span>Source "+(e.reference?"✓":"—")+"</span></div><div class='axCardFoot'><button class='axMiniBtn' data-ax-inspect='"+esc(s.id)+"'>INSPECT DOSSIER ↗</button><label class='axCheck'><input type='checkbox' data-ax-site value='"+esc(s.id)+"' "+(["chagai_small_playas","hamun_i_mashkel","koh_i_sultan","hispar_glacier"].includes(s.id)?"checked":"")+"> Agent set</label></div></article>";
 }).join("")||"<div class='axCard'>No candidate matches these filters.</div>";
 renderMap(currentSites);
 if(!currentSites.some(s=>s.id===state.selected))state.selected=currentSites[0]?.id;
 dossier(state.selected);
}
function renderMap(sites){
 if(!window.L||!$("axDiscoveryMap"))return;
 if(!state.map){state.map=L.map("axDiscoveryMap",{zoomControl:false,scrollWheelZoom:false}).setView([20,18],2);L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",{maxZoom:12,attribution:"© OpenStreetMap contributors"}).addTo(state.map);L.control.zoom({position:"bottomright"}).addTo(state.map);}
 Object.values(state.markers).forEach(m=>state.map.removeLayer(m));state.markers={};
 sites.forEach(s=>{const lead=s.discovery_tier==="under_characterized_candidate";const m=L.circleMarker([s.latitude,s.longitude],{radius:lead?8:6,color:lead?"#edc77e":"#50d6c2",weight:2,fillColor:lead?"#b8853d":"#1b8e8c",fillOpacity:.85});m.bindPopup("<b>"+esc(s.name)+"</b><br>"+esc(s.country)+"<br><small>"+(lead?"Under-characterized candidate lead":"Established/reference seed")+"</small>");m.on("click",()=>{state.selected=s.id;document.querySelectorAll(".axCard").forEach(x=>x.classList.toggle("selected",x.dataset.axCard===s.id));dossier(s.id);});m.addTo(state.map);state.markers[s.id]=m;});
}
function dossier(id){
 const s=findSite(id);if(!s){$("axDossier").innerHTML="<div><h4>NO SITE SELECTED</h4><p>Choose a point or card.</p></div><div></div>";return;}
 const e=layers(id),count=[e.power,e.spectral,e.terrain,e.reference].filter(Boolean).length;
 const links=(s.source_references||[]).map(x=>"<a href='"+esc(x.url)+"' target='_blank' rel='noopener'>"+esc(x.title)+" ↗</a>").join("");
 const tasks=(s.rehearsal_tasks||[]).map(x=>"<li>"+esc(x)+"</li>").join("");
 const limits=(s.non_transferable||[]).map(x=>"<li>"+esc(x)+"</li>").join("");
 let measured="";
 if(e.spectralRecord){const ix=e.spectralRecord.indices||{};measured+="<li>Sentinel-2 scene "+esc(e.spectralRecord.scene?.datetime||"date unavailable")+"; 20 m valid pixels: "+(e.spectralRecord.processing?.valid_pixel_count??"—")+"</li><li>BSI median: "+(ix.BSI?.median?.toFixed(3)??"—")+"; NDSI median: "+(ix.NDSI?.median?.toFixed(3)??"—")+" (screening indices, not mineral/ice proof)</li>";}
 if(e.terrainRecord?.terrain_metrics){const m=e.terrainRecord.terrain_metrics;measured+="<li>Median slope: "+m.slope_deg.median.toFixed(2)+"°; P90 local relief: "+m["3x3_local_relief_m"].p90.toFixed(0)+" m</li>";}
 $("axDossier").innerHTML="<div><h4>"+esc(s.name)+" / "+esc(s.region||s.country)+"</h4><p>"+esc(s.hypothesis||"Candidate seed with documented environment context.")+"</p><p><b style='color:#b8d9e4'>Evidence layers:</b> "+count+"/4 available · "+(e.power?"NASA POWER":"climate pending")+" · "+(e.spectral?"Sentinel-2 profile":"spectral pending")+" · "+(e.terrain?"terrain processed":"terrain pending")+"</p><ul>"+measured+"</ul><div class='axLinks'>"+links+"</div></div><div><h4>FIELD REHEARSAL / LIMITS</h4><ul>"+tasks+limits+"</ul><p>Coordinates are data-discovery references, not surveyed boundaries, access routes or permission to enter.</p></div>";
 if(state.map&&state.markers[id])state.markers[id].openPopup();
}
function renderAgentChoices(){
 $("axAgentCandidates").innerHTML=state.catalog.candidate_sites.map(s=>"<label class='axCandidate'><input type='checkbox' data-ax-site value='"+esc(s.id)+"' "+(["chagai_small_playas","hamun_i_mashkel","koh_i_sultan","hispar_glacier"].includes(s.id)?"checked":"")+"> "+esc(s.name)+"</label>").join("");
}
function renderGame(){
 const q=scenarios[state.game];state.answered=false;
 $("axGameTitle").textContent=q.title;$("axGameQuestion").textContent=q.question;
 $("axGameProgress").textContent="MISSION "+String(state.game+1).padStart(2,"0")+" / "+scenarios.length;
 $("axGameFeedback").style.display="none";$("axGameFeedback").textContent="";
 $("axGameOptions").innerHTML=q.options.map(([id,label])=>"<button class='axGameOption' data-ax-game='"+esc(id)+"'>"+esc(label)+"</button>").join("");
}
function answerGame(id){
 if(state.answered)return;state.answered=true;const q=scenarios[state.game],ok=id===q.correct;
 document.querySelectorAll("[data-ax-game]").forEach(b=>{b.disabled=true;if(b.dataset.axGame===q.correct)b.classList.add("correct");else if(b.dataset.axGame===id)b.classList.add("wrong");});
 const fb=$("axGameFeedback");fb.style.display="block";fb.style.borderLeftColor=ok?"#35b99b":"#d4a45d";fb.textContent=(ok?"Correct field-method choice. ":"Not the strongest selection for this task. ")+q.why;
 $("axAgentMission").value=q.target;$("axAgentObjective").value=q.objective;$("axAgentQuestion").value=q.question+" Explain what evidence supports the choice, where the analogy breaks down and what measurement should come next.";
}
function relevanceTags(o){return o==="playa"?["playa","evaporite","closed-basin","salt","arid","sediment"]:o==="volcanic"?["volcanic","andesitic","lava","tuff","agglomerate","hydrothermal"]:o==="cryosphere"?["glacier","ice","cryosphere","polar","permafrost","snow"]:["terrain","desert","crater","alluvial","polar","slope"];}
function driestMonths(p){return (p?.monthly||[]).filter(x=>Number.isFinite(x.precip)).sort((a,b)=>a.precip-b.precip).slice(0,3).map(x=>({month:x.month,precip_mm_day:x.precip,temperature_c:x.temp,wind_10m_ms:x.wind,solar_kwh_m2_day:x.solar}));}
function siteSummary(id,objective){
 const s=findSite(id),e=layers(id),tags=(s?.environment_tags||[]).map(x=>x.toLowerCase()),terms=relevanceTags(objective);
 return {id,name:s?.name||id,site_status:s?.candidate_status||"unregistered",matched_environment_tags:tags.filter(t=>terms.some(z=>t.includes(z)||z.includes(t))),evidence:{climate:!!e.power,sentinel2:!!e.spectral,terrain:e.terrain,source_references:e.reference},campaign:driestMonths(e.powerRecord),spectral:e.spectralRecord?{scene_id:e.spectralRecord.scene?.item_id,datetime:e.spectralRecord.scene?.datetime,valid_pixels:e.spectralRecord.processing?.valid_pixel_count,BSI_median:e.spectralRecord.indices?.BSI?.median,NDSI_median:e.spectralRecord.indices?.NDSI?.median,interpretation:e.spectralRecord.interpretation_note}:null,terrain_profile:e.terrain?{median_slope_deg:e.terrainRecord.terrain_metrics.slope_deg.median,p90_slope_deg:e.terrainRecord.terrain_metrics.slope_deg.p90,p90_local_relief_m:e.terrainRecord.terrain_metrics["3x3_local_relief_m"].p90,coverage_percent:e.terrainRecord.terrain_metrics.coverage.valid_percent}:null};
}
function localAnalysis(req){
 const ids=req.candidate_ids.length?req.candidate_ids:["chagai_small_playas","hamun_i_mashkel","koh_i_sultan","hispar_glacier"];
 const rows=ids.map(id=>siteSummary(id,req.objective)).sort((a,b)=>b.matched_environment_tags.length-a.matched_environment_tags.length);
 const top=rows[0],ties=rows.filter(x=>x.matched_environment_tags.length===top.matched_environment_tags.length);
 const target=state.terrain?.planetary_target?.terrain_metrics,moon=state.terrain;
 return {mode:"offline deterministic evidence review",question:req.question,mission_target:req.mission_target,objective:req.objective,
   decision:"Task-tag match and evidence availability are reported separately; there is no universal analog score or single-winner override.",
   most_task_relevant:ties.map(x=>({id:x.id,name:x.name,tags:x.matched_environment_tags,evidence:x.evidence})),
   candidate_matrix:rows,
   planetary_terrain:{mars:target?{name:moon.planetary_target.name,median_slope_deg:target.slope_deg.median,p90_slope_deg:target.slope_deg.p90,p90_local_relief_m:target["3x3_local_relief_m"].p90,coverage_percent:target.coverage.valid_percent,complete_neighborhoods:target.complete_3x3_neighbourhood_count}:null,moon:window.ANALOGX_LUNAR||null},
   data_timestamps:{power:state.powerIndex?.generated_at_utc,terrain:state.terrain?.generated_at_utc,imagery:state.imagery?.generated_at_utc},
   scientific_gaps:["Chagai salt-playa coordinates are historical reference points; verify the exact AOI against current imagery and geology.","Sentinel-2 indices are spectral screening descriptors, not mineral identification, brine chemistry, or validated glacier outlines.","NASA POWER is gridded climate climatology, not an on-site station or field forecast.","Nili Patera MOLA observed-cell coverage is limited; planetary terrain profiles are coarse regional descriptors.","Field ground truth, permits, access/safety review and specialist validation are mandatory before a campaign."],
   method:"Count of directly matching environment tags is a transparent retrieval heuristic, not a calibrated similarity score. Climate, Sentinel, terrain and source completeness remain separate evidence layers."
 };
}
function fmt(v,n=2){return typeof v==="number"&&Number.isFinite(v)?v.toFixed(n):"—";}
function renderLocal(result){
 const list=result.most_task_relevant.map(s=>"<li><b>"+esc(s.name)+"</b> — "+esc(s.tags.join(", ")||"no direct tag match")+"; evidence "+Object.values(s.evidence).filter(Boolean).length+"/4</li>").join("");
 const matrix=result.candidate_matrix.map(s=>"<tr><td>"+esc(s.name)+"</td><td>"+esc(s.matched_environment_tags.join(", ")||"—")+"</td><td>"+Object.values(s.evidence).filter(Boolean).length+"/4</td><td>"+esc(s.campaign.map(x=>x.month+" ("+fmt(x.precip_mm_day)+" mm/day)").join(", ")||"—")+"</td></tr>").join("");
 const gaps=result.scientific_gaps.map(x=>"<li>"+esc(x)+"</li>").join("");
 return "<h4>DECISION SIGNAL</h4><p>"+esc(result.decision)+"</p><h4>MOST TASK-RELEVANT LEADS</h4><ul>"+(list||"<li>No matching candidate.</li>")+"</ul><h4>EVIDENCE MATRIX</h4><div style='overflow-x:auto'><table class='labTable'><thead><tr><th>Earth site</th><th>Task tags</th><th>Layers present</th><th>3 driest months (climatology)</th></tr></thead><tbody>"+matrix+"</tbody></table></div><h4>SCIENTIFIC GAPS / STOP CONDITIONS</h4><ul>"+gaps+"</ul><p><small>Method: "+esc(result.method)+"</small></p>";
}
function endpointSaved(){try{return localStorage.getItem("analogx_agent_endpoint")||"";}catch{return "";}}
async function testEndpoint(show=true){
 const endpoint=$("axAgentEndpoint").value.trim().replace(/\/$/,"");
 if(!endpoint){state.connected=false;pill($("axAgentModeStatus"),"LOCAL MODE READY","gold");$("axAgentRunCloud").disabled=true;if(show)$("axAgentStatus").textContent="Paste Worker URL to connect cloud inference.";return false;}
 try{
  $("axAgentConnect").disabled=true;$("axAgentConnect").textContent="TESTING…";
  const r=await fetch(endpoint+"/health");if(!r.ok)throw Error("HTTP "+r.status);const h=await r.json();if(!h.ok)throw Error("Workers AI binding unavailable");
  state.connected=true;state.endpoint=endpoint;localStorage.setItem("analogx_agent_endpoint",endpoint);pill($("axAgentModeStatus"),"WORKERS AI CONNECTED","blue");$("axAgentRunCloud").disabled=false;$("axAgentStatus").textContent=h.model+" · free daily quota applies";return true;
 }catch(e){state.connected=false;$("axAgentRunCloud").disabled=true;pill($("axAgentModeStatus"),"LOCAL MODE / CLOUD OFFLINE","gold");$("axAgentStatus").textContent="Connection failed: "+e.message;if(show)renderOutput("Cloud agent is not connected. The offline science review remains available.");return false;}
 finally{$("axAgentConnect").disabled=false;$("axAgentConnect").textContent="CONNECT & TEST";}
}
function requestData(){return {question:$("axAgentQuestion").value.trim(),mission_target:$("axAgentMission").value,objective:$("axAgentObjective").value,candidate_ids:[...document.querySelectorAll("[data-ax-site]:checked")].map(x=>x.value).slice(0,5),evidence_mode:$("axAgentEvidenceMode").value};}
function renderOutput(content,asHtml=true){$("axAgentOutput").innerHTML=asHtml?content:"<p>"+esc(content)+"</p>";}
async function runLocal(){
 const req=requestData();if(req.question.length<8){$("axAgentStatus").textContent="Enter a research question first.";return;}
 $("axAgentRunLocal").disabled=true;$("axAgentRunCloud").disabled=true;pill($("axAgentOutputStatus"),"ANALYSING","gold");$("axAgentOutput").innerHTML="<div class='axLoading'></div><p>Running terrain, climate, surface and evidence-integrity analysts…</p>";
 try{const result=localAnalysis(req);state.brief=result;renderOutput(renderLocal(result));pill($("axAgentOutputStatus"),"OFFLINE REVIEW COMPLETE","blue");$("axAgentStatus").textContent="Completed locally · no API/LLM call";$("axAgentTraceText").textContent=JSON.stringify({method:result.method,candidates:result.candidate_matrix.map(x=>({id:x.id,evidence:x.evidence,matched_tags:x.matched_environment_tags})),timestamps:result.data_timestamps},null,2);}
 catch(e){renderOutput("Offline review failed: "+e.message,false);pill($("axAgentOutputStatus"),"REVIEW FAILED","gold");}
 finally{$("axAgentRunLocal").disabled=false;$("axAgentRunCloud").disabled=!state.connected;}
}
async function runCloud(){
 if(!state.connected){$("axAgentStatus").textContent="Connect and test the Worker endpoint first.";return;}
 const req=requestData();if(req.candidate_ids.length===0){$("axAgentStatus").textContent="Select at least one Earth site.";return;}
 const endpoint=$("axAgentEndpoint").value.trim().replace(/\/$/,"");
 $("axAgentRunCloud").disabled=true;$("axAgentRunLocal").disabled=true;pill($("axAgentOutputStatus"),"AGENTS ACTIVE","gold");$("axAgentOutput").innerHTML="<div class='axLoading'></div><p>Mission Director is inspecting published evidence and may call data tools…</p>";
 try{
  const r=await fetch(endpoint+"/analyze",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(req)});
  const data=await r.json();if(!r.ok||!data.ok)throw Error(data.detail||data.error||"Agent API failed");
  state.brief=data;renderOutput("<h4>MISSION DIRECTOR DECISION</h4><p>"+esc(data.analysis||"No synthesis returned.")+"</p><h4>SPECIALIST AGENT FINDINGS</h4>"+(data.agents||[]).map(x=>"<p><b>"+esc(x.agent)+"</b><br><code>"+esc(JSON.stringify(x.result))+"</code></p>").join(""));
  pill($("axAgentOutputStatus"),"CLOUD AGENT COMPLETE","blue");$("axAgentStatus").textContent="Completed · "+(data.tool_trace?.length||0)+" tool calls · "+data.model;$("axAgentTraceText").textContent=JSON.stringify({mode:data.mode,model:data.model,data_timestamps:data.data_generated_at_utc,tool_trace:data.tool_trace,disclaimer:data.disclaimer},null,2);
 }catch(e){pill($("axAgentOutputStatus"),"CLOUD UNAVAILABLE","gold");$("axAgentStatus").textContent="Cloud run failed: "+e.message+" · use offline review";renderOutput("Cloud agent could not complete. No cloud recommendation was accepted; run the offline review for source-backed local results.",false);}
 finally{$("axAgentRunCloud").disabled=!state.connected;$("axAgentRunLocal").disabled=false;}
}
function exportBrief(){
 if(!state.brief){$("axAgentStatus").textContent="Run an analysis first.";return;}
 const blob=new Blob([JSON.stringify(state.brief,null,2)],{type:"application/json"}),url=URL.createObjectURL(blob),a=document.createElement("a");a.href=url;a.download="ANALOG-X_Evidence_Decision_Brief.json";a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
}
function bind(){
 ["axMissionFilter","axTierFilter"].forEach(id=>$(id).addEventListener("change",render));
 $("axSearch").addEventListener("input",render);
 $("axCards").addEventListener("click",e=>{const b=e.target.closest("[data-ax-inspect]");if(b){state.selected=b.dataset.axInspect;document.querySelectorAll(".axCard").forEach(x=>x.classList.toggle("selected",x.dataset.axCard===state.selected));dossier(state.selected);}});
 $("axGameOptions").addEventListener("click",e=>{const b=e.target.closest("[data-ax-game]");if(b)answerGame(b.dataset.axGame);});
 $("axGameNext").addEventListener("click",()=>{state.game=(state.game+1)%scenarios.length;renderGame();});
 $("axAgentConnect").addEventListener("click",()=>testEndpoint(true));
 $("axAgentRunLocal").addEventListener("click",runLocal);
 $("axAgentRunCloud").addEventListener("click",runCloud);
 $("axAgentExport").addEventListener("click",exportBrief);
}
async function start(){bind();renderGame();const url=endpointSaved();if(url)$("axAgentEndpoint").value=url;await load();if(url)await testEndpoint(false);$("axAgentRunLocal").click();}
start();
})();

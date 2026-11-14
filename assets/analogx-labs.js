(function(){
"use strict";
const $=id=>document.getElementById(id);
const esc=s=>String(s??"").replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
const POWER_FILE={koh_i_sultan:"koh",koh:"koh",hispar_glacier:"hispar_glacier"};
const state={catalog:null,powerIndex:null,terrain:null,imagery:null,lunar:null,powers:{},selected:"chagai_small_playas",map:null,markers:{},endpoint:"",workerAvailable:false,aiEnabled:false,connected:false,brief:null,scoutData:null,scoutMap:null,scoutMarker:null,scoutBounds:null,game:0,answered:false};
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
  const [c,p,t,i,l]=await Promise.all([json("./data/agents/candidate_catalog.json"),json("./data/power/index.json"),json("./data/terrain/terrain_comparison.json"),json("./data/pakistan/imagery/index.json"),json("./data/moon/shackleton_lola_80m.json")]);
  state.catalog=c;state.powerIndex=p;state.terrain=t;state.imagery=i;state.lunar=l;
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
  return "<article class='axCard "+(state.selected===s.id?"selected":"")+"' data-ax-card='"+esc(s.id)+"'><div class='axCardTop'><h4>"+esc(s.name)+"</h4><span class='statuspill "+(lead?"gold":"gray")+"'>"+(lead?"RESEARCH LEAD":"REFERENCE")+"</span></div><p>"+esc(s.region||s.country)+" · "+esc((s.environment_tags||[]).slice(0,3).join(" / "))+"</p><div class='axPills'><span class='axPill'>"+esc(s.candidate_status||"candidate")+"</span><span class='axPill'>"+esc((s.mission_targets||[]).join(" + "))+"</span></div><div class='axEvidence'><span>Climate "+(e.power?"✓":"—")+"</span><span>Sentinel "+(e.spectral?"✓":"—")+"</span><span>Terrain "+(e.terrain?"✓":"—")+"</span><span>Source "+(e.reference?"✓":"—")+"</span></div><div class='axCardFoot'><button class='axMiniBtn' data-ax-inspect='"+esc(s.id)+"'>INSPECT DOSSIER ↗</button><label class='axCheck'><input type='checkbox' data-ax-site-card value='"+esc(s.id)+"' "+(["chagai_small_playas","hamun_i_mashkel","koh_i_sultan","hispar_glacier"].includes(s.id)?"checked":"")+"> Agent set</label></div></article>";
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

function targetTerrain(mission){
 if(mission==="Moon"){
  const m=state.lunar?.matched_coarse_support_approx_925m;
  if(!m?.slope_deg||!m["3x3_local_relief_m_2775m_footprint"])return null;
  return {name:state.lunar.site?.name||"Shackleton Rim / Moon",median_slope_deg:m.slope_deg.median,p90_slope_deg:m.slope_deg.p90,p90_local_relief_m:m["3x3_local_relief_m_2775m_footprint"].p90,support_m:m.pixel_size_m,coverage_percent:m.elevation_coverage_percent,return_support_percent:m.ldec_positive_return_support?.mean_native_pixel_fraction_per_coarse_cell_percent};
 }
 const m=state.terrain?.planetary_target?.terrain_metrics;
 if(!m?.slope_deg||!m["3x3_local_relief_m"])return null;
 return {name:state.terrain.planetary_target.name,median_slope_deg:m.slope_deg.median,p90_slope_deg:m.slope_deg.p90,p90_local_relief_m:m["3x3_local_relief_m"].p90,support_m:925,coverage_percent:m.coverage?.valid_percent,complete_neighbourhoods:m.complete_3x3_neighbourhood_count};
}
function terrainComparison(ids,mission){
 const targets=mission==="Both"?["Moon","Mars"]:[mission];
 return targets.map(targetName=>{
  const target=targetTerrain(targetName);
  if(!target)return {mission_target:targetName,status:"planetary terrain reference unavailable"};
  const profiles=ids.map(id=>({id,rec:state.terrain?.earth_sites?.[id]})).filter(x=>x.rec?.status==="processed"&&x.rec.terrain_metrics);
  const metrics=profiles.map(({id,rec})=>{const m=rec.terrain_metrics;return {id,name:rec.site?.name||id,median_slope_deg:m.slope_deg.median,p90_slope_deg:m.slope_deg.p90,p90_local_relief_m:m["3x3_local_relief_m"].p90,coverage_percent:m.coverage?.valid_percent};});
  const fields=["median_slope_deg","p90_slope_deg","p90_local_relief_m"];
  const differences=metrics.map(site=>({id:site.id,name:site.name,differences:Object.fromEntries(fields.map(k=>[k,Math.abs(site[k]-target[k])]))}));
  const closest=Object.fromEntries(fields.map(k=>{const valid=differences.filter(x=>Number.isFinite(x.differences[k]));const min=valid.length?Math.min(...valid.map(x=>x.differences[k])):null;return [k,valid.filter(x=>x.differences[k]===min).map(x=>x.name)];}));
  return {mission_target:targetName,planetary_reference:target,earth_profiles:metrics,absolute_differences:differences,closest_per_descriptor:closest,interpretation:"Regional terrain descriptors only; a numerically closer profile does not establish geological, mineralogical or operational equivalence."};
 });
}
function localAnalysisWithTerrain(req){
 const ids=req.candidate_ids.length?req.candidate_ids:["chagai_small_playas","hamun_i_mashkel","koh_i_sultan","hispar_glacier"];
 const rows=ids.map(id=>siteSummary(id,req.objective)).sort((a,b)=>b.matched_environment_tags.length-a.matched_environment_tags.length);
 const top=rows[0],ties=rows.filter(x=>x.matched_environment_tags.length===top.matched_environment_tags.length);
 return {mode:"offline deterministic evidence review",question:req.question,mission_target:req.mission_target,objective:req.objective,
  decision:"Task-tag match and evidence availability are reported separately. There is no universal analog score. Terrain is compared by measured descriptor, not collapsed into one ranking.",
  most_task_relevant:ties.map(x=>({id:x.id,name:x.name,tags:x.matched_environment_tags,evidence:x.evidence})),
  candidate_matrix:rows,terrain_comparisons:terrainComparison(ids,req.mission_target),
  data_timestamps:{power:state.powerIndex?.generated_at_utc,terrain:state.terrain?.generated_at_utc,imagery:state.imagery?.generated_at_utc},
  scientific_gaps:["Chagai salt-playa coordinates are historical reference points; verify the AOI against current imagery and geology.","Sentinel-2 indices are spectral screening descriptors, not mineral identification, brine chemistry, or validated glacier outlines.","NASA POWER is gridded climate climatology, not an on-site station or field forecast.","Nili Patera MOLA observed-cell coverage is limited; lunar LOLA is interpolated and return counts are not an illumination or ice map.","New Chagai playa Copernicus terrain processing is still pending in the published profile.","Field ground truth, permits, access/safety review and specialist validation are mandatory before a campaign."],
  method:"Count of directly matching environment tags is a transparent retrieval heuristic, not a calibrated similarity score. Climate, Sentinel, terrain and source completeness remain separate evidence layers."
 };
}
function renderLocalWithTerrain(result){
 const list=result.most_task_relevant.map(s=>"<li><b>"+esc(s.name)+"</b> — "+esc(s.tags.join(", ")||"no direct tag match")+"; evidence "+Object.values(s.evidence).filter(Boolean).length+"/4</li>").join("");
 const matrix=result.candidate_matrix.map(s=>"<tr><td>"+esc(s.name)+"</td><td>"+esc(s.matched_environment_tags.join(", ")||"—")+"</td><td>"+Object.values(s.evidence).filter(Boolean).length+"/4</td><td>"+esc(s.campaign.map(x=>x.month+" ("+fmt(x.precip_mm_day)+" mm/day)").join(", ")||"—")+"</td></tr>").join("");
 const terrain=result.terrain_comparisons.map(t=>{
  const rows=(t.earth_profiles||[]).map(s=>"<tr><td>"+esc(s.name)+"</td><td>"+fmt(s.median_slope_deg)+"°</td><td>"+fmt(s.p90_slope_deg)+"°</td><td>"+fmt(s.p90_local_relief_m,0)+" m</td><td>"+fmt(s.coverage_percent,1)+"%</td></tr>").join("");
  const closest=Object.entries(t.closest_per_descriptor||{}).map(([k,v])=>"<li>"+esc(k.replaceAll("_"," "))+": "+esc(v.join(", ")||"no processed Earth profile")+"</li>").join("");
  return "<h4>"+esc(t.mission_target)+" / "+esc(t.planetary_reference?.name||"Terrain unavailable")+"</h4><p>"+esc(t.interpretation||t.status||"")+"</p><table class='labTable'><thead><tr><th>Earth site</th><th>Median slope</th><th>P90 slope</th><th>P90 local relief</th><th>Coverage</th></tr></thead><tbody>"+(rows||"<tr><td colspan='5'>No processed Earth terrain profiles for this selection.</td></tr>")+"</tbody></table><ul>"+closest+"</ul>";
 }).join("");
 const gaps=result.scientific_gaps.map(x=>"<li>"+esc(x)+"</li>").join("");
 return "<h4>DECISION SIGNAL</h4><p>"+esc(result.decision)+"</p><h4>MOST TASK-RELEVANT LEADS</h4><ul>"+(list||"<li>No matching candidate.</li>")+"</ul><h4>EARTH / PLANETARY TERRAIN EVIDENCE</h4>"+terrain+"<h4>EVIDENCE MATRIX</h4><table class='labTable'><thead><tr><th>Earth site</th><th>Task tags</th><th>Layers present</th><th>3 driest months (climatology)</th></tr></thead><tbody>"+matrix+"</tbody></table><h4>SCIENTIFIC GAPS / STOP CONDITIONS</h4><ul>"+gaps+"</ul><p><small>Method: "+esc(result.method)+"</small></p>";
}

function scoutBboxLocal(lat,lon,radiusKm){
 const latDelta=radiusKm/110.574,cosLat=Math.max(.05,Math.cos(lat*Math.PI/180)),lonDelta=Math.min(180,radiusKm/(111.32*cosLat));
 return [Math.max(-180,lon-lonDelta),Math.max(-89.9,lat-latDelta),Math.min(180,lon+lonDelta),Math.min(89.9,lat+latDelta)];
}
function updateScoutMap(lat,lon,radiusKm,bbox){
 if(!window.L||!$("axScoutMap"))return;
 if(!state.scoutMap){
  state.scoutMap=L.map("axScoutMap",{zoomControl:false,scrollWheelZoom:false}).setView([lat,lon],7);
  L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",{maxZoom:15,attribution:"© OpenStreetMap contributors"}).addTo(state.scoutMap);
  L.control.zoom({position:"bottomright"}).addTo(state.scoutMap);
 }
 if(state.scoutMarker)state.scoutMap.removeLayer(state.scoutMarker);
 if(state.scoutBounds)state.scoutMap.removeLayer(state.scoutBounds);
 state.scoutMarker=L.circleMarker([lat,lon],{radius:8,color:"#e6bc78",weight:2,fillColor:"#bc8844",fillOpacity:.9}).bindPopup("<b>Scout coordinate</b><br>"+lat.toFixed(5)+", "+lon.toFixed(5)).addTo(state.scoutMap);
 const b=bbox||scoutBboxLocal(lat,lon,radiusKm);
 state.scoutBounds=L.rectangle([[b[1],b[0]],[b[3],b[2]]],{color:"#45d1bd",weight:1,dashArray:"5 5",fillOpacity:.07}).addTo(state.scoutMap);
 state.scoutMap.setView([lat,lon],Math.max(3,Math.min(12,Math.round(10-Math.log2(radiusKm/5)))));
 $("axScoutMapLabel").textContent=lat.toFixed(5)+"° "+(lat>=0?"N":"S")+" · "+lon.toFixed(5)+"° "+(lon>=0?"E":"W");
 setTimeout(()=>state.scoutMap?.invalidateSize(),120);
}
function renderScoutResults(scout){
 const p=scout.evidence?.nasa_power?.data;
 const s=scout.evidence?.sentinel_2_l2a;
 const d=scout.evidence?.copernicus_dem;
 const m=p?.annual||{};
 const climate=[["Mean air temperature",m.mean_air_temperature_c,"°C"],["Relative humidity",m.mean_relative_humidity_percent,"%"],["Wind at 10 m",m.mean_wind_10m_ms,"m/s"],["Precipitation",m.mean_precipitation_mm_day,"mm/day"],["All-sky solar",m.mean_all_sky_solar_kwh_m2_day,"kWh/m²/day"]];
 const metricHtml=climate.map(([label,value,unit])=>"<div class='axScoutMetric'><span>"+esc(label)+"</span><b>"+(typeof value==="number"?value.toFixed(2):"—")+"<small>"+unit+"</small></b></div>").join("");
 const dry=(p?.driest_climatological_months||[]).map(x=>"<tr><td>"+esc(x.month)+"</td><td>"+(Number.isFinite(x.precipitation_mm_day)?x.precipitation_mm_day.toFixed(2):"—")+"</td><td>"+(Number.isFinite(x.temperature_c)?x.temperature_c.toFixed(1):"—")+"</td><td>"+(Number.isFinite(x.wind_10m_ms)?x.wind_10m_ms.toFixed(1):"—")+"</td></tr>").join("");
 const scenes=(s?.best_scene_candidates||[]).map(x=>"<div class='axScoutScene'><b>"+esc(x.id||"Scene id unavailable")+"</b><small>"+esc(x.datetime||"Date unknown")+" · "+esc(x.platform||"platform unknown")+" · cloud metadata "+(Number.isFinite(x.cloud_cover_percent)?x.cloud_cover_percent.toFixed(2)+"%":"not reported")+" · "+esc(x.mgrs_tile||"tile not reported")+"</small>"+(x.item_url&&/^https:\/\//i.test(x.item_url)?"<a href='"+esc(x.item_url)+"' target='_blank' rel='noopener'>Open STAC item ↗</a>":"")+"</div>").join("");
 const tiles=(d?.tiles||[]).map(x=>"<tr><td>"+esc(x.id)+"</td><td>"+(Number.isFinite(x.gsd_m)?x.gsd_m+" m":"—")+"</td><td>"+esc(x.epsg||"—")+"</td></tr>").join("");
 const statusRows=[["NASA POWER",scout.evidence?.nasa_power?.status||"unavailable"],["Sentinel-2 L2A",s?.status||"unavailable"],["Copernicus DEM",d?.status||"unavailable"]];
 $("axScoutResults").innerHTML="<div class='axScoutSummary'><b>COORDINATE SCAN / "+scout.coordinate.latitude.toFixed(5)+", "+scout.coordinate.longitude.toFixed(5)+"</b><p>Study radius "+scout.study_window.radius_km+" km · WGS84 bbox "+scout.study_window.bbox_wgs84.map(x=>x.toFixed(5)).join(", ")+" · scanned "+new Date(scout.generated_at_utc).toLocaleString()+"</p></div>"+
  "<div class='axScoutMetrics'>"+metricHtml+"</div>"+
  "<div class='axScoutBlock'><h4>NASA POWER / LOW-PRECIPITATION CLIMATOLOGICAL MONTHS</h4><table class='axScoutTable'><thead><tr><th>Month</th><th>Precip mm/day</th><th>Air °C</th><th>Wind m/s</th></tr></thead><tbody>"+(dry||"<tr><td colspan='4'>NASA POWER values unavailable.</td></tr>")+"</tbody></table></div>"+
  "<div class='axScoutBlock'><h4>SENTINEL-2 L2A / RECENT SCENE DISCOVERY</h4><p style='font-size:8px;color:#86a6b8'>"+(s?((s.number_matched??s.returned_items)+" scene records returned/matched in a rolling 24-month search; showing best candidates by reported scene cloud fraction."):"STAC search unavailable.")+"</p>"+(scenes||"<small>No scene metadata returned.</small>")+"</div>"+
  "<div class='axScoutBlock'><h4>COPERNICUS DEM GLO-30 / CATALOGUE TILES</h4><p style='font-size:8px;color:#86a6b8'>"+(d?(d.number_matched??d.returned_items)+" matching catalogue items. Tiles are not yet processed into a terrain profile.":"DEM STAC search unavailable.")+"</p><table class='axScoutTable'><thead><tr><th>Tile item</th><th>GSD</th><th>EPSG</th></tr></thead><tbody>"+(tiles||"<tr><td colspan='3'>No DEM tile metadata returned.</td></tr>")+"</tbody></table></div>"+
  "<div class='axScoutWarnings'><b style='color:#b7d3de'>SOURCE STATUS</b><ul>"+statusRows.map(x=>"<li>"+esc(x[0])+": "+esc(x[1])+"</li>").join("")+"</ul><b style='color:#b7d3de'>INTERPRETATION BOUNDARY</b><p>"+esc(scout.decision_boundary)+" NASA POWER is gridded climatology, scene cloud metadata is not an AOI mask, and DEM STAC records are tile discovery rather than terrain metrics.</p></div>";
}
async function runCoordinateScout(){
 const endpoint=$("axAgentEndpoint").value.trim().replace(/\/$/,"");
 if(!state.workerAvailable||!endpoint){$("axScoutHint").textContent="Connect a Cloudflare Worker first. The scout queries public data and does not require an AI model, but it needs the server endpoint.";return;}
 const latitude=Number($("axScoutLat").value),longitude=Number($("axScoutLon").value),radius_km=Number($("axScoutRadius").value);
 if(!Number.isFinite(latitude)||latitude< -89.9||latitude>89.9||!Number.isFinite(longitude)||longitude< -180||longitude>180){$("axScoutHint").textContent="Enter valid WGS84 latitude and longitude.";return;}
 if(!Number.isFinite(radius_km)||radius_km<1||radius_km>50){$("axScoutHint").textContent="Choose a study radius between 1 and 50 km.";return;}
 $("axScoutRun").disabled=true;$("axScoutExport").disabled=true;$("axScoutAskDirector").disabled=true;
 pill($("axScoutStatus"),"QUERYING OPEN DATA","gold");$("axScoutHint").textContent="Querying NASA POWER, Sentinel-2 L2A STAC and Copernicus DEM STAC…";
 $("axScoutResults").innerHTML="<div class='axLoading'></div><div class='axScoutPlaceholder'><b>GLOBAL SCOUT ACTIVE</b><p>Retrieving live public catalogue records. No AI inference is required.</p></div>";
 updateScoutMap(latitude,longitude,radius_km);
 try{
  const r=await fetch(endpoint+"/scout",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({latitude,longitude,radius_km,mission_target:$("axAgentMission").value})});
  const data=await r.json();if(!r.ok||!data.ok)throw Error(data.error||"Scout API failed with HTTP "+r.status);
  state.scoutData=data.scout;renderScoutResults(data.scout);updateScoutMap(latitude,longitude,radius_km,data.scout.study_window.bbox_wgs84);
  pill($("axScoutStatus"),"OPEN-DATA SCAN COMPLETE","blue");$("axScoutExport").disabled=false;$("axScoutAskDirector").disabled=!state.aiEnabled;
  const available=Object.values(data.scout.evidence||{}).filter(x=>x.status!=="unavailable").length;
  $("axScoutHint").textContent=available+"/3 data sources returned evidence. Review scene and coverage limits before treating the area as a candidate.";
 }catch(e){
  state.scoutData=null;pill($("axScoutStatus"),"SCOUT FAILED","gold");
  $("axScoutResults").innerHTML="<div class='axScoutPlaceholder'><b>COORDINATE SCAN UNAVAILABLE</b><p>"+esc(e.message)+"</p><p>Check Worker URL/API status or try another radius. The curated offline atlas remains available.</p></div>";
  $("axScoutHint").textContent="No result was accepted. Retry after checking the Worker connection.";
 }finally{$("axScoutRun").disabled=!state.workerAvailable;}
}
function useSelectedCandidateForScout(){
 const s=findSite(state.selected);if(!s)return;
 $("axScoutLat").value=s.latitude;$("axScoutLon").value=s.longitude;
 $("coordinateScout").scrollIntoView({behavior:"smooth",block:"start"});
 updateScoutMap(s.latitude,s.longitude,Number($("axScoutRadius").value));
 $("axScoutHint").textContent="Loaded "+s.name+". Run a fresh live scan for this location.";
}
function askDirectorAboutScout(){
 if(!state.scoutData)return;
 $("axAgentQuestion").value="Assess this newly scouted Earth location for a "+$("axAgentMission").value+" field-rehearsal task. Separate measured climate and satellite evidence from hypotheses. Which evidence is promising, what is missing, and which field measurements should come next?";
 $("agentBay").scrollIntoView({behavior:"smooth",block:"start"});
 if(state.aiEnabled)runCloud();
 else $("axAgentStatus").textContent="Scout dossier ready. Mission Director AI is not enabled on this Worker; export the scan or use the offline review.";
}
function exportScoutDossier(){
 if(!state.scoutData)return;
 const blob=new Blob([JSON.stringify(state.scoutData,null,2)],{type:"application/json"}),url=URL.createObjectURL(blob),a=document.createElement("a");
 a.href=url;a.download="ANALOG-X_Global_Coordinate_Scout.json";a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
}
function endpointSaved(){try{return localStorage.getItem("analogx_agent_endpoint")||"";}catch{return "";}}
async function testEndpoint(show=true){
 const endpoint=$("axAgentEndpoint").value.trim().replace(/\/$/,"");
 if(!endpoint){
  state.workerAvailable=false;state.aiEnabled=false;state.connected=false;
  pill($("axAgentModeStatus"),"LOCAL MODE READY","gold");
  $("axAgentRunCloud").disabled=true;$("axScoutRun").disabled=true;$("axScoutAskDirector").disabled=true;
  if(show){$("axAgentStatus").textContent="Paste Worker URL to connect global data scouting and cloud inference.";$("axScoutHint").textContent="Connect a Worker to enable the live global data scan.";}
  return false;
 }
 try{
  $("axAgentConnect").disabled=true;$("axAgentConnect").textContent="TESTING…";
  const r=await fetch(endpoint+"/health");if(!r.ok)throw Error("HTTP "+r.status);const h=await r.json();if(!h.ok)throw Error("Worker health check failed");
  state.workerAvailable=true;state.aiEnabled=!!h.ai_enabled;state.connected=state.aiEnabled;state.endpoint=endpoint;localStorage.setItem("analogx_agent_endpoint",endpoint);
  $("axScoutRun").disabled=false;$("axScoutHint").textContent="Global data scout connected · no AI inference needed for the scan.";
  $("axScoutAskDirector").disabled=!state.aiEnabled;
  pill($("axAgentModeStatus"),state.aiEnabled?"WORKERS AI CONNECTED":"SCOUT API READY / AI OFF",state.aiEnabled?"blue":"gold");
  $("axAgentRunCloud").disabled=!state.aiEnabled;
  $("axAgentStatus").textContent=state.aiEnabled?(h.model+" · free daily allocation applies"):"Worker connected; offline evidence agents remain active. Enable the AI binding for LLM synthesis.";
  return true;
 }catch(e){
  state.workerAvailable=false;state.aiEnabled=false;state.connected=false;
  $("axAgentRunCloud").disabled=true;$("axScoutRun").disabled=true;$("axScoutAskDirector").disabled=true;
  pill($("axAgentModeStatus"),"LOCAL MODE / CLOUD OFFLINE","gold");
  $("axAgentStatus").textContent="Connection failed: "+e.message;
  if(show){renderOutput("Worker is not connected. Offline science review remains available.");$("axScoutHint").textContent="Coordinate scout requires a Worker API; the curated offline atlas remains available.";}
  return false;
 }finally{$("axAgentConnect").disabled=false;$("axAgentConnect").textContent="CONNECT & TEST";}
}
function requestData(){return {question:$("axAgentQuestion").value.trim(),mission_target:$("axAgentMission").value,objective:$("axAgentObjective").value,candidate_ids:[...document.querySelectorAll("[data-ax-site]:checked")].map(x=>x.value).slice(0,5),evidence_mode:$("axAgentEvidenceMode").value,scout_coordinates:state.scoutData?{latitude:state.scoutData.coordinate.latitude,longitude:state.scoutData.coordinate.longitude,radius_km:state.scoutData.study_window.radius_km}:null};}
function renderOutput(content,asHtml=true){$("axAgentOutput").innerHTML=asHtml?content:"<p>"+esc(content)+"</p>";}
async function runLocal(){
 const req=requestData();if(req.question.length<8){$("axAgentStatus").textContent="Enter a research question first.";return;}
 $("axAgentRunLocal").disabled=true;$("axAgentRunCloud").disabled=true;pill($("axAgentOutputStatus"),"ANALYSING","gold");$("axAgentOutput").innerHTML="<div class='axLoading'></div><p>Running terrain, climate, surface and evidence-integrity analysts…</p>";
 try{const result=localAnalysisWithTerrain(req);if(state.scoutData)result.coordinate_scout=state.scoutData;state.brief=result;renderOutput(renderLocalWithTerrain(result));pill($("axAgentOutputStatus"),"OFFLINE REVIEW COMPLETE","blue");$("axAgentStatus").textContent="Completed locally · no API/LLM call";$("axAgentTraceText").textContent=JSON.stringify({method:result.method,candidates:result.candidate_matrix.map(x=>({id:x.id,evidence:x.evidence,matched_tags:x.matched_environment_tags})),timestamps:result.data_timestamps},null,2);}
 catch(e){renderOutput("Offline review failed: "+e.message,false);pill($("axAgentOutputStatus"),"REVIEW FAILED","gold");}
 finally{$("axAgentRunLocal").disabled=false;$("axAgentRunCloud").disabled=!state.connected;}
}
async function runCloud(){
 if(!state.connected){$("axAgentStatus").textContent="Connect and test the Worker endpoint first.";return;}
 const req=requestData();if(req.candidate_ids.length===0&&!req.scout_coordinates){$("axAgentStatus").textContent="Select at least one Earth site or run a coordinate scout first.";return;}
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
 $("axScoutRun").addEventListener("click",runCoordinateScout);
 $("axScoutUseCandidate").addEventListener("click",useSelectedCandidateForScout);
 $("axScoutAskDirector").addEventListener("click",askDirectorAboutScout);
 $("axScoutExport").addEventListener("click",exportScoutDossier);
}
async function start(){bind();renderGame();const url=endpointSaved();if(url)$("axAgentEndpoint").value=url;await load();if(url)await testEndpoint(false);updateScoutMap(Number($("axScoutLat").value),Number($("axScoutLon").value),Number($("axScoutRadius").value));$("axAgentRunLocal").click();}
start();
})();

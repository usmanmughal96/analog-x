(function () {
"use strict";
const $ = (id) => document.getElementById(id);
const esc = (value) => String(value ?? "").replace(/[&<>"']/g, (c) => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
const state = {catalog:null,powerIndex:null,imagery:null,terrain:null,lunar:null,diviner:null,records:[],db:null,selected:null,assessment:null};
const DB_NAME="analogx-field-evidence"; const DB_VERSION=1; const STORE="records";
const POWER_ALIAS={koh_i_sultan:"koh"};
const OBJECTIVES={
 playa:{label:"Evaporite / playa / paleolake processes",terms:["playa","evaporite","salt","saline","paleolake","sediment","inundation","drying"]},
 volcanic:{label:"Volcanic outcrop / alteration mapping",terms:["volcanic","lava","tuff","agglomerate","alteration","outcrop","basalt"]},
 cryosphere:{label:"Cryosphere / ice-debris field methods",terms:["glacier","ice","snow","debris","cryosphere","permafrost","cold-region"]},
 terrain:{label:"Terrain morphology / traverse documentation",terms:["terrain","slope","relief","traverse","morphology","navigation","field logistics"]}
};
function setStatus(message, tone="neutral"){const node=$("axFpStatus");if(node){node.textContent=message;node.dataset.tone=tone;}}
function setOfflineBadge(){
 const node=$("axOfflineStatus"); if(!node)return;
 node.textContent=navigator.onLine?"LOCAL DATA · OFFLINE PACK READY":"OFFLINE MODE · LOCAL DATA ACTIVE";
 node.dataset.online=navigator.onLine?"true":"false";
}
function download(name,content,type="application/json"){
 const blob=new Blob([content],{type}),url=URL.createObjectURL(blob),a=document.createElement("a");
 a.href=url;a.download=name;a.click();setTimeout(()=>URL.revokeObjectURL(url),1200);
}
async function fetchLocal(path){const r=await fetch(path,{cache:"no-store"});if(!r.ok)throw new Error(path+" returned "+r.status);return r.json();}
async function loadData(){
 const paths=["./data/agents/candidate_catalog.json","./data/power/index.json","./data/pakistan/imagery/index.json","./data/terrain/terrain_comparison.json","./data/moon/shackleton_lola_80m.json","./data/moon/shackleton_diviner_prp.json"];
 const values=await Promise.all(paths.map(fetchLocal));
 state.catalog=values[0];state.powerIndex=values[1];state.imagery=values[2];state.terrain=values[3];state.lunar=values[4];state.diviner=values[5];
 const select=$("axFpSite");select.innerHTML=state.catalog.candidate_sites.map(s=>"<option value='"+esc(s.id)+"'>"+esc(s.name)+" · "+esc(s.country)+"</option>").join("");
 select.value="chagai_small_playas";
 $("axFpSite").addEventListener("change",()=>{state.selected=null;renderAssessment();renderProtocol();});
 $("axFpTarget").addEventListener("change",renderAssessment);
 $("axFpObjective").addEventListener("change",()=>{renderAssessment();renderProtocol();});
 $("axFpStrictness").addEventListener("change",renderAssessment);
 $("axFpExportDossier").addEventListener("click",exportDossier);
 $("axFpPrint").addEventListener("click",()=>window.print());
 $("axFpLocate").addEventListener("click",locate);
 $("axFpSaveRecord").addEventListener("click",saveRecord);
 $("axFpExportJson").addEventListener("click",exportJson);
 $("axFpExportGeoJson").addEventListener("click",exportGeoJson);
 $("axFpExportCsv").addEventListener("click",exportCsv);
 $("axFpImport").addEventListener("change",importJson);
 $("axFpBackendUrl").addEventListener("input",syncButtonState);
 $("axFpSync").addEventListener("click",syncRecords);
 $("axFpRecords").addEventListener("click",recordAction);
 renderAssessment();renderProtocol();await refreshRecords();syncButtonState();
 setStatus("All six science references loaded from the project bundle · no external data call","good");
}
function sitePowerId(id){return POWER_ALIAS[id]||id;}
function sitePower(id){return state.powerIndex?.records?.[sitePowerId(id)]||null;}
function siteImage(id){return state.imagery?.sites?.[id]||null;}
function siteTerrain(id){return state.terrain?.earth_sites?.[id]||null;}
function siteRecord(id){return state.catalog?.candidate_sites?.find(x=>x.id===id)||null;}
function targetRecord(target){
 if(target==="Moon")return {name:"Shackleton Rim / lunar south pole",coverage:state.lunar?.matched_coarse_support_approx_925m?.elevation_coverage_percent,terrain:"NASA LRO LOLA 80 m / ~925 m regional profile",thermal:"Diviner PRP V2.0 processed for 6,823 Shackleton-window triangles",thermalStats:state.diviner?.results};
 return {name:"Nili Patera / Syrtis Major, Mars",coverage:state.terrain?.planetary_target?.terrain_metrics?.coverage?.valid_percent,terrain:"NASA MGS MOLA MEGDR 64 ppd / ~925 m regional profile",thermal:"Mars thermal / atmospheric resource profile not integrated"};
}
function assess(id,target,objective,strictness){
 const site=siteRecord(id);if(!site)return null;
 const tasks=(site.rehearsal_tasks||[]).join(" ").toLowerCase();
 const tags=(site.environment_tags||[]).join(" ").toLowerCase();
 const rule=OBJECTIVES[objective]||OBJECTIVES.terrain;
 const matches=rule.terms.filter(t=>tasks.includes(t)||tags.includes(t));
 const missionEligible=target==="Both"?(site.mission_targets||[]).length>0:(site.mission_targets||[]).includes(target);
 const power=sitePower(id),image=siteImage(id),terrain=siteTerrain(id);
 const evidence=[
  {key:"source",label:"Traceable source references",available:(site.source_references||[]).length>0,detail:(site.source_references||[]).length+" linked source(s); supports the stated historical or institutional context, not necessarily a measured site property."},
  {key:"climate",label:"NASA POWER climatology",available:!!power,detail:power?(power.valid_parameters||[]).length+" parameters recorded; gridded climate context, not a surface-temperature or dust-flux measurement.":"No local NASA POWER snapshot in the published bundle."},
  {key:"spectral",label:"Site-specific Sentinel-2 evidence",available:!!image||!!site.measured_context?.sentinel2,detail:image?"Processed site screen available; reflectance indices are screening descriptors, not mineral identification.":site.measured_context?.sentinel2?"Scene-level spectral context is recorded; inspect coverage and dates.":"No site-specific Sentinel-2 processing is included for this reference."},
  {key:"terrain",label:"Processed terrain profile",available:terrain?.status==="processed",detail:terrain?.status==="processed"?"Copernicus DEM GLO-30 DSM regional profile at ~925 m support; not rover-scale roughness or bare-earth elevation.":"No site-specific processed terrain profile in this release."},
  {key:"geology",label:"Geology / material context",available:!!(site.evidence_status?.geology||site.evidence_status?.historical_geologic_context||site.source_references?.length),detail:site.evidence_status?.geology||site.evidence_status?.historical_geologic_context||"References provide context only; no site-scale mineral or geochemical map is integrated."},
  {key:"ground",label:"Field measurements / ground truth",available:false,detail:"No field station observations or laboratory analyses are bundled. Log new observations below; do not treat the proposed protocol as collected data."}
 ];
 const layerCount=evidence.filter(x=>x.available).length;
 const taskMatch=matches.length>0;
 const strictReady=missionEligible&&taskMatch&&["source","climate","spectral","terrain"].every(k=>evidence.find(e=>e.key===k)?.available);
 let verdict, tone;
 if(!missionEligible){verdict="MISSION-TAG MISMATCH · exploratory comparison only";tone="warning";}
 else if(!taskMatch){verdict="NO DOCUMENTED TASK OVERLAP · do not claim a direct rehearsal match";tone="warning";}
 else if(strictReady){verdict="STRICT EVIDENCE LEAD · suitable for the next field-validation stage, not a validated planetary analog";tone="good";}
 else if(layerCount>=3){verdict="CONDITIONAL FIELD-REHEARSAL CANDIDATE · multiple evidence layers, with material gaps";tone="good";}
 else{verdict="EXPLORATORY RESEARCH LEAD · insufficient evidence for a stronger claim";tone="warning";}
 const targetData=target==="Both"?[targetRecord("Moon"),targetRecord("Mars)".slice(0,-1))]:[targetRecord(target)];
 const claims=[
  {name:"A specific field method can be rehearsed here",ok:missionEligible&&taskMatch,why:missionEligible&&taskMatch?"The candidate record documents a task/environment overlap. Treat this as a research hypothesis.":"The selected site has no documented direct overlap with this target/objective."},
  {name:"The target mineral / salt / ice deposit is confirmed",ok:false,why:"No project-integrated field chemistry, mineral identification, subsurface profile or validated resource measurement supports this claim."},
  {name:"The site reproduces the planetary environment",ok:false,why:"Earth cannot reproduce lunar vacuum/reduced gravity/radiation or the Martian atmosphere/radiation environment."},
  {name:"The site is safe for landing, rovers or crews",ok:false,why:"No engineering-grade trafficability, surface strength, slope hazard, radiation or access/safety assessment is performed."},
  {name:"The comparison is rover-scale",ok:false,why:"The shared terrain comparison is approximately 925 m support; it is regional reconnaissance, not rover-scale hazard resolution."}
 ];
 const limitations=[...(site.non_transferable||[])];
 if(!limitations.length)limitations.push("No single Earth site reproduces the full Moon/Mars environment.");
 if(!evidence.find(x=>x.key==="ground").available)limitations.push("Field validation and independent specialist review are still required.");
 if(target==="Moon")limitations.push("The lunar PRP ice-depth variable is a thermal-model stability diagnostic, not direct ice detection, abundance or accessibility.");
 if(target==="Mars")limitations.push("Nili Patera MOLA coverage is 50.53% (567/1,122 observed cells; 87 complete 3×3 neighbourhoods); keep its profile provisional.");
 const readiness=strictness==="strict"?(strictReady?"Strict data gates passed; field validation is still absent.":"Strict evidence gate not passed; at least one required direct layer is missing."):(taskMatch?"Exploratory task overlap is present; weaker contextual evidence is allowed and must remain labelled.":"No direct rehearsal task overlap is documented.");
 return {site,target,objective,rule,matches,missionEligible,taskMatch,evidence,layerCount,strictReady,verdict,tone,claims,limitations,targetData,readiness,generatedAt:new Date().toISOString(),strictness};
}
function renderAssessment(){
 const id=$("axFpSite").value,target=$("axFpTarget").value,objective=$("axFpObjective").value,strictness=$("axFpStrictness").value;
 const a=assess(id,target,objective,strictness);state.assessment=a;if(!a)return;
 const site=a.site;
 $("axFpVerdict").innerHTML="<span class='axFpVerdictLabel'>"+esc(a.verdict)+"</span><p>"+esc(site.name)+" · "+esc(a.rule.label)+" · "+esc(target==="Both"?"Moon + Mars":target)+"</p><div class='axFpCounts'><b>"+a.layerCount+" / 6</b><small>evidence layers present · not an analogy score</small></div>";
 $("axFpEvidence").innerHTML=a.evidence.map(e=>"<article class='axFpEvidenceRow'><span class='axFpState "+(e.available?"present":"missing")+"'>"+(e.available?"AVAILABLE":"NOT PRESENT")+"</span><div><b>"+esc(e.label)+"</b><p>"+esc(e.detail)+"</p></div></article>").join("");
 $("axFpClaims").innerHTML=a.claims.map(c=>"<article class='axFpClaim'><span class='axFpState "+(c.ok?"present":"missing")+"'>"+(c.ok?"SUPPORTED AS A HYPOTHESIS":"NOT DEMONSTRATED")+"</span><div><b>"+esc(c.name)+"</b><p>"+esc(c.why)+"</p></div></article>").join("");
 $("axFpLimits").innerHTML=a.limitations.map(x=>"<li>"+esc(x)+"</li>").join("");
 $("axFpRobustness").textContent=a.readiness;
 const td=a.targetData.map(t=>"<article><b>"+esc(t.name)+"</b><p>"+esc(t.terrain)+"</p><p>Observed / valid-cell coverage: "+(Number.isFinite(t.coverage)?t.coverage.toFixed(2)+"%":"not supplied")+"</p><small>"+esc(t.thermal)+"</small></article>").join("");
 $("axFpPlanetary").innerHTML=td;
 $("axFpSiteMeta").textContent=(site.discovery_tier||"candidate").replaceAll("_"," ")+" · "+(site.candidate_status||"status not supplied").replaceAll("_"," ");
}
function protocolFor(site,objective){
 const id=site.id;
 const common=[
  ["01 · Pre-field verification","Confirm the exact study polygon, access permissions, land ownership/protected-area rules, current hazards and local partner approval. The catalogue coordinate/AOI is a screening reference, not a surveyed boundary."],
  ["02 · Station control","Record WGS84 GNSS coordinates, UTC timestamp, coordinate uncertainty, operator, instrument make/model, calibration state, geotagged overview and close-up photographs."],
  ["03 · Repeatable observations","Use a consistent station identifier, observation method, units and field notes. Record non-detections and missing measurements rather than filling them with estimates."],
  ["04 · Quality and custody","Use field duplicates, blanks and instrument checks where appropriate. Photograph labels, maintain sample chain-of-custody and document any deviation from the plan."],
  ["05 · Close-out","Export GeoJSON and CSV, preserve the original photos/notes, and have a domain specialist review the interpretation before upgrading any candidate status."]
 ];
 let specialised=[];
 if(objective==="playa"||id==="chagai_small_playas"||id==="hamun_i_mashkel"){
  specialised=[
   ["Playa boundary and facies","Map the actual playa edge, surface crust, polygons, channels, alluvial margins and transition to surrounding terrain. Repeat after wet and dry periods where safe and permitted."],
   ["Sediment and salt sampling","Record crust thickness only where measured, grain size, moisture, colour and sedimentary structures. Collect representative samples under an approved sampling plan; do not label a material as a mineral or brine without laboratory confirmation."],
   ["On-site screening and lab confirmation","Where trained staff and equipment are available, measure electrical conductivity, pH and temperature with calibrated instruments. Use laboratory XRD/XRF/ion analysis to test mineralogy and soluble-salt composition; these are proposed methods, not current project measurements."]
  ];
 }else if(objective==="volcanic"||id==="koh_i_sultan"){
  specialised=[
   ["Outcrop and lithology logging","Record mapped unit, contact, grain size, alteration, fracture/vesicle context, weathering and sample position. Distinguish regional map context from the lithology actually observed at each station."],
   ["Spectral-to-ground validation","Collect calibrated field spectra and co-located photographs where equipment is available. Compare with Sentinel-2 screening only after atmospheric, illumination and surface-mixture limitations are recorded."],
   ["Laboratory checks","Use qualified petrography and XRD/XRF analyses to verify lithology and alteration minerals. Do not infer basaltic equivalence from a volcanic landscape or RGB colour."]
  ];
 }else if(objective==="cryosphere"||id==="hispar_glacier"){
  specialised=[
   ["Ice/debris boundary observations","Map visible snow, clean ice, debris cover, meltwater and exposed substrate separately. Record season, illumination and recent weather context."],
   ["Repeat observations","Use repeat GNSS/photo stations and time-stamped imagery to quantify boundary changes. Document sensor/field uncertainty."],
   ["Safety and transferability","Use local glacier-safety guidance and trained personnel. The glacier is a cold-region field-method analogue, not a lunar permanently shadowed region."]
  ];
 }else{
  specialised=[
   ["Terrain transect","Record route geometry, slope/aspect, surface type, obstacles and instrument position at each station. Use a field survey instrument appropriate to the required resolution."],
   ["Resolution check","Compare field measurements with the ~925 m regional terrain context. Do not infer rover-scale mobility from the current gridded profile."],
   ["Repeatability","Run a duplicate transect or independent observer check where practical; preserve raw GNSS and instrument records."]
  ];
 }
 return [...common.slice(0,1),...specialised,...common.slice(1)];
}
function renderProtocol(){
 const site=siteRecord($("axFpSite").value);if(!site)return;
 const obj=$("axFpObjective").value;
 $("axFpProtocolTitle").textContent=site.name+" · "+OBJECTIVES[obj].label;
 $("axFpProtocol").innerHTML=protocolFor(site,obj).map((x,i)=>"<article class='axFpProtocolStep'><span>"+String(i+1).padStart(2,"0")+"</span><div><b>"+esc(x[0])+"</b><p>"+esc(x[1])+"</p></div></article>").join("");
 const lat=site.latitude,lon=site.longitude;
 if(!$("axFpLat").value)$("axFpLat").value=Number.isFinite(lat)?lat:"";
 if(!$("axFpLon").value)$("axFpLon").value=Number.isFinite(lon)?lon:"";
 if(!$("axFpStationId").value)$("axFpStationId").value=site.id.toUpperCase()+"-ST-001";
}
function exportDossier(){
 if(!state.assessment)return;
 const a=state.assessment;
 const payload={product:"ANALOG-X Field Evidence Passport",schema_version:"1.0",claim_stress_test:a,field_protocol:protocolFor(a.site,a.objective),disclaimer:"Offline research decision aid. This is not a validated analog certification, resource detection or safety assessment."};
 download("ANALOG-X_Claim_Stress_Test_"+a.site.id+".json",JSON.stringify(payload,null,2));
}
function openDb(){
 if(!("indexedDB" in window))return Promise.resolve(null);
 if(state.db)return Promise.resolve(state.db);
 return new Promise((resolve,reject)=>{
  const req=indexedDB.open(DB_NAME,DB_VERSION);
  req.onupgradeneeded=()=>{const db=req.result;if(!db.objectStoreNames.contains(STORE)){const s=db.createObjectStore(STORE,{keyPath:"id"});s.createIndex("site_id","site_id",{unique:false});s.createIndex("observed_at","observed_at",{unique:false});}};
  req.onsuccess=()=>{state.db=req.result;resolve(state.db);};req.onerror=()=>reject(req.error);
 });
}
function storeTx(mode,action){
 return openDb().then(db=>{
  if(!db)throw new Error("IndexedDB unavailable");
  return new Promise((resolve,reject)=>{const tx=db.transaction(STORE,mode),store=tx.objectStore(STORE);let req;
   if(action.type==="getAll")req=store.getAll();
   else if(action.type==="put")req=store.put(action.value);
   else if(action.type==="delete")req=store.delete(action.id);
   req.onsuccess=()=>resolve(req.result);req.onerror=()=>reject(req.error);tx.onabort=()=>reject(tx.error||new Error("Storage transaction failed"));
  });
 });
}
function localFallbackRead(){try{return JSON.parse(localStorage.getItem("analogx_fp_records")||"[]");}catch{return [];}}
function localFallbackWrite(records){localStorage.setItem("analogx_fp_records",JSON.stringify(records));}
async function getAllRecords(){
 try{return await storeTx("readonly",{type:"getAll"});}
 catch{return localFallbackRead();}
}
async function refreshRecords(){
 state.records=await getAllRecords();
 $("axFpRecordCount").textContent=state.records.length+" local station record(s)";
 $("axFpRecords").innerHTML=state.records.length?state.records.slice().sort((a,b)=>String(b.observed_at).localeCompare(String(a.observed_at))).map(r=>"<article class='axFpRecord'><div><b>"+esc(r.station_id||r.id)+" · "+esc(r.site_name||r.site_id)+"</b><small>"+esc(r.observed_at||"date not supplied")+" · "+esc(r.observation_type||"observation")+"</small><p>"+esc(r.notes||r.value===null?"Field note saved":String(r.value??"No numeric reading")+" "+String(r.unit||""))+"</p></div><button class='axFpDelete' data-delete-record='"+esc(r.id)+"'>DELETE</button></article>").join(""):"<p class='axFpEmpty'>No field observations recorded yet. Save real observations here; the project never inserts synthetic field measurements.</p>";
}
async function saveRecord(){
 const site=siteRecord($("axFpSite").value),lat=Number($("axFpLat").value),lon=Number($("axFpLon").value);
 if(!site||!Number.isFinite(lat)||lat< -90||lat>90||!Number.isFinite(lon)||lon< -180||lon>180){setStatus("Enter a valid site and WGS84 station coordinate before saving.","warning");return;}
 const file=$("axFpPhoto").files?.[0]||null;
 if(file&&file.size>4*1024*1024){setStatus("Photo exceeds 4 MB. Resize it before adding it to the offline record.","warning");return;}
 const reading=$("axFpValue").value.trim();
 const record={id:(crypto.randomUUID?crypto.randomUUID():"ax-"+Date.now()+"-"+Math.random().toString(16).slice(2)),site_id:site.id,site_name:site.name,station_id:$("axFpStationId").value.trim()||site.id+"-ST",observed_at:$("axFpObservedAt").value||new Date().toISOString(),latitude:lat,longitude:lon,observation_type:$("axFpType").value,value:reading===""?null:Number(reading),value_text:reading===""?"":reading,unit:$("axFpUnit").value,method:$("axFpMethod").value.trim(),notes:$("axFpNotes").value.trim(),photo:file||null,created_at:new Date().toISOString(),sync_status:"local-only"};
 if(reading!==""&&!Number.isFinite(record.value)){setStatus("Reading must be numeric, or leave it blank and describe the observation in notes.","warning");return;}
 try{await storeTx("readwrite",{type:"put",value:record});}
 catch{const rows=localFallbackRead();rows.push({...record,photo:null});localFallbackWrite(rows);}
 $("axFpNotes").value="";$("axFpValue").value="";$("axFpPhoto").value="";
 await refreshRecords();setStatus("Station record saved on this device. It has not been uploaded or verified.","good");
}
function locate(){
 if(!navigator.geolocation){setStatus("This browser does not offer geolocation. Enter the WGS84 coordinate manually.","warning");return;}
 setStatus("Requesting device location permission…");
 navigator.geolocation.getCurrentPosition(pos=>{$("axFpLat").value=pos.coords.latitude.toFixed(6);$("axFpLon").value=pos.coords.longitude.toFixed(6);setStatus("Device coordinates filled. Accuracy ±"+Math.round(pos.coords.accuracy)+" m; confirm the station position before saving.","good");},err=>setStatus("Location unavailable: "+err.message+" · manual coordinates remain available.","warning"),{enableHighAccuracy:true,timeout:12000,maximumAge:0});
}
function recordAction(e){
 const b=e.target.closest("[data-delete-record]");if(!b)return;
 const id=b.dataset.deleteRecord;
 if(!confirm("Delete this local field record from this device?"))return;
 storeTx("readwrite",{type:"delete",id}).catch(()=>{localFallbackWrite(localFallbackRead().filter(x=>x.id!==id));}).then(refreshRecords);
}
function blobToDataUrl(blob){return new Promise((resolve,reject)=>{const r=new FileReader();r.onload=()=>resolve(r.result);r.onerror=()=>reject(r.error);r.readAsDataURL(blob);});}
function dataUrlToBlob(url){const [meta,data]=url.split(",");const mime=(meta.match(/data:([^;]+)/)||[])[1]||"application/octet-stream";const raw=atob(data);const arr=new Uint8Array(raw.length);for(let i=0;i<raw.length;i++)arr[i]=raw.charCodeAt(i);return new Blob([arr],{type:mime});}
async function serializableRecords(){
 const rows=await getAllRecords();
 return Promise.all(rows.map(async r=>{const copy={...r};if(copy.photo instanceof Blob){copy.photo_data_url=await blobToDataUrl(copy.photo);delete copy.photo;}return copy;}));
}
async function exportJson(){const payload={schema_version:"1.0",product:"ANALOG-X Field Evidence Passport",exported_at:new Date().toISOString(),records:await serializableRecords(),note:"User-entered field records only; no synthetic measurements are generated."};download("ANALOG-X_Field_Evidence_Passport.json",JSON.stringify(payload,null,2));}
function csvCell(v){return '"'+String(v??"").replace(/"/g,'""')+'"';}
async function exportCsv(){
 const rows=await getAllRecords();const headers=["id","site_id","site_name","station_id","observed_at","latitude","longitude","observation_type","value","value_text","unit","method","notes","sync_status"];
 const lines=[headers.join(","),...rows.map(r=>headers.map(k=>csvCell(r[k])).join(","))];
 download("ANALOG-X_Field_Stations.csv",lines.join("\r\n"),"text/csv");
}
async function exportGeoJson(){
 const rows=await getAllRecords();
 const features=rows.map(r=>({type:"Feature",geometry:{type:"Point",coordinates:[r.longitude,r.latitude]},properties:Object.fromEntries(Object.entries(r).filter(([k])=>k!=="photo"))}));
 download("ANALOG-X_Field_Stations.geojson",JSON.stringify({type:"FeatureCollection",name:"ANALOG-X field observations",features},null,2),"application/geo+json");
}
async function importJson(event){
 const file=event.target.files?.[0];if(!file)return;
 try{
  if(file.size>12*1024*1024)throw new Error("Import file is over 12 MB.");
  const payload=JSON.parse(await file.text()),rows=Array.isArray(payload)?payload:payload.records;
  if(!Array.isArray(rows))throw new Error("Expected a records array.");
  let count=0;
  for(const raw of rows.slice(0,500)){
   if(!raw||!siteRecord(raw.site_id)||!Number.isFinite(Number(raw.latitude))||!Number.isFinite(Number(raw.longitude))||Number(raw.latitude)<-90||Number(raw.latitude)>90||Number(raw.longitude)<-180||Number(raw.longitude)>180)continue;
   const r={...raw};if(r.photo_data_url){r.photo=dataUrlToBlob(r.photo_data_url);delete r.photo_data_url;}
   await storeTx("readwrite",{type:"put",value:r});count++;
  }
  await refreshRecords();setStatus(count+" valid record(s) imported locally. Review provenance before using them scientifically.","good");
 }catch(e){setStatus("Import failed: "+e.message,"warning");}
 finally{event.target.value="";}
}
function syncButtonState(){
 const url=$("axFpBackendUrl").value.trim();$("axFpSync").disabled=!url;
}
async function syncRecords(){
 const url=$("axFpBackendUrl").value.trim().replace(/\/+$/,"");if(!url)return;
 const rows=await getAllRecords();if(!rows.length){setStatus("There are no local records to sync.","warning");return;}
 const key=$("axFpApiKey").value.trim();
 try{
  const response=await fetch(url+"/api/v1/field-records/bulk",{method:"POST",headers:{"Content-Type":"application/json",...(key?{"Authorization":"Bearer "+key}:{})},body:JSON.stringify({records:rows.map(r=>({...r,photo:undefined}))})});
  const data=await response.json();if(!response.ok)throw new Error(data.detail||"Backend returned HTTP "+response.status);
  setStatus((data.accepted??rows.length)+" record(s) synced to the configured self-hosted backend.","good");
 }catch(e){setStatus("Sync unavailable. Your offline records remain on this device. "+e.message,"warning");}
}
function initPwa(){
 setOfflineBadge();window.addEventListener("online",setOfflineBadge);window.addEventListener("offline",setOfflineBadge);
 if("serviceWorker" in navigator){navigator.serviceWorker.register("./service-worker.js",{scope:"./"}).then(()=>setStatus("Offline app shell and science data are being cached on this device.","good")).catch(e=>setStatus("Offline cache could not start: "+e.message,"warning"));}
}
async function init(){
 if(!$("fieldPassport"))return;
 $("axFpObservedAt").value=new Date().toISOString().slice(0,16);
 initPwa();
 try{await loadData();}catch(e){setStatus("Bundled science data could not load: "+e.message+" · reconnect once to install the offline pack.","warning");}
}
if(document.readyState==="loading")document.addEventListener("DOMContentLoaded",init,{once:true});else init();
})();
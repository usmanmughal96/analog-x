"use strict";
const CACHE_VERSION="analogx-offline-v4";
const APP_CACHE=CACHE_VERSION+"-app";
const DATA_CACHE=CACHE_VERSION+"-data";
const APP_FILES=[
 "./","./index.html","./demo.html","./transferability.html","./discovery.html","./manifest.webmanifest",
 "./assets/analogx-labs.js?v=20261115-offline",
 "./assets/analogx-labs.css?v=20261115-offline",
 "./assets/analogx-scout.css?v=20261114-portalfix",
 "./assets/analogx-field-passport.js?v=20261115-offline",
 "./assets/analogx-field-passport.css?v=20261115-offline"
];
const DATA_FILES=[
 "./data/agents/candidate_catalog.json","./data/transferability/transferability.json","./data/analog_benchmark/regional_window_scan.json",
 "./data/planetary/pds_search.json","./data/nasa/modis_browse_index.json","./data/power/index.json",
 "./data/power/koh.json","./data/power/dallol.json","./data/power/atacama.json",
 "./data/power/mcmurdo.json","./data/power/haughton.json","./data/power/iceland.json",
 "./data/power/death.json","./data/power/hispar_glacier.json",
 "./data/power/chagai_small_playas.json","./data/power/hamun_i_mashkel.json",
 "./data/pakistan/imagery/index.json","./data/pakistan/quicklooks/index.json",
 "./data/terrain/terrain_comparison.json","./data/moon/shackleton_lola_80m.json",
 "./data/moon/shackleton_diviner_prp.json","./data/nasa/earthdata_cmr_catalog.json",
 "./data/pakistan/quicklooks/chagai_small_playas.png",
 "./data/pakistan/quicklooks/hamun_i_mashkel.png",
 "./data/pakistan/quicklooks/hispar_glacier.png",
 "./data/pakistan/quicklooks/koh_i_sultan.png",
 "./data/terrain/chagai_small_playas_copdem_hillshade.png",
 "./data/terrain/hamun_i_mashkel_copdem_hillshade.png",
 "./data/terrain/hispar_glacier_copdem_hillshade.png",
 "./data/terrain/koh_i_sultan_copdem_hillshade.png",
 "./data/terrain/nili_patera_mola_hillshade.png",
 "./data/moon/shackleton_lola_80m_elevation_preview.png",
 "./data/nasa/modis_browse/atacama_1.jpg",
 "./data/nasa/modis_browse/atacama_2.jpg",
 "./data/nasa/modis_browse/chagai_small_playas_1.jpg",
 "./data/nasa/modis_browse/chagai_small_playas_2.jpg",
 "./data/nasa/modis_browse/dallol_1.jpg",
 "./data/nasa/modis_browse/dallol_2.jpg",
 "./data/nasa/modis_browse/death_1.jpg",
 "./data/nasa/modis_browse/death_2.jpg",
 "./data/nasa/modis_browse/hamun_i_mashkel_1.jpg",
 "./data/nasa/modis_browse/hamun_i_mashkel_2.jpg",
 "./data/nasa/modis_browse/haughton_1.jpg",
 "./data/nasa/modis_browse/haughton_2.jpg",
 "./data/nasa/modis_browse/hispar_glacier_1.jpg",
 "./data/nasa/modis_browse/hispar_glacier_2.jpg",
 "./data/nasa/modis_browse/iceland_1.jpg",
 "./data/nasa/modis_browse/iceland_2.jpg",
 "./data/nasa/modis_browse/koh_i_sultan_1.jpg",
 "./data/nasa/modis_browse/koh_i_sultan_2.jpg",
 "./data/nasa/modis_browse/mcmurdo_1.jpg",
 "./data/nasa/modis_browse/mcmurdo_2.jpg"
];
self.addEventListener("install",(event)=>{
 event.waitUntil((async()=>{
  const app=await caches.open(APP_CACHE); await app.addAll(APP_FILES);
  const data=await caches.open(DATA_CACHE);
  await Promise.all(DATA_FILES.map(async path=>{try{const response=await fetch(path,{cache:"reload"});if(response.ok)await data.put(path,response);}catch{}}));
  await self.skipWaiting();
 })());
});
self.addEventListener("activate",(event)=>{
 event.waitUntil((async()=>{
  const keys=await caches.keys();
  await Promise.all(keys.filter(key=>key.startsWith("analogx-")&&!key.startsWith(CACHE_VERSION)).map(key=>caches.delete(key)));
  await self.clients.claim();
 })());
});
self.addEventListener("fetch",(event)=>{
 const request=event.request;if(request.method!=="GET")return;
 const url=new URL(request.url);if(url.origin!==self.location.origin)return;
 if(request.mode==="navigate"){
  event.respondWith((async()=>{try{const response=await fetch(request);const cache=await caches.open(APP_CACHE);cache.put("./index.html",response.clone());return response;}catch{return (await caches.match(request))||(await caches.match("./index.html"))||Response.error();}})());return;
 }
 event.respondWith((async()=>{
  const cached=await caches.match(request)||await caches.match(url.pathname);if(cached)return cached;
  try{const response=await fetch(request);if(response.ok){const cache=await caches.open(url.pathname.includes("/data/")?DATA_CACHE:APP_CACHE);cache.put(request,response.clone());}return response;}
  catch{return request.destination==="image"?new Response("",{status:504,statusText:"Offline image not cached"}):Response.error();}
 })());
});

// Offline support. Pages: network first (always newest), cache as backup. Icons/manifest: cache first.
const C='gtb-v2',FILES=['./','index.html','manifest.webmanifest','icon-192.png','icon-512.png'];
self.addEventListener('install',e=>{e.waitUntil(caches.open(C).then(c=>c.addAll(FILES)));self.skipWaiting()});
self.addEventListener('activate',e=>e.waitUntil(caches.keys().then(k=>Promise.all(k.filter(x=>x!==C).map(x=>caches.delete(x)))).then(()=>self.clients.claim())));
self.addEventListener('fetch',e=>{if(e.request.method!=='GET')return;
  const page=e.request.mode==='navigate';
  if(page){e.respondWith(fetch(e.request).then(n=>{const cp=n.clone();caches.open(C).then(c=>c.put('./',cp));return n}).catch(()=>caches.match('./')));return}
  e.respondWith(caches.match(e.request,{ignoreSearch:true}).then(r=>r||fetch(e.request)))});

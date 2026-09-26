const properties = [
  {price:"ETB 12,500,000", title:"3 Bed Apartment", location:"Bole, Addis Ababa", meta:"3 Beds • 2 Baths • 150 sqm", status:"For Sale", image:"assets/property-bole.jpg"},
  {price:"ETB 18,000,000", title:"4 Bed Apartment", location:"Kazanchis, Addis Ababa", meta:"4 Beds • 3 Baths • 220 sqm", status:"For Sale", image:"assets/property-kazanchis.jpg"},
  {price:"ETB 8,500,000", title:"3 Bed House", location:"Ayat, Addis Ababa", meta:"3 Beds • 2 Baths • 180 sqm", status:"For Sale", image:"assets/property-ayat.jpg"},
  {price:"ETB 25,000,000", title:"4 Bed Villa", location:"Summit, Addis Ababa", meta:"4 Beds • 4 Baths • 300 sqm", status:"For Sale", image:"assets/property-summit.jpg"},
  {price:"ETB 9,800,000", title:"3 Bed Apartment", location:"CMC, Addis Ababa", meta:"3 Beds • 2 Baths • 140 sqm", status:"For Sale", image:"assets/property-kera.jpg"},
  {price:"ETB 15,000,000", title:"Commercial Space", location:"Kera, Addis Ababa", meta:"180 sqm • Commercial", status:"For Sale", image:"assets/project-sites.jpg"},
  {price:"ETB 11,900,000", title:"3 Bed Apartment", location:"Megenagna, Addis Ababa", meta:"3 Beds • 2 Baths • 145 sqm", status:"For Sale", image:"assets/project-residence.jpg"}
];

const tones = {
  one:"linear-gradient(145deg,#0d3f23,#b68a29)",
  two:"linear-gradient(145deg,#1e5b35,#b8c9bd)",
  three:"linear-gradient(145deg,#315c43,#d0b45b)",
  four:"linear-gradient(145deg,#183f2a,#789b84)",
  five:"linear-gradient(145deg,#96742a,#16492b)",
  six:"linear-gradient(145deg,#2c6941,#c5a24b)",
  seven:"linear-gradient(145deg,#6c7e63,#163f28)",
  eight:"linear-gradient(145deg,#214f33,#b59643)"
};

function renderProperties(list=properties){
  const grid=document.getElementById("propertyGrid");
  grid.innerHTML=list.map((p,i)=>`
    <article class="property-card">
      <div class="property-image" style="background-image:url("\${p.image}")"><span class="badge">${p.status}</span></div>
      <div class="property-body">
        <div class="price">${p.price}</div>
        <h3>${p.title}</h3>
        <p>${p.location}</p>
        <div class="meta">${p.meta.split(" • ").map(x=>`<span>${x}</span>`).join("")}</div>
        <button onclick="notify('${p.title} — ${p.location}')">View Details</button>
      </div>
    </article>`).join("");
}
renderProperties();

document.querySelectorAll(".tab").forEach(tab=>{
  tab.addEventListener("click",()=>{
    document.querySelectorAll(".tab").forEach(t=>t.classList.remove("active"));
    tab.classList.add("active");
  });
});

function runSearch(){
  const q=document.getElementById("searchInput").value.trim().toLowerCase();
  const loc=document.getElementById("location").value.toLowerCase();
  const type=document.getElementById("type").value.toLowerCase();
  const result=document.getElementById("searchResult");
  let filtered=properties.filter(p=>{
    const text=(p.title+" "+p.location+" "+p.meta).toLowerCase();
    return (!q || text.includes(q) || q.split(" ").some(w=>w.length>3 && text.includes(w))) &&
           (loc==="any location" || p.location.toLowerCase().includes(loc)) &&
           (type==="any type" || p.title.toLowerCase().includes(type) || (type==="commercial" && p.title.toLowerCase().includes("commercial")));
  });
  renderProperties(filtered.length ? filtered : properties);
  result.style.display="block";
  result.textContent=filtered.length ? `Found ${filtered.length} matching properties.` : "No exact match — showing our latest properties.";
  document.getElementById("properties").scrollIntoView({behavior:"smooth"});
}

function toggleMenu(){document.getElementById("mobileMenu").classList.toggle("show")}
function toggleLang(){alert("Language selector ready — English is active in this starter.")}
function notify(message){alert(message+"\\n\\nConnect this action to your real property database later.")}
function submitContact(e){
  e.preventDefault();
  document.getElementById("formMessage").textContent="Message captured. Connect this form to your email/CRM endpoint when you are ready.";
  e.target.reset();
}


async function applyLiveSite(){
  try{
    const r=await fetch('/api/site?_=' + Date.now(), {cache:'no-store', headers:{'Cache-Control':'no-cache'}});
    if(!r.ok) return;
    const d=await r.json();
    const cacheBust='?v=' + Date.now();
    const hero=document.querySelector('.hero');
    if(hero){
      let v=document.getElementById('heroBackgroundVideo');
      if(d.hero_video){
        if(!v){
          v=document.createElement('video');
          v.id='heroBackgroundVideo';
          v.autoplay=true; v.muted=true; v.loop=true; v.playsInline=true;
          v.setAttribute('aria-hidden','true');
          hero.prepend(v);
        }
        v.pause();
        v.src=d.hero_video + (d.hero_video.includes('?')?'&':'?') + 'v=' + Date.now();
        v.style.display='block';
        hero.style.backgroundImage='none';
        v.load();
        v.play().catch(()=>{});
      } else {
        if(v){ v.pause(); v.removeAttribute('src'); v.load(); v.style.display='none'; }
        hero.style.backgroundImage=`url("${(d.hero_image || 'assets/hero-background.jpg')}${(d.hero_image||'').includes('?')?'&':'?'}v=${Date.now()}")`;
      }
    }
    const setImg=(selector,url)=>{ const el=document.querySelector(selector); if(el&&url) el.src=url+(url.includes('?')?'&':'?')+'v='+Date.now(); };
    setImg('.agent-photo img',d.sales_officer_image);
    setImg('.team-photo img',d.meet_mahlet_image);
    setImg('.featured-project-image img',d.featured_image);
    document.querySelectorAll('[data-live-phone]').forEach(el=>{el.textContent=d.phone; if(el.tagName==='A') el.href='tel:'+d.phone.replace(/\s/g,'');});
    document.querySelectorAll('[data-live-telegram]').forEach(el=>{el.textContent=d.telegram_user; if(el.tagName==='A') el.href=d.telegram;});
    if(d.investment_message){ const el=document.querySelector('[data-investment-message]'); if(el) el.textContent=d.investment_message; }
    if(d.diaspora_message){ const el=document.querySelector('[data-diaspora-message]'); if(el) el.textContent=d.diaspora_message; }
    properties.forEach(p=>{
      const file=(p.image||'').split('/').pop();
      const key=file.replace(/^property-/, '').replace(/\.(jpg|jpeg|png|webp|gif)$/i,'');
      if(d.property_images && d.property_images[key]) p.image=d.property_images[key] + (d.property_images[key].includes('?')?'&':'?') + 'v=' + Date.now();
    });
    renderProperties();
  }catch(e){ console.warn('Live site settings unavailable',e); }
}
applyLiveSite();

// Re-check shortly after load so an uploaded image/video is reflected even when
// the browser has restored the page from its cache.
setTimeout(applyLiveSite, 1200);

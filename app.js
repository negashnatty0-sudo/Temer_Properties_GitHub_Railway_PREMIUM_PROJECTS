const properties = [
  {id:"bole",price:"ETB 12,500,000", title:"3 Bed Apartment", location:"Bole, Addis Ababa", meta:"3 Beds • 2 Baths • 150 sqm", status:"For Sale", image:"assets/property-bole.jpg"},
  {id:"kazanchis",price:"ETB 18,000,000", title:"4 Bed Apartment", location:"Kazanchis, Addis Ababa", meta:"4 Beds • 3 Baths • 220 sqm", status:"For Sale", image:"assets/property-kazanchis.jpg"},
  {id:"ayat",price:"ETB 8,500,000", title:"3 Bed House", location:"Ayat, Addis Ababa", meta:"3 Beds • 2 Baths • 180 sqm", status:"For Sale", image:"assets/property-ayat.jpg"},
  {id:"cmc",price:"ETB 9,800,000", title:"3 Bed Apartment", location:"CMC, Addis Ababa", meta:"3 Beds • 2 Baths • 140 sqm", status:"For Sale", image:"assets/property-cmc.jpg"},
  {id:"summit",price:"ETB 25,000,000", title:"4 Bed Villa", location:"Summit, Addis Ababa", meta:"4 Beds • 4 Baths • 300 sqm", status:"For Sale", image:"assets/property-summit.jpg"},
  {id:"kera",price:"ETB 15,000,000", title:"Commercial Space", location:"Kera, Addis Ababa", meta:"180 sqm • Commercial", status:"For Sale", image:"assets/project-sites.jpg"},
  {id:"megenagna",price:"ETB 11,900,000", title:"3 Bed Apartment", location:"Megenagna, Addis Ababa", meta:"3 Beds • 2 Baths • 145 sqm", status:"For Sale", image:"assets/project-residence.jpg"}
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


async function loadLiveSite(){
  try{
    const r=await fetch('/api/site',{cache:'no-store'});
    if(!r.ok) return;
    const d=await r.json();
    if(Array.isArray(d.properties)){
      d.properties.forEach(lp=>{const p=properties.find(x=>x.id===lp.id); if(p && lp.image) p.image=lp.image;});
      renderProperties();
    }
    const hero=document.querySelector('.hero');
    if(hero){
      const old=hero.querySelector('.live-hero-media');
      if(old) old.remove();
      if(d.hero_video){
        const v=document.createElement('video'); v.className='live-hero-media'; v.src=d.hero_video; v.autoplay=true; v.muted=true; v.loop=true; v.playsInline=true; v.setAttribute('aria-hidden','true');
        hero.prepend(v); hero.classList.add('has-live-video');
      }else if(d.hero_image){
        hero.style.backgroundImage=`url("${d.hero_image}")`; hero.style.backgroundSize='cover'; hero.style.backgroundPosition='center';
      }
    }
    const sales=document.querySelector('.agent-photo img'); if(sales && d.sales_officer_photo) sales.src=d.sales_officer_photo;
    const meet=document.querySelector('.team-photo img'); if(meet && d.meet_mahlet_photo) meet.src=d.meet_mahlet_photo;
    const featured=document.querySelector('.featured-project-image img'); if(featured && d.featured_project_photo) featured.src=d.featured_project_photo;
    document.querySelectorAll('.premium-phone-btn').forEach(a=>{a.href='tel:'+d.phone.replace(/[^+0-9]/g,''); a.textContent='Call Mahlet · '+d.phone;});
    document.querySelectorAll('.telegram-contact-btn').forEach(a=>{a.href=d.telegram; a.textContent='Telegram · '+d.telegram_user;});
    const banner=document.querySelector('.diaspora-contact-banner');
    if(banner){ const h=banner.querySelector('h2'), p=banner.querySelector('p'); if(h) h.textContent=d.investment_message; if(p) p.textContent=d.diaspora_message; }
  }catch(e){ console.warn('Live site settings unavailable',e); }
}

loadLiveSite();

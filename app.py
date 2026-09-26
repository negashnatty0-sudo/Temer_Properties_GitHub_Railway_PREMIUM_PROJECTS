import os, json, secrets
from pathlib import Path
from flask import Flask, request, redirect, send_from_directory, session, jsonify, render_template_string

BASE = Path(__file__).resolve().parent
DATA_ROOT = Path(os.environ.get('DATA_DIR', str(BASE / 'data')))
UPLOADS = DATA_ROOT / 'uploads'
DATA_ROOT.mkdir(parents=True, exist_ok=True)
UPLOADS.mkdir(parents=True, exist_ok=True)
DB = DATA_ROOT / 'site.json'

PROPERTY_DEFAULTS = [
    ['bole','Bole'], ['kazanchis','Kazanchis'], ['ayat','Ayat'], ['cmc','CMC'],
    ['summit','Summit'], ['kera','Kera'], ['project-sites','Kera Commercial'], ['project-residence','Megenagna']
]
DEFAULT_PROPERTIES = [
  {'id':'bole','price':'ETB 12,500,000','title':'3 Bed Apartment','location':'Bole, Addis Ababa','meta':'3 Beds • 2 Baths • 150 sqm','status':'For Sale','image':'assets/property-bole.jpg'},
  {'id':'kazanchis','price':'ETB 18,000,000','title':'4 Bed Apartment','location':'Kazanchis, Addis Ababa','meta':'4 Beds • 3 Baths • 220 sqm','status':'For Sale','image':'assets/property-kazanchis.jpg'},
  {'id':'ayat','price':'ETB 8,500,000','title':'3 Bed House','location':'Ayat, Addis Ababa','meta':'3 Beds • 2 Baths • 180 sqm','status':'For Sale','image':'assets/property-ayat.jpg'},
  {'id':'summit','price':'ETB 25,000,000','title':'4 Bed Villa','location':'Summit, Addis Ababa','meta':'4 Beds • 4 Baths • 300 sqm','status':'For Sale','image':'assets/property-summit.jpg'},
  {'id':'cmc','price':'ETB 9,800,000','title':'3 Bed Apartment','location':'CMC, Addis Ababa','meta':'3 Beds • 2 Baths • 140 sqm','status':'For Sale','image':'assets/property-cmc.jpg'},
  {'id':'kera','price':'ETB 15,000,000','title':'Commercial Space','location':'Kera, Addis Ababa','meta':'180 sqm • Commercial','status':'For Sale','image':'assets/project-sites.jpg'},
  {'id':'project-residence','price':'ETB 11,900,000','title':'3 Bed Apartment','location':'Megenagna, Addis Ababa','meta':'3 Beds • 2 Baths • 145 sqm','status':'For Sale','image':'assets/project-residence.jpg'}
]
DEFAULT_TEXTS = {
 'hero_eyebrow':'CREATE | CONSTRUCT | DELIVER',
 'hero_title':'Find Your Perfect Property in Ethiopia',
 'hero_subtitle':'Premium residential and investment properties in prime locations.',
 'agent_name':'Mahlet Ademe','agent_role':'Sales Officer','agent_member':'Member of: Ajwa Wing','agent_location':'Sarbet to Kera Road, Woldemaryam Building',
 'about_title':'Smart property search built for Ethiopia.','about_text':'Discover homes, apartments, commercial spaces and development opportunities with a clean, modern experience designed around the Ethiopian market.',
 'team_kicker':'OUR TEAM','team_title':'Meet Mahlet Ademe','team_role':'Sales Officer • Ajwa Wing','team_text':'Professional and personalised real-estate support for clients looking to buy and explore investment opportunities.',
 'contact_title':"Let's find your next property.",'contact_office':'Our office: Sarbet to Kera Road, Woldemaryam Building, Addis Ababa, Ethiopia.',
 'footer_line':'CREATE | CONSTRUCT | DELIVER • Ethiopia'
}
DEFAULT = {
    'phone': '+251 98 363 8578','telegram_user': '@mahii15','telegram': 'https://t.me/mahletrealestateadvisorr',
    'investment_message': 'Invest in real estate & make a big difference in your life.','diaspora_message': 'We stand to serve Ethiopian diaspora.',
    'hero_image': 'assets/hero-background.jpg','hero_video': '','sales_officer_image': 'assets/mahlet-ademe.jpg','meet_mahlet_image': 'assets/mahlet-ademe.jpg','featured_image': 'assets/megenagna-chaka-project.jpg',
    'texts': DEFAULT_TEXTS,'properties': DEFAULT_PROPERTIES
}

def load():
    try:
        data = json.loads(DB.read_text(encoding='utf-8')) if DB.exists() else {}
        merged = {**DEFAULT, **data}
        merged['texts'] = {**DEFAULT_TEXTS, **data.get('texts', {})}
        merged['properties'] = data.get('properties') or DEFAULT_PROPERTIES
        return merged
    except Exception:
        return json.loads(json.dumps(DEFAULT))

def save(data): DB.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')

app = Flask(__name__, static_folder=None)
app.secret_key = os.environ.get('SESSION_SECRET') or secrets.token_hex(32)
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'change-me-now')
ALLOWED_IMAGES={'.jpg','.jpeg','.png','.webp','.gif'}; ALLOWED_VIDEO={'.mp4','.webm','.mov','.m4v'}
if not DB.exists(): save(DEFAULT)

@app.after_request
def no_cache(response):
    if request.path.startswith('/api/') or request.path.startswith('/uploads/') or request.path == '/' or request.path == '/app.js':
        response.headers['Cache-Control']='no-store, no-cache, must-revalidate, max-age=0'
        response.headers['Pragma']='no-cache'; response.headers['Expires']='0'
    return response

@app.get('/')
def home(): return send_from_directory(BASE,'index.html')

@app.get('/admin')
def admin():
    if not session.get('admin'): return render_template_string(LOGIN,error='')
    return render_template_string(ADMIN,d=load())

@app.post('/admin/login')
def login():
    if secrets.compare_digest(request.form.get('password',''),ADMIN_PASSWORD): session['admin']=True; return redirect('/admin')
    return render_template_string(LOGIN,error='Incorrect password.')

@app.post('/admin/save')
def admin_save():
    if not session.get('admin'): return ('Unauthorized',401)
    d=load()
    for key in ['phone','telegram_user','telegram','investment_message','diaspora_message']:
        if key in request.form: d[key]=request.form[key]
    for key in DEFAULT_TEXTS:
        if key in request.form: d['texts'][key]=request.form[key]
    save(d); return redirect('/admin?saved=1')

@app.post('/admin/property/save')
def property_save():
    if not session.get('admin'): return ('Unauthorized',401)
    d=load(); pid=request.form.get('id'); p=next((x for x in d['properties'] if x['id']==pid),None)
    if not p: return ('Unknown property',400)
    for key in ['price','title','location','meta','status']:
        if key in request.form: p[key]=request.form[key]
    save(d); return redirect('/admin?saved=1')

@app.post('/admin/upload')
def upload():
    if not session.get('admin'): return ('Unauthorized',401)
    f=request.files.get('file'); slot=request.form.get('slot','')
    if not f or not f.filename: return ('No file selected',400)
    ext=Path(f.filename).suffix.lower(); allowed=ALLOWED_VIDEO if slot=='hero_video' else ALLOWED_IMAGES
    if ext not in allowed: return ('Unsupported file type',400)
    safe={'hero_image':'hero-image','hero_video':'hero-video','sales_officer_image':'sales-officer','meet_mahlet_image':'meet-mahlet','featured_image':'featured-sales'}
    if slot in safe: filename=safe[slot]+ext
    elif slot.startswith('property:'):
        pid=slot.split(':',1)[1]
        if pid not in {p['id'] for p in load()['properties']}: return ('Unknown property',400)
        filename='property-'+pid+ext
    else: return ('Unknown upload slot',400)
    prefix=filename.rsplit('.',1)[0]
    for old in UPLOADS.glob(prefix+'.*'):
        try: old.unlink()
        except OSError: pass
    dest=UPLOADS/filename; f.save(dest)
    url='/uploads/'+filename+'?v='+str(dest.stat().st_mtime_ns)
    d=load()
    if slot.startswith('property:'):
        p=next(x for x in d['properties'] if x['id']==slot.split(':',1)[1]); p['image']=url
    else: d[slot]=url
    if slot=='hero_video': d['hero_image']=d.get('hero_image',DEFAULT['hero_image'])
    if slot=='hero_image': d['hero_video']=''
    save(d); return redirect('/admin?saved=1')

@app.post('/admin/clear-video')
def clear_video():
    if not session.get('admin'): return ('Unauthorized',401)
    d=load(); d['hero_video']=''; save(d); return redirect('/admin?saved=1')

@app.post('/logout')
def logout(): session.clear(); return redirect('/admin')

@app.get('/api/site')
def api_site(): return jsonify(load())

@app.get('/<path:path>')
def files(path):
    if path.startswith('uploads/'):
        rel=path[len('uploads/'):]; fp=UPLOADS/rel
        if fp.is_file(): return send_from_directory(UPLOADS,rel)
    fp=BASE/path
    if fp.is_file(): return send_from_directory(BASE,path)
    return ('Not Found',404)

LOGIN="""<!doctype html><meta name='viewport' content='width=device-width,initial-scale=1'><title>Temer Admin Login</title><style>body{font-family:Arial;background:#0b3d2e;display:grid;place-items:center;min-height:100vh;margin:0}.card{background:white;padding:30px;border-radius:20px;width:min(420px,90vw)}input,button{width:100%;padding:14px;margin-top:12px;box-sizing:border-box;border-radius:10px}button{background:#c9a227;border:0;font-weight:800}.err{color:#a21d2d}</style><div class='card'><h1>Temer Properties</h1><p>Secure Admin Login</p>{% if error %}<p class='err'>{{error}}</p>{% endif %}<form method='post' action='/admin/login'><input type='password' name='password' placeholder='Admin password' required><button>Sign in</button></form></div>"""

ADMIN="""<!doctype html><html><head><meta name='viewport' content='width=device-width,initial-scale=1'><title>Temer Properties Admin</title><style>*{box-sizing:border-box}body{font-family:Arial,sans-serif;background:#f5f4ef;margin:0;color:#14231d}.wrap{max-width:1150px;margin:auto;padding:18px}.top{display:flex;justify-content:space-between;gap:15px;align-items:center;flex-wrap:wrap}.card{background:#fff;padding:20px;border-radius:20px;margin:15px 0;box-shadow:0 10px 30px #0001}.grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:15px}.media{border:1px solid #dfe6e1;border-radius:16px;padding:15px;background:#fbfcfa}.preview,.video{width:100%;height:180px;object-fit:cover;border-radius:12px;background:#e7eee9;display:block;margin-bottom:10px}.video{background:#111}.label{font-weight:800;color:#0b3d2e}.hint{font-size:13px;color:#64736b;margin:5px 0 9px}input,textarea{width:100%;padding:11px;margin:6px 0 9px;border:1px solid #ccd4cf;border-radius:10px}textarea{min-height:70px}button,a{display:inline-block;padding:11px 16px;border-radius:999px;border:0;margin-top:6px;text-decoration:none;font-weight:800;cursor:pointer}.gold{background:#c9a227;color:#14231d}.dark{background:#0b3d2e;color:#fff}.danger{background:#eee;color:#333}.ok{background:#e8f5ee;padding:12px;border-radius:10px;color:#0b3d2e;font-weight:700}.property{border:1px solid #e0e5e1;border-radius:16px;padding:15px}.property h3{margin:0 0 8px}@media(max-width:720px){.grid{grid-template-columns:1fr}.wrap{padding:10px}}
</style></head><body><div class='wrap'><div class='top'><div><h1>Temer Properties — Admin</h1><p>Facebook-style media + text controls. Admin only.</p></div><div><a class='dark' href='/' target='_blank'>Open Website</a><form style='display:inline' method='post' action='/logout'><button class='dark'>Logout</button></form></div></div>{% if request.args.get('saved') %}<div class='ok'>✓ Saved. Open the website and refresh to see the change.</div>{% endif %}
<div class='card'><h2>🎬 Homepage Background</h2><div class='grid'><div class='media'><div class='label'>Background Picture</div><img class='preview' src='{{d.hero_image}}'><form method='post' action='/admin/upload' enctype='multipart/form-data'><input type='hidden' name='slot' value='hero_image'><input type='file' name='file' accept='image/*' required><button class='gold'>📷 Change Picture</button></form></div><div class='media'><div class='label'>Background Video</div>{% if d.hero_video %}<video class='video' src='{{d.hero_video}}' controls></video>{% else %}<div class='video'></div>{% endif %}<form method='post' action='/admin/upload' enctype='multipart/form-data'><input type='hidden' name='slot' value='hero_video'><input type='file' name='file' accept='video/*' required><button class='gold'>🎥 Change Video</button></form><form method='post' action='/admin/clear-video'><button class='danger'>Use Picture Instead</button></form></div></div></div>
<div class='card'><h2>👩‍💼 People & Sales Images</h2><div class='grid'>{% for slot,title in [('sales_officer_image','Sales Officer — Mahlet Ademe'),('meet_mahlet_image','Meet Mahlet Ademe'),('featured_image','Featured Sales / Project')] %}<div class='media'><div class='label'>{{title}}</div><img class='preview' src='{{d[slot]}}'><form method='post' action='/admin/upload' enctype='multipart/form-data'><input type='hidden' name='slot' value='{{slot}}'><input type='file' name='file' accept='image/*' required><button class='gold'>📷 Change Picture</button></form></div>{% endfor %}</div></div>
<div class='card'><h2>🏠 Properties — photo + text</h2>{% for p in d.properties %}<div class='property'><h3>{{p.title}} — {{p.location}}</h3><div class='grid'><div><img class='preview' src='{{p.image}}'><form method='post' action='/admin/upload' enctype='multipart/form-data'><input type='hidden' name='slot' value='property:{{p.id}}'><input type='file' name='file' accept='image/*' required><button class='gold'>📷 Change Property Picture</button></form></div><form method='post' action='/admin/property/save'><input type='hidden' name='id' value='{{p.id}}'><label>Title<input name='title' value='{{p.title}}'></label><label>Price<input name='price' value='{{p.price}}'></label><label>Location<input name='location' value='{{p.location}}'></label><label>Details<input name='meta' value='{{p.meta}}'></label><label>Status<input name='status' value='{{p.status}}'></label><button class='gold'>Save Property Text</button></form></div></div>{% endfor %}</div>
<div class='card'><h2>✏️ Website Text & Contact</h2><form method='post' action='/admin/save'><div class='grid'>{% for key,label in [('hero_eyebrow','Hero eyebrow'),('hero_title','Hero title'),('hero_subtitle','Hero subtitle'),('agent_name','Sales Officer name'),('agent_role','Sales Officer role'),('agent_member','Agent membership'),('agent_location','Agent location'),('about_title','About title'),('about_text','About text'),('team_kicker','Team kicker'),('team_title','Meet section title'),('team_role','Meet section role'),('team_text','Meet section text'),('contact_title','Contact title'),('contact_office','Office text'),('footer_line','Footer line')] %}<label>{{label}}<textarea name='{{key}}'>{{d.texts[key]}}</textarea></label>{% endfor %}<label>Phone<input name='phone' value='{{d.phone}}'></label><label>Telegram username<input name='telegram_user' value='{{d.telegram_user}}'></label><label>Telegram link<input name='telegram' value='{{d.telegram}}'></label><label>Investment message<textarea name='investment_message'>{{d.investment_message}}</textarea></label><label>Diaspora message<textarea name='diaspora_message'>{{d.diaspora_message}}</textarea></label></div><button class='gold'>💾 Save Text Changes</button></form></div></div></body></html>"""

if __name__=='__main__': app.run(host='0.0.0.0',port=int(os.environ.get('PORT','5000')))

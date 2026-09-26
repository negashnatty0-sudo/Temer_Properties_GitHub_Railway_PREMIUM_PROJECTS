import os, json, secrets, re
from pathlib import Path
from flask import Flask, request, redirect, send_from_directory, session, jsonify, render_template_string

BASE = Path(__file__).resolve().parent
DATA = Path(os.environ.get('DATA_DIR', str(BASE / 'data')))
UPLOADS = DATA / 'uploads'
DATA.mkdir(parents=True, exist_ok=True)
UPLOADS.mkdir(parents=True, exist_ok=True)
DB = DATA / 'site.json'

PROPERTY_DEFAULTS = [
    {"id":"bole","title":"3 Bed Apartment","location":"Bole, Addis Ababa","meta":"3 Beds • 2 Baths • 150 sqm","status":"For Sale","price":"ETB 12,500,000","image":"assets/property-bole.jpg"},
    {"id":"kazanchis","title":"4 Bed Apartment","location":"Kazanchis, Addis Ababa","meta":"4 Beds • 3 Baths • 220 sqm","status":"For Sale","price":"ETB 18,000,000","image":"assets/property-kazanchis.jpg"},
    {"id":"ayat","title":"3 Bed House","location":"Ayat, Addis Ababa","meta":"3 Beds • 2 Baths • 180 sqm","status":"For Sale","price":"ETB 8,500,000","image":"assets/property-ayat.jpg"},
    {"id":"cmc","title":"3 Bed Apartment","location":"CMC, Addis Ababa","meta":"3 Beds • 2 Baths • 140 sqm","status":"For Sale","price":"ETB 9,800,000","image":"assets/property-cmc.jpg"},
    {"id":"summit","title":"4 Bed Villa","location":"Summit, Addis Ababa","meta":"4 Beds • 4 Baths • 300 sqm","status":"For Sale","price":"ETB 25,000,000","image":"assets/property-summit.jpg"},
    {"id":"kera","title":"Commercial Space","location":"Kera, Addis Ababa","meta":"180 sqm • Commercial","status":"For Sale","price":"ETB 15,000,000","image":"assets/project-sites.jpg"},
    {"id":"megenagna","title":"3 Bed Apartment","location":"Megenagna, Addis Ababa","meta":"3 Beds • 2 Baths • 145 sqm","status":"For Sale","price":"ETB 11,900,000","image":"assets/project-residence.jpg"},
]

DEFAULT = {
    'phone': '+251 98 363 8578',
    'telegram_user': '@mahii15',
    'telegram': 'https://t.me/mahletrealestateadvisorr',
    'investment_message': 'Invest in real estate & make a big difference in your life.',
    'diaspora_message': 'We stand to serve Ethiopian diaspora.',
    'hero_image': 'assets/hero-background.jpg',
    'hero_video': '',
    'sales_officer_photo': 'assets/mahlet-ademe.jpg',
    'meet_mahlet_photo': 'assets/mahlet-ademe.jpg',
    'featured_project_photo': 'assets/megenagna-chaka-project.jpg',
    'properties': PROPERTY_DEFAULTS,
}

ALLOWED = {'.jpg','.jpeg','.png','.webp','.gif','.mp4','.webm','.mov'}


def load():
    try:
        saved = json.loads(DB.read_text(encoding='utf-8')) if DB.exists() else {}
        d = {**DEFAULT, **saved}
        if not isinstance(d.get('properties'), list): d['properties'] = PROPERTY_DEFAULTS
        return d
    except Exception:
        return DEFAULT.copy()


def save(d):
    DB.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding='utf-8')


app = Flask(__name__, static_folder=None)
app.secret_key = os.environ.get('SESSION_SECRET', secrets.token_hex(32))
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'change-me-now')


@app.get('/')
def home():
    return send_from_directory(BASE, 'index.html')


@app.get('/admin')
def admin():
    if not session.get('admin'):
        return render_template_string(LOGIN, error='')
    return render_template_string(ADMIN, d=load())


@app.post('/admin/login')
def login():
    if secrets.compare_digest(request.form.get('password',''), ADMIN_PASSWORD):
        session['admin'] = True
        return redirect('/admin')
    return render_template_string(LOGIN, error='Incorrect password.')


@app.post('/admin/save')
def admin_save():
    if not session.get('admin'): return ('Unauthorized', 401)
    d = load()
    for k in ['phone','telegram_user','telegram','investment_message','diaspora_message','hero_image','hero_video','sales_officer_photo','meet_mahlet_photo','featured_project_photo']:
        if k in request.form: d[k] = request.form[k]
    save(d)
    return redirect('/admin?saved=1')


@app.post('/admin/upload')
def upload():
    if not session.get('admin'): return ('Unauthorized', 401)
    f = request.files.get('file')
    kind = request.form.get('kind','hero_image')
    if not f or not f.filename: return redirect('/admin')
    ext = Path(f.filename).suffix.lower()
    if ext not in ALLOWED: return ('File type not allowed', 400)

    safe_kind = re.sub(r'[^a-z0-9_-]', '', kind.lower())
    if safe_kind == 'hero_video':
        filename = 'hero-video' + ext
        key = 'hero_video'
    elif safe_kind == 'sales_officer_photo':
        filename = 'sales-officer' + ext
        key = 'sales_officer_photo'
    elif safe_kind == 'meet_mahlet_photo':
        filename = 'meet-mahlet' + ext
        key = 'meet_mahlet_photo'
    elif safe_kind == 'featured_project_photo':
        filename = 'featured-project' + ext
        key = 'featured_project_photo'
    elif safe_kind.startswith('property_'):
        pid = safe_kind[len('property_'):]
        filename = f'property-{pid}{ext}'
        key = None
    else:
        filename = 'hero-image' + ext
        key = 'hero_image'

    target = UPLOADS / filename
    f.save(target)
    public_path = '/uploads/' + filename
    d = load()
    if key:
        d[key] = public_path
    else:
        for p in d['properties']:
            if p['id'] == pid:
                p['image'] = public_path
                break
    save(d)
    return redirect('/admin?saved=1')


@app.post('/admin/logout')
def logout():
    session.clear()
    return redirect('/admin')


@app.get('/api/site')
def api_site():
    return jsonify(load())


@app.get('/uploads/<path:path>')
def uploads(path):
    return send_from_directory(UPLOADS, path)


@app.get('/<path:path>')
def files(path):
    return send_from_directory(BASE, path)


LOGIN = """<!doctype html><meta name='viewport' content='width=device-width,initial-scale=1'><title>Temer Admin Login</title><style>body{font-family:Arial;background:#0b3d2e;display:grid;place-items:center;min-height:100vh;margin:0}.card{background:white;padding:30px;border-radius:20px;width:min(420px,90vw);box-sizing:border-box}input,button{width:100%;padding:14px;margin-top:12px;box-sizing:border-box;border-radius:10px}button{background:#c9a227;border:0;font-weight:800}.err{color:#a21d2d}</style><div class='card'><h1>Temer Properties</h1><p>Admin Login</p>{% if error %}<p class='err'>{{error}}</p>{% endif %}<form method='post' action='/admin/login'><input type='password' name='password' placeholder='Admin password' required><button>Sign in</button></form></div>"""


def upload_card(title, kind, accept='image/*'):
    return f"""<div class='upload-card'><div><h3>{title}</h3><p>Choose a new file from your phone or computer.</p></div><form method='post' action='/admin/upload' enctype='multipart/form-data'><input type='hidden' name='kind' value='{kind}'><input type='file' name='file' accept='{accept}' required><button class='gold'>Upload & Use</button></form></div>"""

ADMIN = """<!doctype html><meta name='viewport' content='width=device-width,initial-scale=1'><title>Temer Properties — Media Admin</title><style>
body{font-family:Arial,sans-serif;background:#f5f4ef;margin:0;color:#14231d}.wrap{max-width:1050px;margin:auto;padding:20px}.top{display:flex;justify-content:space-between;gap:12px;align-items:center;flex-wrap:wrap}.card{background:#fff;padding:22px;border-radius:20px;margin:16px 0;box-shadow:0 12px 35px #0001}h1,h2,h3{color:#0b3d2e}label{display:block;font-weight:700;margin-top:12px}input,textarea{width:100%;box-sizing:border-box;padding:12px;margin-top:7px;border:1px solid #ccd4cf;border-radius:10px}textarea{min-height:90px}button,a{display:inline-block;padding:12px 18px;border-radius:999px;border:0;margin-top:12px;text-decoration:none;font-weight:800;cursor:pointer}.gold{background:#c9a227;color:#14231d}.dark{background:#0b3d2e;color:#fff}.ok{background:#e8f5ee;padding:12px;border-radius:10px}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:14px}.upload-card{border:1px solid #dfe6e1;border-radius:16px;padding:16px;background:#fbfcfa}.upload-card h3{margin:0}.hint{color:#66736c;font-size:14px}.danger{background:#222;color:#fff}.preview{max-width:150px;max-height:90px;border-radius:10px;margin-top:10px}.prop{display:grid;grid-template-columns:1fr auto;gap:10px;align-items:center;border-top:1px solid #eee;padding:14px 0}.prop img{width:110px;height:75px;object-fit:cover;border-radius:10px}.prop form{display:flex;gap:8px;align-items:center;flex-wrap:wrap}.prop input[type=file]{max-width:220px}.small{font-size:13px;color:#6a746f}
</style><div class='wrap'><div class='top'><div><h1>Temer Properties — Live Control Centre</h1><p class='hint'>Upload from your phone. Each section has its own upload button.</p></div><div><a class='dark' href='/'>Open Website</a><form method='post' action='/admin/logout' style='display:inline'><button class='danger'>Logout</button></form></div></div>{% if request.args.get('saved') %}<div class='ok'>Saved successfully. The website is using the new media.</div>{% endif %}
<div class='card'><h2>🎬 Main Homepage Background</h2><div class='grid'>{{hero_image}}{{hero_video}}</div><form method='post' action='/admin/save'><label>Hero image path</label><input name='hero_image' value='{{d.hero_image}}'><label>Hero video path</label><input name='hero_video' value='{{d.hero_video}}'><button class='gold'>Save Background Settings</button></form></div>
<div class='card'><h2>👩‍💼 Sales Officer</h2>{{sales}}</div>
<div class='card'><h2>🏠 Featured Sales Picture</h2>{{featured}}</div>
<div class='card'><h2>👩 Meet Mahlet Ademe — End Section</h2>{{meet}}</div>
<div class='card'><h2>🏢 Apartment / Property Pictures</h2><p class='hint'>Every property has its own upload button. Upload a different picture for each one.</p>{{properties}}</div>
<div class='card'><h2>📞 Contact & Marketing</h2><form method='post' action='/admin/save'><label>Phone</label><input name='phone' value='{{d.phone}}'><label>Telegram username</label><input name='telegram_user' value='{{d.telegram_user}}'><label>Telegram link</label><input name='telegram' value='{{d.telegram}}'><label>Investment message</label><textarea name='investment_message'>{{d.investment_message}}</textarea><label>Diaspora message</label><textarea name='diaspora_message'>{{d.diaspora_message}}</textarea><button class='gold'>Save Text & Contact</button></form></div></div>"""


def make_admin():
    d = load()
    return render_template_string(ADMIN, d=d,
        hero_image=upload_card('Upload homepage background picture','hero_image','image/*'),
        hero_video=upload_card('Upload homepage background video','hero_video','video/*'),
        sales=upload_card('Upload Sales Officer picture','sales_officer_photo','image/*'),
        featured=upload_card('Upload Featured Sales / Project picture','featured_project_photo','image/*'),
        meet=upload_card('Upload Meet Mahlet Ademe picture','meet_mahlet_photo','image/*'),
        properties=''.join(f"<div class='prop'><div><b>{p['title']} — {p['location']}</b><div class='small'>{p['image']}</div><form method='post' action='/admin/upload' enctype='multipart/form-data'><input type='hidden' name='kind' value='property_{p['id']}'><input type='file' name='file' accept='image/*' required><button class='gold'>Upload Picture</button></form></div><img src='{p['image']}' alt=''></div>" for p in d['properties']))

# Replace the admin route with the richer dashboard.
app.view_functions['admin'] = lambda: make_admin() if session.get('admin') else render_template_string(LOGIN, error='')

if not DB.exists(): save(DEFAULT)

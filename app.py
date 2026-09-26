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
DEFAULT = {
    'phone': '+251 98 363 8578',
    'telegram_user': '@mahii15',
    'telegram': 'https://t.me/mahletrealestateadvisorr',
    'investment_message': 'Invest in real estate & make a big difference in your life.',
    'diaspora_message': 'We stand to serve Ethiopian diaspora.',
    'hero_image': 'assets/hero-background.jpg',
    'hero_video': '',
    'sales_officer_image': 'assets/mahlet-ademe.jpg',
    'meet_mahlet_image': 'assets/mahlet-ademe.jpg',
    'featured_image': 'assets/megenagna-chaka-project.jpg',
    'property_images': {k: f'assets/property-{k}.jpg' if k not in ('project-sites','project-residence') else ('assets/project-sites.jpg' if k=='project-sites' else 'assets/project-residence.jpg') for k,_ in PROPERTY_DEFAULTS},
}

def load():
    try:
        data = json.loads(DB.read_text(encoding='utf-8')) if DB.exists() else {}
        merged = {**DEFAULT, **data}
        merged['property_images'] = {**DEFAULT['property_images'], **data.get('property_images', {})}
        return merged
    except Exception:
        return json.loads(json.dumps(DEFAULT))

def save(data):
    DB.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')

app = Flask(__name__, static_folder=None)
app.secret_key = os.environ.get('SESSION_SECRET') or secrets.token_hex(32)
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'change-me-now')
ALLOWED_IMAGES = {'.jpg','.jpeg','.png','.webp','.gif'}
ALLOWED_VIDEO = {'.mp4','.webm','.mov','.m4v'}

if not DB.exists():
    save(DEFAULT)

@app.get('/')
def home():
    return send_from_directory(BASE, 'index.html')

@app.get('/admin')
def admin():
    if not session.get('admin'):
        return render_template_string(LOGIN, error='')
    return render_template_string(ADMIN, d=load(), properties=PROPERTY_DEFAULTS)

@app.post('/admin/login')
def login():
    supplied = request.form.get('password','')
    if secrets.compare_digest(supplied, ADMIN_PASSWORD):
        session['admin'] = True
        return redirect('/admin')
    return render_template_string(LOGIN, error='Incorrect password.')

@app.post('/admin/save')
def admin_save():
    if not session.get('admin'):
        return ('Unauthorized', 401)
    d = load()
    for key in ['phone','telegram_user','telegram','investment_message','diaspora_message']:
        if key in request.form:
            d[key] = request.form[key]
    save(d)
    return redirect('/admin?saved=1')

@app.post('/admin/upload')
def upload():
    if not session.get('admin'):
        return ('Unauthorized', 401)
    f = request.files.get('file')
    slot = request.form.get('slot','')
    if not f or not f.filename:
        return ('No file selected', 400)
    ext = Path(f.filename).suffix.lower()
    if slot == 'hero_video':
        allowed = ALLOWED_VIDEO
    else:
        allowed = ALLOWED_IMAGES
    if ext not in allowed:
        return ('Unsupported file type', 400)

    safe_names = {
        'hero_image':'hero-image', 'hero_video':'hero-video',
        'sales_officer_image':'sales-officer', 'meet_mahlet_image':'meet-mahlet',
        'featured_image':'featured-sales'
    }
    if slot in safe_names:
        filename = safe_names[slot] + ext
    elif slot.startswith('property:'):
        key = slot.split(':',1)[1]
        if key not in dict(PROPERTY_DEFAULTS):
            return ('Unknown property', 400)
        filename = 'property-' + key + ext
    else:
        return ('Unknown upload slot', 400)

    # Remove old extensions for this slot so the browser always gets one current file.
    prefix = filename.rsplit('.',1)[0]
    for old in UPLOADS.glob(prefix + '.*'):
        try: old.unlink()
        except OSError: pass
    destination = UPLOADS / filename
    f.save(destination)
    public_path = '/uploads/' + filename
    d = load()
    if slot.startswith('property:'):
        d['property_images'][slot.split(':',1)[1]] = public_path
    else:
        d[slot] = public_path
    # A new hero video automatically becomes the active hero media; uploading a hero image clears it.
    if slot == 'hero_video':
        d['hero_image'] = d.get('hero_image', DEFAULT['hero_image'])
    elif slot == 'hero_image':
        d['hero_video'] = ''
    save(d)
    return redirect('/admin?saved=1')

@app.post('/admin/clear-video')
def clear_video():
    if not session.get('admin'):
        return ('Unauthorized', 401)
    d = load(); d['hero_video'] = ''; save(d)
    return redirect('/admin?saved=1')

@app.post('/logout')
def logout():
    session.clear(); return redirect('/admin')

@app.get('/api/site')
def api_site():
    response = jsonify(load())
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    return response

@app.get('/<path:path>')
def files(path):
    upload_path = UPLOADS / path
    if upload_path.is_file():
        return send_from_directory(UPLOADS, path)
    base_path = BASE / path
    if base_path.is_file():
        return send_from_directory(BASE, path)
    return ('Not Found', 404)

LOGIN = """<!doctype html><meta name='viewport' content='width=device-width,initial-scale=1'><title>Temer Admin Login</title><style>body{font-family:Arial;background:#0b3d2e;display:grid;place-items:center;min-height:100vh;margin:0}.card{background:white;padding:30px;border-radius:20px;width:min(420px,90vw);box-sizing:border-box}input,button{width:100%;padding:14px;margin-top:12px;box-sizing:border-box;border-radius:10px}input{border:1px solid #ccd4cf}button{background:#c9a227;border:0;font-weight:800;cursor:pointer}.err{color:#a21d2d}</style><div class='card'><h1>Temer Properties</h1><p>Secure Admin Login</p>{% if error %}<p class='err'>{{error}}</p>{% endif %}<form method='post' action='/admin/login'><input type='password' name='password' placeholder='Admin password' required><button>Sign in</button></form></div>"""

ADMIN = """<!doctype html><html><head><meta name='viewport' content='width=device-width,initial-scale=1'><title>Temer Properties Admin</title><style>
*{box-sizing:border-box}body{font-family:Arial,sans-serif;background:#f5f4ef;margin:0;color:#14231d}.wrap{max-width:1100px;margin:auto;padding:22px}.top{display:flex;justify-content:space-between;gap:15px;align-items:center;flex-wrap:wrap}.card{background:#fff;padding:22px;border-radius:20px;margin:16px 0;box-shadow:0 12px 35px #0001}.grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:16px}.media{border:1px solid #dfe6e1;border-radius:16px;padding:16px;background:#fbfcfa}.preview{width:100%;height:180px;object-fit:cover;border-radius:12px;background:#e7eee9;display:block;margin-bottom:12px}.video{width:100%;height:180px;object-fit:cover;border-radius:12px;background:#111;margin-bottom:12px}.label{font-weight:800;color:#0b3d2e}.hint{font-size:13px;color:#64736b;margin:5px 0 10px}input,textarea{width:100%;padding:12px;margin-top:7px;border:1px solid #ccd4cf;border-radius:10px}textarea{min-height:80px}button,a{display:inline-block;padding:12px 18px;border-radius:999px;border:0;margin-top:12px;text-decoration:none;font-weight:800;cursor:pointer}.gold{background:#c9a227;color:#14231d}.dark{background:#0b3d2e;color:#fff}.danger{background:#eee;color:#333}.ok{background:#e8f5ee;padding:12px;border-radius:10px;color:#0b3d2e;font-weight:700}@media(max-width:700px){.grid{grid-template-columns:1fr}.wrap{padding:12px}}
</style></head><body><div class='wrap'>
<div class='top'><div><h1>Temer Properties — Admin</h1><p>Upload and change the live website without editing code.</p></div><div><a class='dark' href='/' target='_blank'>Open Website</a><form style='display:inline' method='post' action='/logout'><button class='dark'>Logout</button></form></div></div>
{% if request.args.get('saved') %}<div class='ok'>✓ Saved successfully. Your new media is now connected to the website.</div>{% endif %}
<div class='card'><h2>🎬 Main Homepage Background</h2><div class='grid'>
<div class='media'><div class='label'>Background Picture</div><div class='hint'>Upload the photo you want behind the homepage.</div><img class='preview' src='{{d.hero_image}}' onerror="this.style.display='none'"><form method='post' action='/admin/upload' enctype='multipart/form-data'><input type='hidden' name='slot' value='hero_image'><input type='file' name='file' accept='image/*' required><button class='gold'>Upload Background Picture</button></form></div>
<div class='media'><div class='label'>Background Video</div><div class='hint'>Upload MP4/WebM/MOV. When uploaded, it becomes the homepage background.</div>{% if d.hero_video %}<video class='video' src='{{d.hero_video}}' controls></video>{% endif %}<form method='post' action='/admin/upload' enctype='multipart/form-data'><input type='hidden' name='slot' value='hero_video'><input type='file' name='file' accept='video/*' required><button class='gold'>Upload Background Video</button></form><form method='post' action='/admin/clear-video'><button class='danger'>Use Background Picture Instead</button></form></div>
</div></div>
<div class='card'><h2>👩‍💼 People & Sales Images</h2><div class='grid'>
{% for slot,title in [('sales_officer_image','Sales Officer — Mahlet Ademe'),('meet_mahlet_image','Meet Mahlet Ademe — End Section'),('featured_image','Featured Sales / Project Picture')] %}<div class='media'><div class='label'>{{title}}</div><img class='preview' src='{{d[slot]}}' onerror="this.style.display='none'"><form method='post' action='/admin/upload' enctype='multipart/form-data'><input type='hidden' name='slot' value='{{slot}}'><input type='file' name='file' accept='image/*' required><button class='gold'>Upload Picture</button></form></div>{% endfor %}</div></div>
<div class='card'><h2>🏠 Apartment / Property Pictures</h2><p>Each property has its own upload button.</p><div class='grid'>{% for key,title in properties %}<div class='media'><div class='label'>{{title}}</div><img class='preview' src='{{d.property_images[key]}}' onerror="this.style.display='none'"><form method='post' action='/admin/upload' enctype='multipart/form-data'><input type='hidden' name='slot' value='property:{{key}}'><input type='file' name='file' accept='image/*' required><button class='gold'>Upload {{title}} Picture</button></form></div>{% endfor %}</div></div>
<div class='card'><h2>📞 Contact & Marketing</h2><form method='post' action='/admin/save'><label>Phone<input name='phone' value='{{d.phone}}'></label><label>Telegram username<input name='telegram_user' value='{{d.telegram_user}}'></label><label>Telegram link<input name='telegram' value='{{d.telegram}}'></label><label>Investment message<textarea name='investment_message'>{{d.investment_message}}</textarea></label><label>Diaspora message<textarea name='diaspora_message'>{{d.diaspora_message}}</textarea></label><button class='gold'>Save Text & Contact Changes</button></form></div>
</div></body></html>"""

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT','5000')))

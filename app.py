import os, json, secrets
from pathlib import Path
from flask import Flask, request, redirect, send_from_directory, session, jsonify, render_template_string
BASE=Path(__file__).resolve().parent; DATA=BASE/'data'; UPLOADS=BASE/'uploads'; DATA.mkdir(exist_ok=True); UPLOADS.mkdir(exist_ok=True); DB=DATA/'site.json'
DEFAULT={'phone':'+251 98 363 8578','telegram_user':'@mahii15','telegram':'https://t.me/mahletrealestateadvisorr','investment_message':'Invest in real estate & make a big difference in your life.','diaspora_message':'We stand to serve Ethiopian diaspora.','hero_image':'assets/hero-background.jpg','hero_video':''}
def load():
    try: return {**DEFAULT,**json.loads(DB.read_text())} if DB.exists() else DEFAULT.copy()
    except: return DEFAULT.copy()
def save(d): DB.write_text(json.dumps(d,ensure_ascii=False,indent=2))
app=Flask(__name__,static_folder=None); app.secret_key=os.environ.get('SESSION_SECRET',secrets.token_hex(32)); ADMIN_PASSWORD=os.environ.get('ADMIN_PASSWORD','change-me-now')
ALLOWED={'.jpg','.jpeg','.png','.webp','.gif','.mp4','.webm','.mov'}
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
    for k in DEFAULT:
        if k in request.form: d[k]=request.form[k]
    save(d); return redirect('/admin?saved=1')
@app.post('/admin/upload')
def upload():
    if not session.get('admin'): return ('Unauthorized',401)
    f=request.files.get('file'); kind=request.form.get('kind','image')
    if not f or not f.filename: return redirect('/admin')
    ext=Path(f.filename).suffix.lower()
    if ext not in ALLOWED: return ('File type not allowed',400)
    name=('hero-video'+ext) if kind=='video' else ('site-image'+ext); f.save(UPLOADS/name)
    d=load(); d['hero_video' if kind=='video' else 'hero_image']='/uploads/'+name; save(d); return redirect('/admin?saved=1')
@app.post('/logout')
def logout(): session.clear(); return redirect('/admin')
@app.get('/api/site')
def api_site(): return jsonify(load())
@app.get('/<path:path>')
def files(path):
    p=UPLOADS/path
    if p.is_file(): return send_from_directory(UPLOADS,path)
    return send_from_directory(BASE,path)
LOGIN="""<!doctype html><meta name='viewport' content='width=device-width,initial-scale=1'><title>Temer Admin</title><style>body{font-family:Arial;background:#0b3d2e;display:grid;place-items:center;min-height:100vh}.card{background:white;padding:30px;border-radius:20px;width:min(420px,90vw)}input,button{width:100%;padding:13px;margin-top:10px;box-sizing:border-box;border-radius:10px}button{background:#c9a227;border:0;font-weight:800}.err{color:#a21d2d}</style><div class='card'><h1>Temer Properties</h1><p>Admin Login</p>{% if error %}<p class='err'>{{error}}</p>{% endif %}<form method='post' action='/admin/login'><input type='password' name='password' placeholder='Admin password' required><button>Sign in</button></form></div>"""
ADMIN="""<!doctype html><meta name='viewport' content='width=device-width,initial-scale=1'><title>Temer Admin</title><style>body{font-family:Arial;background:#f5f4ef;margin:0;color:#14231d}.wrap{max-width:950px;margin:auto;padding:24px}.card{background:white;padding:24px;border-radius:20px;margin:16px 0;box-shadow:0 12px 35px #0001}h1,h2{color:#0b3d2e}label{display:block;font-weight:700;margin-top:14px}input,textarea{width:100%;box-sizing:border-box;padding:12px;margin-top:7px;border:1px solid #ccd4cf;border-radius:10px}textarea{min-height:90px}button,a{display:inline-block;padding:12px 18px;border-radius:999px;border:0;margin-top:16px;text-decoration:none;font-weight:800}.save{background:#c9a227;color:#14231d}.dark{background:#0b3d2e;color:#fff}.ok{background:#e8f5ee;padding:12px;border-radius:10px}</style><div class='wrap'><h1>Temer Properties — Live Control Centre</h1>{% if request.args.get('saved') %}<div class='ok'>Saved successfully. Changes are live.</div>{% endif %}<div class='card'><form method='post' action='/admin/save'><h2>Contact</h2><label>Phone</label><input name='phone' value='{{d.phone}}'><label>Telegram username</label><input name='telegram_user' value='{{d.telegram_user}}'><label>Telegram link</label><input name='telegram' value='{{d.telegram}}'><h2>Homepage</h2><label>Investment message</label><textarea name='investment_message'>{{d.investment_message}}</textarea><label>Diaspora message</label><textarea name='diaspora_message'>{{d.diaspora_message}}</textarea><label>Hero image path</label><input name='hero_image' value='{{d.hero_image}}'><label>Hero video path</label><input name='hero_video' value='{{d.hero_video}}'><button class='save'>Save Live Changes</button></form></div><div class='card'><h2>Upload hero image</h2><form method='post' action='/admin/upload' enctype='multipart/form-data'><input type='hidden' name='kind' value='image'><input type='file' name='file' accept='image/*' required><button class='save'>Upload & Use Image</button></form><h2>Upload hero video</h2><form method='post' action='/admin/upload' enctype='multipart/form-data'><input type='hidden' name='kind' value='video'><input type='file' name='file' accept='video/*' required><button class='save'>Upload & Use Video</button></form></div><a class='dark' href='/'>Open Website</a><form method='post' action='/logout'><button class='dark'>Logout</button></form></div>"""
if not DB.exists(): save(DEFAULT)

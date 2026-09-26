
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import re, os, json

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "temer-dev-secret")

PROPERTIES = [
    {"id":1,"title":"3 Bedroom Apartment","location":"Bole, Addis Ababa","city":"Addis Ababa","type":"Apartment","status":"For Sale","price":12500000,"beds":3,"baths":2,"sqm":150,"image":"https://images.unsplash.com/photo-1600607687920-4e2a09cf159d?auto=format&fit=crop&w=900&q=80"},
    {"id":2,"title":"4 Bedroom Villa","location":"Summit, Addis Ababa","city":"Addis Ababa","type":"Villa","status":"For Sale","price":25000000,"beds":4,"baths":4,"sqm":300,"image":"https://images.unsplash.com/photo-1600585154340-be6161a56a0c?auto=format&fit=crop&w=900&q=80"},
    {"id":3,"title":"2 Bedroom Apartment","location":"CMC, Addis Ababa","city":"Addis Ababa","type":"Apartment","status":"For Rent","price":65000,"beds":2,"baths":2,"sqm":120,"image":"https://images.unsplash.com/photo-1600566753190-17f0baa2a6c3?auto=format&fit=crop&w=900&q=80"},
    {"id":4,"title":"Townhouse","location":"Kazanchis, Addis Ababa","city":"Addis Ababa","type":"Townhouse","status":"For Sale","price":18000000,"beds":3,"baths":3,"sqm":220,"image":"https://images.unsplash.com/photo-1600047509807-ba8f99d2cdde?auto=format&fit=crop&w=900&q=80"},
    {"id":5,"title":"3 Bedroom House","location":"Ayat, Addis Ababa","city":"Addis Ababa","type":"House","status":"For Sale","price":8500000,"beds":3,"baths":2,"sqm":180,"image":"https://images.unsplash.com/photo-1600566753086-00f18fb6b3ea?auto=format&fit=crop&w=900&q=80"},
    {"id":6,"title":"Off-Plan Family Apartment","location":"Sarbet, Addis Ababa","city":"Addis Ababa","type":"Apartment","status":"Off-Plan","price":9800000,"beds":3,"baths":2,"sqm":145,"image":"https://images.unsplash.com/photo-1600607688969-a5bfcd646154?auto=format&fit=crop&w=900&q=80"},
]

PROJECTS = [
    {"name":"Ajwa Residence","location":"Bole, Addis Ababa","status":"Ongoing"},
    {"name":"Kera Heights","location":"Kera, Addis Ababa","status":"Ongoing"},
    {"name":"Woldemaryam Tower","location":"Kera, Addis Ababa","status":"Completed"},
    {"name":"Temer Gardens","location":"Summit, Addis Ababa","status":"Off-Plan"},
]

def parse_ai_query(q):
    q=(q or "").lower()
    criteria={}
    locs=["bole","cmc","kazanchis","megenagna","summit","ayat","sarbet","kera"]
    for l in locs:
        if l in q: criteria["location"]=l
    types={"apartment":"Apartment","villa":"Villa","house":"House","townhouse":"Townhouse","land":"Land"}
    for k,v in types.items():
        if k in q: criteria["type"]=v
    m=re.search(r'(\d+)\s*(?:bed|bedroom)',q)
    if m: criteria["beds"]=int(m.group(1))
    m=re.search(r'(?:under|below|less than|up to)\s*(\d+(?:\.\d+)?)\s*(m|million|k)?',q)
    if m:
        n=float(m.group(1)); unit=(m.group(2) or "").lower()
        criteria["max_price"]=n*(1_000_000 if unit in ("m","million") else 1_000 if unit=="k" else 1)
    return criteria

def filter_properties(criteria):
    out=[]
    for p in PROPERTIES:
        ok=True
        if criteria.get("location") and criteria["location"] not in p["location"].lower(): ok=False
        if criteria.get("type") and p["type"]!=criteria["type"]: ok=False
        if criteria.get("beds") and p["beds"]<criteria["beds"]: ok=False
        if criteria.get("max_price") and p["price"]>criteria["max_price"]: ok=False
        if ok: out.append(p)
    return out

@app.context_processor
def inject():
    return {"saved":session.get("saved",[]), "lang":session.get("lang","EN")}

@app.route("/")
def home():
    return render_template("home.html", properties=PROPERTIES[:4], projects=PROJECTS)

@app.route("/properties")
def properties():
    q=request.args.get("q","")
    criteria=parse_ai_query(q)
    results=filter_properties(criteria) if criteria else PROPERTIES
    return render_template("properties.html", properties=results, query=q)

@app.route("/property/<int:pid>")
def property_detail(pid):
    p=next((x for x in PROPERTIES if x["id"]==pid),None)
    if not p: return "Property not found",404
    return render_template("property.html", p=p)

@app.post("/api/ai-search")
def ai_search():
    q=request.json.get("query","")
    criteria=parse_ai_query(q)
    results=filter_properties(criteria)
    return jsonify({"query":q,"criteria":criteria,"count":len(results),"properties":results})

@app.post("/api/save/<int:pid>")
def save(pid):
    saved=session.get("saved",[])
    if pid not in saved: saved.append(pid)
    session["saved"]=saved
    return jsonify({"ok":True,"count":len(saved)})

@app.post("/api/unsave/<int:pid>")
def unsave(pid):
    saved=[x for x in session.get("saved",[]) if x!=pid]
    session["saved"]=saved
    return jsonify({"ok":True,"count":len(saved)})

@app.route("/dashboard")
def dashboard():
    saved_ids=session.get("saved",[])
    saved_props=[p for p in PROPERTIES if p["id"] in saved_ids]
    return render_template("dashboard.html", saved_props=saved_props)

@app.post("/api/alert")
def alert():
    alerts=session.get("alerts",[])
    alerts.append({"query":request.json.get("query",""),"email":request.json.get("email","")})
    session["alerts"]=alerts
    return jsonify({"ok":True})

@app.route("/calculator")
def calculator():
    return render_template("calculator.html")

@app.route("/map")
def map_page():
    return render_template("map.html", properties=PROPERTIES)

@app.route("/admin")
def admin():
    return render_template("admin.html", properties=PROPERTIES, projects=PROJECTS)

@app.post("/api/admin/property")
def admin_property():
    data=request.json
    pid=int(data.get("id",0))
    p=next((x for x in PROPERTIES if x["id"]==pid),None)
    if not p: return jsonify({"ok":False}),404
    for k in ["title","location","type","status","price","beds","baths","sqm"]:
        if k in data: p[k]=data[k]
    return jsonify({"ok":True,"property":p})

@app.post("/api/lang")
def lang():
    session["lang"]="AM" if session.get("lang","EN")=="EN" else "EN"
    return jsonify({"lang":session["lang"]})

if __name__=="__main__":
    app.run(host="0.0.0.0",port=int(os.environ.get("PORT",5000)),debug=True)

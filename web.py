# web.py

from flask import Flask, render_template, request, redirect, url_for
import json, os
from config import ADMIN_IDS
from datetime import datetime

app = Flask(__name__)
LOG_FILE, KEY_FILE = "logs.json", "keys.json"

def load(f): return json.load(open(f)) if os.path.exists(f) else []
def save(f,d): json.dump(d, open(f,"w"), indent=2)

@app.route("/")
def dashboard():
    logs = load(LOG_FILE)
    keys = load(KEY_FILE)
    return render_template("index.html", logs=logs[::-1], keys=keys)

@app.route("/send_key", methods=["POST"])
def send_key():
    uid, pkg = int(request.form["user_id"]), request.form["package"]
    from main import bot, get_key, save_keys
    key = get_key(pkg); save_keys(load(KEY_FILE))
    bot.send_message(uid, f"🔑 Đây là key `{pkg}` của bạn:\n`{key}`")
    logs = load(LOG_FILE)
    for e in reversed(logs):
        if e["user_id"]==uid and e["status"]=="pending":
            e.update(status="confirmed", confirmed_by="WEB", confirmed_time=datetime.now().isoformat())
            break
    save(LOG_FILE, logs)
    return redirect(url_for("dashboard"))

@app.route("/add_keys", methods=["POST"])
def add_keys():
    pkg = request.form["package"].upper()
    new = request.form["keys"].splitlines()
    d = load(KEY_FILE)
    d.setdefault(pkg, []).extend(new)
    save(KEY_FILE, d)
    return redirect(url_for("dashboard"))

if __name__=="__main__":
    app.run(port=8000)

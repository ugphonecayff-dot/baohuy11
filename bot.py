import telebot, json, os
from flask import Flask, request, render_template, redirect, url_for
from datetime import datetime
from config import BOT_TOKEN, ADMIN_IDS, MB_ACCOUNT, MB_BANK_CODE, WEBHOOK_SECRET

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

KEYS_FILE = "keys.json"
LOGS_FILE = "logs.json"

def load_json(f):
    return json.load(open(f)) if os.path.exists(f) else []

def save_json(f, d):
    with open(f, "w") as file:
        json.dump(d, file, indent=2)

def get_key(pkg):
    keys = load_json(KEYS_FILE)
    if pkg in keys and keys[pkg]:
        return keys[pkg].pop(0)
    return None

def save_keyfile(keys):
    save_json(KEYS_FILE, keys)

# ===== BOT COMMANDS =====
@bot.message_handler(commands=["start"])
def cmd_start(msg):
    bot.reply_to(msg, "👋 Xin chào! Gửi /buy để chọn gói key bạn muốn mua.")

@bot.message_handler(commands=["buy"])
def cmd_buy(msg):
    markup = telebot.types.InlineKeyboardMarkup()
    packages = {
        "7DAY": {"price": 30000, "label": "🔹 Gói 7 ngày – 30.000đ"},
        "30DAY": {"price": 70000, "label": "🔸 Gói 30 ngày – 70.000đ"},
        "365DAY": {"price": 250000, "label": "💎 Gói 365 ngày – 250.000đ"},
    }
    for k, v in packages.items():
        markup.add(telebot.types.InlineKeyboardButton(v["label"], callback_data=f"buy_{k}"))
    bot.send_message(msg.chat.id, "💰 Chọn gói key bạn muốn mua:", reply_markup=markup)

@bot.callback_query_handler(func=lambda c: c.data.startswith("buy_"))
def cb_buy(call):
    pkg = call.data.split("_")[1]
    price = {"7DAY":30000,"30DAY":70000,"365DAY":250000}[pkg]
    note = f"key-{pkg}-{call.from_user.id}"
    url = f"https://img.vietqr.io/image/{MB_BANK_CODE}-{MB_ACCOUNT}-compact.png?amount={price}&addInfo={note}"
    cap = f"📦 Gói: *{pkg}*\n💳 Số tiền: *{price}đ*\n🏦 MB Bank\n📄 Nội dung: `{note}`\n\nSau khi thanh toán, gửi ảnh CK tại đây!"
    bot.send_photo(call.message.chat.id, url, caption=cap, parse_mode="Markdown")

# ===== ẢNH CK =====
@bot.message_handler(content_types=["photo"])
def handle_photo(msg):
    logs = load_json(LOGS_FILE)
    uid = msg.from_user.id
    fid = msg.photo[-1].file_id
    guess = "7DAY" if "7" in (msg.caption or "") else "30DAY" if "30" in (msg.caption or "") else "365DAY"
    entry = {
        "user_id": uid, "username": msg.from_user.username,
        "file_id": fid, "caption": msg.caption,
        "status": "pending", "guess_package": guess,
        "time": datetime.now().isoformat()
    }
    logs.append(entry)
    save_json(LOGS_FILE, logs)
    for admin in ADMIN_IDS:
        btn = telebot.types.InlineKeyboardMarkup()
        btn.add(telebot.types.InlineKeyboardButton("✅ Xác nhận", callback_data=f"confirm_{uid}_{guess}"))
        bot.send_photo(admin, fid, caption=f"Ảnh từ @{msg.from_user.username}\nGói: {guess}", reply_markup=btn)
    bot.reply_to(msg, "✅ Đã gửi ảnh, chờ admin xác nhận.")

@bot.callback_query_handler(func=lambda c: c.data.startswith("confirm_"))
def confirm_cb(call):
    uid, pkg = call.data.split("_")[1:]
    key = get_key(pkg)
    if key:
        bot.send_message(uid, f"🔑 Đây là key `{pkg}` của bạn:\n`{key}`", parse_mode="Markdown")
        logs = load_json(LOGS_FILE)
        for entry in reversed(logs):
            if entry["user_id"] == int(uid) and entry["status"] == "pending":
                entry["status"] = "confirmed"
                break
        save_json(LOGS_FILE, logs)
        keys = load_json(KEYS_FILE)
        save_keyfile(keys)
        bot.answer_callback_query(call.id, "✅ Đã gửi key!")
    else:
        bot.answer_callback_query(call.id, "❌ Hết key!")

# ===== WEB UI =====
@app.route("/")
def admin_ui():
    logs = load_json(LOGS_FILE)[::-1]
    keys = load_json(KEYS_FILE)
    return render_template("index.html", logs=logs, keys=keys)

@app.route("/send_key", methods=["POST"])
def web_sendkey():
    uid, pkg = int(request.form["user_id"]), request.form["package"]
    key = get_key(pkg)
    if key:
        bot.send_message(uid, f"🔑 Đây là key `{pkg}` của bạn:\n`{key}`", parse_mode="Markdown")
        logs = load_json(LOGS_FILE)
        for entry in reversed(logs):
            if entry["user_id"] == uid and entry["status"] == "pending":
                entry["status"] = "confirmed"
                break
        save_json(LOGS_FILE, logs)
        save_keyfile(load_json(KEYS_FILE))
    return redirect(url_for("admin_ui"))

@app.route("/add_keys", methods=["POST"])
def add_keys():
    pkg = request.form["package"].upper()
    keys = [k.strip() for k in request.form["keys"].splitlines() if k.strip()]
    all_keys = load_json(KEYS_FILE)
    all_keys.setdefault(pkg, []).extend(keys)
    save_keyfile(all_keys)
    return redirect(url_for("admin_ui"))

# ===== WEBHOOK API =====
@app.route("/webhook", methods=["POST"])
def handle_webhook():
    data = request.get_json()
    if data.get("secret") != WEBHOOK_SECRET:
        return {"error": "unauthorized"}, 403
    uid, pkg = int(data["user_id"]), data["package"]
    key = get_key(pkg)
    if not key:
        return {"error": "no key"}, 400
    bot.send_message(uid, f"🔑 Đây là key `{pkg}` của bạn:\n`{key}`", parse_mode="Markdown")
    save_keyfile(load_json(KEYS_FILE))
    return {"status": "ok"}

# ===== CHẠY BOT + WEB =====
if __name__ == "__main__":
    from threading import Thread
    Thread(target=lambda: bot.infinity_polling()).start()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

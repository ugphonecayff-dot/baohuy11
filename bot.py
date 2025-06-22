import telebot
import json
import os
from telebot import types
from datetime import datetime
from config import BOT_TOKEN, ADMIN_IDS
from keep_alive import keep_alive

bot = telebot.TeleBot(BOT_TOKEN)

MB_ACCOUNT = "0971487462"
MB_BANK_CODE = "mbbank"

PACKAGES = {
    "7DAY": {"price": 30000, "label": "🔹 Gói 7 ngày – 30.000đ"},
    "30DAY": {"price": 70000, "label": "🔸 Gói 30 ngày – 70.000đ"},
    "365DAY": {"price": 250000, "label": "💎 Gói 365 ngày – 250.000đ"},
}

KEYS_FILE = "keys.json"
LOG_FILE = "logs.json"
ANTI_SPAM_SECONDS = 15
last_photo_time = {}

# === Quản lý keys.json ===

def load_keys():
    if not os.path.exists(KEYS_FILE):
        with open(KEYS_FILE, "w") as f:
            json.dump({}, f)
    with open(KEYS_FILE, "r") as f:
        return json.load(f)

def save_keys(data):
    with open(KEYS_FILE, "w") as f:
        json.dump(data, f, indent=2)

def get_key(package):
    data = load_keys()
    if package in data and data[package]:
        key = data[package].pop(0)
        save_keys(data)
        return key
    return None

# === Quản lý logs.json ===

def load_logs():
    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, "w") as f:
            json.dump([], f)
    with open(LOG_FILE, "r") as f:
        return json.load(f)

def save_log(entry):
    logs = load_logs()
    logs.append(entry)
    with open(LOG_FILE, "w") as f:
        json.dump(logs, f, indent=2)

# === /start ===

@bot.message_handler(commands=["start"])
def start(message):
    welcome_msg = (
        "👋 *Chào mừng bạn đến với Bot Bán Key!*\n\n"
        "🧾 Các gói hiện có:\n"
        "🔹 *7 ngày* – 30.000đ\n"
        "🔸 *30 ngày* – 70.000đ\n"
        "💎 *365 ngày* – 250.000đ\n\n"
        "Gửi /buy để bắt đầu mua key\n"
        "Sau khi thanh toán, gửi ảnh chuyển khoản để admin xác nhận."
    )
    bot.send_message(message.chat.id, welcome_msg, parse_mode="Markdown")

# === /buy ===

@bot.message_handler(commands=["buy"])
def handle_buy(message):
    markup = types.InlineKeyboardMarkup()
    for code, pkg in PACKAGES.items():
        markup.add(types.InlineKeyboardButton(pkg["label"], callback_data=f"buy_{code}"))
    bot.send_message(message.chat.id, "💰 Chọn gói key bạn muốn mua:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("buy_"))
def handle_package_selected(call):
    package_code = call.data.split("_")[1]
    package = PACKAGES.get(package_code)
    if not package:
        return bot.answer_callback_query(call.id, "❌ Gói không hợp lệ")

    amount = package['price']
    note = f"key-{package_code}-{call.from_user.id}"

    qr_url = (
        f"https://img.vietqr.io/image/{MB_BANK_CODE}-{MB_ACCOUNT}-compact.png"
        f"?amount={amount}&addInfo={note}"
    )

    caption = (
        f"📦 Gói: *{package['label']}*\n"
        f"💳 Số tiền: *{amount:,} VNĐ*\n"
        f"🏦 Ngân hàng: *MB Bank*\n"
        f"👤 STK: `{MB_ACCOUNT}`\n"
        f"📄 Nội dung: `{note}`\n\n"
        f"📸 Quét mã VietQR để thanh toán. Sau đó gửi ảnh chuyển khoản cho bot!"
    )
    bot.send_photo(call.message.chat.id, qr_url, caption=caption, parse_mode="Markdown")
    bot.answer_callback_query(call.id)

# === /confirm user_id gói ===

@bot.message_handler(commands=["confirm"])
def handle_confirm(message):
    if message.from_user.id not in ADMIN_IDS:
        return bot.reply_to(message, "⛔ Bạn không có quyền xác nhận.")
    try:
        _, user_id, package = message.text.split()
        user_id = int(user_id)
        package = package.upper()

        key = get_key(package)
        if key:
            bot.send_message(user_id, f"🔑 Cảm ơn bạn!\nĐây là key `{package}` của bạn:\n\n`{key}`", parse_mode="Markdown")
            bot.reply_to(message, f"✅ Đã gửi key `{package}` cho user `{user_id}`.", parse_mode="Markdown")
        else:
            bot.reply_to(message, f"❌ Hết key trong gói {package}.")
    except Exception as e:
        bot.reply_to(message, f"⚠️ Lỗi: {e}")

# === /addkey ===

@bot.message_handler(commands=["addkey"])
def addkey_command(message):
    if message.from_user.id not in ADMIN_IDS:
        return bot.reply_to(message, "⛔ Bạn không có quyền.")
    msg = bot.reply_to(message, "📦 Nhập tên gói key (VD: 7DAY):")
    bot.register_next_step_handler(msg, handle_package_input)

def handle_package_input(message):
    package = message.text.strip().upper()
    msg = bot.reply_to(message, f"Gửi danh sách key cho gói `{package}` (mỗi dòng 1 key):", parse_mode="Markdown")
    bot.register_next_step_handler(msg, lambda m: save_keys_for_package(m, package))

def save_keys_for_package(message, package):
    keys = [k.strip() for k in message.text.strip().split("\n") if k.strip()]
    data = load_keys()
    if package not in data:
        data[package] = []
    data[package].extend(keys)
    save_keys(data)
    bot.reply_to(message, f"✅ Đã thêm {len(keys)} key vào gói `{package}`.", parse_mode="Markdown")

# === 📸 Xử lý ảnh, log, chống spam, chống trùng ===

@bot.message_handler(content_types=["photo"])
def handle_photo(message):
    user = message.from_user
    file_id = message.photo[-1].file_id
    caption = message.caption or "Không có"
    now = datetime.now()

    # Anti-spam
    if user.id in last_photo_time:
        diff = (now - last_photo_time[user.id]).total_seconds()
        if diff < ANTI_SPAM_SECONDS:
            return bot.reply_to(message, f"⏱ Vui lòng đợi {ANTI_SPAM_SECONDS - int(diff)} giây trước khi gửi ảnh khác.")
    last_photo_time[user.id] = now

    # Kiểm tra trùng ảnh
    logs = load_logs()
    for entry in logs:
        if entry["file_id"] == file_id:
            return bot.reply_to(message, "⚠️ Ảnh này đã gửi trước đó. Vui lòng không gửi lại.")

    # Gợi ý gói
    guess = "UNKNOWN"
    if "7" in caption:
        guess = "7DAY"
    elif "30" in caption:
        guess = "30DAY"
    elif "365" in caption:
        guess = "365DAY"

    # Log ảnh
    entry = {
        "user_id": user.id,
        "username": user.username,
        "file_id": file_id,
        "caption": caption,
        "status": "pending",
        "guess_package": guess,
        "time": now.isoformat()
    }
    save_log(entry)

    # Nút xác nhận
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(
        "✅ Xác nhận & Gửi key",
        callback_data=f"confirmkey_{user.id}_{guess}"
    ))

    # Gửi ảnh tới admin
    for admin in ADMIN_IDS:
        bot.send_photo(admin, file_id,
            caption=f"📸 Từ: @{user.username or 'Không có'} | ID: `{user.id}`\n📄 {caption}\n🎯 Gợi ý: `{guess}`",
            parse_mode="Markdown", reply_markup=markup)

    bot.reply_to(message, "✅ Đã gửi ảnh cho admin. Vui lòng chờ xác nhận.")

# === 🔘 Xác nhận gửi key từ ảnh

@bot.callback_query_handler(func=lambda call: call.data.startswith("confirmkey_"))
def handle_confirm_button(call):
    try:
        _, user_id, package = call.data.split("_")
        user_id = int(user_id)
        package = package.upper()

        key = get_key(package)
        if not key:
            return bot.answer_callback_query(call.id, "❌ Hết key!")

        bot.send_message(user_id, f"🔑 Đây là key `{package}` của bạn:\n\n`{key}`", parse_mode="Markdown")
        bot.send_message(call.message.chat.id, f"✅ Đã gửi key `{package}` cho user `{user_id}`.")

        # Cập nhật log
        logs = load_logs()
        for entry in reversed(logs):
            if entry["user_id"] == user_id and entry["status"] == "pending":
                entry["status"] = "confirmed"
                entry["confirmed_by"] = call.from_user.id
                entry["confirmed_time"] = datetime.now().isoformat()
                break
        with open(LOG_FILE, "w") as f:
            json.dump(logs, f, indent=2)

        bot.answer_callback_query(call.id, "✅ Gửi thành công.")
    except Exception as e:
        bot.answer_callback_query(call.id, f"Lỗi: {e}")

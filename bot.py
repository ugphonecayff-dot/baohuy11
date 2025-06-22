import telebot
import json
import os
from datetime import datetime
from telebot import types
from config import BOT_TOKEN, ADMIN_IDS, MB_ACCOUNT, MB_BANK_CODE
from keep_alive import keep_alive

bot = telebot.TeleBot(BOT_TOKEN)
pending_users = {}

PACKAGES = {
    "7DAY": {"price": 30000, "label": "🔹 Gói 7 ngày – 30.000đ"},
    "30DAY": {"price": 70000, "label": "🔸 Gói 30 ngày – 70.000đ"},
    "365DAY": {"price": 250000, "label": "💎 Gói 365 ngày – 250.000đ"},
}

def load_keys():
    if not os.path.exists("keys.json"):
        with open("keys.json", "w") as f:
            json.dump({}, f)
    with open("keys.json", "r") as f:
        return json.load(f)

def save_keys(data):
    with open("keys.json", "w") as f:
        json.dump(data, f, indent=2)

def get_key(package):
    data = load_keys()
    if package in data and data[package]:
        key = data[package].pop(0)
        save_keys(data)
        return key
    return None

@bot.message_handler(commands=["start"])
def start(message):
    bot.send_message(message.chat.id, "👋 Xin chào! Gửi /buy để chọn gói key bạn muốn mua🔦")

@bot.message_handler(commands=['buy'])
def handle_buy(message):
    markup = types.InlineKeyboardMarkup()
    for code, pkg in PACKAGES.items():
        markup.add(types.InlineKeyboardButton(pkg["label"], callback_data=f"buy_{code}"))
    bot.send_message(message.chat.id, "💰 Chọn gói key bạn muốn mua:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("buy_"))
def handle_package_selected(call):
    package_code = call.data.split("_")[1]
    pending_users[call.from_user.id] = package_code
    package = PACKAGES.get(package_code)
    amount = package['price']
    note = f"key-{package_code}-{call.from_user.id}"
    qr_url = (
        f"https://img.vietqr.io/image/{MB_BANK_CODE}-{MB_ACCOUNT}-compact.png"
        f"?amount={amount}&addInfo={note}"
    )
    caption = (
        f"📦 Gói đã chọn: *{package['label']}*\n"
        f"💳 Số tiền: *{amount:,} VNĐ*\n"
        f"🏦 Ngân hàng: *MB Bank*\n"
        f"👤 STK: `{MB_ACCOUNT}`\n"
        f"📄 Nội dung chuyển khoản: `{note}`\n\n"
        f"📸 Quét mã VietQR để thanh toán rồi gửi ảnh.\n"
        f"⏳ Chờ admin xác nhận sau khi gửi ảnh."
    )
    bot.send_photo(call.message.chat.id, qr_url, caption=caption, parse_mode="Markdown")
    bot.answer_callback_query(call.id)

@bot.message_handler(content_types=["photo"])
def handle_photo(msg):
    uid = msg.from_user.id
    username = msg.from_user.username or "Không rõ"
    file_id = msg.photo[-1].file_id
    pkg = pending_users.get(uid, "UNKNOWN")
    amount = PACKAGES.get(pkg, {}).get("price", 0)
    note = f"key-{pkg}-{uid}"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    logs = []
    if os.path.exists("logs.json"):
        with open("logs.json", "r") as f:
            logs = json.load(f)
    logs.append({
        "user_id": uid,
        "username": username,
        "file_id": file_id,
        "package": pkg,
        "timestamp": timestamp,
        "status": "pending"
    })
    with open("logs.json", "w") as f:
        json.dump(logs, f, indent=2)

    caption = (
        f"🧾 Ảnh từ @{username}\n"
        f"👤 ID: `{uid}`\n"
        f"📦 Gói: *{pkg}*\n"
        f"💰 Số tiền: *{amount:,}đ*\n"
        f"📄 Nội dung: `{note}`\n"
        f"🕒 Thời gian: `{timestamp}`"
    )
    btn = types.InlineKeyboardMarkup()
    btn.add(types.InlineKeyboardButton("✅ Xác nhận", callback_data=f"confirm_{uid}_{pkg}"))

    for admin_id in ADMIN_IDS:
        bot.send_photo(admin_id, file_id, caption=caption, reply_markup=btn, parse_mode="Markdown")

    bot.reply_to(msg, "✅ Đã nhận ảnh thanh toán. Chờ admin xác nhận.")

@bot.callback_query_handler(func=lambda c: c.data.startswith("confirm_"))
def inline_confirm_callback(call):
    _, user_id, package = call.data.split("_")
    user_id = int(user_id)
    key = get_key(package)
    if key:
        bot.send_message(user_id, f"🔑 Đây là key `{package}` của bạn:\n\n`{key}`", parse_mode="Markdown")
        bot.edit_message_caption("✅ Đã xác nhận và gửi key!", chat_id=call.message.chat.id, message_id=call.message.message_id)
    else:
        bot.send_message(call.message.chat.id, f"❌ Hết key gói `{package}`.")

@bot.message_handler(commands=["confirm"])
def confirm_command(message):
    if message.from_user.id not in ADMIN_IDS:
        return bot.reply_to(message, "⛔ Bạn không có quyền.")
    try:
        _, uid, package = message.text.split()
        uid = int(uid)
        key = get_key(package)
        if key:
            bot.send_message(uid, f"🔑 Đây là key `{package}` của bạn:\n\n`{key}`", parse_mode="Markdown")
            bot.reply_to(message, f"✅ Đã gửi key gói `{package}` cho user `{uid}`.", parse_mode="Markdown")
        else:
            bot.reply_to(message, f"❌ Hết key trong gói `{package}`.")
    except:
        bot.reply_to(message, "❗ Dùng đúng cú pháp: /confirm <user_id> <gói>")

@bot.message_handler(commands=["addkey"])
def addkey_command(message):
    if message.from_user.id not in ADMIN_IDS:
        return bot.reply_to(message, "⛔ Bạn không có quyền.")
    msg = bot.reply_to(message, "📦 Nhập tên gói key muốn thêm (VD: 7DAY, 30DAY, 365DAY):")
    bot.register_next_step_handler(msg, handle_package_input)

def handle_package_input(message):
    user_input = message.text.strip().upper()

    matched_package = None
    for pkg in PACKAGES:
        if user_input == pkg.upper():
            matched_package = pkg
            break

    if not matched_package:
        available = ", ".join(PACKAGES.keys())
        return bot.reply_to(
            message,
            f"❗ Gói không hợp lệ.\n📦 Các gói hợp lệ: {available}"
        )

    msg = bot.reply_to(
        message,
        f"📥 Gửi danh sách key cho gói `{matched_package}` (mỗi dòng 1 key):",
        parse_mode="Markdown"
    )
    bot.register_next_step_handler(msg, lambda m: save_keys_for_package(m, matched_package))

def save_keys_for_package(message, package):
    new_keys = [k.strip() for k in message.text.strip().split("\n") if k.strip()]
    data = load_keys()
    data.setdefault(package, []).extend(new_keys)
    save_keys(data)
    bot.reply_to(message, f"✅ Đã thêm {len(new_keys)} key vào gói `{package}`.", parse_mode="Markdown")

keep_alive()
print("🤖 Bot is running...")
bot.infinity_polling()

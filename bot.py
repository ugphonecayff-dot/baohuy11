# ======================= IMPORT VÀ CẤU HÌNH ==========================
import telebot
import json
import os
from telebot import types
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

# ======================= HÀM QUẢN LÝ KEY =============================

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

# ======================= /start – CHÀO MỪNG NGƯỜI DÙNG =============================

@bot.message_handler(commands=["start"])
def start(message):
    welcome_msg = (
        "👋 *Chào mừng bạn đến với Bot Bán Key👨‍💻*\n\n"
        "🧾 Các gói hiện có:\n"
        "   🔹 *7 ngày* – 30.000đ\n"
        "   🔸 *30 ngày* – 70.000đ\n"
        "   💎 *365 ngày* – 250.000đ\n\n"
        "📌 Gửi lệnh /buy để bắt đầu mua key\n"
        "📸 Sau khi chuyển khoản, gửi ảnh cho admin xác nhận."
    )
    bot.send_message(message.chat.id, welcome_msg, parse_mode="Markdown")

# ======================= /buy – CHỌN GÓI MUA KEY =============================

@bot.message_handler(commands=['buy'])
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
        f"📦 Gói đã chọn: *{package['label']}*\n"
        f"💳 Số tiền: *{amount:,} VNĐ*\n"
        f"🏦 Ngân hàng: *MB Bank*\n"
        f"👤 STK: `{MB_ACCOUNT}`\n"
        f"📄 Nội dung chuyển khoản: `{note}`\n\n"
        f"📸 Quét mã VietQR dưới đây để thanh toán.\n"
        f"⏳ Sau khi thanh toán, vui lòng chụp ảnh gửi lại để admin xác nhận."
    )
    bot.send_photo(call.message.chat.id, qr_url, caption=caption, parse_mode="Markdown")
    bot.answer_callback_query(call.id)

# ======================= /confirm – ADMIN XÁC NHẬN VÀ GỬI KEY =============================

@bot.message_handler(commands=['confirm'])
def handle_confirm(message):
    if message.from_user.id not in ADMIN_IDS:
        return bot.reply_to(message, "⛔ Bạn không có quyền xác nhận.")
    try:
        parts = message.text.split()
        if len(parts) != 3:
            return bot.reply_to(message, "❗ Dùng đúng cú pháp: /confirm <user_id> <gói>\nVí dụ: /confirm 123456789 30DAY")
        user_id = int(parts[1])
        package = parts[2].upper()

        key = get_key(package)
        if key:
            bot.send_message(user_id, f"🔑 Cảm ơn bạn đã thanh toán!\nĐây là key `{package}` của bạn:\n\n`{key}`", parse_mode="Markdown")
            bot.reply_to(message, f"✅ Đã gửi key gói {package} cho user `{user_id}`.", parse_mode="Markdown")
        else:
            bot.reply_to(message, f"❌ Hết key trong gói {package}.")
    except Exception as e:
        bot.reply_to(message, f"⚠️ Lỗi: {str(e)}")

# ======================= /addkey – ADMIN THÊM KEY =============================

@bot.message_handler(commands=["addkey"])
def addkey_command(message):
    if message.from_user.id not in ADMIN_IDS:
        return bot.reply_to(message, "⛔ Bạn không có quyền.")
    msg = bot.reply_to(message, "📦 Nhập tên gói key muốn thêm (VD: 7DAY, 30DAY, 365DAY):")
    bot.register_next_step_handler(msg, handle_package_input)

def handle_package_input(message):
    package = message.text.strip().upper()
    msg = bot.reply_to(message, f"📥 Gửi danh sách key cho gói `{package}` (mỗi dòng 1 key):", parse_mode="Markdown")
    bot.register_next_step_handler(msg, lambda m: save_keys_for_package(m, package))

def save_keys_for_package(message, package):
    new_keys = [k.strip() for k in message.text.strip().split("\n") if k.strip()]
    data = load_keys()
    if package not in data:
        data[package] = []
    data[package].extend(new_keys)
    save_keys(data)
    bot.reply_to(message, f"✅ Đã thêm {len(new_keys)} key vào gói `{package}`.", parse_mode="Markdown")

# ======================= KHỞI CHẠY BOT =============================

keep_alive()
print("🤖 Bot is running...")
bot.infinity_polling()

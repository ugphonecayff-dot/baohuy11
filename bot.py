import telebot
import os
import time
import logging
import requests
from dotenv import load_dotenv
from keep_alive import keep_alive
from openai import OpenAI

# === TẢI .env ===
load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN") or "6367532329:AAGJh1RnIa-UZGBUdzKHTy3lyKnB81NdqjM"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY") or "sk-proj-xxx..."

# === CẤU HÌNH LOG ===
logging.basicConfig(
    filename='bot.log',
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s - %(message)s'
)

# === KHỞI TẠO BOT TELEGRAM ===
bot = telebot.TeleBot(TELEGRAM_TOKEN)
keep_alive()

# === ADMIN & KEY ===
ADMIN_IDS = [5736655322]
KEY_FILE = "keys.txt"
api_keys = []
current_key_index = 0
client = None

# === LOAD KEY ===
def load_keys():
    global api_keys
    if os.path.exists(KEY_FILE):
        with open(KEY_FILE, "r") as f:
            api_keys = [line.strip() for line in f if line.strip().startswith("sk-")]
    if not api_keys:
        api_keys = [OPENAI_API_KEY]
load_keys()

# === GHI KEY VÀO FILE ===
def save_keys():
    with open(KEY_FILE, "w") as f:
        f.write("\n".join(api_keys))

# === UPTIME ===
start_time = time.time()
def get_uptime():
    elapsed = int(time.time() - start_time)
    h, rem = divmod(elapsed, 3600)
    m, s = divmod(rem, 60)
    return f"⏱ Uptime: {h}h {m}m {s}s"

# === CHUYỂN KEY ===
def get_current_key():
    return api_keys[current_key_index]

def switch_to_key(index):
    global current_key_index, client
    current_key_index = index
    client = OpenAI(api_key=api_keys[current_key_index])

switch_to_key(0)

# === KIỂM TRA KEY GIỐNG CÁCH CURL ===
def test_openai_key_direct(key: str) -> bool:
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {key}"
    }
    payload = {
        "model": "gpt-4o-mini",
        "messages": [{"role": "user", "content": "Ping"}],
        "max_tokens": 5
    }
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        return response.status_code == 200
    except Exception as e:
        logging.error(f"Lỗi kiểm tra key trực tiếp: {e}")
        return False

# === LỆNH CƠ BẢN ===
@bot.message_handler(commands=["start", "help"])
def welcome(message):
    bot.reply_to(message,
        "🤖 Xin chào! Tôi là trợ lý AI sử dụng GPT-4.\n\n"
        "✏️ Gõ nội dung để tôi trả lời bạn.\n\n"
        "📚 Lệnh:\n/start hoặc /help - Giới thiệu bot\n/uptime - Thời gian hoạt động bot\n/addkey - (Chỉ admin) thêm API key"
    )

@bot.message_handler(commands=["uptime"])
def uptime(message):
    bot.reply_to(message, get_uptime())

# === LỆNH ADD KEY ===
@bot.message_handler(commands=['addkey'])
def add_key(message):
    user_id = message.from_user.id
    if user_id not in ADMIN_IDS:
        bot.reply_to(message, "🚫 Bạn không có quyền sử dụng lệnh này.")
        return

    parts = message.text.strip().split(" ", 1)
    if len(parts) != 2 or not parts[1].startswith("sk-"):
        bot.reply_to(message, "⚠️ Dùng đúng cú pháp:\n`/addkey sk-...`", parse_mode='Markdown')
        return

    new_key = parts[1].strip()
    bot.reply_to(message, "🔍 Đang kiểm tra key mới...")

    if test_openai_key_direct(new_key):
        if new_key not in api_keys:
            api_keys.append(new_key)
            save_keys()
        switch_to_key(api_keys.index(new_key))
        bot.send_message(message.chat.id, "✅ Key hợp lệ và đã được sử dụng.")
    else:
        bot.send_message(message.chat.id, "❌ Key không hợp lệ hoặc đã hết hạn.")

# === XỬ LÝ CHAT ===
@bot.message_handler(func=lambda m: True)
def handle_message(message):
    username = message.from_user.username or "unknown"
    content = message.text.strip()
    logging.info(f"Người dùng: @{username} | Nội dung: {content}")

    wait_msg = bot.reply_to(message, "⏳ Đang xử lý...")

    for attempt in range(len(api_keys)):
        try:
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": content}],
                max_tokens=1000,
                temperature=0.7
            )
            reply = response.choices[0].message.content.strip()
            bot.edit_message_text(reply, chat_id=wait_msg.chat.id, message_id=wait_msg.message_id)
            return
        except Exception as e:
            logging.error(f"Lỗi với key index {current_key_index}: {e}")
            if attempt < len(api_keys) - 1:
                switch_to_key((current_key_index + 1) % len(api_keys))
            else:
                bot.edit_message_text(f"⚠️ Đã lỗi ở tất cả key:\n{e}", chat_id=wait_msg.chat.id, message_id=wait_msg.message_id)

# === CHẠY BOT ===
logging.info("🤖 Bot Telegram GPT-4 đang chạy...")
bot.infinity_polling(timeout=10, long_polling_timeout=5)

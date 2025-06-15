import os
import time
import logging
from dotenv import load_dotenv
from keep_alive import keep_alive
import telebot
from openai import OpenAI, OpenAIError

# === LOAD ENV ===
load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
DEFAULT_KEY = os.getenv("OPENAI_API_KEY")

# === CẤU HÌNH ===
bot = telebot.TeleBot(TELEGRAM_TOKEN)
keep_alive()
ADMIN_IDS = [5736655322]
KEY_FILE = "keys.txt"
api_keys = []
current_key_index = 0
start_time = time.time()

# === LOGGING ===
logging.basicConfig(
    filename="bot.log",
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s - %(message)s'
)

# === HÀM QUẢN LÝ KEY ===
def load_keys():
    global api_keys
    if os.path.exists(KEY_FILE):
        with open(KEY_FILE, "r") as f:
            api_keys = [line.strip() for line in f if line.strip().startswith("sk-")]
    if not api_keys and DEFAULT_KEY:
        api_keys = [DEFAULT_KEY]

def save_keys():
    with open(KEY_FILE, "w") as f:
        f.write("\n".join(api_keys))

def switch_to_key(index):
    global current_key_index, client
    current_key_index = index
    client = OpenAI(api_key=api_keys[current_key_index])

load_keys()
switch_to_key(0)

def get_uptime():
    elapsed = int(time.time() - start_time)
    h, rem = divmod(elapsed, 3600)
    m, s = divmod(rem, 60)
    return f"⏱ Uptime: {h}h {m}m {s}s"

# === COMMAND: START / HELP ===
@bot.message_handler(commands=["start", "help"])
def cmd_start(message):
    bot.reply_to(message,
        "🤖 Xin chào! Tôi là bot GPT-4.\n\n"
        "📚 Lệnh:\n"
        "/start - Giới thiệu\n"
        "/uptime - Thời gian hoạt động\n"
        "/addkey <sk-...> - (Admin) thêm key"
    )

@bot.message_handler(commands=["uptime"])
def cmd_uptime(message):
    bot.reply_to(message, get_uptime())

# === ADMIN THÊM KEY ===
@bot.message_handler(commands=["addkey"])
def cmd_addkey(message):
    if message.from_user.id not in ADMIN_IDS:
        bot.reply_to(message, "🚫 Bạn không có quyền sử dụng lệnh này.")
        return

    parts = message.text.strip().split(" ", 1)
    if len(parts) != 2 or not parts[1].startswith("sk-"):
        bot.reply_to(message, "⚠️ Dùng đúng cú pháp: `/addkey sk-...`", parse_mode="Markdown")
        return

    new_key = parts[1].strip()
    test_client = OpenAI(api_key=new_key)

    try:
        _ = test_client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": "ping"}],
            max_tokens=5
        )
        if new_key not in api_keys:
            api_keys.append(new_key)
            save_keys()
        switch_to_key(api_keys.index(new_key))
        bot.reply_to(message, "✅ Key hợp lệ và đã được thêm.")
    except OpenAIError as e:
        bot.reply_to(message, f"❌ Key không hợp lệ:\n{e}")

# === XỬ LÝ TIN NHẮN AI ===
@bot.message_handler(func=lambda m: True)
def handle_ai(message):
    content = message.text.strip()
    wait_msg = bot.reply_to(message, "⏳ Đang xử lý...")
    for attempt in range(len(api_keys)):
        try:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": content}],
                max_tokens=1000
            )
            result = response.choices[0].message.content.strip()
            bot.edit_message_text(result, chat_id=wait_msg.chat.id, message_id=wait_msg.message_id)
            return
        except OpenAIError as e:
            logging.error(f"Lỗi key {current_key_index}: {e}")
            if attempt < len(api_keys) - 1:
                switch_to_key((current_key_index + 1) % len(api_keys))
            else:
                bot.edit_message_text(f"⚠️ Lỗi với tất cả key:\n{e}", chat_id=wait_msg.chat.id, message_id=wait_msg.message_id)

# === CHẠY BOT ===
logging.info("🤖 Bot Telegram đang chạy...")
bot.infinity_polling(timeout=10, long_polling_timeout=5)
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

def get_current_client():
    return OpenAI(api_key=api_keys[current_key_index])

def switch_to_key(index):
    global current_key_index
    current_key_index = index

# === LỆNH CƠ BẢN ===
@bot.message_handler(commands=["start", "help"])
def welcome(message):
    bot.reply_to(message,
        "🤖 Xin chào! Tôi là trợ lý AI sử dụng GPT-4.\n\n"
        "📚 Lệnh:\n/start hoặc /help - Giới thiệu bot\n/uptime - Thời gian hoạt động\n/addkey - Thêm key (chỉ admin)"
    )

@bot.message_handler(commands=["uptime"])
def uptime(message):
    bot.reply_to(message, get_uptime())

# === LỆNH THÊM KEY ===
@bot.message_handler(commands=['addkey'])
def add_key(message):
    user_id = message.from_user.id
    if user_id not in ADMIN_IDS:
        bot.reply_to(message, "🚫 Bạn không có quyền sử dụng lệnh này.")
        return

    parts = message.text.strip().split(" ", 1)
    if len(parts) != 2 or not parts[1].startswith("sk-"):
        bot.reply_to(message, "⚠️ Vui lòng nhập đúng cú pháp:\n`/addkey sk-...`", parse_mode='Markdown')
        return

    new_key = parts[1].strip()
    try:
        client = OpenAI(api_key=new_key)
        test = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": "Test key"}],
            max_tokens=5,
            temperature=0.5
        )
        if new_key not in api_keys:
            api_keys.append(new_key)
            save_keys()
        switch_to_key(api_keys.index(new_key))
        bot.reply_to(message, "✅ Đã thêm key mới và chuyển sang sử dụng.")
    except Exception as e:
        bot.reply_to(message, f"❌ Key không hợp lệ hoặc lỗi:\n{e}")

# === TRẢ LỜI NGƯỜI DÙNG ===
@bot.message_handler(func=lambda m: True)
def handle_message(message):
    username = message.from_user.username or "unknown"
    content = message.text.strip()
    logging.info(f"Người dùng: @{username} | Nội dung: {content}")

    wait_msg = bot.reply_to(message, "⏳ Đang xử lý...")

    for attempt in range(len(api_keys)):
        try:
            client = get_current_client()
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": content}],
                max_tokens=1000,
                temperature=0.7
            )
            reply = response.choices[0].message.content.strip()
            bot.edit_message_text(reply, chat_id=wait_msg.chat.id, message_id=wait_msg.message_id)
            return
        except OpenAIError as e:
            logging.error(f"Lỗi key {current_key_index}: {e}")
            if attempt < len(api_keys) - 1:
                switch_to_key((current_key_index + 1) % len(api_keys))
            else:
                bot.edit_message_text(f"⚠️ Đã lỗi ở tất cả key:\n{e}", chat_id=wait_msg.chat.id, message_id=wait_msg.message_id)

# === CHẠY BOT ===
logging.info("🤖 Bot GPT Telegram đã chạy...")
bot.infinity_polling(timeout=10, long_polling_timeout=5)

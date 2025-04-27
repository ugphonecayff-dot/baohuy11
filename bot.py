from keep_alive import keep_alive
import telebot
import requests
import time
import threading
from functools import wraps

keep_alive()

# Token bot Telegram
TOKEN = "6367532329:AAEuSSv8JuGKzJQD6qI431udTvdq1l25zo0"
bot = telebot.TeleBot(TOKEN)

# ID nhóm và ID admin
GROUP_IDS = [-1002221629819, -1002334731264]  # Các nhóm được phép dùng bot
ADMIN_ID = 5736655322  # ID admin (bạn)

# Cooldown dictionary
user_cooldowns = {}
auto_buff_tasks = {}

# Hàm kiểm tra cooldown
def is_on_cooldown(user_id, command):
    now = time.time()
    key = f"{user_id}_{command}"
    if key in user_cooldowns and now - user_cooldowns[key] < 30:
        return True
    user_cooldowns[key] = now
    return False

# Decorator: chỉ cho phép trong nhóm
def only_in_group(func):
    @wraps(func)
    def wrapper(message):
        if message.chat.id not in GROUP_IDS:
            bot.reply_to(message, "❌ Lệnh này chỉ sử dụng trong nhóm được cho phép.")
            return
        return func(message)
    return wrapper

# Decorator: chỉ cho phép admin
def only_admin(func):
    @wraps(func)
    def wrapper(message):
        if message.from_user.id != ADMIN_ID:
            bot.reply_to(message, "❌ Bạn không có quyền dùng lệnh này.")
            return
        return func(message)
    return wrapper

# Auto buff followers TikTok
def auto_buff(username, chat_id, user_id):
    if user_id not in auto_buff_tasks:
        return  # Người dùng đã huỷ treo

    api_url = f"https://dichvukey.site/fl.php?username={username}&key=ngocanvip"
    try:
        response = requests.get(api_url, timeout=60)
        data = response.json()

        message = (
            f"✅ Auto buff cho `@{username}` thành công!\n\n"
            f"➕ Thêm: {data.get('followers_add', 0)} followers\n"
            f"💬 {data.get('message', 'Không rõ')}"
        )
        bot.send_message(chat_id, message, parse_mode="Markdown")
    except Exception as e:
        bot.send_message(chat_id, f"❌ Lỗi buff auto: {e}")

    if user_id in auto_buff_tasks:
        task = threading.Timer(900, auto_buff, args=[username, chat_id, user_id])
        auto_buff_tasks[user_id] = task
        task.start()

# Lệnh /start
@bot.message_handler(commands=['start'])
@only_in_group
def handle_start(message):
    text = (
        "👋 Chào bạn!\n"
        "Dùng các lệnh sau:\n\n"
        "`/buff <username>` - Buff followers TikTok (API 2)\n"
        "`/fl3 <username>` - Buff followers TikTok (API 3)\n"
        "`/treo <username>` - Tự động buff mỗi 15 phút (Admin)\n"
        "`/huytreo` - Huỷ treo auto buff\n\n"
        "Ví dụ: `/buff baohuydz158`, `/treo baohuydz158`"
    )
    bot.reply_to(message, text, parse_mode="Markdown")

# Lệnh /buff
@bot.message_handler(commands=['buff'])
@only_in_group
def handle_buff(message):
    if is_on_cooldown(message.from_user.id, 'buff'):
        bot.reply_to(message, "⏳ Vui lòng đợi 30 giây trước khi dùng lại.")
        return

    parts = message.text.split()
    if len(parts) < 2:
        bot.reply_to(message, "❗ Vui lòng nhập username. Ví dụ: `/buff baohuydz158`", parse_mode="Markdown")
        return

    username = parts[1].lstrip("@")
    api_url = f"https://dichvukey.site/fl.php?username={username}&key=ngocanvip"

    bot.send_chat_action(message.chat.id, "typing")
    try:
        response = requests.get(api_url, timeout=60)
        data = response.json()
    except Exception:
        bot.reply_to(message, "❌ Lỗi API hoặc lỗi mạng.")
        return

    if str(data.get("status", "")).lower() not in ["true", "1", "success"]:
        bot.reply_to(message, f"✅Thông báo: {data.get('message', 'Không rõ')}")
        return

    reply = (
        f"✅ *Buff Followers Thành Công!*\n\n"
        f"👥 *Trước:* {data.get('followers_before', 'N/A')}\n"
        f"👥 *Sau:* {data.get('followers_after', 'N/A')}\n"
        f"✨ *Thêm:* {data.get('followers_add', 'N/A')}\n"
        f"💬 *Ghi chú:* {data.get('message', '')}"
    )
    bot.reply_to(message, reply, parse_mode="Markdown")

# Lệnh /fl3 (dùng API mới)
@bot.message_handler(commands=['fl3'])
@only_in_group
def handle_fl3(message):
    if is_on_cooldown(message.from_user.id, 'fl3'):
        bot.reply_to(message, "⏳ Vui lòng đợi 30 giây trước khi dùng lại.")
        return

    parts = message.text.split()
    if len(parts) < 2:
        bot.reply_to(message, "❗ Vui lòng nhập username. Ví dụ: `/fl3 ngocanvip`", parse_mode="Markdown")
        return

    username = parts[1].lstrip("@")
    api_url = f"https://nvp310107.x10.mx/fltik.php?username={username}&key=30T42025VN"

    bot.send_chat_action(message.chat.id, "typing")
    try:
        response = requests.get(api_url, timeout=30)
        data = response.json()
    except Exception:
        bot.reply_to(message, "❌ Lỗi API hoặc lỗi mạng.")
        return

    reply = (
        f"✅ *Buff Followers (API 3) Thành Công!*\n\n"
        f"👥 *Trước:* {data.get('followers_before', 'N/A')}\n"
        f"👥 *Sau:* {data.get('followers_after', 'N/A')}\n"
        f"✨ *Thêm:* {data.get('followers_add', 'N/A')}\n"
        f"💬 *Ghi chú:* {data.get('message', '')}\n"
        f"🔍 *Trạng thái:* {data.get('status', 'Không rõ')}"
    )
    bot.reply_to(message, reply, parse_mode="Markdown")

# Lệnh /treo
@bot.message_handler(commands=['treo'])
@only_in_group
@only_admin
def handle_treo(message):
    parts = message.text.split()
    if len(parts) < 2:
        bot.reply_to(message, "❗ Vui lòng nhập username. Ví dụ: `/treo baohuydz158`", parse_mode="Markdown")
        return

    username = parts[1].lstrip("@")
    user_id = message.from_user.id

    if user_id in auto_buff_tasks:
        bot.reply_to(message, "⚠️ Bạn đang treo rồi! Muốn đổi username phải `/huytreo` trước.")
        return

    bot.reply_to(message, f"✅ Đã bắt đầu treo buff cho `@{username}` mỗi 15 phút.", parse_mode="Markdown")
    auto_buff_tasks[user_id] = None
    auto_buff(username, message.chat.id, user_id)

# Lệnh /huytreo
@bot.message_handler(commands=['huytreo'])
@only_in_group
@only_admin
def handle_huytreo(message):
    user_id = message.from_user.id
    task = auto_buff_tasks.pop(user_id, None)
    if task:
        task.cancel()

    bot.reply_to(message, "✅ Đã huỷ treo buff.")

# Chạy bot
if __name__ == "__main__":
    print("Bot is running...")
    bot.infinity_polling(timeout=90, long_polling_timeout=45)

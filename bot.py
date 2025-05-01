from keep_alive import keep_alive
import telebot
import requests
import time
import threading
from functools import wraps
import urllib3

keep_alive()

# Token bot Telegram
TOKEN = "6367532329:AAEuSSv8JuGKzJQD6qI431udTvdq1l25zo0"
bot = telebot.TeleBot(TOKEN)

# ID admin
ADMIN_ID = 5736655322

# Cooldown dictionary
user_cooldowns = {}
auto_buff_tasks = {}

# Tắt cảnh báo SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def is_on_cooldown(user_id, command):
    now = time.time()
    key = f"{user_id}_{command}"
    if key in user_cooldowns:
        if now - user_cooldowns[key] < 30:
            return True
    user_cooldowns[key] = now
    return False

def auto_buff(username, chat_id, user_id):
    if user_id not in auto_buff_tasks:
        return
    api_url = f"https://dichvukey.site/fl.php?username={username}&key=ngocanvip"
    try:
        response = requests.get(api_url, timeout=80)
        data = response.json()
        bot.send_message(chat_id, f"✅ Tự động buff cho `@{username}` thành công!\n"
                                  f"➕ Thêm: {data.get('followers_add', 0)}\n"
                                  f"💬 {data.get('message', 'Không có')}",
                         parse_mode="Markdown")
    except Exception as e:
        bot.send_message(chat_id, f"❌ Lỗi khi tự động buff: {e}")

    if user_id in auto_buff_tasks:
        task = threading.Timer(900, auto_buff, args=[username, chat_id, user_id])
        auto_buff_tasks[user_id] = task
        task.start()

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message,
        "Xin chào!\n"
        "Sử dụng các lệnh sau để kiểm tra tài khoản TikTok:\n\n"
        "`/buff <username>` - Kiểm tra bằng API 2\n"
        "`/fl3 <username>` - Kiểm tra bằng API 3 (Soundcast)\n"
        "`/treo <username>` - Tự động buff mỗi 15 phút (chỉ admin)\n"
        "`/huytreo` - Huỷ treo\n\n"
        "Ví dụ: `/buff baohuydz158`, `/treo baohuydz158`",
        parse_mode="Markdown"
    )

@bot.message_handler(commands=['buff'])
def handle_buff(message):
    if is_on_cooldown(message.from_user.id, 'buff'):
        bot.reply_to(message, "⏳ Vui lòng đợi 30 giây trước khi dùng lại lệnh này.")
        return

    parts = message.text.strip().split()
    if len(parts) < 2:
        bot.reply_to(message, "❌ Vui lòng cung cấp tên người dùng TikTok. Ví dụ: `/buff baohuydz158`", parse_mode="Markdown")
        return
    username = parts[1].lstrip("@")

    bot.send_chat_action(message.chat.id, "typing")
    time.sleep(1)
    bot.reply_to(message, f"🔍 Đang kiểm tra `@{username}` bằng API 2...", parse_mode="Markdown")

    api_url = f"https://dichvukey.site/fl.php?username={username}&key=ngocanvip"

    try:
        response = requests.get(api_url, timeout=80)
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.RequestException:
        bot.reply_to(message, "❌ Lỗi khi kết nối với API. Vui lòng thử lại sau.")
        return
    except ValueError:
        bot.reply_to(message, f"✅Thông báo: {response.text.strip()}")
        return

    if str(data.get("status", "")).lower() not in ["true", "1", "success"]:
        bot.reply_to(message, f"✅Thông báo: {data.get('message', 'Tăng Thành công')}")
        return

    reply_text = (
        f"✅ *Thông tin tài khoản (API 2):*\n\n"
        f"💬 *Thông báo:* {data.get('message', 'Không có')}\n"
        f"👥 *Followers Trước:* {data.get('followers_before', 0)}\n"
        f"👥 *Followers Sau:* {data.get('followers_after', 0)}\n"
        f"✨ *Đã thêm:* {data.get('followers_add', 0)}\n\n"
        f"🔍 *Trạng thái:* ✅"
    )
    bot.reply_to(message, reply_text, parse_mode="Markdown", disable_web_page_preview=True)

@bot.message_handler(commands=['fl3'])
def handle_fl3(message):
    if is_on_cooldown(message.from_user.id, 'fl3'):
        bot.reply_to(message, "⏳ Vui lòng đợi 30 giây trước khi dùng lại lệnh này.")
        return

    parts = message.text.strip().split()
    if len(parts) < 2:
        bot.reply_to(message, "❌ Vui lòng cung cấp tên người dùng TikTok. Ví dụ: `/fl3 ngocanvip`", parse_mode="Markdown")
        return
    username = parts[1].lstrip("@")

    bot.send_chat_action(message.chat.id, "typing")
    time.sleep(1)
    bot.reply_to(message, f"🔍 Đang kiểm tra `@{username}` bằng API 3...", parse_mode="Markdown")

    api_url = f"https://nvp310107.x10.mx/fltik.php?username={username}&key=30T42025VN"

    try:
        response = requests.get(api_url, timeout=100, verify=False)
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.RequestException:
        bot.reply_to(message, "❌ Không thể kết nối đến API 3. Vui lòng thử lại sau.")
        return
    except ValueError:
        bot.reply_to(message, f"✅Thông báo: {response.text.strip()}")
        return

    reply_text = (
        f"✅ *Thông tin tài khoản (API 3):*\n\n"
        f"💬 *Thông báo:* {data.get('message', 'Không có')}\n"
        f"👥 *Followers Trước:* {data.get('followers_before', 'N/A')}\n"
        f"👥 *Followers Sau:* {data.get('followers_after', 'N/A')}\n"
        f"✨ *Đã thêm:* {data.get('followers_add', 'N/A')}\n\n"
        f"🔍 *Trạng thái:* {data.get('status', 'Không rõ')}"
    )
    bot.reply_to(message, reply_text, parse_mode="Markdown", disable_web_page_preview=True)

@bot.message_handler(commands=['treo'])
def handle_treo(message):
    if message.from_user.id != ADMIN_ID:
        bot.reply_to(message, "❌ Lệnh này chỉ admin được phép sử dụng.")
        return

    parts = message.text.strip().split()
    if len(parts) < 2:
        bot.reply_to(message, "❌ Vui lòng cung cấp username TikTok. Ví dụ: `/treo baohuydz158`", parse_mode="Markdown")
        return

    username = parts[1].lstrip("@")
    user_id = message.from_user.id
    chat_id = message.chat.id

    if user_id in auto_buff_tasks:
        bot.reply_to(message, "⚠️ Đang treo rồi. Muốn treo khác thì dùng `/huytreo` trước.")
        return

    bot.reply_to(message, f"✅ Đã bắt đầu tự động buff `@{username}` mỗi 15 phút.", parse_mode="Markdown")
    auto_buff_tasks[user_id] = None
    auto_buff(username, chat_id, user_id)

@bot.message_handler(commands=['huytreo'])
def handle_huytreo(message):
    if message.from_user.id != ADMIN_ID:
        bot.reply_to(message, "❌ Lệnh này chỉ admin được phép sử dụng.")
        return

    user_id = message.from_user.id
    task = auto_buff_tasks.pop(user_id, None)
    if task:
        task.cancel()

    bot.reply_to(message, "✅ Đã dừng tự động buff.")

# Chạy bot
if __name__ == "__main__":
    print("Bot đang chạy...")
    bot.infinity_polling()

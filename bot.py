import os
from keep_alive import keep_alive
import telebot
import requests
import time

keep_alive()

# Lấy token từ biến môi trường
TOKEN = os.getenv("6367532329:AAEuSSv8JuGKzJQD6qI431udTvdq1l25zo0")
bot = telebot.TeleBot(TOKEN)

# ID nhóm cho phép dùng bot
GROUP_ID = -1002221629819

# Cooldown dictionary
user_cooldowns = {}

# Hàm kiểm tra cooldown
def is_on_cooldown(user_id, command):
    now = time.time()
    key = f"{user_id}_{command}"
    if key in user_cooldowns:
        if now - user_cooldowns[key] < 30:
            return True
    user_cooldowns[key] = now
    return False

# Decorator chỉ dùng trong nhóm
def only_in_group(func):
    def wrapper(message):
        if message.chat.id != GROUP_ID:
            bot.reply_to(message, "❌ Lệnh này chỉ sử dụng được trong nhóm @Baohuydevs được chỉ định.")
            return
        return func(message)
    return wrapper

# Lệnh /start
@bot.message_handler(commands=['start'])
@only_in_group
def send_welcome(message):
    bot.reply_to(message,
        "Xin chào!\n"
        "Sử dụng các lệnh sau để kiểm tra tài khoản TikTok:\n\n"
        "`/buff <username>` - Kiểm tra bằng API 2\n"
        "`/fl3 <username>` - Kiểm tra bằng API 3 (Soundcast)\n\n"
        "Ví dụ: `/buff baohuydz158` hoặc `/fl3 baohuydz158`\n"
        "Nếu gặp lỗi, vui lòng thử lại sau.",
        parse_mode="Markdown"
    )

# Lệnh /buff
@bot.message_handler(commands=['buff'])
@only_in_group
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

# Lệnh /fl3
@bot.message_handler(commands=['fl3'])
@only_in_group
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

    user_id = "5736655322"
    api_url = f"https://apitangfltiktok.soundcast.me/telefl.php?user={username}&userid={user_id}&tokenbot={TOKEN}"

    try:
        response = requests.get(api_url, timeout=40)
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.RequestException:
        bot.reply_to(message, "❌ Lỗi khi kết nối với API 3. Vui lòng thử lại sau.")
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

# Chạy bot
if __name__ == "__main__":
    print("Bot đang chạy trên Render...")
    bot.infinity_polling()

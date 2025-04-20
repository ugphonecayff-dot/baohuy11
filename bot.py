from keep_alive import keep_alive
import telebot
import requests
import time

# Khởi động web server giữ bot hoạt động trên Render
keep_alive()

# Token bot Telegram
TOKEN = "6367532329:AAEuSSv8JuGKzJQD6qI431udTvdq1l25zo0"
bot = telebot.TeleBot(TOKEN)

# /start để hướng dẫn sử dụng
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message,
        "Xin chào!\n"
        "Sử dụng các lệnh sau để kiểm tra tài khoản TikTok:\n"
        "`/fl <username>` - Kiểm tra loại 1\n"
        "`/fl2 <username>` - Kiểm tra loại 2",
        parse_mode="Markdown"
    )

# Lệnh /fl sử dụng API 1
@bot.message_handler(commands=['fl'])
def get_fl_info(message):
    try:
        username = message.text.split()[1]
    except IndexError:
        return  # Không trả lời nếu thiếu username

    bot.send_chat_action(message.chat.id, "typing")
    time.sleep(1)
    bot.reply_to(message, f"🔍 Đang kiểm tra `@{username}` bằng API 1...", parse_mode="Markdown")

    api_url = f"https://dichvukey.site/flt.php?username={username}&key=ngocanvip"

    try:
        response = requests.get(api_url, timeout=30)
        response.raise_for_status()
        data = response.json()
    except:
        return  # Không trả lời nếu lỗi

    if not data or not data.get("status"):
        return  # Không trả lời nếu không có dữ liệu hợp lệ

    reply_text = (
        f"✅ *Thông tin tài khoản (API 1):*\n\n"
        f"💬 *Thông báo:* {data.get('message', 'Không có')}\n"
        f"👥 *Followers Trước:* {data.get('followers_before', 0)}\n"
        f"👥 *Followers Sau:* {data.get('followers_after', 0)}\n"
        f"✨ *Đã thêm:* {data.get('followers_add', 0)}\n\n"
        f"🔍 *Trạng thái:* ✅"
    )

    bot.reply_to(message, reply_text, parse_mode="Markdown", disable_web_page_preview=True)

# Lệnh /fl2 sử dụng API 2
@bot.message_handler(commands=['fl2'])
def get_fl2_info(message):
    try:
        username = message.text.split()[1]
    except IndexError:
        return  # Không trả lời nếu thiếu username

    bot.send_chat_action(message.chat.id, "typing")
    time.sleep(1)
    bot.reply_to(message, f"🔍 Đang kiểm tra `@{username}` bằng API 2...", parse_mode="Markdown")

    api_url = f"https://dichvukey.site/fl.php?username={username}&key=ngocanvip"

    try:
        response = requests.get(api_url, timeout=30)
        response.raise_for_status()
        data = response.json()
    except:
        return  # Không trả lời nếu lỗi

    if not data or not data.get("status"):
        return  # Không trả lời nếu không có dữ liệu hợp lệ

    reply_text = (
        f"✅ *Thông tin tài khoản (API 2):*\n\n"
        f"💬 *Thông báo:* {data.get('message', 'Không có')}\n"
        f"👥 *Followers Trước:* {data.get('followers_before', 0)}\n"
        f"👥 *Followers Sau:* {data.get('followers_after', 0)}\n"
        f"✨ *Đã thêm:* {data.get('followers_add', 0)}\n\n"
        f"🔍 *Trạng thái:* ✅"
    )

    bot.reply_to(message, reply_text, parse_mode="Markdown", disable_web_page_preview=True)

# KHÔNG phản hồi với các tin nhắn khác — bỏ handler mặc định
# Không cần handler func=lambda m: True

# Chạy bot
if __name__ == "__main__":
    print("Bot đang chạy trên Render...")
    bot.infinity_polling()

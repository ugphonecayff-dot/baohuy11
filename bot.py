import telebot
import requests
import time
from keep_alive import keep_alive  # Import file keep_alive.py

# Token bot Telegram (thay mới token)
TOKEN = "6367532329:AAEuSSv8JuGKzJQD6qI431udTvdq1l25zo0"
bot = telebot.TeleBot(TOKEN)

# Lệnh /start để hướng dẫn sử dụng
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message,
        "Xin chào!\n"
        "Sử dụng lệnh sau để kiểm tra tài khoản TikTok:\n"
        "`/fl <username>`\n"
        "Ví dụ: `/fl baohuydz158`\n\n"
        "Hoặc dùng `/buff` để thực hiện tác vụ từ API cố định.",
        parse_mode="Markdown"
    )

# Lệnh /fl <username> để gọi API và hiển thị kết quả
@bot.message_handler(commands=['fl'])
def fl_handler(message):
    try:
        username = message.text.split()[1]
    except IndexError:
        bot.reply_to(message, "⚠️ Vui lòng nhập username. Ví dụ: /fl baohuydz158")
        return

    bot.send_chat_action(message.chat.id, "typing")
    time.sleep(1)

    api_url = f"https://dichvukey.site/fl.php?username={username}&key=ngocanvip"

    try:
        response = requests.get(api_url, timeout=10)
        response.raise_for_status()
        bot.reply_to(message, f"✅ Kết quả từ API cho @{username}:\n\n{response.text}")
    except Exception as e:
        bot.reply_to(message, f"❌ Lỗi khi gọi API: {e}")

# Lệnh /buff gọi API với username mặc định
@bot.message_handler(commands=['buff'])
def buff_handler(message):
    bot.send_chat_action(message.chat.id, "typing")
    time.sleep(1)

    api_url = "https://dichvukey.site/fl.php?username=chipjuoi_209&key=ngocanvip"

    try:
        response = requests.get(api_url, timeout=30)
        response.raise_for_status()
        bot.reply_to(message, f"✅ Kết quả từ API:\n\n{response.text}")
    except Exception as e:
        bot.reply_to(message, f"❌ Lỗi khi gọi API: {e}")

# Bắt mọi tin nhắn không hợp lệ
@bot.message_handler(func=lambda m: True)
def handle_unknown(message):
    bot.reply_to(message, "❓ Không rõ lệnh. Dùng `/fl <username>` hoặc `/buff`.", parse_mode="Markdown")

# Khởi động web server để giữ bot sống
keep_alive()

# Khởi động bot Telegram
if __name__ == "__main__":
    print("Bot đang chạy...")
    bot.polling()

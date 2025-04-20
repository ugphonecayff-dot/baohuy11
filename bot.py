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
        "Sử dụng lệnh sau để kiểm tra tài khoản TikTok:\n"
        "`/fl <username>`\n"
        "Ví dụ: `/fl baohuydz158`",
        parse_mode="Markdown"
    )

# /fl <username> để tra thông tin TikTok
@bot.message_handler(commands=['fl'])
def get_account_info(message):
    try:
        username = message.text.split()[1]
    except IndexError:
        bot.reply_to(message, "⚠️ Vui lòng nhập username. Ví dụ: /fl baohuydz158")
        return

    bot.send_chat_action(message.chat.id, "typing")
    time.sleep(1.2)
    bot.reply_to(message, f"🔍 Đang tìm thông tin tài khoản `@{username}`...", parse_mode="Markdown")

    api_url = f"https://dichvukey.site/flt.php?username={username}&key=ngocanvip"

    try:
        response = requests.get(api_url, timeout=30)
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.Timeout:
        bot.reply_to(message, "⏳ Lỗi: Huy đã Hết thời gian chờ phản hồi từ API.")
        return
    except Exception as e:
        bot.reply_to(message, f"❌ Lỗi khi gọi API: {e}")
        return

    if not data:
        bot.reply_to(message, "❌ Không nhận được dữ liệu từ API.")
        return

    if not data.get("status"):
        bot.reply_to(message, f"❌ {data.get('message', 'Không tìm thấy tài khoản.')}")
        return

    reply_text = (
        f"✅ *Thông tin tài khoản:*\n\n"
        f"💬 *Thông báo:* {data.get('message', 'Không có')}\n"
        f"👥 *Followers Trước:* {data.get('followers_before', 0)}\n"
        f"👥 *Followers Sau:* {data.get('followers_after', 0)}\n"
        f"✨ *Đã thêm:* {data.get('followers_add', 0)}\n\n"
        f"🔍 *Trạng thái:* ✅"
    )

    time.sleep(1)
    bot.reply_to(message, reply_text, parse_mode="Markdown", disable_web_page_preview=True)

# Xử lý lệnh không hợp lệ
@bot.message_handler(func=lambda m: True)
def handle_unknown(message):
    bot.reply_to(message, "❓ Không rõ lệnh. Dùng `/fl <username>` để tra cứu.", parse_mode="Markdown")

# Chạy bot
if __name__ == "__main__":
    print("Bot đang chạy trên Render...")
    bot.infinity_polling()

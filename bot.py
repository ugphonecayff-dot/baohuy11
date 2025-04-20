from keep_alive import keep_alive
import telebot
import requests
import time
import os

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

    api_main = f"https://dichvukey.site/flt.php?username={username}&key=ngocanvip"
    api_alt = f"https://guanghai.x10.mx/infott.php?username={username}"

    # Gọi API chính
    try:
        response_main = requests.get(api_main, timeout=30)
        response_main.raise_for_status()
        data_main = response_main.json()
    except requests.exceptions.Timeout:
        bot.reply_to(message, "⏳ Lỗi: Hết thời gian chờ phản hồi từ API chính.")
        return
    except Exception as e:
        bot.reply_to(message, f"❌ Lỗi API chính: {e}")
        return

    # Gọi API phụ (không bắt buộc)
    try:
        response_alt = requests.get(api_alt, timeout=10)
        data_alt = response_alt.json()
    except:
        data_alt = {}

    if not data_main:
        bot.reply_to(message, "❌ Không nhận được dữ liệu từ API chính.")
        return

    status_icon = "✅" if data_main.get("status") else "❌"

    # Chuẩn bị nội dung phản hồi
    reply_text = (
        f"{status_icon} *Thông tin tài khoản:*\n\n"
        f"💬 *Thông báo:* {data_main.get('message', 'Không có')}\n"
        f"👥 *Followers Trước:* {data_main.get('followers_before', 0)}\n"
        f"👥 *Followers Sau:* {data_main.get('followers_after', 0)}\n"
        f"✨ *Đã thêm:* {data_main.get('followers_add', 0)}\n\n"
        f"🔍 *Trạng thái:* {status_icon}"
    )

    # Thêm dữ liệu từ API phụ nếu có
    if data_alt:
        followers = data_alt.get("follower")
        likes = data_alt.get("like")
        if followers or likes:
            reply_text += "\n\n📊 *Dữ liệu phụ:*"
            if followers:
                reply_text += f"\n👥 *Followers:* {followers}"
            if likes:
                reply_text += f"\n❤️ *Likes:* {likes}"

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

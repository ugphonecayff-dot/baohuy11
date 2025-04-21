from keep_alive import keep_alive
import telebot
import requests
import time

# Khởi động web server giữ bot hoạt động trên Render
keep_alive()

# Token bot Telegram
TOKEN = "6367532329:AAEuSSv8JuGKzJQD6qI431udTvdq1l25zo0"
bot = telebot.TeleBot(TOKEN)

# /start hướng dẫn sử dụng bot
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message,
        "Xin chào!\n"
        "Sử dụng các lệnh sau để kiểm tra tài khoản TikTok:\n\n"
        "`/fl <username>` - Kiểm tra bằng API chính\n"
        "`/fl3 <username>` - Kiểm tra loại 3 (API mới)\n\n"
        "Ví dụ: `/fl emifukameo._`",
        parse_mode="Markdown"
    )

# /fl -> API chính tại https://dichvukey.site/fl.php
@bot.message_handler(commands=['fl'])
def handle_fl(message):
    try:
        username = message.text.split()[1]
    except IndexError:
        bot.reply_to(message, "❌ Vui lòng cung cấp tên người dùng TikTok. Ví dụ: `/fl emifukameo._`", parse_mode="Markdown")
        return

    bot.send_chat_action(message.chat.id, "typing")
    time.sleep(1)
    bot.reply_to(message, f"🔍 Đang kiểm tra `@{username}` bằng API chính...", parse_mode="Markdown")

    api_url = f"https://dichvukey.site/fl.php?username={username}&key=ngocanvip"

    try:
        response = requests.get(api_url, timeout=40)
        response.raise_for_status()
        data = response.json()
        print("Dữ liệu API FL:", data)
    except requests.exceptions.RequestException as e:
        print(f"Lỗi khi gọi API FL: {e}")
        bot.reply_to(message, "❌ Lỗi khi kết nối với API. Vui lòng thử lại sau.")
        return
    except ValueError as e:
        print(f"Lỗi JSON từ API FL: {e}")
        bot.reply_to(message, "❌ Dữ liệu trả về không hợp lệ.")
        return

    if not data or str(data.get("status")).lower() not in ["true", "1", "success"]:
        bot.reply_to(message, f"❌ Không thể kiểm tra tài khoản @{username}. Vui lòng thử lại sau.")
        return

    reply_text = (
        f"✅ *Thông tin tài khoản (API Chính):*\n\n"
        f"💬 *Thông báo:* {data.get('message', 'Không có')}\n"
        f"👥 *Followers Trước:* {data.get('followers_before', 0)}\n"
        f"👥 *Followers Sau:* {data.get('followers_after', 0)}\n"
        f"✨ *Đã thêm:* {data.get('followers_add', 0)}\n\n"
        f"🔍 *Trạng thái:* ✅"
    )

    bot.reply_to(message, reply_text, parse_mode="Markdown", disable_web_page_preview=True)

# /fl3 -> API 3
@bot.message_handler(commands=['fl3'])
def get_fl3_info(message):
    try:
        username = message.text.split()[1]
    except IndexError:
        bot.reply_to(message, "❌ Vui lòng cung cấp tên người dùng TikTok. Ví dụ: `/fl3 emifukameo._`", parse_mode="Markdown")
        return

    bot.send_chat_action(message.chat.id, "typing")
    time.sleep(1)
    bot.reply_to(message, f"🔍 Đang kiểm tra `@{username}` bằng API 3...", parse_mode="Markdown")

    user_id = "5736655322"
    api_url = f"https://apitangfltiktok.soundcast.me/telefl.php?user={username}&userid={user_id}&tokenbot={TOKEN}"

    try:
        response = requests.get(api_url, timeout=40)
        response.raise_for_status()
        data = response.json()
        print("Dữ liệu nhận được từ API 3:", data)
    except requests.exceptions.RequestException as e:
        print(f"Lỗi khi gọi API 3: {e}")
        bot.reply_to(message, "❌ Lỗi khi kết nối với API 3. Vui lòng thử lại sau.")
        return
    except ValueError as e:
        print(f"Lỗi JSON từ API 3: {e}")
        bot.reply_to(message, "❌ Dữ liệu trả về không hợp lệ.")
        return

    reply_text = (
        f"✅ *Thông tin tài khoản (API 3):*\n\n"
        f"💬 *Thông báo:* {data.get('message', 'Không có thông báo')}\n"
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

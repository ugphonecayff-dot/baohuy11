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
        "`/fl2 <username>` - Kiểm tra loại 2\n\n"
        "Hãy nhập lệnh với tên tài khoản TikTok bạn muốn kiểm tra."
        " Ví dụ: `/fl ngocanvip` hoặc `/fl2 ngocanvip` để kiểm tra tài khoản."
        " Nếu gặp lỗi, vui lòng thử lại sau.",
        parse_mode="Markdown"
    )

# Lệnh /fl sử dụng API 1
@bot.message_handler(commands=['fl'])
def get_fl_info(message):
    try:
        username = message.text.split()[1]
    except IndexError:
        bot.reply_to(message, "❌ Vui lòng cung cấp tên người dùng TikTok. Ví dụ: `/fl ngocanvip`")
        return  # Không trả lời nếu thiếu username

    bot.send_chat_action(message.chat.id, "typing")
    time.sleep(1)
    bot.reply_to(message, f"🔍 Đang kiểm tra `@{username}` bằng API 1...", parse_mode="Markdown")

    api_url = f"https://dichvukey.site/flt.php?username={username}&key=ngocanvip"

    try:
        response = requests.get(api_url, timeout=30)
        response.raise_for_status()  # Kiểm tra lỗi HTTP
        data = response.json()  # Chuyển đổi dữ liệu sang JSON
        print("Dữ liệu nhận được:", data)  # In dữ liệu ra để kiểm tra
    except requests.exceptions.RequestException as e:
        print(f"Lỗi khi gọi API: {e}")
        bot.reply_to(message, "❌ Lỗi khi kết nối với API. Vui lòng thử lại sau.")
        return
    except ValueError as e:
        print(f"Lỗi trong quá trình xử lý dữ liệu JSON: {e}")
        bot.reply_to(message, "❌ Dữ liệu trả về không hợp lệ.")
        return

    if not data or str(data.get("status")).lower() not in ["true", "1", "success"]:
        bot.reply_to(message, "❌ Không tìm thấy dữ liệu tài khoản.")
        return

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
        bot.reply_to(message, "❌ Vui lòng cung cấp tên người dùng TikTok. Ví dụ: `/fl2 ngocanvip`")
        return  # Không trả lời nếu thiếu username

    bot.send_chat_action(message.chat.id, "typing")
    time.sleep(1)
    bot.reply_to(message, f"🔍 Đang kiểm tra `@{username}` bằng API 2...", parse_mode="Markdown")

    api_url = f"https://dichvukey.site/fl.php?username={username}&key=ngocanvip"

    try:
        response = requests.get(api_url, timeout=30)
        response.raise_for_status()  # Kiểm tra lỗi HTTP
        data = response.json()  # Chuyển đổi dữ liệu sang JSON
        print("Dữ liệu nhận được:", data)  # In dữ liệu ra để kiểm tra
    except requests.exceptions.RequestException as e:
        print(f"Lỗi khi gọi API: {e}")
        bot.reply_to(message, "❌ Lỗi khi kết nối với API. Vui lòng thử lại sau.")
        return
    except ValueError as e:
        print(f"Lỗi trong quá trình xử lý dữ liệu JSON: {e}")
        bot.reply_to(message, "❌ Dữ liệu trả về không hợp lệ.")
        return

    if not data or str(data.get("status")).lower() not in ["true", "1", "success"]:
        bot.reply_to(message, "❌ Không tìm thấy dữ liệu tài khoản.")
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

# Chạy bot
if __name__ == "__main__":
    print("Bot đang chạy trên Render...")
    bot.infinity_polling()

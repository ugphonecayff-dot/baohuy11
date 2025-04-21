from keep_alive import keep_alive
import telebot
import requests
import time

# Khởi động web server giữ bot hoạt động trên Render
keep_alive()

# Token bot Telegram
TOKEN = "6367532329:AAEuSSv8JuGKzJQD6qI431udTvdq1l25zo0"
bot = telebot.TeleBot(TOKEN)

# Hàm dùng chung để xử lý API 1 và 2
def handle_fl_command(message, api_type):
    try:
        username = message.text.split()[1]
    except IndexError:
        bot.reply_to(message, f"❌ Vui lòng cung cấp tên người dùng TikTok. Ví dụ: `/{api_type} ngocanvip`", parse_mode="Markdown")
        return

    bot.send_chat_action(message.chat.id, "typing")
    time.sleep(1)
    bot.reply_to(message, f"🔍 Đang kiểm tra `@{username}` bằng API {1 if api_type == 'fl' else 2}...", parse_mode="Markdown")

    endpoint = "flt.php" if api_type == "fl" else "fl.php"
    api_url = f"https://dichvukey.site/{endpoint}?username={username}&key=ngocanvip"

    try:
        response = requests.get(api_url, timeout=40)
        response.raise_for_status()
        data = response.json()
        print(f"Dữ liệu API {api_type.upper()}:", data)
    except requests.exceptions.RequestException as e:
        print(f"Lỗi khi gọi API {api_type.upper()}: {e}")
        bot.reply_to(message, "❌ Lỗi khi kết nối với API. Vui lòng thử lại sau.")
        return
    except ValueError as e:
        print(f"Lỗi JSON API {api_type.upper()}: {e}")
        bot.reply_to(message, "❌ Dữ liệu trả về không hợp lệ.")
        return

    if not data or str(data.get("status")).lower() not in ["true", "1", "success"]:
        bot.reply_to(message, "✅Thông báo: Tăng Thành công")
        return

    reply_text = (
        f"✅ *Thông tin tài khoản (API {1 if api_type == 'fl' else 2}):*\n\n"
        f"💬 *Thông báo:* {data.get('message', 'Không có')}\n"
        f"👥 *Followers Trước:* {data.get('followers_before', 0)}\n"
        f"👥 *Followers Sau:* {data.get('followers_after', 0)}\n"
        f"✨ *Đã thêm:* {data.get('followers_add', 0)}\n\n"
        f"🔍 *Trạng thái:* ✅"
    )

    bot.reply_to(message, reply_text, parse_mode="Markdown", disable_web_page_preview=True)

# /start hướng dẫn sử dụng bot
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message,
        "Xin chào!\n"
        "Sử dụng các lệnh sau để kiểm tra tài khoản TikTok:\n\n"
        "`/fl <username>` - Kiểm tra loại 1\n"
        "`/fl2 <username>` - Kiểm tra loại 2\n"
        "`/fl3 <username>` - Kiểm tra loại 3 (API mới)\n\n"
        "Ví dụ: `/fl ngocanvip` hoặc `/fl3 ngocanvip`\n"
        "Nếu gặp lỗi, vui lòng thử lại sau.",
        parse_mode="Markdown"
    )

# /fl -> API 1
@bot.message_handler(commands=['fl'])
def handle_fl(message):
    handle_fl_command(message, 'fl')

# /fl2 -> API 2
@bot.message_handler(commands=['fl2'])
def handle_fl2(message):
    handle_fl_command(message, 'fl2')

# /fl3 -> API mới (API 3)
@bot.message_handler(commands=['fl3'])
def get_fl3_info(message):
    try:
        username = message.text.split()[1]
    except IndexError:
        bot.reply_to(message, "❌ Vui lòng cung cấp tên người dùng TikTok. Ví dụ: `/fl3 ngocanvip`", parse_mode="Markdown")
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

from keep_alive import keep_alive
import telebot
import requests
import time

# Khởi động web server giữ bot hoạt động trên Render
keep_alive()

# Token bot Telegram
TOKEN = "6367532329:AAEuSSv8JuGKzJQD6qI431udTvdq1l25zo0"
bot = telebot.TeleBot(TOKEN)

# ID nhóm được phép sử dụng bot
GROUP_ID = -1002221629819

# Decorator hạn chế lệnh chỉ dùng trong nhóm
def only_in_group(func):
    def wrapper(message):
        if message.chat.id != GROUP_ID:
            bot.reply_to(message, "❌ Lệnh này chỉ sử dụng được trong nhóm @Baohuydevs được chỉ định.")
            return
        return func(message)
    return wrapper

# Lệnh /start hướng dẫn người dùng
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

# ============================
# Lệnh /buff (API 2)
# ============================
@bot.message_handler(commands=['buff'])
@only_in_group
def handle_buff(message):
    try:
        username = message.text.split()[1]
    except IndexError:
        bot.reply_to(message, "❌ Vui lòng cung cấp tên người dùng TikTok. Ví dụ: `/buff ngocanvip`", parse_mode="Markdown")
        return

    bot.send_chat_action(message.chat.id, "typing")
    time.sleep(1)
    bot.reply_to(message, f"🔍 Đang kiểm tra `@{username}` bằng API 2...", parse_mode="Markdown")

    api_url = f"https://dichvukey.site/fl.php?username={username}&key=ngocanvip"

    try:
        response = requests.get(api_url, timeout=40)
        response.raise_for_status()
        data = response.json()
        print("Dữ liệu nhận được từ API 2:", data)
    except requests.exceptions.RequestException as e:
        print(f"Lỗi khi gọi API 2: {e}")
        bot.reply_to(message, "❌ Lỗi khi kết nối với API. Vui lòng thử lại sau.")
        return
    except ValueError:
        print("API 2 không trả JSON:", response.text)
        bot.reply_to(message, f"✅Thông báo: {response.text.strip()}")
        return

    status = str(data.get("status", "")).lower()
    if status not in ["true", "1", "success"]:
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

# ============================
# Lệnh /fl3 - API Soundcast
# ============================
@bot.message_handler(commands=['fl3'])
@only_in_group
def handle_fl3(message):
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
    except ValueError:
        print("API 3 không trả JSON:", response.text)
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

# ============================
# Chạy bot
# ============================
if __name__ == "__main__":
    print("Bot đang chạy trên Render...")
    bot.infinity_polling()

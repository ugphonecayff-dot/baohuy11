from keep_alive import keep_alive
import telebot
import requests
import time

# Khởi động keep_alive để giữ bot hoạt động
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

# /fl <username> để tra thông tin
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

    api_url = f"https://dichvukey.site/fl.php?username={username}&key=ngocanvip"

    # Gắn delay trước khi gửi yêu cầu API
    time.sleep(2)  # Delay 2 giây trước khi gọi API

    try:
        # Thêm tham số timeout vào yêu cầu GET
        response = requests.get(api_url, timeout=30)  # Timeout sau 30 giây
        response.raise_for_status()  # Kiểm tra nếu mã trạng thái HTTP là lỗi
        data = response.json()
    except requests.exceptions.Timeout:
        bot.reply_to(message, "⏳ Lỗi: Yêu cầu đã hết thời gian chờ.")
        return
    except requests.exceptions.RequestException as e:
        bot.reply_to(message, f"❌ Lỗi khi gọi API: {e}")
        return

    if not data:
        bot.reply_to(message, "❌ Không nhận được dữ liệu từ API.")
        return

    status_icon = "✅" if data.get("status") else "❌"

    # Soạn nội dung trả về
    reply_text = (
        f"{status_icon} *Thông tin tài khoản:*\n\n"
        f"🏖️ *Khu Vực:* {data.get('khu_vuc', 'N/A')}\n"
        f"👤 *Tên:* {data.get('name', 'N/A')}\n"
        f"🆔 *User ID:* `{data.get('user_id', 'N/A')}`\n"
        f"📸 *Avatar:* [Xem ảnh]({data.get('avatar', '')})\n"
        f"📅 *Ngày tạo:* {data.get('create_time', 'N/A')}\n"
        f"📌 *Username:* @{data.get('username', 'N/A')}\n\n"
        f"👥 *Followers Trước:* {data.get('followers_before', 0)}\n"
        f"👥 *Followers Sau:* {data.get('followers_after', 0)}\n"
        f"✨ *Đã thêm:* {data.get('followers_add', 0)}\n\n"
        f"💬 *Thông báo:* {data.get('message', '')}\n"
        f"🔍 *Trạng thái:* {status_icon}"
    )

    time.sleep(1)
    bot.reply_to(message, reply_text, parse_mode="Markdown", disable_web_page_preview=True)

# Nếu gõ sai lệnh
@bot.message_handler(func=lambda m: True)
def handle_unknown(message):
    bot.reply_to(message, "❓ Không rõ lệnh. Dùng `/fl <username>` để tra cứu.", parse_mode="Markdown")

# Khởi động bot
if __name__ == "__main__":
    print("Bot đang chạy...")
    bot.polling()

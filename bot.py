import telebot
import requests

# Dán trực tiếp token vào đây
BOT_TOKEN = "6367532329:AAFzGAqQZ_f4VQqX7VbwAoQ7iqbFO07Hzqk"

bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['fl'])
def handle_fl_command(message):
    args = message.text.split()
    if len(args) < 2:
        bot.reply_to(message, "Vui lòng nhập username. Ví dụ: /fl baohuydz158")
        return

    username = args[1]
    api_url = f"https://ksjdjdmfmxm.x10.mx/api/fl.php?user={username}&key=4I1TK-YXQZ4-GNFPL8&info=true"

    try:
        response = requests.get(api_url)
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.RequestException as e:
        bot.reply_to(message, f"Lỗi khi gọi API: {str(e)}")
        return
    except ValueError:
        bot.reply_to(message, "API không trả về dữ liệu JSON hợp lệ.")
        return

    status_text = "✅ Thành công" if data.get('status') else "❌ Thất bại"

    reply_text = (
        f"<b>🏖️ Khu Vực:</b> {data.get('khu_vuc', 'N/A')}\n"
        f"<b>👤 Tên:</b> {data.get('name', 'N/A')}\n"
        f"<b>🆔 User ID:</b> {data.get('user_id', 'N/A')}\n"
        f"<b>📅 Ngày tạo:</b> {data.get('create_time', 'N/A')}\n"
        f"<b>📌 Username:</b> @{data.get('username', 'N/A')}\n"
        f"<b>👥 Followers (Trước):</b> {data.get('followers_before', 0)}\n"
        f"<b>👥 Followers (Sau):</b> {data.get('followers_after', 0)}\n"
        f"<b>✨ Đã thêm:</b> {data.get('followers_add', 0)}\n"
        f"<b>💬 Thông báo:</b> {data.get('message', '')}\n"
        f"<b>🔍 Trạng thái:</b> {status_text}"
    )

    avatar_url = data.get('avatar')
    if avatar_url and avatar_url.startswith("http"):
        bot.send_photo(message.chat.id, avatar_url)

    bot.send_message(message.chat.id, reply_text, parse_mode='HTML')


if __name__ == "__main__":
    print("Bot is running...")
    bot.polling()

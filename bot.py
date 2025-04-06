import telebot
import os
import tempfile
import subprocess
from keep_alive import keep_alive

TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
bot = telebot.TeleBot(TOKEN)

name_bot = "MySpamBot"

@bot.message_handler(commands=['spam'])
def spam(message):
    params = message.text.split()[1:]
    if len(params) != 2:
        bot.reply_to(message, "Dùng như này nhé: /spam sdt số_lần")
        return

    sdt, count = params

    if not count.isdigit():
        bot.reply_to(message, "Vui lòng nhập số lần hợp lệ.")
        return

    count = int(count)

    bot.send_message(message.chat.id, f'''
┌──────⭓ {name_bot}
│ Spam: Thành Công 
│ Số Lần Spam Free: {count}
│ Đang Tấn Công : {sdt}
└─────────────
    ''')

    try:
        if not os.path.isfile("dec.py"):
            bot.reply_to(message, "Không tìm thấy file script dec.py.")
            return

        with open("dec.py", 'r', encoding='utf-8') as f:
            script = f.read()

        with tempfile.NamedTemporaryFile(delete=False, suffix=".py") as tmp:
            tmp.write(script.encode('utf-8'))
            temp_path = tmp.name

        subprocess.Popen(["python", temp_path, sdt, str(count)])
    except Exception as e:
        bot.reply_to(message, f"Lỗi: {str(e)}")

# Kích hoạt web server keep_alive
keep_alive()

# Chạy bot
print("Bot đang chạy...")
bot.polling()

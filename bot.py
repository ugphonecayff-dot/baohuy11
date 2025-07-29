import os
import json
import time
import socket
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from keep_alive import keep_alive  # Web server giữ bot sống

BOT_TOKEN = "6320148381:AAEhTaMhPw9ArYp3Jy_PTkVVSBaqrxhS7dA"  # Token Telegram của bạn
RESET_LOCK_PATH = "/storage/emulated/0/脚本/detect/reset.lock"  # Đường dẫn file khóa hệ thống

# Gửi yêu cầu tới Auto.js server và nhận kết quả
def send_to_autojs_and_get_result(username):
    try:
        start_time = time.time()
        with socket.create_connection(("127.0.0.1", 5000), timeout=30) as sock:
            payload = json.dumps({"username": username}) + "\n"
            sock.sendall(payload.encode("utf-8"))
            sock.settimeout(30)
            result = sock.recv(2048).decode("utf-8").strip()
        elapsed_time = time.time() - start_time
        return result, elapsed_time
    except Exception as e:
        print(f"[Socket Error] {e}")
        return f"__ERROR__: {e}", 0

# Xử lý lệnh /check
async def check_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args:
        username = " ".join(context.args).strip()
        chat_id = update.effective_chat.id

        if os.path.exists(RESET_LOCK_PATH):
            await context.bot.send_message(
                chat_id=chat_id,
                text="⚠️ Hệ thống đang bảo trì. Vui lòng thử lại sau 1-2 phút."
            )
            return

        await context.bot.send_message(chat_id=chat_id, text=f"⏳ Đang kiểm tra: {username}")
        result, duration = send_to_autojs_and_get_result(username)

        if result.startswith("__ERROR__"):
            await context.bot.send_message(chat_id=chat_id, text="❌ " + result.replace("__ERROR__: ", ""))
        elif os.path.isfile(result) and result.lower().endswith((".jpg", ".png")):
            with open(result, "rb") as img:
                await context.bot.send_photo(
                    chat_id=chat_id,
                    photo=img,
                    caption=f"👤 {username} – Hồ sơ\n⏱ Xử lý: {duration:.2f} giây"
                )
        else:
            await context.bot.send_message(chat_id=chat_id, text=result)
    else:
        await update.message.reply_text("❗ Nhập tên người dùng. Ví dụ: /check abc123")

# Khởi chạy bot
if __name__ == '__main__':
    keep_alive()
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("check", check_handler))
    print("✅ Bot Telegram đã khởi chạy!")
    app.run_polling()
        

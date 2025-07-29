import os
import json
import time
import socket
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from keep_alive import keep_alive  # Khởi chạy web server giữ bot sống

# 👉 Token Telegram bot (hãy thay token thật của bạn vào đây hoặc dùng biến môi trường)
BOT_TOKEN = "6320148381:AAEhTaMhPw9ArYp3Jy_PTkVVSBaqrxhS7dA"

# 👉 Đường dẫn file lock nếu Auto.js đang chạy bảo trì
RESET_LOCK_PATH = "/storage/emulated/0/脚本/detect/reset.lock"

# ✅ Hàm gửi tên acc sang Auto.js qua socket
def send_to_autojs_and_get_result(name):
    try:
        start_time = time.time()
        with socket.create_connection(("127.0.0.1", 5000), timeout=30) as sock:
            payload = json.dumps({"name": name}) + "\n"
            sock.sendall(payload.encode("utf-8"))
            sock.settimeout(30)
            result = sock.recv(2048).decode("utf-8").strip()
        elapsed_time = time.time() - start_time
        return result, elapsed_time
    except Exception as e:
        print(f"[Socket Error] {e}")
        return f"__ERROR__: {e}", 0

# ✅ Xử lý lệnh /check <tên_acc>
async def check_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args:
        name = " ".join(context.args).strip()
        chat_id = update.effective_chat.id

        if os.path.exists(RESET_LOCK_PATH):
            await context.bot.send_message(
                chat_id=chat_id,
                text="⚠️ Hệ thống đang bảo trì. Vui lòng thử lại sau 1-2 phút."
            )
            return

        await context.bot.send_message(chat_id=chat_id, text=f"🔍 Đang kiểm tra tài khoản: {name}")
        result, duration = send_to_autojs_and_get_result(name)

        if result.startswith("__ERROR__"):
            await context.bot.send_message(chat_id=chat_id, text="❌ " + result.replace("__ERROR__: ", ""))
        elif os.path.isfile(result) and result.lower().endswith((".jpg", ".png")):
            with open(result, "rb") as img:
                await context.bot.send_photo(
                    chat_id=chat_id,
                    photo=img,
                    caption=f"🎮 {name} – Thông tin tài khoản\n⏱ Xử lý: {duration:.2f} giây"
                )
        else:
            await context.bot.send_message(chat_id=chat_id, text=result)
    else:
        await update.message.reply_text("❗ Nhập tên tài khoản Liên Quân. Ví dụ: /check ZataPro99")

# ✅ Lệnh /start và /help
async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤖 Xin chào! Gõ lệnh /check <tên_acc> để kiểm tra tài khoản Liên Quân.")

async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📌 Hướng dẫn:\n/check ZataPro99\n/check TênTàiKhoảnLiênQuân")

# ✅ Chạy bot
if __name__ == '__main__':
    keep_alive()  # Giữ bot sống (nếu chạy trên Replit hoặc dùng UptimeRobot)

    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("check", check_handler))
    app.add_handler(CommandHandler("start", start_handler))
    app.add_handler(CommandHandler("help", help_handler))

    print("✅ Bot Telegram đã khởi chạy!")
    app.run_polling()
    

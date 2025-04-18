import os
import time
import asyncio
import requests
from flask import Flask, request
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from telegram.constants import ChatAction

# --- Cấu hình bot ---
BOT_TOKEN = os.getenv("BOT_TOKEN", "6367532329:AAFzGAqQZ_f4VQqX7VbwAoQ7iqbFO07Hzqk")
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "https://your-domain.com/")  # Thay bằng domain bạn host

# --- Khởi tạo Flask và Telegram bot ---
flask_app = Flask(__name__)
telegram_app = ApplicationBuilder().token(BOT_TOKEN).build()

# --- Lệnh /start ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Chào mừng bạn đến với bot hỗ trợ Free Fire!\n\n"
        "Các lệnh có sẵn:\n"
        "/likeff <idgame> - Tăng lượt like\n"
        "/viewff <uid> - Xem thông tin người chơi"
    )

# --- Lệnh /likeff ---
async def likeff(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❗ Vui lòng nhập đúng cú pháp:\n/likeff <idgame>")
        return

    idgame = context.args[0]
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
    await update.message.reply_text("⏳ Đang xử lý lượt like...")

    await asyncio.sleep(3)  # Delay trước khi gọi API

    urllike = f"https://dichvukey.site/likeff2.php?key=vlong&uid={idgame}"
    max_retries = 5
    data = {}

    for attempt in range(max_retries):
        try:
            response = requests.get(urllike, timeout=30)
            response.raise_for_status()
            data = response.json()
            break
        except requests.exceptions.RequestException:
            if attempt == max_retries - 1:
                await update.message.reply_text("❌ Server đang quá tải, vui lòng thử lại sau.")
                return
            time.sleep(5)
        except ValueError:
            await update.message.reply_text("❌ Phản hồi từ server không hợp lệ.")
            return

    if isinstance(data, dict) and "status" in data:
        if data["status"] == 2:
            await update.message.reply_text("⚠️ Bạn đã đạt giới hạn lượt like hôm nay, vui lòng thử lại sau.")
            return

        reply_text = (
            f"✅ **Kết quả Like thành công:**\n\n"
            f"👤 Tên: {data.get('username', 'Không xác định')}\n"
            f"🆔 UID: {data.get('uid', 'Không xác định')}\n"
            f"🎚 Level: {data.get('level', 'Không xác định')}\n"
            f"👍 Like trước: {data.get('likes_before', 'Không xác định')}\n"
            f"✅ Like sau: {data.get('likes_after', 'Không xác định')}\n"
            f"➕ Tổng cộng: {data.get('likes_given', 'Không xác định')} like"
        )
    else:
        reply_text = "❌ Không thể xử lý yêu cầu."

    await update.message.reply_text(reply_text, parse_mode="Markdown")

# --- Lệnh /viewff ---
async def viewff(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❗ Vui lòng nhập đúng cú pháp:\n/viewff <uid>")
        return

    uid = context.args[0]
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
    await update.message.reply_text("🔍 Đang tìm thông tin người chơi...")

    await asyncio.sleep(3)  # Delay trước khi gọi API

    urlview = f"https://visit-plum.vercel.app/send_visit?uid={uid}"

    try:
        response = requests.get(urlview, timeout=15)
        response.raise_for_status()
        data = response.json()
    except Exception:
        await update.message.reply_text("❌ Không thể truy cập API Garena.")
        return

    if not isinstance(data, dict) or "data" not in data:
        await update.message.reply_text("❌ Không tìm thấy thông tin người chơi.")
        return

    info = data["data"]

    reply_text = (
        f"🎮 **THÔNG TIN NGƯỜI CHƠI FF**\n\n"
        f"👤 Tên: {info.get('nickname', 'Không xác định')}\n"
        f"🆔 UID: {info.get('uid', uid)}\n"
        f"⚔️ Huy hiệu: {info.get('badge', 'Không có')}\n"
        f"🎯 Rank: {info.get('rank', {}).get('name', 'Không rõ')}\n"
        f"🏅 Mùa: {info.get('season', 'Không rõ')}\n"
        f"🔥 Tổng điểm: {info.get('points', 'Không có')}"
    )

    await update.message.reply_text(reply_text, parse_mode="Markdown")

# --- Đăng ký handler ---
telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(CommandHandler("likeff", likeff))
telegram_app.add_handler(CommandHandler("viewff", viewff))

# --- Flask webhook handler ---
@flask_app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook_handler():
    update = Update.de_json(request.get_json(force=True), telegram_app.bot)
    telegram_app.update_queue.put(update)
    return "ok"

@flask_app.route("/", methods=["GET"])
def index():
    return "Bot đang hoạt động!"

# --- Set webhook ---
def set_webhook():
    url = f"{WEBHOOK_URL}{BOT_TOKEN}"
    asyncio.run(telegram_app.bot.set_webhook(url=url))

# --- Chạy ứng dụng ---
if __name__ == "__main__":
    set_webhook()
    flask_app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

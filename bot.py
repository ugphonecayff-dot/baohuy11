import time
import asyncio
import requests
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from telegram.constants import ChatAction

BOT_TOKEN = "6367532329:AAFzGAqQZ_f4VQqX7VbwAoQ7iqbFO07Hzqk"
WEBHOOK_URL = "https://your-domain.com/"  # <-- Thay bằng domain thật

# Khởi tạo Flask và Bot Telegram
flask_app = Flask(__name__)
telegram_app = Application.builder().token(BOT_TOKEN).build()

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Chào mừng bạn đến với bot Free Fire!\n"
        "/likeff <idgame> - Tăng like\n"
        "/viewff <uid> - Xem thông tin người chơi"
    )

# /likeff
async def likeff(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❗ Nhập đúng cú pháp:\n/likeff <idgame>")
        return

    idgame = context.args[0]
    await update.message.reply_text("⏳ Đang xử lý lượt like...")
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
    await asyncio.sleep(3)

    url = f"https://dichvukey.site/likeff2.php?key=vlong&uid={idgame}"
    for attempt in range(5):
        try:
            res = requests.get(url, timeout=30)
            res.raise_for_status()
            data = res.json()
            break
        except Exception:
            if attempt == 4:
                await update.message.reply_text("❌ Server lỗi. Vui lòng thử lại.")
                return
            time.sleep(3)
    else:
        await update.message.reply_text("❌ Không thể kết nối.")
        return

    if data.get("status") == 2:
        await update.message.reply_text("⚠️ Bạn đã đạt giới hạn lượt like hôm nay.")
        return

    reply = (
        f"✅ **Like Thành Công:**\n\n"
        f"👤 Tên: {data.get('username', 'Không xác định')}\n"
        f"🆔 UID: {data.get('uid', idgame)}\n"
        f"🎚 Level: {data.get('level', '?')}\n"
        f"👍 Trước: {data.get('likes_before', '?')}\n"
        f"✅ Sau: {data.get('likes_after', '?')}\n"
        f"➕ Đã thêm: {data.get('likes_given', '?')} like"
    )
    await update.message.reply_text(reply, parse_mode="Markdown")

# /viewff
async def viewff(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❗ Nhập đúng cú pháp:\n/viewff <uid>")
        return

    uid = context.args[0]
    await update.message.reply_text("🔍 Đang tìm thông tin...")
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
    await asyncio.sleep(2)

    try:
        res = requests.get(f"https://visit-plum.vercel.app/send_visit?uid={uid}", timeout=15)
        res.raise_for_status()
        data = res.json()
    except Exception:
        await update.message.reply_text("❌ API Garena không phản hồi.")
        return

    if "data" not in data:
        await update.message.reply_text("❌ Không tìm thấy người chơi.")
        return

    info = data["data"]
    reply = (
        f"🎮 **THÔNG TIN NGƯỜI CHƠI FF**\n\n"
        f"👤 Tên: {info.get('nickname', 'Không rõ')}\n"
        f"🆔 UID: {info.get('uid', uid)}\n"
        f"⚔️ Huy hiệu: {info.get('badge', 'Không có')}\n"
        f"🎯 Rank: {info.get('rank', {}).get('name', 'Không rõ')}\n"
        f"🏅 Mùa: {info.get('season', 'Không rõ')}\n"
        f"🔥 Tổng điểm: {info.get('points', 'Không rõ')}"
    )
    await update.message.reply_text(reply, parse_mode="Markdown")

# Đăng ký các lệnh
telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(CommandHandler("likeff", likeff))
telegram_app.add_handler(CommandHandler("viewff", viewff))

# Flask Webhook
@flask_app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), telegram_app.bot)
    telegram_app.update_queue.put(update)
    return "ok"

@flask_app.route("/", methods=["GET"])
def index():
    return "Bot Free Fire đang hoạt động!"

# Webhook setup
async def set_webhook():
    url = f"{WEBHOOK_URL}{BOT_TOKEN}"
    await telegram_app.bot.set_webhook(url)

if __name__ == "__main__":
    import threading

    threading.Thread(target=lambda: telegram_app.run_polling(), daemon=True).start()
    asyncio.run(set_webhook())
    flask_app.run(host="0.0.0.0", port=5000)

import time
import asyncio
import requests
from flask import Flask, request
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from telegram.constants import ChatAction

# --- Thông tin cấu hình ---
BOT_TOKEN = "6367532329:AAFzGAqQZ_f4VQqX7VbwAoQ7iqbFO07Hzqk"
WEBHOOK_URL = "https://your-domain.com/"  # Thay bằng domain thật khi deploy

# --- Khởi tạo Flask và Bot ---
flask_app = Flask(__name__)
telegram_app = ApplicationBuilder().token(BOT_TOKEN).build()

# --- /start ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Chào mừng bạn đến với bot hỗ trợ Free Fire!\n\n"
        "Lệnh sử dụng:\n"
        "/likeff <idgame> - Tăng lượt like\n"
        "/viewff <uid> - Xem thông tin người chơi"
    )

# --- /likeff ---
async def likeff(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❗ Nhập đúng cú pháp:\n/likeff <idgame>")
        return

    idgame = context.args[0]
    await update.message.reply_text("⏳ Đang xử lý lượt like...")
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)

    await asyncio.sleep(3)  # Delay gọi API

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
                await update.message.reply_text("❌ Server đang quá tải, vui lòng thử lại.")
                return
            time.sleep(5)
        except ValueError:
            await update.message.reply_text("❌ Phản hồi không hợp lệ từ server.")
            return

    if isinstance(data, dict) and "status" in data:
        if data["status"] == 2:
            await update.message.reply_text("⚠️ Đã đạt giới hạn like hôm nay.")
            return

        reply = (
            f"✅ **Kết quả Like:**\n\n"
            f"👤 Tên: {data.get('username', 'Không xác định')}\n"
            f"🆔 UID: {data.get('uid', 'Không xác định')}\n"
            f"🎚 Level: {data.get('level', 'Không xác định')}\n"
            f"👍 Trước: {data.get('likes_before', '?')}\n"
            f"✅ Sau: {data.get('likes_after', '?')}\n"
            f"➕ Đã thêm: {data.get('likes_given', '?')} like"
        )
    else:
        reply = "❌ Không thể xử lý yêu cầu."

    await update.message.reply_text(reply, parse_mode="Markdown")

# --- /viewff ---
async def viewff(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❗ Nhập đúng cú pháp:\n/viewff <uid>")
        return

    uid = context.args[0]
    await update.message.reply_text("🔍 Đang tìm kiếm thông tin...")
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)

    await asyncio.sleep(3)  # Delay gọi API

    try:
        res = requests.get(f"https://visit-plum.vercel.app/send_visit?uid={uid}", timeout=15)
        res.raise_for_status()
        data = res.json()
    except Exception:
        await update.message.reply_text("❌ Lỗi khi truy cập API Garena.")
        return

    if not isinstance(data, dict) or "data" not in data:
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

# --- Đăng ký các lệnh ---
telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(CommandHandler("likeff", likeff))
telegram_app.add_handler(CommandHandler("viewff", viewff))

# --- Webhook xử lý ---
@flask_app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook_handler():
    update = Update.de_json(request.get_json(force=True), telegram_app.bot)
    telegram_app.update_queue.put(update)
    return "ok"

@flask_app.route("/", methods=["GET"])
def index():
    return "Bot Free Fire đang chạy!"

# --- Thiết lập webhook ---
def set_webhook():
    import asyncio
    url = f"{WEBHOOK_URL}{BOT_TOKEN}"
    asyncio.run(telegram_app.bot.set_webhook(url=url))

# --- Chạy bot ---
if __name__ == "__main__":
    set_webhook()
    flask_app.run(host="0.0.0.0", port=5000)

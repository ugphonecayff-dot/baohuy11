import requests
import time
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from telegram.constants import ChatAction

BOT_TOKEN = "6367532329:AAFzGAqQZ_f4VQqX7VbwAoQ7iqbFO07Hzqk"  # Thay bằng token thật

# /likeff lệnh
async def likeff(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❗ Vui lòng nhập đúng:\n/likeff <idgame>")
        return

    idgame = context.args[0]
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
    await update.message.reply_text("⏳ Đang xử lý lượt like...")

    urllike = f"https://dichvukey.site/likeff2.php?key=vlong&uid={idgame}"
    max_retries = 5

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


# /viewff lệnh
async def viewff(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❗ Vui lòng nhập đúng:\n/viewff <uid>")
        return

    uid = context.args[0]
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
    await update.message.reply_text("🔍 Đang tìm thông tin người chơi...")

    urlview = f"https://ff-garena.run.place/visitor/?uid={uid}"

    try:
        response = requests.get(urlview, timeout=100)
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

# Main bot
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("likeff", likeff))
    app.add_handler(CommandHandler("viewff", viewff))
    print("Bot Telegram đang chạy...")
    app.run_polling()

if __name__ == "__main__":
    main()

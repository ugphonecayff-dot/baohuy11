import json
import os
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, CallbackQueryHandler, ContextTypes
from keep_alive import keep_alive
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
admin_id_env = os.getenv("ADMIN_ID")
if admin_id_env is None:
    raise Exception("ADMIN_ID chưa được cấu hình trong file .env!")
ADMIN_ID = int(admin_id_env)

# ---------------------- Utility Functions ----------------------
def load_json(file):
    try:
        with open(file, 'r') as f:
            return json.load(f)
    except:
        return {}

def save_json(file, data):
    with open(file, 'w') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def is_admin(user_id):
    return user_id == ADMIN_ID

# ---------------------- Bot Commands ----------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎮 *SHOP ACC LIÊN QUÂN*\n\n"
        "🔄 /random - Mua acc ngẫu nhiên\n"
        "📦 /myacc - Xem acc đã mua\n"
        "💰 /sodu - Kiểm tra số dư\n"
        "💳 /nap <sotien> - Nạp tiền\n",
        parse_mode="Markdown"
    )

async def sodu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    balances = load_json('balances.json')
    user_id = str(update.message.from_user.id)
    balance = balances.get(user_id, 0)
    await update.message.reply_text(f"💰 Số dư của bạn: {balance:,} VND")

async def nap(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 1:
        await update.message.reply_text("❗ Cú pháp: /nap <sotien>")
        return
    try:
        sotien = int(context.args[0])
    except:
        await update.message.reply_text("❗ Số tiền không hợp lệ!")
        return

    user_id = str(update.message.from_user.id)
    pending = load_json('pending.json')
    pending[user_id] = sotien
    save_json('pending.json', pending)

    await update.message.reply_text(
        f"💳 Vui lòng chuyển khoản theo thông tin sau:\n\n"
        f"- 📲 *STK:* `0971487462`\n"
        f"- 🏦 *Ngân hàng:* MB Bank\n"
        f"- 💬 *Nội dung:* `{user_id}`\n"
        f"- 💰 *Số tiền:* `{sotien:,} VND`\n\n"
        "Sau đó gửi ảnh chuyển khoản vào bot để admin duyệt.",
        parse_mode="Markdown"
    )

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    username = update.message.from_user.username or "Không có username"
    pending = load_json('pending.json')

    if user_id not in pending:
        await update.message.reply_text("❗ Bạn chưa yêu cầu nạp tiền bằng /nap!")
        return

    sotien = pending[user_id]
    keyboard = [[InlineKeyboardButton(f"✅ Duyệt {sotien:,} VND", callback_data=f"duyet_{user_id}_{sotien}")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await context.bot.forward_message(chat_id=ADMIN_ID, from_chat_id=update.message.chat_id, message_id=update.message.message_id)
    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=f"💰 *Yêu cầu nạp:* {sotien:,} VND\n👤 *User ID:* {user_id}\n👑 *Username:* @{username}",
        parse_mode="Markdown",
        reply_markup=reply_markup
    )

    await update.message.reply_text("✅ Đã gửi ảnh nạp tiền cho admin. Vui lòng chờ duyệt!")

async def random_acc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    balances = load_json('balances.json')
    accounts = load_json('acc.json')
    user_id = str(update.message.from_user.id)

    available = [acc for acc in accounts if acc['trangthai'] == 'chua_ban']
    if not available:
        await update.message.reply_text("❌ Hết acc để random!")
        return

    price = 1000
    balance = balances.get(user_id, 0)
    if balance < price:
        await update.message.reply_text(f"❌ Bạn không đủ {price:,} VND để mua acc.")
        return

    acc = random.choice(available)
    acc['trangthai'] = 'da_ban'
    acc['owner_id'] = user_id
    save_json('acc.json', accounts)

    balances[user_id] = balance - price
    save_json('balances.json', balances)

    await update.message.reply_text(
        f"🎉 Bạn đã nhận được tài khoản:\n\n"
        f"👤 *Tài khoản:* `{acc['taikhoan']}`\n"
        f"🔑 *Mật khẩu:* `{acc['matkhau']}`\n"
        f"💰 *Số dư còn lại:* {balances[user_id]:,} VND",
        parse_mode="Markdown"
    )

async def myacc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    accounts = load_json('acc.json')
    user_id = str(update.message.from_user.id)
    my_accounts = [acc for acc in accounts if acc.get('owner_id') == user_id]

    if not my_accounts:
        await update.message.reply_text("📭 Bạn chưa mua acc nào.")
        return

    message = "📦 *Tài khoản bạn đã mua:*\n\n"
    for i, acc in enumerate(my_accounts, 1):
        message += f"*{i}. 👤* `{acc['taikhoan']}`\n🔑 `{acc['matkhau']}`\n\n"

    await update.message.reply_text(message, parse_mode="Markdown")

async def themacc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.message.from_user.id):
        await update.message.reply_text("❌ Bạn không phải admin.")
        return
    if len(context.args) < 2:
        await update.message.reply_text("📌 Cú pháp: /themacc <taikhoan> <matkhau>")
        return

    taikhoan, matkhau = context.args[0], context.args[1]
    accounts = load_json('acc.json')

    if any(acc['taikhoan'] == taikhoan for acc in accounts):
        await update.message.reply_text("⚠️ Tài khoản đã tồn tại!")
        return

    accounts.append({"taikhoan": taikhoan, "matkhau": matkhau, "trangthai": "chua_ban"})
    save_json('acc.json', accounts)

    await update.message.reply_text(
        f"✅ Đã thêm acc mới:\n👤 `{taikhoan}`\n🔑 `{matkhau}`",
        parse_mode="Markdown"
    )

async def cong(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.message.from_user.id):
        await update.message.reply_text("❌ Bạn không phải admin.")
        return
    if len(context.args) < 2:
        await update.message.reply_text("📌 Cú pháp: /cong <user_id> <sotien>")
        return

    try:
        uid = str(int(context.args[0]))
        amount = int(context.args[1])
    except:
        await update.message.reply_text("❌ Sai định dạng!")
        return

    balances = load_json('balances.json')
    balances[uid] = balances.get(uid, 0) + amount
    save_json('balances.json', balances)
    await update.message.reply_text(f"✅ Đã cộng {amount:,} VND cho user `{uid}`", parse_mode="Markdown")

async def trutien(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.message.from_user.id):
        await update.message.reply_text("❌ Bạn không phải admin.")
        return
    if len(context.args) < 2:
        await update.message.reply_text("📌 Cú pháp: /trutien <user_id> <sotien>")
        return

    try:
        uid = str(int(context.args[0]))
        amount = int(context.args[1])
    except:
        await update.message.reply_text("❌ Sai định dạng!")
        return

    balances = load_json('balances.json')
    if balances.get(uid, 0) < amount:
        await update.message.reply_text(f"⚠️ User `{uid}` không đủ tiền!", parse_mode="Markdown")
        return

    balances[uid] -= amount
    save_json('balances.json', balances)
    await update.message.reply_text(f"✅ Đã trừ {amount:,} VND từ user `{uid}`", parse_mode="Markdown")

# ---------------------- Callback for Duyệt Nạp ----------------------
async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data
    if data.startswith("duyet_"):
        _, user_id, sotien = data.split("_")
        user_id = str(user_id)
        sotien = int(sotien)

        balances = load_json('balances.json')
        pending = load_json('pending.json')

        balances[user_id] = balances.get(user_id, 0) + sotien
        pending.pop(user_id, None)

        save_json('balances.json', balances)
        save_json('pending.json', pending)

        await context.bot.send_message(chat_id=int(user_id), text=f"✅ Admin đã duyệt nạp {sotien:,} VND vào tài khoản!")
        await query.edit_message_text(f"✅ Đã duyệt và cộng {sotien:,} VND cho user {user_id}")

# ---------------------- Start Bot ----------------------
if __name__ == '__main__':
    keep_alive()
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('sodu', sodu))
    app.add_handler(CommandHandler('nap', nap))
    app.add_handler(CommandHandler('random', random_acc))
    app.add_handler(CommandHandler('myacc', myacc))
    app.add_handler(CommandHandler('themacc', themacc))
    app.add_handler(CommandHandler('cong', cong))
    app.add_handler(CommandHandler('trutien', trutien))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(CallbackQueryHandler(handle_callback))

    print("🤖 Bot đang chạy...")
    app.run_polling()
                                

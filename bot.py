import json
import os
import random
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, CallbackQueryHandler, ContextTypes
from keep_alive import keep_alive
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
admin_id_env = os.getenv("ADMIN_ID")
if admin_id_env is None:
    raise Exception("ADMIN_ID chưa được cấu hình trong file .env!")
ADMIN_ID = int(admin_id_env)

# Load và lưu dữ liệu JSON
def load_json(file):
    try:
        with open(file, 'r') as f:
            return json.load(f)
    except:
        return []

def save_json(file, data):
    with open(file, 'w') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# Kiểm tra quyền admin
def is_admin(user_id):
    return user_id == ADMIN_ID

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        ["🔄 Mua Acc Ngẫu Nhiên", "📦 Acc Đã Mua"],
        ["💰 Xem Số Dư", "💳 Nạp Tiền"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text(
        "Chào mừng bạn đến shop acc Liên Quân!\n\n"
        "Chọn chức năng bên dưới hoặc dùng lệnh tương ứng.",
        reply_markup=reply_markup
    )

# /sodu
async def sodu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    balances = load_json('balances.json')
    user_id = str(update.message.from_user.id)
    balance = balances.get(user_id, 0)
    await update.message.reply_text(f"💰 Số dư hiện tại của bạn: {balance} VND")

# /nap
async def nap(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 1:
        await update.message.reply_text("Cú pháp: /nap <sotien>")
        return

    try:
        sotien = int(context.args[0])
    except:
        await update.message.reply_text("Số tiền phải là số!")
        return

    user_id = update.message.from_user.id
    pending = load_json('pending.json')
    pending[str(user_id)] = sotien
    save_json('pending.json', pending)

    await update.message.reply_text(
        f"Vui lòng chuyển khoản theo thông tin sau:\n\n"
        "📲 Số tài khoản: 0971487462\n"
        "🏦 Ngân hàng: MB Bank\n"
        f"💬 Nội dung chuyển khoản: {user_id}\n"
        f"💰 Số tiền: {sotien} VND\n\n"
        "Sau khi chuyển khoản, vui lòng gửi ảnh chuyển khoản vào đây.\n"
        "Bot sẽ chuyển ảnh cho admin kiểm duyệt."
    )

# Xử lý ảnh chuyển khoản
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    username = update.message.from_user.username or "Không có username"
    pending = load_json('pending.json')

    if str(user_id) not in pending:
        await update.message.reply_text("Bạn chưa yêu cầu nạp tiền! Vui lòng dùng lệnh /nap <sotien> trước.")
        return

    sotien = pending[str(user_id)]
    keyboard = [[InlineKeyboardButton(f"✅ Duyệt {sotien} VND", callback_data=f"duyet_{user_id}_{sotien}")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await context.bot.forward_message(chat_id=ADMIN_ID, from_chat_id=update.message.chat_id, message_id=update.message.message_id)
    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=f"💰 Yêu cầu nạp: {sotien} VND\n👤 User ID: {user_id}\n👑 Username: {username}",
        reply_markup=reply_markup
    )
    await update.message.reply_text("✅ Đã gửi ảnh nạp tiền cho admin. Vui lòng chờ duyệt!")

# /random
async def random_acc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    balances = load_json('balances.json')
    accounts = load_json('acc.json')
    user_id = str(update.message.from_user.id)

    balance = balances.get(user_id, 0)
    available_accounts = [acc for acc in accounts if acc['trangthai'] == 'chua_ban']

    if not available_accounts:
        await update.message.reply_text("⚠️ Hiện không còn acc nào để random!")
        return

    acc_price = 400
    if balance < acc_price:
        await update.message.reply_text(f"❌ Bạn không đủ tiền! Mỗi acc random có giá {acc_price} VND.")
        return

    acc = random.choice(available_accounts)
    balances[user_id] = balance - acc_price
    save_json('balances.json', balances)

    for a in accounts:
        if a == acc:
            a['trangthai'] = 'da_ban'
            a['owner_id'] = update.message.from_user.id
            break
    save_json('acc.json', accounts)

    await update.message.reply_text(
        f"🎉 Bạn đã nhận được acc:\n\n"
        f"Tài khoản: {acc['taikhoan']}\nMật khẩu: {acc['matkhau']}\n\n"
        f"Số dư còn lại: {balances[user_id]} VND"
    )

# /myacc
async def myacc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    accounts = load_json('acc.json')
    user_id = update.message.from_user.id

    bought_accounts = [acc for acc in accounts if acc.get('owner_id') == user_id]

    if not bought_accounts:
        await update.message.reply_text("Bạn chưa mua acc nào.")
        return

    message = "📦 Acc bạn đã nhận:\n\n"
    for acc in bought_accounts:
        message += f"👤 {acc['taikhoan']} | 🔑 {acc['matkhau']}\n"

    await update.message.reply_text(message)

# Admin /themacc
async def themacc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if not is_admin(user_id):
        await update.message.reply_text("❌ Bạn không có quyền dùng lệnh này.")
        return

    if len(context.args) < 2:
        await update.message.reply_text("⚠️ Cú pháp đúng: /themacc <taikhoan> <matkhau>")
        return

    taikhoan = context.args[0]
    matkhau = context.args[1]

    accounts = load_json('acc.json')
    if any(acc['taikhoan'] == taikhoan for acc in accounts):
        await update.message.reply_text("⚠️ Tài khoản này đã tồn tại!")
        return

    accounts.append({
        "taikhoan": taikhoan,
        "matkhau": matkhau,
        "trangthai": "chua_ban"
    })
    save_json('acc.json', accounts)

    await update.message.reply_text(
        f"✅ Đã thêm acc mới:\n👤 `{taikhoan}`\n🔑 `{matkhau}`",
        parse_mode="Markdown"
    )

# Xử lý callback duyệt nạp
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

        await context.bot.send_message(chat_id=int(user_id), text=f"✅ Admin đã duyệt nạp {sotien} VND vào tài khoản!")
        await query.edit_message_text(f"✅ Đã duyệt và cộng {sotien} VND cho user {user_id}.")

# Chạy bot
if __name__ == '__main__':
    keep_alive()

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('sodu', sodu))
    app.add_handler(CommandHandler('nap', nap))
    app.add_handler(CommandHandler('random', random_acc))
    app.add_handler(CommandHandler('myacc', myacc))
    app.add_handler(CommandHandler('themacc', themacc))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(CallbackQueryHandler(handle_callback))

    print("🤖 Bot đang chạy...")
    app.run_polling()
    

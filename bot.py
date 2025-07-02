import json
import os
import random
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from keep_alive import keep_alive
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
admin_id_env = os.getenv("ADMIN_ID")
if admin_id_env is None:
    raise Exception("ADMIN_ID chưa được cấu hình trong file .env!")
ADMIN_ID = int(admin_id_env)

# Load và lưu dữ liệu
def load_json(file):
    try:
        with open(file, 'r') as f:
            return json.load(f)
    except:
        return {}


def save_json(file, data):
    with open(file, 'w') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


# Kiểm tra quyền admin
def is_admin(user_id):
    return user_id == ADMIN_ID


# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Chào mừng bạn đến shop acc Liên Quân!\n\n"
        "/random - Mua acc ngẫu nhiên\n"
        "/myacc - Xem acc đã mua\n"
        "/sodu - Xem số dư\n"
        "/nap <sotien> - Yêu cầu nạp tiền\n\n"
        "Quản lý (Admin):\n"
        "/addacc <taikhoan> <matkhau> - Thêm acc\n"
        "/delacc <id> - Xóa acc\n"
        "/stats - Xem thống kê\n"
        "/cong <user_id> <sotien> - Cộng tiền cho người dùng"
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
    username = update.message.from_user.username or "Không có username"

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


# Xử lý ảnh nạp tiền
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    username = update.message.from_user.username or "Không có username"
    pending = load_json('pending.json')

    if str(user_id) not in pending:
        await update.message.reply_text("Bạn chưa yêu cầu nạp tiền! Vui lòng sử dụng lệnh /nap <sotien> trước.")
        return

    sotien = pending[str(user_id)]

    await context.bot.forward_message(chat_id=ADMIN_ID, from_chat_id=update.message.chat_id, message_id=update.message.message_id)
    await context.bot.send_message(chat_id=ADMIN_ID, text=f"💰 Yêu cầu nạp: {sotien} VND\n👤 User ID: {user_id}\n👑 Username: {username}")

    await update.message.reply_text("Đã gửi ảnh nạp tiền cho admin. Vui lòng chờ duyệt!")


# /cong (Admin cộng tiền)
async def cong(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.message.from_user.id):
        await update.message.reply_text("Bạn không có quyền sử dụng lệnh này!")
        return

    if len(context.args) < 2:
        await update.message.reply_text("Cú pháp: /cong <user_id> <sotien>")
        return

    try:
        user_id = str(context.args[0])
        sotien = int(context.args[1])
    except:
        await update.message.reply_text("Sai định dạng, vui lòng kiểm tra lại!")
        return

    balances = load_json('balances.json')
    balances[user_id] = balances.get(user_id, 0) + sotien
    save_json('balances.json', balances)

    await update.message.reply_text(f"✅ Đã cộng {sotien} VND cho người dùng {user_id}.")

    try:
        await context.bot.send_message(chat_id=int(user_id), text=f"🎉 Bạn đã được cộng {sotien} VND vào tài khoản!")
    except:
        pass


# /random
async def random_acc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    balances = load_json('balances.json')
    accounts = load_json('acc.json')
    user_id = str(update.message.from_user.id)

    balance = balances.get(user_id, 0)
    available_accounts = [acc for acc in accounts if acc['trangthai'] == 'chua_ban']

    if not available_accounts:
        await update.message.reply_text("Hiện không còn acc nào để random!")
        return

    acc = random.choice(available_accounts)
    acc_price = 2000  # Giá mỗi acc random

    if balance < acc_price:
        await update.message.reply_text(f"Bạn không đủ tiền! Mỗi acc random có giá {acc_price} VND.")
        return

    balances[user_id] = balance - acc_price
    save_json('balances.json', balances)

    acc['trangthai'] = 'da_ban'
    acc['owner_id'] = update.message.from_user.id
    save_json('acc.json', accounts)

    await update.message.reply_text(f"🎉 Bạn đã nhận được acc:\n\nTài khoản: {acc['taikhoan']}\nMật khẩu: {acc['matkhau']}\n\nSố dư còn lại: {balances[user_id]} VND")


# /myacc
async def myacc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    accounts = load_json('acc.json')
    user_id = update.message.from_user.id

    bought_accounts = [acc for acc in accounts if acc.get('owner_id') == user_id]

    if not bought_accounts:
        await update.message.reply_text("Bạn chưa mua acc nào.")
        return

    message = "Acc bạn đã nhận:\n\n"
    for acc in bought_accounts:
        message += f"Tài khoản: {acc['taikhoan']} | Mật khẩu: {acc['matkhau']}\n"

    await update.message.reply_text(message)


# /addacc
async def addacc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.message.from_user.id):
        await update.message.reply_text("Bạn không có quyền thêm acc!")
        return

    if len(context.args) < 2:
        await update.message.reply_text("Cú pháp: /addacc <taikhoan> <matkhau>")
        return

    taikhoan = context.args[0]
    matkhau = context.args[1]

    accounts = load_json('acc.json')
    new_id = max([acc['id'] for acc in accounts], default=0) + 1

    accounts.append({
        "id": new_id,
        "taikhoan": taikhoan,
        "matkhau": matkhau,
        "trangthai": "chua_ban"
    })
    save_json('acc.json', accounts)

    await update.message.reply_text(f"✅ Đã thêm acc ID {new_id} thành công!")


# /delacc
async def delacc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.message.from_user.id):
        await update.message.reply_text("Bạn không có quyền xóa acc!")
        return

    if len(context.args) < 1:
        await update.message.reply_text("Cú pháp: /delacc <id>")
        return

    try:
        acc_id = int(context.args[0])
    except:
        await update.message.reply_text("ID phải là số!")
        return

    accounts = load_json('acc.json')
    new_accounts = [acc for acc in accounts if acc['id'] != acc_id]

    if len(new_accounts) == len(accounts):
        await update.message.reply_text("Không tìm thấy acc với ID này.")
        return

    save_json('acc.json', new_accounts)
    await update.message.reply_text(f"✅ Đã xóa acc ID {acc_id} thành công!")


# /stats
async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.message.from_user.id):
        await update.message.reply_text("Bạn không có quyền xem thống kê!")
        return

    accounts = load_json('acc.json')
    balances = load_json('balances.json')

    total_acc = len(accounts)
    sold_acc = len([acc for acc in accounts if acc['trangthai'] == 'da_ban'])
    available_acc = len([acc for acc in accounts if acc['trangthai'] == 'chua_ban'])
    total_users = len(balances)

    await update.message.reply_text(f"📊 Thống kê:\n\n"
                                    f"Tổng số acc: {total_acc}\n"
                                    f"Acc đã bán: {sold_acc}\n"
                                    f"Acc còn lại: {available_acc}\n"
                                    f"Số người dùng: {total_users}")


# Chạy bot
if __name__ == '__main__':
    keep_alive()

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('sodu', sodu))
    app.add_handler(CommandHandler('nap', nap))
    app.add_handler(CommandHandler('cong', cong))
    app.add_handler(CommandHandler('random', random_acc))
    app.add_handler(CommandHandler('myacc', myacc))
    app.add_handler(CommandHandler('addacc', addacc))
    app.add_handler(CommandHandler('delacc', delacc))
    app.add_handler(CommandHandler('stats', stats))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    print("Bot đang chạy...")
    app.run_polling()

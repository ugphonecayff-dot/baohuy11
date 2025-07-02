import json
import os
import random
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from keep_alive import keep_alive
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

def load_json(file):
    try:
        with open(file, 'r') as f:
            return json.load(f)
    except:
        return []

def save_json(file, data):
    with open(file, 'w') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def is_admin(user_id):
    users = load_json('users.json')
    for user in users:
        if user['id'] == user_id and user['role'] == 'admin':
            return True
    return False

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Chào mừng bạn đến shop acc Liên Quân!\n\n"
        "/listacc - Xem acc đang bán\n"
        "/buy <id> - Mua acc theo ID\n"
        "/random - Mua acc ngẫu nhiên\n"
        "/myacc - Xem acc đã mua\n\n"
        "Quản lý (Admin):\n"
        "/addacc <taikhoan> <matkhau> <gia> - Thêm acc\n"
        "/editacc <id> <gia> - Sửa giá acc\n"
        "/delacc <id> - Xóa acc\n"
        "/stats - Xem thống kê\n"
        "/xacnhan <acc_id> <user_id> - Xác nhận thanh toán"
    )

async def listacc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    accounts = load_json('acc.json')
    text = "Danh sách acc đang bán:\n"
    for acc in accounts:
        if acc['trangthai'] == 'chua_ban':
            text += f"ID: {acc['id']} | Giá: {acc['gia']} VND\n"
    if text == "Danh sách acc đang bán:\n":
        text = "Hiện tại không có acc nào đang bán."
    await update.message.reply_text(text)

async def buy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) == 0:
        await update.message.reply_text("Vui lòng nhập ID acc muốn mua: /buy <id>")
        return

    try:
        acc_id = int(context.args[0])
    except:
        await update.message.reply_text("Vui lòng nhập ID hợp lệ.")
        return

    accounts = load_json('acc.json')
    for acc in accounts:
        if acc['id'] == acc_id:
            if acc['trangthai'] == 'da_ban':
                await update.message.reply_text("Acc này đã được bán rồi!")
                return

            orders = load_json('orders.json')
            orders.append({
                "acc_id": acc_id,
                "user_id": update.message.from_user.id,
                "gia": acc['gia'],
                "trangthai": "cho_duyet"
            })
            save_json('orders.json', orders)

            await update.message.reply_text(f"Đơn hàng đã được tạo!\n\nVui lòng chuyển khoản {acc['gia']} VND vào số tài khoản sau:\n\n"
                                            "🏦 Ngân hàng: MB Bank\n"
                                            "🔢 Số tài khoản: 123456789\n"
                                            "👤 Chủ tài khoản: NGUYEN VAN A\n"
                                            f"📌 Nội dung chuyển khoản: {update.message.from_user.id}\n\nSau khi chuyển, admin sẽ duyệt đơn cho bạn.")
            await context.bot.send_message(chat_id=ADMIN_ID, text=f"📥 Đơn hàng mới:\nUser: {update.message.from_user.id}\nAcc ID: {acc_id}\nGiá: {acc['gia']} VND")
            return

    await update.message.reply_text("Không tìm thấy acc với ID này.")

async def random_acc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    accounts = load_json('acc.json')
    available = [acc for acc in accounts if acc['trangthai'] == 'chua_ban']

    if not available:
        await update.message.reply_text("Hiện tại không còn acc nào để random.")
        return

    acc = random.choice(available)

    orders = load_json('orders.json')
    orders.append({
        "acc_id": acc['id'],
        "user_id": update.message.from_user.id,
        "gia": acc['gia'],
        "trangthai": "cho_duyet"
    })
    save_json('orders.json', orders)

    await update.message.reply_text(f"Đơn hàng random đã được tạo!\n\nVui lòng chuyển khoản {acc['gia']} VND vào số tài khoản sau:\n\n"
                                    "🏦 Ngân hàng: MB Bank\n"
                                    "🔢 Số tài khoản: 0971487462\n"
                                    "👤 Chủ tài khoản: Ngo Quang Khai\n"
                                    f"📌 Nội dung chuyển khoản: {update.message.from_user.id}\n\nSau khi chuyển, admin sẽ duyệt đơn cho bạn.")
    await context.bot.send_message(chat_id=ADMIN_ID, text=f"📥 Đơn hàng random:\nUser: {update.message.from_user.id}\nAcc ID: {acc['id']}\nGiá: {acc['gia']} VND")

async def myacc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    accounts = load_json('acc.json')
    text = "Acc bạn đã mua:\n"
    found = False
    for acc in accounts:
        if acc.get('nguoi_mua') == user_id:
            text += f"ID: {acc['id']} | Tài khoản: {acc['taikhoan']} | Mật khẩu: {acc['matkhau']} | Giá: {acc['gia']} VND\n"
            found = True

    if found:
        await update.message.reply_text(text)
    else:
        await update.message.reply_text("Bạn chưa mua acc nào.")

async def xacnhan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.message.from_user.id):
        await update.message.reply_text("Bạn không có quyền xác nhận!")
        return

    if len(context.args) < 2:
        await update.message.reply_text("Cú pháp: /xacnhan <acc_id> <user_id>")
        return

    try:
        acc_id = int(context.args[0])
        user_id = int(context.args[1])
    except:
        await update.message.reply_text("ID phải là số!")
        return

    accounts = load_json('acc.json')
    orders = load_json('orders.json')

    for order in orders:
        if order['acc_id'] == acc_id and order['user_id'] == user_id and order['trangthai'] == "cho_duyet":
            for acc in accounts:
                if acc['id'] == acc_id:
                    acc['trangthai'] = 'da_ban'
                    acc['nguoi_mua'] = user_id
                    order['trangthai'] = 'da_duyet'
                    save_json('acc.json', accounts)
                    save_json('orders.json', orders)

                    await context.bot.send_message(chat_id=user_id, text=f"✅ Đơn hàng của bạn đã được xác nhận!\n\nTài khoản: {acc['taikhoan']}\nMật khẩu: {acc['matkhau']}")
                    await update.message.reply_text("✅ Đã giao acc cho khách thành công.")
                    return

    await update.message.reply_text("Không tìm thấy đơn hàng hợp lệ.")

if __name__ == '__main__':
    keep_alive()

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('listacc', listacc))
    app.add_handler(CommandHandler('buy', buy))
    app.add_handler(CommandHandler('random', random_acc))
    app.add_handler(CommandHandler('myacc', myacc))
    app.add_handler(CommandHandler('xacnhan', xacnhan))

    print("Bot đang chạy...")
    app.run_polling()

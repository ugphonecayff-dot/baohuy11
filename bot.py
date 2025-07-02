import json
import os
import random
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
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
        return []


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
        "/listacc - Xem acc đang bán\n"
        "/buy <id> - Mua acc theo ID\n"
        "/random - Mua acc ngẫu nhiên\n"
        "/myacc - Xem acc đã mua\n\n"
        "Quản lý (Admin):\n"
        "/addacc <taikhoan> <matkhau> <gia> - Thêm acc\n"
        "/editacc <id> <gia> - Sửa giá acc\n"
        "/delacc <id> - Xóa acc\n"
        "/stats - Xem thống kê"
    )


# /listacc
async def listacc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    accounts = load_json('acc.json')
    message = "Danh sách acc đang bán:\n\n"
    for acc in accounts:
        if acc['trangthai'] == 'chua_ban':
            message += f"ID: {acc['id']} | Giá: {acc['gia']} VND\n"
    await update.message.reply_text(message)


# /buy
async def buy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 1:
        await update.message.reply_text("Cú pháp: /buy <id>")
        return

    try:
        acc_id = int(context.args[0])
    except:
        await update.message.reply_text("ID phải là số!")
        return

    accounts = load_json('acc.json')
    for acc in accounts:
        if acc['id'] == acc_id and acc['trangthai'] == 'chua_ban':
            orders = load_json('orders.json')
            orders.append({
                "user_id": update.message.from_user.id,
                "username": update.message.from_user.username,
                "acc_id": acc_id,
                "trangthai": "cho_duyet"
            })
            save_json('orders.json', orders)
            await update.message.reply_text("Đã tạo đơn hàng, vui lòng chờ admin xác nhận!")
            return

    await update.message.reply_text("Acc không tồn tại hoặc đã bán!")


# /random
async def random_acc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    accounts = load_json('acc.json')
    available_accounts = [acc for acc in accounts if acc['trangthai'] == 'chua_ban']

    if not available_accounts:
        await update.message.reply_text("Hiện không còn acc nào để random!")
        return

    acc = random.choice(available_accounts)

    orders = load_json('orders.json')
    orders.append({
        "user_id": update.message.from_user.id,
        "username": update.message.from_user.username,
        "acc_id": acc['id'],
        "trangthai": "cho_duyet"
    })
    save_json('orders.json', orders)

    await update.message.reply_text(f"Đã tạo đơn hàng random acc ID {acc['id']}, vui lòng chờ admin xác nhận!")


# /myacc
async def myacc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    accounts = load_json('acc.json')
    user_id = update.message.from_user.id

    bought_accounts = [acc for acc in accounts if acc.get('owner_id') == user_id]

    if not bought_accounts:
        await update.message.reply_text("Bạn chưa mua acc nào.")
        return

    message = "Acc bạn đã mua:\n\n"
    for acc in bought_accounts:
        message += f"Tài khoản: {acc['taikhoan']} | Mật khẩu: {acc['matkhau']}\n"

    await update.message.reply_text(message)


# /addacc
async def addacc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.message.from_user.id):
        await update.message.reply_text("Bạn không có quyền thêm acc!")
        return

    if len(context.args) < 3:
        await update.message.reply_text("Cú pháp: /addacc <taikhoan> <matkhau> <gia>")
        return

    taikhoan = context.args[0]
    matkhau = context.args[1]
    try:
        gia = int(context.args[2])
    except:
        await update.message.reply_text("Giá phải là số!")
        return

    accounts = load_json('acc.json')
    new_id = max([acc['id'] for acc in accounts], default=0) + 1

    accounts.append({
        "id": new_id,
        "taikhoan": taikhoan,
        "matkhau": matkhau,
        "gia": gia,
        "trangthai": "chua_ban"
    })
    save_json('acc.json', accounts)

    await update.message.reply_text(f"✅ Đã thêm acc ID {new_id} thành công!")


# /editacc
async def editacc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.message.from_user.id):
        await update.message.reply_text("Bạn không có quyền sửa acc!")
        return

    if len(context.args) < 2:
        await update.message.reply_text("Cú pháp: /editacc <id> <gia>")
        return

    try:
        acc_id = int(context.args[0])
        gia_moi = int(context.args[1])
    except:
        await update.message.reply_text("ID và giá phải là số!")
        return

    accounts = load_json('acc.json')
    for acc in accounts:
        if acc['id'] == acc_id:
            acc['gia'] = gia_moi
            save_json('acc.json', accounts)
            await update.message.reply_text(f"✅ Đã cập nhật giá acc ID {acc_id} thành {gia_moi} VND.")
            return

    await update.message.reply_text("Không tìm thấy acc với ID này.")


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
    orders = load_json('orders.json')

    total_acc = len(accounts)
    sold_acc = len([acc for acc in accounts if acc['trangthai'] == 'da_ban'])
    waiting_orders = len([order for order in orders if order['trangthai'] == 'cho_duyet'])

    await update.message.reply_text(f"📊 Thống kê:\n\n"
                                    f"Tổng số acc: {total_acc}\n"
                                    f"Acc đã bán: {sold_acc}\n"
                                    f"Đơn hàng chờ duyệt: {waiting_orders}")


# /xacnhan
async def xacnhan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.message.from_user.id):
        await update.message.reply_text("Bạn không có quyền xác nhận đơn!")
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

    for acc in accounts:
        if acc['id'] == acc_id:
            acc['trangthai'] = 'da_ban'
            acc['owner_id'] = user_id
            save_json('acc.json', accounts)

            for order in orders:
                if order['acc_id'] == acc_id and order['user_id'] == user_id:
                    order['trangthai'] = 'da_duyet'
                    save_json('orders.json', orders)
                    await update.message.reply_text("✅ Đã xác nhận đơn hàng và giao acc!")
                    return

    await update.message.reply_text("Không tìm thấy acc hoặc đơn hàng này!")


# Chạy bot
if __name__ == '__main__':
    keep_alive()

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('listacc', listacc))
    app.add_handler(CommandHandler('buy', buy))
    app.add_handler(CommandHandler('random', random_acc))
    app.add_handler(CommandHandler('myacc', myacc))
    app.add_handler(CommandHandler('addacc', addacc))
    app.add_handler(CommandHandler('editacc', editacc))
    app.add_handler(CommandHandler('delacc', delacc))
    app.add_handler(CommandHandler('stats', stats))
    app.add_handler(CommandHandler('xacnhan', xacnhan))

    print("Bot đang chạy...")
    app.run_polling()

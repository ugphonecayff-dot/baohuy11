from telethon.sync import TelegramClient
from telethon.sessions import StringSession
from telethon.tl.functions.account import UpdateProfileRequest
from datetime import datetime
import pytz
import time
from keep_alive import keep_alive  # Giữ bot sống khi host (Replit/Render...)

# Khởi động web server (nếu dùng để giữ hoạt động liên tục)
keep_alive()

# === Thay bằng API ID và API Hash lấy từ https://my.telegram.org ===
api_id = 27657608
api_hash = '3b6e52a3713b44ad5adaa2bcf579de66'

# === Tạo client Telegram và đăng nhập ===
with TelegramClient(StringSession(), api_id, api_hash) as client:
    client.start()  # Nhập số điện thoại và mã nếu chưa từng đăng nhập

    print("🚀 Bot đã bắt đầu cập nhật tên theo giờ Việt Nam...")

    while True:
        # Lấy giờ hiện tại tại Việt Nam
        vietnam_tz = pytz.timezone('Asia/Ho_Chi_Minh')
        now = datetime.now(vietnam_tz)

        # Tạo tên mới với giờ phút giây
        new_name = f"Bảo Huy🇻🇳 {now.strftime('%H:%M:%S - %d/%m/%Y')}"

        # Gửi yêu cầu cập nhật tên
        client(UpdateProfileRequest(first_name=new_name))
        print(f"✅ Tên đã cập nhật thành: {new_name}")

        # Đợi 60 giây để cập nhật lại
        time.sleep(60)

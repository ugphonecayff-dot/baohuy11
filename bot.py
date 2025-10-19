import requests
import asyncio
from telegram.ext import ApplicationBuilder
import logging
from datetime import datetime
from keep_alive import keep_alive  # file keep_alive.py

# ===== Logging =====
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# ===== Cấu hình =====
TOKEN = "8080338995:AAHYQHo0lSry8MupGC0RJt_o8kLbRDiYjQQ"
GROUP_CHAT_IDS = [-1002666964512]  # Nhóm nhận kết quả
CHECK_INTERVAL = 5  # giây giữa các lần kiểm tra API

# ===== API phân biệt =====
API_LIST = {
    "Sunwin": "https://hitclub-pre.onrender.com/api/taixiu",
    "HitMD5": "https://hitclub-pre.onrender.com/api/taixiumd5",
    "History": "https://hitclub-pre.onrender.com/api/history"
}

# ===== Hàm gọi API =====
def call_api(name):
    url = API_LIST.get(name)
    if not url:
        logging.warning(f"API {name} không tồn tại")
        return None
    try:
        r = requests.get(url, timeout=5)
        data = r.json()
        return data
    except Exception as e:
        logging.error(f"Lỗi gọi API {name}: {e}")
        return None

# ===== Tạo tin nhắn gọn, phân biệt API =====
def format_message(result, hist, name="Sunwin"):
    now = datetime.now().strftime("%H:%M:%S")
    phien = result.get("id", "??")
    dice = result.get("dice", [])
    total = sum(dice) if dice else "??"
    ketqua = result.get("result", "??")
    phien_truoc = hist[0] if hist else "??"
    prediction = "Tài" if hist.count("Tài") >= hist.count("Xỉu") else "Xỉu"
    dice_str = " | ".join(str(d) for d in dice) if dice else "??"
    message = (
        f"[{name}]\n"
        f"Giờ: {now}\n"
        f"Phiên: {phien}\n"
        f"🎲 {dice_str} → Tổng: {total}\n"
        f"Kết quả: {ketqua}\n"
        f"Phiên trước: {phien_truoc}\n"
        f"Dự đoán tiếp theo: {prediction}"
    )
    return message

# ===== Task auto-send theo phiên =====
async def auto_send_task(bot_app):
    # Khởi tạo phiên cuối cùng từng API = 0 để gửi lần đầu
    last_phien = {"Sunwin": 0, "HitMD5": 0}

    while True:
        try:
            for name in ["Sunwin", "HitMD5"]:
                result = call_api(name)
                hist = call_api("History")[:50] or []

                # Debug log để kiểm tra API
                logging.info(f"[DEBUG] {name} result: {result}")

                if not result or "id" not in result:
                    continue

                phien = result["id"]

                # Gửi ngay lần đầu hoặc khi có phiên mới
                if last_phien[name] == 0 or phien > last_phien[name]:
                    message = format_message(result, hist, name)
                    for chat_id in GROUP_CHAT_IDS:
                        try:
                            await bot_app.bot.send_message(chat_id=chat_id, text=message)
                        except Exception as e:
                            logging.warning(f"Lỗi gửi message cho {chat_id}: {e}")
                    last_phien[name] = phien
                    logging.info(f"[{name}] Phiên {phien} đã gửi")

        except Exception as e:
            logging.error(f"Lỗi task auto-send: {e}")

        await asyncio.sleep(CHECK_INTERVAL)

# ===== Main =====
async def main():
    keep_alive()  # Khởi động server nhỏ để bot không bị sleep
    bot_app = ApplicationBuilder().token(TOKEN).build()
    asyncio.create_task(auto_send_task(bot_app))
    logging.info("Bot đang chạy...")
    await bot_app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
    

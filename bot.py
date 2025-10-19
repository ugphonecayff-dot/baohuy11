import requests
import asyncio
from telegram.ext import ApplicationBuilder
import logging
from datetime import datetime
from keep_alive import keep_alive  # file keep_alive.py

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# ===== Cấu hình =====
TOKEN = "8080338995:AAHYQHo0lSry8MupGC0RJt_o8kLbRDiYjQQ"
GROUP_CHAT_IDS = [-1002666964512]  # Nhóm nhận kết quả
CHECK_INTERVAL = 5  # giây

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
        return None
    try:
        r = requests.get(url)
        return r.json()
    except:
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
    last_phien = {}  # Lưu phiên cuối cùng từng API
    while True:
        try:
            for name in ["Sunwin", "HitMD5"]:
                result = call_api(name)
                hist = call_api("History")[:50] or []

                if not result:
                    continue

                phien = result.get("id", 0)
                if last_phien.get(name) is None:
                    last_phien[name] = phien
                elif phien > last_phien[name]:
                    message = format_message(result, hist, name)
                    for chat_id in GROUP_CHAT_IDS:
                        try:
                            await bot_app.bot.send_message(chat_id=chat_id, text=message)
                        except Exception as e:
                            logging.warning(f"Lỗi gửi message cho {chat_id}: {e}")
                    last_phien[name] = phien

        except Exception as e:
            logging.error(f"Lỗi task auto-send: {e}")

        await asyncio.sleep(CHECK_INTERVAL)

# ===== Main =====
async def main():
    keep_alive()  # Khởi động server nhỏ để bot không bị sleep
    bot_app = ApplicationBuilder().token(TOKEN).build()
    asyncio.create_task(auto_send_task(bot_app))
    print("Bot đang chạy...")
    await bot_app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
    

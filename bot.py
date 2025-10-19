import requests
import asyncio
from telegram.ext import ApplicationBuilder
import logging
from datetime import datetime
from keep_alive import keep_alive
import nest_asyncio

nest_asyncio.apply()  # Fix "event loop already running"

logging.basicConfig(level=logging.INFO)

TOKEN = "8080338995:AAHYQHo0lSry8MupGC0RJt_o8kLbRDiYjQQ"
GROUP_CHAT_IDS = [-1002666964512]
CHECK_INTERVAL = 5

API_LIST = {
    "Sunwin": "https://hitclub-pre.onrender.com/api/taixiu",
    "HitMD5": "https://hitclub-pre.onrender.com/api/taixiumd5",
    "History": "https://hitclub-pre.onrender.com/api/history"
}

def call_api(name):
    url = API_LIST.get(name)
    if not url:
        logging.warning(f"API {name} không tồn tại")
        return None
    try:
        r = requests.get(url, timeout=5)
        return r.json()
    except Exception as e:
        logging.error(f"Lỗi gọi API {name}: {e}")
        return None

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

async def auto_send_task(bot_app):
    last_phien = {"Sunwin": 0, "HitMD5": 0}

    while True:
        try:
            for name in ["Sunwin", "HitMD5"]:
                result = call_api(name)

                # Fix slice lỗi
                hist_data = call_api("History")
                if isinstance(hist_data, list):
                    hist = hist_data[:50]
                else:
                    hist = []

                logging.info(f"[DEBUG] {name} result: {result}")

                if not result or "id" not in result:
                    continue

                phien = result["id"]

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

async def main():
    keep_alive()
    bot_app = ApplicationBuilder().token(TOKEN).build()
    asyncio.create_task(auto_send_task(bot_app))
    logging.info("Bot đang chạy...")
    await bot_app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
                    

import requests
import time
import asyncio
from telegram import Bot
from keep_alive import keep_alive

TELEGRAM_TOKEN = "8080338995:AAHYQHo0lSry8MupGC0RJt_o8kLbRDiYjQQ"
CHAT_ID = "-1002666964512"
API_URL = "https://binhtool-b52predict.onrender.com/api/taixiu"

bot = Bot(token=TELEGRAM_TOKEN)

async def send_msg(msg):
    try:
        await bot.send_message(chat_id=CHAT_ID, text=msg)
    except Exception as e:
        print("❌ Lỗi gửi Telegram:", e)

def get_result():
    try:
        res = requests.get(API_URL, timeout=10)
        if res.status_code == 200:
            return res.json()
    except Exception as e:
        print("❌ API lỗi:", e)
    return None

async def main():
    last_phien = None
    while True:
        data = get_result()
        if data and "phien" in data:
            phien = data.get("phien")
            ketqua = data.get("ketqua")
            tong = data.get("tong")
            kq_text = data.get("kq_text")
            du_doan = data.get("du_doan")

            if phien != last_phien:
                msg = (
                    f"🎲 Phiên: {phien}\n"
                    f"🎯 Kết quả: {ketqua} = {tong} ⇒ {kq_text}\n"
                    f"📊 Dự đoán tiếp: {du_doan}"
                )
                await send_msg(msg)
                print("✅ Đã gửi phiên:", phien)
                last_phien = phien

        await asyncio.sleep(5)

if __name__ == "__main__":
    keep_alive()
    asyncio.run(main())
    

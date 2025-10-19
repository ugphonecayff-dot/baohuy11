import requests
import time
from telegram import Bot
from keep_alive import keep_alive   # để giữ bot sống 24/7 (nếu deploy online)

# === Config ===
TELEGRAM_TOKEN = "8080338995:AAHYQHo0lSry8MupGC0RJt_o8kLbRDiYjQQ"  # Bot Token
CHAT_ID = "-1002666964512"  # Group chat ID
API_URL = "https://binhtool-b52predict.onrender.com/api/taixiu"

bot = Bot(token=TELEGRAM_TOKEN)

def get_result():
    try:
        res = requests.get(API_URL, timeout=5).json()
        return res
    except Exception as e:
        print("❌ Lỗi API:", e)
        return None

def main():
    last_phien = None
    while True:
        data = get_result()
        if data:
            phien = data.get("phien")
            ketqua = data.get("ketqua")
            tong = data.get("tong")
            kq_text = data.get("kq_text")
            du_doan = data.get("du_doan")

            # Nếu có phiên mới thì gửi vào group
            if phien != last_phien:
                msg = (
                    f"🎲 Phiên: {phien}\n"
                    f"🎯 Kết quả: {ketqua} = {tong} ⇒ {kq_text}\n"
                    f"📊 Dự đoán tiếp: {du_doan}"
                )
                bot.send_message(chat_id=CHAT_ID, text=msg)
                print("✅ Đã gửi phiên:", phien)
                last_phien = phien

        time.sleep(5)  # check API mỗi 5 giây

if __name__ == "__main__":
    keep_alive()  # ⚡ giữ bot chạy 24/7 khi deploy
    main()
    

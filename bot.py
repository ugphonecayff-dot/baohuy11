import requests
import time
from telegram import Bot
from keep_alive import keep_alive

TELEGRAM_TOKEN = "8080338995:AAHYQHo0lSry8MupGC0RJt_o8kLbRDiYjQQ"
CHAT_ID = "-1002666964512"
API_URL = "https://binhtool-b52predict.onrender.com/api/taixiu"

bot = Bot(token=TELEGRAM_TOKEN)

history = []  # lưu lịch sử kết quả

def get_result():
    try:
        res = requests.get(API_URL, timeout=10)
        if res.status_code == 200:
            return res.json()
    except Exception as e:
        print("❌ API lỗi:", e)
    return None

def analyze_history():
    if not history:
        return ""

    total = len(history)
    count_tai = sum(1 for h in history if h["kq_text"] == "Tài")
    count_xiu = total - count_tai

    msg = f"\n📈 Thống kê {total} phiên gần đây:\n"
    msg += f"- Tài: {count_tai} ({count_tai/total*100:.1f}%)\n"
    msg += f"- Xỉu: {count_xiu} ({count_xiu/total*100:.1f}%)"

    # Check chuỗi liên tiếp
    if len(history) >= 3:
        last_results = [h["kq_text"] for h in history[-5:]]
        if len(set(last_results[-3:])) == 1:  # 3 kết quả gần nhất giống nhau
            msg += f"\n🚨 Chuỗi {len(set(last_results[-3:]))+2} ván liên tiếp: {last_results[-1]}!"

    return msg

def main():
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
                # Lưu lịch sử tối đa 20 phiên
                history.append({"phien": phien, "kq_text": kq_text})
                if len(history) > 20:
                    history.pop(0)

                msg = (
                    f"🎲 Phiên: {phien}\n"
                    f"🎯 Kết quả: {ketqua} = {tong} ⇒ {kq_text}\n"
                    f"📊 Dự đoán tiếp: {du_doan}"
                )
                msg += analyze_history()

                try:
                    bot.send_message(chat_id=CHAT_ID, text=msg)
                    print("✅ Đã gửi phiên:", phien)
                except Exception as e:
                    print("❌ Lỗi gửi Telegram:", e)

                last_phien = phien

        time.sleep(5)

if __name__ == "__main__":
    keep_alive()
    main()
    

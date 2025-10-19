import asyncio
import requests
import logging
from datetime import datetime
from telegram import Bot
from keep_alive import keep_alive
import nest_asyncio
from collections import deque

nest_asyncio.apply()
logging.basicConfig(level=logging.INFO)

# === Cấu hình ===
TOKEN = "8080338995:AAHYQHo0lSry8MupGC0RJt_o8kLbRDiYjQQ"
CHAT_ID = -1002666964512

API_B52 = "https://hitclub-pre.onrender.com/api/taixiu"
API_HITMD5 = "https://hitclub-pre.onrender.com/api/taixiumd5"

bot = Bot(token=TOKEN)

# Biến lưu lịch sử cầu
history_sunwin = deque(maxlen=10)
history_md5 = deque(maxlen=10)
last_phien_sunwin = None
last_phien_md5 = None


# ==== Hàm lấy dữ liệu API ====
def get_api_data(url):
    try:
        res = requests.get(url, timeout=10)
        res.raise_for_status()
        return res.json()
    except Exception as e:
        logging.error(f"Lỗi API {url}: {e}")
        return None


# ==== AI dự đoán cầu theo chuỗi ====
def ai_predict(history):
    if not history:
        return "Không đủ dữ liệu"
    count_tai = history.count("Tài")
    count_xiu = history.count("Xỉu")
    if abs(count_tai - count_xiu) < 2:
        return "Tài" if history[-1] == "Xỉu" else "Xỉu"  # Đảo cầu
    return "Tài" if count_tai > count_xiu else "Xỉu"


# ==== Hàm gửi kết quả ====
async def send_result(api_name, data, history_deque):
    try:
        phien = data.get("Phien") or data.get("phien") or "Không rõ"
        x1, x2, x3 = data.get("Xuc_xac_1"), data.get("Xuc_xac_2"), data.get("Xuc_xac_3")
        tong = data.get("Tong", "?")
        ket_qua = data.get("Ket_qua", "?")

        # Kiểm tra dữ liệu hợp lệ
        if not all([x1, x2, x3, ket_qua != "?"]):
            logging.warning(f"Dữ liệu thiếu cho {api_name}, bỏ qua.")
            return

        # Thêm vào lịch sử cầu
        history_deque.append(ket_qua)
        list_cau = " - ".join(history_deque)
        du_doan = ai_predict(list(history_deque))

        now = datetime.now().strftime("%H:%M:%S")
        text = (
            f"🎯 {api_name}\n"
            f"🕒 Giờ: {now}\n"
            f"📦 Phiên: {phien}\n"
            f"🎲 {x1} | {x2} | {x3} → Tổng: {tong}\n"
            f"🏁 Kết quả: {ket_qua}\n"
            f"📈 Chuỗi gần đây: {list_cau}\n"
            f"🔮 AI dự đoán tiếp theo: {du_doan}"
        )

        await bot.send_message(chat_id=CHAT_ID, text=text)
        logging.info(f"Đã gửi kết quả {api_name} phiên {phien}")

    except Exception as e:
        logging.error(f"Lỗi gửi kết quả {api_name}: {e}")


# ==== Nhiệm vụ gửi kết quả tự động ====
async def auto_send_results():
    global last_phien_sunwin, last_phien_md5

    while True:
        sunwin_data = get_api_data(API_SUNWIN)
        md5_data = get_api_data(API_HITMD5)

        if sunwin_data:
            phien_sunwin = sunwin_data.get("Phien")
            if phien_sunwin and phien_sunwin != last_phien_sunwin:
                last_phien_sunwin = phien_sunwin
                await send_result("b52", sunwin_data, history_sunwin)

        if md5_data:
            phien_md5 = md5_data.get("Phien")
            if phien_md5 and phien_md5 != last_phien_md5:
                last_phien_md5 = phien_md5
                await send_result("HitMD5", md5_data, history_md5)

        await asyncio.sleep(30)


# ==== Khởi động bot ====
async def main():
    keep_alive()
    logging.info("🤖 Bot đang hoạt động và phân tích cầu...")
    await auto_send_results()


if __name__ == "__main__":
    asyncio.run(main())
        

import asyncio
import requests
import logging
from datetime import datetime
from telegram import Bot
from keep_alive import keep_alive
import nest_asyncio
from collections import deque

# --- Cấu hình ---
TOKEN = "8080338995:AAHYQHo0lSry8MupGC0RJt_o8kLbRDiYjQQ"
CHAT_ID = -1002666964512

API_HITTX = "https://hitclub-pre.onrender.com/api/taixiu"
API_HITMD5 = "https://hitclub-pre.onrender.com/api/taixiumd5"

# --- Khởi tạo bot & log ---
bot = Bot(token=TOKEN)
nest_asyncio.apply()
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")

# --- Biến lưu lịch sử cầu ---
history_hit = deque(maxlen=10)
history_md5 = deque(maxlen=10)
last_phien_hit = None
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


# ==== AI dự đoán cầu theo lịch sử ====
def ai_predict(history):
    if not history:
        return "Không đủ dữ liệu"
    count_tai = history.count("Tài")
    count_xiu = history.count("Xỉu")
    if abs(count_tai - count_xiu) < 2:
        # Khi cân bằng → đảo cầu
        return "Tài" if history[-1] == "Xỉu" else "Xỉu"
    # Khi lệch → theo xu hướng
    return "Tài" if count_tai > count_xiu else "Xỉu"


# ==== Tạo biểu đồ cầu đơn giản ====
def draw_cau_chart(history):
    chart = ""
    for kq in history:
        chart += "🔴 " if kq == "Tài" else "🔵 "
    return chart.strip()


# ==== Gửi kết quả ====
async def send_result(api_name, data, history_deque):
    try:
        phien = data.get("Phien") or data.get("phien") or "?"
        x1, x2, x3 = data.get("Xuc_xac_1"), data.get("Xuc_xac_2"), data.get("Xuc_xac_3")
        tong = data.get("Tong", "?")
        ket_qua = data.get("Ket_qua", "?")

        if not all([x1, x2, x3]) or ket_qua == "?":
            logging.warning(f"Dữ liệu thiếu cho {api_name}, bỏ qua.")
            return

        # Cập nhật lịch sử
        history_deque.append(ket_qua)
        list_cau = " - ".join(history_deque)
        du_doan = ai_predict(list(history_deque))
        chart = draw_cau_chart(history_deque)

        now = datetime.now().strftime("%H:%M:%S")
        text = (
            f"🎯 {api_name}\n"
            f"🕒 Giờ: {now}\n"
            f"📦 Phiên: {phien}\n"
            f"🎲 {x1} | {x2} | {x3} → Tổng: {tong}\n"
            f"🏁 Kết quả: {ket_qua}\n"
            f"📈 Chuỗi gần đây: {list_cau}\n"
            f"{chart}\n"
            f"🔮 AI dự đoán tiếp theo: {du_doan}"
        )

        await bot.send_message(chat_id=CHAT_ID, text=text)
        logging.info(f"Đã gửi {api_name} - phiên {phien}")

    except Exception as e:
        logging.error(f"Lỗi gửi kết quả {api_name}: {e}")


# ==== Vòng lặp tự động gửi ====
async def auto_send_results():
    global last_phien_hit, last_phien_md5

    while True:
        try:
            hit_data = get_api_data(API_HITTX)
            md5_data = get_api_data(API_HITMD5)

            if hit_data:
                phien_hit = hit_data.get("Phien")
                if phien_hit and phien_hit != last_phien_hit:
                    last_phien_hit = phien_hit
                    await send_result("🎲 HitTX", hit_data, history_hit)

            if md5_data:
                phien_md5 = md5_data.get("Phien")
                if phien_md5 and phien_md5 != last_phien_md5:
                    last_phien_md5 = phien_md5
                    await send_result("💎 HitMD5", md5_data, history_md5)

        except Exception as e:
            logging.error(f"Lỗi auto_send_results: {e}")

        await asyncio.sleep(30)  # kiểm tra mỗi 30 giây


# ==== Main ====
async def main():
    logging.info("🤖 Bot đang hoạt động và phân tích cầu...")
    await auto_send_results()


# ==== Chạy bot ====
if __name__ == "__main__":
    keep_alive()
    asyncio.run(main())
    

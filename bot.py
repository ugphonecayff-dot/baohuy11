import requests
import asyncio
import matplotlib.pyplot as plt
from telegram import Bot
from keep_alive import keep_alive

# === CONFIG ===
TELEGRAM_TOKEN = "8080338995:AAHYQHo0lSry8MupGC0RJt_o8kLbRDiYjQQ"
CHAT_ID = "-1002666964512"
API_URL = "https://binhtool-b52predict.onrender.com/api/taixiu"

bot = Bot(token=TELEGRAM_TOKEN)
history = []   # lưu kết quả Tài/Xỉu (1 = Tài, 0 = Xỉu)

dice_map = {
    "1": "⚀", "2": "⚁", "3": "⚂",
    "4": "⚃", "5": "⚄", "6": "⚅"
}

# === Gửi tin nhắn ===
async def send_msg(msg):
    try:
        await bot.send_message(chat_id=CHAT_ID, text=msg)
    except Exception as e:
        print("❌ Lỗi gửi Telegram:", e)

# === Gửi biểu đồ ===
async def send_chart():
    if not history:
        return
    try:
        plt.figure(figsize=(8, 4), facecolor="white")
        plt.plot(history, marker="o", color="black", linestyle="-")
        plt.title("Biểu đồ Tài/Xỉu gần đây", color="black")
        plt.xlabel("Phiên", color="black")
        plt.ylabel("Kết quả", color="black")
        plt.grid(True, linestyle="--", alpha=0.5)

        # đổi nhãn trục Y thành Tài/Xỉu
        plt.yticks([0, 1], ["Xỉu", "Tài"])

        # lưu ảnh với nền trắng
        plt.savefig("chart.png", facecolor="white")
        plt.close()

        with open("chart.png", "rb") as img:
            await bot.send_photo(chat_id=CHAT_ID, photo=img)

    except Exception as e:
        print("❌ Lỗi gửi ảnh:", e)

# === Gọi API ===
def get_result():
    try:
        res = requests.get(API_URL, timeout=10)
        if res.status_code == 200:
            return res.json()
    except Exception as e:
        print("❌ API lỗi:", e)
    return None

# === Format kết quả ===
def format_result(data):
    if not data:
        return None

    phien = data.get("phien")
    ketqua = data.get("ketqua")
    tong = data.get("tong")
    kq_text = data.get("kq_text")
    du_doan = data.get("du_doan")

    # nếu thiếu dữ liệu thì bỏ qua
    if not (phien and ketqua and tong and kq_text and du_doan):
        print("⚠️ API trả thiếu dữ liệu, bỏ qua...")
        return None

    icon = "🔴" if kq_text == "Tài" else "🔵"
    dice_parts = ketqua.split("+")
    dice_emojis = " + ".join(dice_map.get(x.strip(), x.strip()) for x in dice_parts)

    msg = (
        f"🆔 Phiên: {phien}\n"
        f"🎲 Xúc xắc: {dice_emojis}\n"
        f"➕ Tổng: {tong} ⇒ {icon} {kq_text}\n"
        f"🔮 Dự đoán tiếp: {du_doan}"
    )
    return msg, phien, kq_text

# === Main loop ===
async def main():
    last_phien = None
    while True:
        data = get_result()
        result = format_result(data)

        if result:
            msg, phien, kq_text = result
            if phien != last_phien:
                history.append(1 if kq_text == "Tài" else 0)
                if len(history) > 20:  # chỉ giữ 20 phiên
                    history.pop(0)

                await send_msg(msg)
                await send_chart()
                print("✅ Đã gửi phiên:", phien)
                last_phien = phien
        else:
            print("⏳ Chưa có dữ liệu mới...")

        await asyncio.sleep(5)

if __name__ == "__main__":
    keep_alive()
    asyncio.run(main())
        

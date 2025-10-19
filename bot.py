import requests
import asyncio
from telegram import Bot, error
from keep_alive import keep_alive

# === CONFIG ===
TELEGRAM_TOKEN = "8080338995:AAHYQHo0lSry8MupGC0RJt_o8kLbRDiYjQQ"
CHAT_ID = "-1002666964512"
API_URL = "https://binhtool-b52predict.onrender.com/api/taixiu"

bot = Bot(token=TELEGRAM_TOKEN)
history = []   # Lưu kết quả Tài/Xỉu (1 = Tài, 0 = Xỉu)

# Emoji xúc xắc
dice_map = {
    1: "⚀", 2: "⚁", 3: "⚂",
    4: "⚃", 5: "⚄", 6: "⚅"
}

# === Gửi tin nhắn ===
async def send_msg(msg: str):
    try:
        await bot.send_message(chat_id=CHAT_ID, text=msg)
        print("📩 Đã gửi tin nhắn vào Telegram")
    except error.TelegramError as e:
        print(f"❌ Lỗi Telegram: {e}")
    except Exception as e:
        print(f"❌ Lỗi khác khi gửi tin nhắn: {e}")

# === Lấy dữ liệu API ===
def get_result():
    try:
        res = requests.get(API_URL, timeout=10)
        if res.status_code == 200:
            data = res.json()
            print("📥 API trả về:", data)  # log để debug
            return data
        else:
            print(f"⚠️ API trả về mã {res.status_code}")
    except Exception as e:
        print("❌ API lỗi:", e)
    return None

# === Tìm chuỗi liên tiếp ===
def find_streak(history):
    if not history:
        return "Chưa có dữ liệu"
    last = history[-1]
    count = 1
    for i in range(len(history) - 2, -1, -1):
        if history[i] == last:
            count += 1
        else:
            break
    return f"🔥 Chuỗi {count} { 'Tài' if last == 1 else 'Xỉu' } liên tiếp"

# === Format dữ liệu API ===
def format_result(data):
    if not data:
        return None

    phien = data.get("phien")
    xx1 = data.get("Xuc_xac_1")
    xx2 = data.get("Xuc_xac_2")
    xx3 = data.get("Xuc_xac_3")
    tong = data.get("Tong")
    ket_qua = data.get("Ket_qua")
    du_doan = data.get("Du_doan")

    if not (phien and xx1 and xx2 and xx3 and tong and ket_qua and du_doan):
        print("⚠️ API trả thiếu dữ liệu, bỏ qua...")
        return None

    icon = "🔴" if ket_qua == "Tài" else "🔵"
    dice_emojis = f"{dice_map.get(xx1, xx1)} + {dice_map.get(xx2, xx2)} + {dice_map.get(xx3, xx3)}"
    streak = find_streak(history + [1 if ket_qua == "Tài" else 0])

    msg = (
        f"🆔 Phiên: {phien}\n"
        f"🎲 Xúc xắc: {dice_emojis}\n"
        f"➕ Tổng: {tong} ⇒ {icon} {ket_qua}\n"
        f"🔮 Dự đoán tiếp: {du_doan}\n"
        f"{streak}"
    )
    return msg, phien, ket_qua

# === Main loop ===
async def main():
    last_phien = None
    while True:
        data = get_result()
        result = format_result(data)

        if result:
            msg, phien, ket_qua = result
            if phien != last_phien:  # chỉ gửi khi có phiên mới
                history.append(1 if ket_qua == "Tài" else 0)
                if len(history) > 30:
                    history.pop(0)

                await send_msg(msg)
                last_phien = phien
        else:
            print("⏳ Chưa có dữ liệu mới...")

        await asyncio.sleep(5)

if __name__ == "__main__":
    keep_alive()
    asyncio.run(main())

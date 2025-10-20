import asyncio
import aiohttp
from telegram import Bot
from keep_alive import keep_alive

# === CONFIG ===
TELEGRAM_TOKEN = "8080338995:AAHYQHo0lSry8MupGC0RJt_o8kLbRDiYjQQ"
CHAT_ID = "-1002666964512"
API_URLS = [
    "https://binhtool-b52predict.onrender.com/api/taixiu",
    "https://b52-taixiu-l69b.onrender.com/api/taixiu"
]

bot = Bot(token=TELEGRAM_TOKEN)
history = []   # lưu lịch sử: 1 = Tài, 0 = Xỉu
ai_total = 0   # tổng số ván dự đoán
ai_correct = 0 # số ván dự đoán đúng

# Emoji xúc xắc
dice_map = {1:"⚀",2:"⚁",3:"⚂",4:"⚃",5:"⚄",6:"⚅"}

# === Gửi text ===
async def send_msg(msg: str):
    try:
        await bot.send_message(chat_id=CHAT_ID, text=msg)
        print(f"✅ Sent: {msg.splitlines()[0]} ...")
    except Exception as e:
        print(f"❌ Lỗi send_msg: {e}")

# === API đa nguồn ===
async def get_result(session: aiohttp.ClientSession, retries: int = 2):
    for url in API_URLS:  # thử từng API
        for attempt in range(1, retries+1):
            try:
                async with session.get(url, timeout=10) as res:
                    if res.status == 200:
                        print(f"🌐 Lấy dữ liệu từ {url}")
                        return await res.json()
                    else:
                        print(f"⚠️ API {url} trả về {res.status}, thử {attempt}/{retries}")
            except Exception as e:
                print(f"❌ Lỗi API {url} ({attempt}/{retries}): {e}")
            await asyncio.sleep(2)
    return None

# === Tìm chuỗi liên tiếp ===
def find_streak(history):
    if not history: return 0, "Chưa có dữ liệu"
    last = history[-1]
    count = 1
    for i in range(len(history)-2,-1,-1):
        if history[i] == last: count += 1
        else: break
    return count, f"🔥 Chuỗi {count} { 'Tài' if last==1 else 'Xỉu'} liên tiếp"

# === AI Dự đoán (logic) ===
def ai_predict(history):
    if not history: 
        return "Ngẫu nhiên"
    streak_count, _ = find_streak(history)
    if streak_count >= 3:
        return "Tài" if history[-1] == 1 else "Xỉu"
    recent = history[-20:]
    tai_ratio = sum(recent)/len(recent)
    return "Tài" if tai_ratio >= 0.5 else "Xỉu"

# === Format kết quả ===
def format_result(data):
    if not data: return None
    phien = data.get("phien")
    xx1,xx2,xx3 = data.get("Xuc_xac_1"),data.get("Xuc_xac_2"),data.get("Xuc_xac_3")
    tong,ket_qua,du_doan_api = data.get("Tong"),data.get("Ket_qua"),data.get("Du_doan")
    if not all([phien,xx1,xx2,xx3,tong,ket_qua,du_doan_api]): return None
    
    icon = "🔴" if ket_qua=="Tài" else "🔵"
    dice = f"{dice_map[xx1]} + {dice_map[xx2]} + {dice_map[xx3]}"
    streak_count, streak_txt = find_streak(history+[1 if ket_qua=="Tài" else 0])
    du_doan_ai = ai_predict(history)
    
    msg = (f"🆔 Phiên: {phien}\n🎲 Xúc xắc: {dice}\n"
           f"➕ Tổng: {tong} ⇒ {icon} {ket_qua}\n"
           f"🔮 Dự đoán API: {du_doan_api}\n"
           f"🤖 Dự đoán AI: {du_doan_ai}\n"
           f"{streak_txt}")
    return msg, phien, ket_qua, du_doan_ai

# === Main loop ===
async def main():
    global ai_total, ai_correct
    last_phien = None
    async with aiohttp.ClientSession() as session:
        while True:
            data = await get_result(session)
            result = format_result(data)
            if result:
                msg, phien, ket_qua, du_doan_ai = result
                if phien != last_phien:
                    # Lưu lịch sử
                    history.append(1 if ket_qua=="Tài" else 0)
                    if len(history) > 50: history.pop(0)

                    # Cập nhật thống kê dự đoán AI
                    if du_doan_ai in ["Tài", "Xỉu"]:
                        ai_total += 1
                        if du_doan_ai == ket_qua:
                            ai_correct += 1
                    acc = (ai_correct / ai_total * 100) if ai_total > 0 else 0

                    # Thêm % chính xác vào tin nhắn
                    msg += f"\n📊 Độ chính xác AI: {ai_correct}/{ai_total} ({acc:.2f}%)"

                    await send_msg(msg)
                    last_phien = phien
            await asyncio.sleep(5)

if __name__=="__main__":
    keep_alive()
    asyncio.run(main())
                    

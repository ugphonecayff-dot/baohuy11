import requests
import asyncio
import random
from telegram import Bot, error
from keep_alive import keep_alive

# === CONFIG ===
TELEGRAM_TOKEN = "8080338995:AAHYQHo0lSry8MupGC0RJt_o8kLbRDiYjQQ"
CHAT_ID = "-1002666964512"
API_URL = "https://binhtool-b52predict.onrender.com/api/taixiu"

bot = Bot(token=TELEGRAM_TOKEN)
history = []

# Emoji xúc xắc
dice_map = {1:"⚀",2:"⚁",3:"⚂",4:"⚃",5:"⚄",6:"⚅"}

# === GIFs & Memes ===

# GIF xúc xắc lăn
GIF_ROLL = [
    "https://media.giphy.com/media/3oEjI6SIIHBdRxXI40/giphy.gif",
    "https://media.giphy.com/media/13CoXDiaCcCoyk/giphy.gif",
]

# GIF Tài / Xỉu
GIF_TAI = [
    "https://media.giphy.com/media/26AHONQ79FdWZhAI0/giphy.gif",
    "https://media.giphy.com/media/l41lFw057lAJQMwg0/giphy.gif",
]
GIF_XIU = [
    "https://media.giphy.com/media/3o7abldj0b3rxrZUxW/giphy.gif",
    "https://media.giphy.com/media/26tPplGWjN0xLybiU/giphy.gif",
]

# GIF Win / Lose
GIF_WIN = [
    "https://media.giphy.com/media/111ebonMs90YLu/giphy.gif",
    "https://media.giphy.com/media/l0MYt5jPR6QX5pnqM/giphy.gif",
]
GIF_LOSE = [
    "https://media.giphy.com/media/9Y5BbDSkSTiY8/giphy.gif",
    "https://media.giphy.com/media/d2lcHJTG5Tscg/giphy.gif",
]

# Meme vui
MEME_FUNNY = [
    "https://i.imgflip.com/30zz5g.jpg",
    "https://i.imgflip.com/4/4acd.jpg",
    "https://i.imgflip.com/1bij.jpg",
    "https://i.imgflip.com/26am.jpg",
]

# Meme buồn
MEME_SAD = [
    "https://i.imgflip.com/1ur9b0.jpg",
    "https://i.imgflip.com/3vzej.jpg",
    "https://i.imgflip.com/2fm6x.jpg",
]

# Meme riêng cho Tài & Xỉu
MEME_TAI = [
    "https://i.imgflip.com/6b8q.jpg",
    "https://i.imgflip.com/7kzog.jpg",
]
MEME_XIU = [
    "https://i.imgflip.com/4acd.jpg",
    "https://i.imgflip.com/3si4.jpg",
]

# Meme cháy cầu 🔥
MEME_CHAIN = [
    "https://i.imgflip.com/4t0m5.jpg",
    "https://i.imgflip.com/28j0te.jpg",
    "https://i.imgflip.com/2wifvo.jpg",
]

# === Gửi text ===
async def send_msg(msg: str):
    try:
        await bot.send_message(chat_id=CHAT_ID, text=msg)
    except Exception as e:
        print(f"❌ Lỗi send_msg: {e}")

# === Gửi media và auto xóa sau 3s ===
async def send_temp_media(url: str, delay: int = 3):
    try:
        if url.endswith(".gif"):
            m = await bot.send_animation(chat_id=CHAT_ID, animation=url)
        else:
            m = await bot.send_photo(chat_id=CHAT_ID, photo=url)
        await asyncio.sleep(delay)
        await bot.delete_message(chat_id=CHAT_ID, message_id=m.message_id)
    except Exception as e:
        print(f"❌ Lỗi send_temp_media: {e}")

# === API ===
def get_result():
    try:
        res = requests.get(API_URL, timeout=10)
        if res.status_code == 200:
            return res.json()
    except Exception as e:
        print("❌ API lỗi:", e)
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

# === Format ===
def format_result(data):
    if not data: return None
    phien = data.get("phien")
    xx1,xx2,xx3 = data.get("Xuc_xac_1"),data.get("Xuc_xac_2"),data.get("Xuc_xac_3")
    tong,ket_qua,du_doan = data.get("Tong"),data.get("Ket_qua"),data.get("Du_doan")
    if not all([phien,xx1,xx2,xx3,tong,ket_qua,du_doan]): return None
    icon = "🔴" if ket_qua=="Tài" else "🔵"
    dice = f"{dice_map[xx1]} + {dice_map[xx2]} + {dice_map[xx3]}"
    streak_count, streak_txt = find_streak(history+[1 if ket_qua=="Tài" else 0])
    msg = (f"🆔 Phiên: {phien}\n🎲 Xúc xắc: {dice}\n"
           f"➕ Tổng: {tong} ⇒ {icon} {ket_qua}\n"
           f"🔮 Dự đoán tiếp: {du_doan}\n{streak_txt}")
    return msg, phien, ket_qua, du_doan, streak_count

# === Main loop ===
async def main():
    last_phien = None
    while True:
        data = get_result()
        result = format_result(data)
        if result:
            msg, phien, ket_qua, du_doan, streak_count = result
            if phien != last_phien:
                history.append(1 if ket_qua=="Tài" else 0)
                if len(history)>30: history.pop(0)

                # Xúc xắc lăn 🎲
                asyncio.create_task(send_temp_media(random.choice(GIF_ROLL)))

                # Tin nhắn kết quả
                await send_msg(msg)

                # GIF theo kết quả
                if ket_qua=="Tài":
                    asyncio.create_task(send_temp_media(random.choice(GIF_TAI)))
                    asyncio.create_task(send_temp_media(random.choice(MEME_TAI)))
                else:
                    asyncio.create_task(send_temp_media(random.choice(GIF_XIU)))
                    asyncio.create_task(send_temp_media(random.choice(MEME_XIU)))

                # Win / Lose meme
                if ket_qua==du_doan:
                    asyncio.create_task(send_temp_media(random.choice(GIF_WIN)))
                    asyncio.create_task(send_temp_media(random.choice(MEME_FUNNY)))
                else:
                    asyncio.create_task(send_temp_media(random.choice(GIF_LOSE)))
                    asyncio.create_task(send_temp_media(random.choice(MEME_SAD)))

                # Meme cháy cầu (nếu >=5)
                if streak_count >= 5:
                    asyncio.create_task(send_temp_media(random.choice(MEME_CHAIN)))

                last_phien = phien
        await asyncio.sleep(5)

if __name__=="__main__":
    keep_alive()
    asyncio.run(main())
    

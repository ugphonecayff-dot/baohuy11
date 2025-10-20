import asyncio
import aiohttp
import json
import os
import random
from collections import defaultdict
from telegram import Bot
from keep_alive import keep_alive

# === CONFIG ===
TELEGRAM_TOKEN = "8080338995:AAHYQHo0lSry8MupGC0RJt_o8kLbRDiYjQQ"
CHAT_ID = "-1002666964512"
API_URL = "https://binhtool-b52predict.onrender.com/api/taixiu"

DATA_DIR = "./data"
MARKOV_FILE = os.path.join(DATA_DIR, "markov.json")
STATS_FILE = os.path.join(DATA_DIR, "stats.json")

bot = Bot(token=TELEGRAM_TOKEN)

# === State ===
history = []            # 1 = Tài, 0 = Xỉu (giữ N recent)
MAX_HISTORY = 200

# AI stats
ai_total = 0
ai_correct = 0

# Pending AI prediction (prediction made for the "next" ván)
# structure: {"prediction": "Tài"/"Xỉu", "base": "Tài"/"Xỉu"} or None
pending_prediction = None

# Emoji xúc xắc (chỉ hiển thị)
dice_map = {1:"⚀",2:"⚁",3:"⚂",4:"⚃",5:"⚄",6:"⚅"}


# === Markov Chain AI Learning ===
class MarkovAI:
    def __init__(self):
        # transitions[state] = {"Tài": count, "Xỉu": count}
        self.transitions = defaultdict(lambda: {"Tài": 0, "Xỉu": 0})

    def update(self, prev_result, current_result):
        """Cập nhật bảng chuyển tiếp prev -> current (prev/current là 'Tài' hoặc 'Xỉu')"""
        if prev_result is None:
            return
        self.transitions[prev_result][current_result] += 1

    def predict(self, last_result):
        """Dự đoán dựa trên last_result (nếu không có dữ liệu => random)"""
        if last_result is None:
            return random.choice(["Tài", "Xỉu"])
        counts = self.transitions.get(last_result)
        if not counts:
            return random.choice(["Tài", "Xỉu"])
        total = counts["Tài"] + counts["Xỉu"]
        if total == 0:
            return random.choice(["Tài", "Xỉu"])
        # Trả về xác suất lớn hơn; nếu bằng thì random theo tỉ lệ
        if counts["Tài"] == counts["Xỉu"]:
            return random.choice(["Tài", "Xỉu"])
        return "Tài" if counts["Tài"] > counts["Xỉu"] else "Xỉu"

    def to_dict(self):
        return dict(self.transitions)

    def load_dict(self, d):
        self.transitions = defaultdict(lambda: {"Tài": 0, "Xỉu": 0})
        for k, v in d.items():
            self.transitions[k] = {"Tài": int(v.get("Tài", 0)), "Xỉu": int(v.get("Xỉu", 0))}


ai_model = MarkovAI()


# === File helpers (async via to_thread) ===
async def ensure_data_dir():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

async def save_markov():
    await ensure_data_dir()
    data = ai_model.to_dict()
    # convert defaultdict -> dict of dicts
    await asyncio.to_thread(lambda: json.dump(data, open(MARKOV_FILE, "w"), indent=2))

async def load_markov():
    if os.path.exists(MARKOV_FILE):
        try:
            data = await asyncio.to_thread(lambda: json.load(open(MARKOV_FILE, "r")))
            ai_model.load_dict(data)
            print("✅ Loaded markov model from", MARKOV_FILE)
        except Exception as e:
            print("⚠️ Không thể load markov file:", e)

async def save_stats():
    await ensure_data_dir()
    s = {"ai_total": ai_total, "ai_correct": ai_correct, "history": history}
    await asyncio.to_thread(lambda: json.dump(s, open(STATS_FILE, "w"), indent=2))

async def load_stats():
    global ai_total, ai_correct, history
    if os.path.exists(STATS_FILE):
        try:
            s = await asyncio.to_thread(lambda: json.load(open(STATS_FILE, "r")))
            ai_total = int(s.get("ai_total", 0))
            ai_correct = int(s.get("ai_correct", 0))
            history = s.get("history", [])
            print("✅ Loaded stats from", STATS_FILE)
        except Exception as e:
            print("⚠️ Không thể load stats file:", e)


# === Telegram send ===
async def send_msg(msg: str):
    try:
        await bot.send_message(chat_id=CHAT_ID, text=msg)
    except Exception as e:
        print("❌ Lỗi send_msg:", e)


# === API request (aiohttp with retries) ===
async def get_result(session: aiohttp.ClientSession, retries: int = 3):
    for attempt in range(1, retries+1):
        try:
            async with session.get(API_URL, timeout=10) as res:
                if res.status == 200:
                    return await res.json()
                else:
                    print(f"⚠️ API trả về {res.status}, thử lại {attempt}/{retries}")
        except Exception as e:
            print(f"❌ API lỗi ({attempt}/{retries}):", e)
        await asyncio.sleep(1 + attempt * 1)
    return None


# === Helpers ===
def find_streak(h):
    if not h: 
        return 0, "Chưa có dữ liệu"
    last = h[-1]
    count = 1
    for i in range(len(h)-2, -1, -1):
        if h[i] == last:
            count += 1
        else:
            break
    return count, f"🔥 Chuỗi {count} {'Tài' if last==1 else 'Xỉu'} liên tiếp"


def format_result_msg(phien, xx1, xx2, xx3, tong, ket_qua, du_doan_api, next_ai_prediction, ai_total_local, ai_correct_local):
    icon = "🔴" if ket_qua == "Tài" else "🔵"
    dice = f"{dice_map.get(xx1,'?')} + {dice_map.get(xx2,'?')} + {dice_map.get(xx3,'?')}"
    streak_count, streak_txt = find_streak(history + [1 if ket_qua == "Tài" else 0])
    acc = (ai_correct_local / ai_total_local * 100) if ai_total_local > 0 else 0.0
    msg = (
        f"🆔 Phiên: {phien}\n"
        f"🎲 Xúc xắc: {dice}\n"
        f"➕ Tổng: {tong} ⇒ {icon} {ket_qua}\n"
        f"🔮 Dự đoán API: {du_doan_api}\n"
        f"🤖 Dự đoán AI (ván tiếp theo): {next_ai_prediction}\n"
        f"{streak_txt}\n"
        f"📊 Độ chính xác AI: {ai_correct_local}/{ai_total_local} ({acc:.2f}%)"
    )
    return msg


# === Main bot loop ===
async def main_loop():
    global ai_total, ai_correct, pending_prediction, history

    await load_markov()
    await load_stats()

    last_phien = None
    last_result = None  # last actual result string "Tài"/"Xỉu" used as base state for Markov

    async with aiohttp.ClientSession() as session:
        while True:
            data = await get_result(session)
            if not data:
                await asyncio.sleep(5)
                continue

            # Read fields from API (adapt if API field names different)
            phien = data.get("phien")
            xx1 = data.get("Xuc_xac_1")
            xx2 = data.get("Xuc_xac_2")
            xx3 = data.get("Xuc_xac_3")
            tong = data.get("Tong")
            ket_qua = data.get("Ket_qua")    # "Tài" or "Xỉu"
            du_doan_api = data.get("Du_doan", "Không có")

            # Skip if some fields missing
            if not all([phien, xx1, xx2, xx3, tong, ket_qua]):
                await asyncio.sleep(3)
                continue

            # Nếu phiên mới (chưa xử lý)
            if phien != last_phien:
                # 1) Nếu có pending_prediction (dự đoán trước cho ván này) -> đánh giá
                if pending_prediction is not None:
                    pred = pending_prediction["prediction"]
                    base = pending_prediction["base"]  # base result when prediction was made
                    ai_total += 1
                    if pred == ket_qua:
                        ai_correct += 1
                    # Cập nhật mô hình Markov: base -> current
                    ai_model.update(base, ket_qua)
                    # clear pending
                    pending_prediction = None
                    # save model & stats (lưu bất kỳ khi nào có update)
                    await save_markov()
                    await save_stats()

                # 2) Thêm result vào history
                history.append(1 if ket_qua == "Tài" else 0)
                if len(history) > MAX_HISTORY:
                    history = history[-MAX_HISTORY:]

                # 3) Tạo dự đoán AI cho **ván tiếp theo** dựa trên kết quả hiện tại
                next_ai_pred = ai_model.predict(ket_qua)
                pending_prediction = {"prediction": next_ai_pred, "base": ket_qua}

                # 4) Lưu last_phien & last_result
                last_phien = phien
                last_result = ket_qua

                # 5) Soạn và gửi message (kết quả hiện tại + dự đoán cho ván tiếp theo + acc)
                msg = format_result_msg(phien, xx1, xx2, xx3, tong, ket_qua, du_doan_api, next_ai_pred, ai_total, ai_correct)
                await send_msg(msg)

            # sleep before next poll
            await asyncio.sleep(5)


# === Entrypoint ===
if __name__ == "__main__":
    keep_alive()   # giữ bot chạy nếu bạn dùng Replit/Glitch...
    try:
        asyncio.run(main_loop())
    except KeyboardInterrupt:
        print("Stopping bot...")
            

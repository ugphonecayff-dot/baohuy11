import requests
import asyncio
from telegram.ext import ApplicationBuilder
import logging
from datetime import datetime
from keep_alive import keep_alive
import nest_asyncio

nest_asyncio.apply()
logging.basicConfig(level=logging.INFO)

# ==== Cấu hình ====
TOKEN = "8080338995:AAHYQHo0lSry8MupGC0RJt_o8kLbRDiYjQQ"
GROUP_CHAT_IDS = [-1002666964512]
CHECK_INTERVAL = 10  # Thời gian kiểm tra (giây)

API_LIST = {
    "Sunwin": "https://hitclub-pre.onrender.com/api/taixiu",
    "HitMD5": "https://hitclub-pre.onrender.com/api/taixiumd5"
}

# ==== Gọi API ====
def call_api(name):
    url = API_LIST.get(name)
    if not url:
        return None
    try:
        r = requests.get(url, timeout=5)
        return r.json()
    except Exception as e:
        logging.error(f"⚠️ Lỗi gọi API {name}: {e}")
        return None


# ==== Định dạng kết quả ====
def format_message(result, name="Sunwin"):
    now = datetime.now().strftime("%H:%M:%S")

    if name == "Sunwin":
        phien = result.get("id", "??")
        dice = result.get("dice", [])
        total = sum(dice) if dice else "??"
        ketqua = result.get("result", "??")
        dice_str = " | ".join(str(d) for d in dice)

        message = (
            f"🎯 *{name}*\n"
            f"🕒 Giờ: {now}\n"
            f"📦 Phiên: `{phien}`\n"
            f"🎲 {dice_str} → Tổng: {total}\n"
            f"🏁 Kết quả: *{ketqua}*"
        )

    elif name == "HitMD5":
        phien = result.get("Phien", "??")
        x1 = result.get("Xuc_xac_1", "?")
        x2 = result.get("Xuc_xac_2", "?")
        x3 = result.get("Xuc_xac_3", "?")
        tong = result.get("Tong", "?")
        ketqua = result.get("Ket_qua", "?")
        du_doan = result.get("du_doan", "?")
        phien_tiep = result.get("phien_hien_tai", "?")

        message = (
            f"🔥 *{name}*\n"
            f"🕒 Giờ: {now}\n"
            f"📦 Phiên: `{phien}`\n"
            f"🎲 {x1} | {x2} | {x3} → Tổng: {tong}\n"
            f"🏁 Kết quả: *{ketqua}*\n"
            f"🔮 Dự đoán tiếp theo: *{du_doan}*\n"
            f"➡️ Phiên kế tiếp: `{phien_tiep}`"
        )

    else:
        message = f"[{name}] Dữ liệu không xác định."

    return message


# ==== Gửi tự động ====
async def auto_send_task(bot_app):
    last_phien = {"Sunwin": 0, "HitMD5": 0}

    while True:
        try:
            for name in ["Sunwin", "HitMD5"]:
                result = call_api(name)
                if not result:
                    continue

                phien = result.get("id") if name == "Sunwin" else result.get("Phien")

                # Gửi nếu là phiên mới
                if last_phien[name] == 0 or phien > last_phien[name]:
                    message = format_message(result, name)
                    for chat_id in GROUP_CHAT_IDS:
                        try:
                            await bot_app.bot.send_message(
                                chat_id=chat_id,
                                text=message,
                                parse_mode="Markdown"
                            )
                        except Exception as e:
                            logging.warning(f"⚠️ Lỗi gửi message cho {chat_id}: {e}")
                    last_phien[name] = phien
                    logging.info(f"[{name}] ✅ Gửi phiên {phien} thành công")

        except Exception as e:
            logging.error(f"❌ Lỗi task auto-send: {e}")

        await asyncio.sleep(CHECK_INTERVAL)


# ==== Khởi động bot ====
async def main():
    keep_alive()
    bot_app = ApplicationBuilder().token(TOKEN).build()
    asyncio.create_task(auto_send_task(bot_app))
    logging.info("🤖 Bot đang chạy & tự động gửi kết quả Tài Xỉu...")
    await bot_app.run_polling()


if __name__ == "__main__":
    asyncio.run(main())
    

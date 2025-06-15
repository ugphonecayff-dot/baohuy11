import telebot
import openai
from keep_alive import keep_alive
import logging
import time

# === THÔNG TIN BẢO MẬT ===
TELEGRAM_TOKEN = '6367532329:AAGJh1RnIa-UZGBUdzKHTy3lyKnB81NdqjM'
OPENAI_API_KEY = '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'

# === KHỞI TẠO BOT & OPENAI ===
bot = telebot.TeleBot(TELEGRAM_TOKEN)
client = openai.OpenAI(api_key=OPENAI_API_KEY)

# === KÍCH HOẠT KEEP ALIVE ===
keep_alive()

# === CẤU HÌNH GHI LOG ===
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s - %(message)s')

# === THEO DÕI UPTIME ===
start_time = time.time()

def get_uptime():
    elapsed = int(time.time() - start_time)
    hours, remainder = divmod(elapsed, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"⏱ Uptime: {hours}h {minutes}m {seconds}s"

# === XỬ LÝ LỆNH ===
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "🤖 Xin chào! Tôi là trợ lý AI sử dụng GPT-4.\n\nGõ bất kỳ nội dung nào để tôi trả lời bạn.\n\nLệnh hỗ trợ:\n/start hoặc /help - Giới thiệu bot\n/uptime - Xem thời gian hoạt động của bot")

@bot.message_handler(commands=['uptime'])
def send_uptime(message):
    bot.reply_to(message, get_uptime())

# === XỬ LÝ CÂU HỎI NGƯỜI DÙNG ===
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    logging.info(f"Người dùng: {message.from_user.username} | Nội dung: {message.text}")
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": message.text}]
        )
        reply = response.choices[0].message.content
        bot.reply_to(message, reply)
    except Exception as e:
        logging.error(f"Lỗi xử lý: {e}")
        bot.reply_to(message, f"⚠️ Đã xảy ra lỗi:\n\n{e}")

# === CHẠY BOT ===
logging.info("🤖 Bot Telegram AI đang chạy với GPT-4...")
bot.infinity_polling(timeout=10, long_polling_timeout=5)

# main.py
from telegram import Update, InputFile
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from openai import OpenAI
from keep_alive import keep_alive
import base64
import json
import os

# ========== CONFIG ==========
TELEGRAM_TOKEN = "6367532329:AAGJh1RnIa-UZGBUdzKHTy3lyKnB81NdqjM"
ADMIN_USER_ID = 5736655322

OPENAI_API_KEYS = [
    "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",
    "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"
]

# ========== GIẢI MÃ ==========
def is_base64(s):
    try:
        return base64.b64encode(base64.b64decode(s)).decode() == s
    except:
        return False

def is_hex(s):
    try:
        bytes.fromhex(s)
        return True
    except:
        return False

def try_json(s):
    try:
        return json.loads(s)
    except:
        return None

def decode_languagemap(encoded_str):
    decoded_str = ""
    parsed_data = None

    if is_base64(encoded_str):
        try:
            decoded_str = base64.b64decode(encoded_str).decode('utf-8')
        except Exception:
            return "❌ Lỗi giải mã Base64.", None
    elif is_hex(encoded_str):
        try:
            decoded_str = bytes.fromhex(encoded_str).decode('utf-8')
        except Exception:
            return "❌ Lỗi giải mã Hex.", None
    else:
        decoded_str = encoded_str

    if decoded_str.startswith("languagemap:"):
        decoded_str = decoded_str[len("languagemap:"):].strip()

    parsed_data = try_json(decoded_str)
    if parsed_data:
        return (
            f"✅ Giải mã thành công!\n\n<pre>{json.dumps(parsed_data, indent=2, ensure_ascii=False)}</pre>",
            parsed_data
        )
    else:
        return f"📄 Chuỗi giải mã:\n<pre>{decoded_str}</pre>", None

# ========== CHATGPT ==========
async def ask_chatgpt(prompt, context=None):
    global OPENAI_API_KEYS
    last_error = None

    for key in OPENAI_API_KEYS.copy():
        try:
            client = OpenAI(api_key=key)
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=1000
            )
            return response.choices[0].message.content.strip()

        except Exception as e:
            last_error = str(e)

            if context:
                await context.bot.send_message(
                    chat_id=ADMIN_USER_ID,
                    text=f"⚠️ API Key lỗi:\n{key[:25]}...\n\nLỗi: {last_error}"
                )

            OPENAI_API_KEYS.remove(key)

    return f"❌ Tất cả API key đều lỗi.\nChi tiết lỗi cuối: {last_error}"

# ========== TELEGRAM HANDLERS ==========
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    await update.message.reply_text(f"👋 Xin chào! ID của bạn là: {user_id}")

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()

    result, parsed = decode_languagemap(text)

    if parsed:
        await update.message.reply_text(result, parse_mode='HTML')
        with open("decoded.json", "w", encoding="utf-8") as f:
            json.dump(parsed, f, indent=2, ensure_ascii=False)
        await update.message.reply_document(InputFile("decoded.json"))
        os.remove("decoded.json")
    else:
        await update.message.reply_text("🤖 Đang xử lý yêu cầu của bạn...")
        reply = await ask_chatgpt(text, context)
        await update.message.reply_text(reply)

async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file = update.message.document
    if file.mime_type not in ['application/json', 'text/plain']:
        await update.message.reply_text("⚠️ Chỉ hỗ trợ file .json hoặc .txt")
        return

    file_obj = await file.get_file()
    temp_path = await file_obj.download_to_drive()

    with open(temp_path, 'r', encoding='utf-8') as f:
        content = f.read()

    result, parsed = decode_languagemap(content)
    await update.message.reply_text(result, parse_mode='HTML')

    if parsed:
        with open("decoded.json", "w", encoding="utf-8") as f:
            json.dump(parsed, f, indent=2, ensure_ascii=False)
        await update.message.reply_document(InputFile("decoded.json"))
        os.remove("decoded.json")

    os.remove(temp_path)

# ========== MAIN ==========
if __name__ == "__main__":
    keep_alive()
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.add_handler(MessageHandler(filters.Document.ALL, handle_file))

    print("🤖 Bot đang chạy...")
    app.run_polling()

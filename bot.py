import base64
import json
import os
import openai
from telegram import Update, InputFile
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from keep_alive import keep_alive  # Gọi server keep-alive

# ========== CONFIG ==========
TELEGRAM_TOKEN = "6367532329:AAGJh1RnIa-UZGBUdzKHTy3lyKnB81NdqjM"
OPENAI_API_KEY = "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"
openai.api_key = OPENAI_API_KEY

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
async def ask_chatgpt(prompt):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=1000
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"❌ Lỗi ChatGPT: {str(e)}"

# ========== HANDLER ==========
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Gửi tôi chuỗi mã hóa để giải mã, hoặc đặt câu hỏi để tôi hỏi AI!")

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
        await update.message.reply_text("🤖 Đang hỏi ChatGPT...")
        reply = await ask_chatgpt(text)
        await update.message.reply_text(reply)

async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file = update.message.document
    if file.mime_type not in ['application/json', 'text/plain']:
        await update.message.reply_text("⚠️ Chỉ hỗ trợ file .json hoặc .txt")
        return

    file_obj = await file.get_file()
    temp = await file_obj.download_to_drive()
    
    with open(temp.name, 'r', encoding='utf-8') as f:
        content = f.read()

    result, parsed = decode_languagemap(content)
    await update.message.reply_text(result, parse_mode='HTML')

    if parsed:
        with open("decoded.json", "w", encoding="utf-8") as f:
            json.dump(parsed, f, indent=2, ensure_ascii=False)
        await update.message.reply_document(InputFile("decoded.json"))
        os.remove("decoded.json")
    
    os.remove(temp.name)

# ========== CHẠY BOT ==========
if __name__ == "__main__":
    keep_alive()
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.add_handler(MessageHandler(filters.Document.ALL, handle_file))

    print("🤖 Bot đang chạy...")
    app.run_polling()

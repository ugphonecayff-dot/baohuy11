from pyrogram import Client, filters
from pyrogram.types import Message
from dotenv import load_dotenv
import requests
import os
import time

# Load biến môi trường từ file .env
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Khởi tạo bot
app = Client("HoangDaiXuBot", bot_token=BOT_TOKEN)

# Thời gian khởi động bot
start_time = time.time()

# Lệnh /start
@app.on_message(filters.command("start"))
async def start(client, message: Message):
    await message.reply("🤖 Bot Bảo Huy 👨‍💻 Xứ sẵn sàng phục vụ!\nDùng /help để xem danh sách lệnh.")

# Lệnh /help
@app.on_message(filters.command("help"))
async def help_command(client, message: Message):
    await message.reply(
        "**📜 Danh sách lệnh:**\n"
        "/uid [url fb]\n/postid [url fb]\n/2fa [mã chữ]\n"
        "/shareao [uid] [cookies]\n/tiktok1 [username]\n/tiktok2 [username]\n"
        "/videott1 [url]\n/videott2 [url]\n"
        "/folow1 [username]\n/folow2 [username]\n/folow3 [username]\n"
        "/like [url]\n/view [url]\n"
        "/insta [username]\n/zalo [sdt]\n"
        "/cccd\n/passport\n/uptime"
    )

# Hàm tiện ích gửi request và trả kết quả
async def send_api_response(message: Message, url: str):
    try:
        res = requests.get(url)
        await message.reply(res.text)
    except Exception as e:
        await message.reply(f"❌ Lỗi: {e}")

# UID
@app.on_message(filters.command("uid"))
async def get_uid(client, message: Message):
    if len(message.command) < 2:
        return await message.reply("❌ Nhập URL Facebook.")
    await send_api_response(message, f"https://example.com/facebook-uid?url={message.command[1]}")

# PostID
@app.on_message(filters.command("postid"))
async def post_id(client, message: Message):
    if len(message.command) < 2:
        return await message.reply("❌ Nhập URL bài viết.")
    await send_api_response(message, f"https://hoangdaixu.x10.bz/api/getpostfb.php?key=hoangdaixu&url={message.command[1]}")

# 2FA
@app.on_message(filters.command("2fa"))
async def to_2fa(client, message: Message):
    code = " ".join(message.command[1:])
    try:
        res = requests.post("https://hoangdaixu.x10.bz/api/to2fa.php?key=hoangdaixuhoangdaixu", data={"code": code})
        await message.reply(res.text)
    except Exception as e:
        await message.reply(f"❌ Lỗi: {e}")

# Share ảo
@app.on_message(filters.command("shareao"))
async def share_ao(client, message: Message):
    try:
        uid = message.command[1]
        cookies = message.command[2]
        await send_api_response(message, f"https://hoangdaixu.x10.bz/api/api-shareao.php?cookies={cookies}&uid={uid}")
    except:
        await message.reply("❌ Nhập dạng: /shareao uid cookies")

# TikTok info
@app.on_message(filters.command(["tiktok1", "tiktok2"]))
async def tiktok_info(client, message: Message):
    if len(message.command) < 2:
        return await message.reply("❌ Nhập username TikTok.")
    username = message.command[1]
    api = "infotiktok.php" if message.command[0] == "tiktok1" else "infotiktokv2.php"
    await send_api_response(message, f"https://hoangdaixu.x10.bz/api/{api}?key=hoangdaixu&username={username}")

# TikTok video
@app.on_message(filters.command(["videott1", "videott2"]))
async def tiktok_video(client, message: Message):
    if len(message.command) < 2:
        return await message.reply("❌ Nhập URL video TikTok.")
    url = message.command[1]
    api = "infovideott.php" if message.command[0] == "videott1" else "infovdttv2.php"
    await send_api_response(message, f"https://hoangdaixu.x10.bz/api/{api}?key=hoangdaixu&urlvideo={url}")

# Follow TikTok
@app.on_message(filters.command(["folow1", "folow2", "folow3"]))
async def follow_tiktok(client, message: Message):
    if len(message.command) < 2:
        return await message.reply("❌ Nhập username.")
    username = message.command[1]
    if message.command[0] == "folow1":
        url = f"https://hoangdaixu.x10.bz/api/autofl.php?key=dinhhoang&username={username}"
    elif message.command[0] == "folow2":
        url = f"https://hoangdaixu.x10.bz/api/autofl2.php?key=dinhhoang&username={username}"
    else:
        url = f"https://hoangdaixu.x10.bz/api/dinhhoang.php?key=toladinhhoang&username={username}"
    await send_api_response(message, url)

# Like & View
@app.on_message(filters.command(["like", "view"]))
async def like_view(client, message: Message):
    if len(message.command) < 2:
        return await message.reply("❌ Nhập URL.")
    type_ = message.command[0]
    url = f"https://hoangdaixu.x10.bz/api/cronview.php?key=hoangdaixu&link={message.command[1]}&type={type_}"
    await send_api_response(message, url)

# Instagram
@app.on_message(filters.command("insta"))
async def insta(client, message: Message):
    if len(message.command) < 2:
        return await message.reply("❌ Nhập username Instagram.")
    await send_api_response(message, f"https://hoangdaixu.x10.bz/api/infoins.php?key=hoangdaixu&username={message.command[1]}")

# Zalo
@app.on_message(filters.command("zalo"))
async def zalo(client, message: Message):
    if len(message.command) < 2:
        return await message.reply("❌ Nhập số điện thoại.")
    await send_api_response(message, f"https://hoangdaixu.x10.bz/api/zalo.php?key=hoangdaixu&sdt={message.command[1]}")

# CCCD & Passport
@app.on_message(filters.command("cccd"))
async def cccd(client, message: Message):
    await message.reply("🔖 Tạo CCCD ảo tại:\nhttps://hoangdaixu.x10.bz/cccd/")

@app.on_message(filters.command("passport"))
async def passport(client, message: Message):
    await message.reply("🛂 Tạo hộ chiếu ảo tại:\nhttps://hoangdaixu.x10.bz/passport/")

# Uptime
@app.on_message(filters.command("uptime"))
async def uptime(client, message: Message):
    uptime_seconds = int(time.time() - start_time)
    h, m, s = uptime_seconds // 3600, (uptime_seconds % 3600) // 60, uptime_seconds % 60
    await message.reply(f"⏱ Bot đã hoạt động: {h} giờ {m} phút {s} giây.")

# Khởi động bot
app.run()

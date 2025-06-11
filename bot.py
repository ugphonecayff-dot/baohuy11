from pyrogram import Client, filters
from pyrogram.types import Message
import requests
import time
import os
import logging
from keep_alive import keep_alive
from dotenv import load_dotenv

# Load biến môi trường
load_dotenv()

# Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Token bot
BOT_TOKEN = os.getenv("6367532329:AAEuSSv8JuGKzJQD6qI431udTvdq1l25zo0")
if not BOT_TOKEN:
    raise ValueError("❌ Bạn chưa thiết lập biến môi trường BOT_TOKEN")

# Khởi động web server để giữ bot sống (nếu cần)
keep_alive()

# Khởi tạo client
app = Client("HoangDaiXuBot", bot_token=BOT_TOKEN)

# Thời gian khởi động bot
start_time = time.time()

# /start
@app.on_message(filters.command("start"))
async def start(client, message: Message):
    await message.reply("🤖 Bot Bảo Huy 👨‍💻 Xứ sẵn sàng phục vụ!\nDùng /help để xem danh sách lệnh.")

# /help
@app.on_message(filters.command("help"))
async def help_command(client, message: Message):
    await message.reply(
        "**📜 Danh sách lệnh:**\n"
        "/uid [url fb]\n"
        "/postid [url fb]\n"
        "/2fa [mã chữ]\n"
        "/shareao [uid] [cookies]\n"
        "/tiktok1 [username]\n"
        "/tiktok2 [username]\n"
        "/videott1 [url]\n"
        "/videott2 [url]\n"
        "/folow1 [username]\n"
        "/folow2 [username]\n"
        "/folow3 [username]\n"
        "/like [url]\n"
        "/view [url]\n"
        "/insta [username]\n"
        "/zalo [sdt]\n"
        "/cccd\n"
        "/passport\n"
        "/uptime"
    )

# Hàm tiện ích gọi API có xử lý lỗi
def safe_request(method, url, **kwargs):
    try:
        res = requests.request(method, url, **kwargs)
        return res.text
    except Exception as e:
        logging.error(f"Lỗi khi gọi API {url}: {e}")
        return f"⚠️ Lỗi khi gọi API: {e}"

# Các lệnh xử lý API
@app.on_message(filters.command("uid"))
async def get_uid(client, message: Message):
    if len(message.command) < 2:
        return await message.reply("❌ Vui lòng nhập URL Facebook.")
    url = message.command[1]
    await message.reply(safe_request("GET", f"https://example.com/facebook-uid?url={url}"))

@app.on_message(filters.command("postid"))
async def post_id(client, message: Message):
    if len(message.command) < 2:
        return await message.reply("❌ Nhập URL bài viết.")
    url = message.command[1]
    await message.reply(safe_request("GET", f"https://hoangdaixu.x10.bz/api/getpostfb.php?key=hoangdaixu&url={url}"))

@app.on_message(filters.command("2fa"))
async def to_2fa(client, message: Message):
    if len(message.command) < 2:
        return await message.reply("❌ Nhập mã 2FA.")
    code = " ".join(message.command[1:])
    await message.reply(safe_request("POST", "https://hoangdaixu.x10.bz/api/to2fa.php?key=hoangdaixuhoangdaixu", data={"code": code}))

@app.on_message(filters.command("shareao"))
async def share_ao(client, message: Message):
    if len(message.command) < 3:
        return await message.reply("❌ Nhập dạng: /shareao uid cookies")
    uid = message.command[1]
    cookies = message.command[2]
    await message.reply(safe_request("GET", f"https://hoangdaixu.x10.bz/api/api-shareao.php?cookies={cookies}&uid={uid}"))

@app.on_message(filters.command("tiktok1"))
async def tiktok1(client, message: Message):
    if len(message.command) < 2:
        return await message.reply("❌ Nhập username TikTok.")
    username = message.command[1]
    await message.reply(safe_request("GET", f"https://hoangdaixu.x10.bz/api/infotiktok.php?key=hoangdaixu&username={username}"))

@app.on_message(filters.command("tiktok2"))
async def tiktok2(client, message: Message):
    if len(message.command) < 2:
        return await message.reply("❌ Nhập username TikTok.")
    username = message.command[1]
    await message.reply(safe_request("GET", f"https://hoangdaixu.x10.bz/api/infotiktokv2.php?key=hoangdaixu&username={username}"))

@app.on_message(filters.command("videott1"))
async def video_tt1(client, message: Message):
    if len(message.command) < 2:
        return await message.reply("❌ Nhập URL video TikTok.")
    url = message.command[1]
    await message.reply(safe_request("GET", f"https://hoangdaixu.x10.bz/api/infovideott.php?key=hoangdaixu&urlvideo={url}"))

@app.on_message(filters.command("videott2"))
async def video_tt2(client, message: Message):
    if len(message.command) < 2:
        return await message.reply("❌ Nhập URL video TikTok.")
    url = message.command[1]
    await message.reply(safe_request("GET", f"https://hoangdaixu.x10.bz/api/infovdttv2.php?key=hoangdaixu&urlvideo={url}"))

@app.on_message(filters.command("folow1"))
async def follow1(client, message: Message):
    if len(message.command) < 2:
        return await message.reply("❌ Nhập username.")
    username = message.command[1]
    await message.reply(safe_request("GET", f"https://hoangdaixu.x10.bz/api/autofl.php?key=dinhhoang&username={username}"))

@app.on_message(filters.command("folow2"))
async def follow2(client, message: Message):
    if len(message.command) < 2:
        return await message.reply("❌ Nhập username.")
    username = message.command[1]
    await message.reply(safe_request("GET", f"https://hoangdaixu.x10.bz/api/autofl2.php?key=dinhhoang&username={username}"))

@app.on_message(filters.command("folow3"))
async def follow3(client, message: Message):
    if len(message.command) < 2:
        return await message.reply("❌ Nhập username.")
    username = message.command[1]
    await message.reply(safe_request("GET", f"https://hoangdaixu.x10.bz/api/dinhhoang.php?key=toladinhhoang&username={username}"))

@app.on_message(filters.command("like"))
async def like(client, message: Message):
    if len(message.command) < 2:
        return await message.reply("❌ Nhập link video.")
    url = message.command[1]
    await message.reply(safe_request("GET", f"https://hoangdaixu.x10.bz/api/cronview.php?key=hoangdaixu&link={url}&type=like"))

@app.on_message(filters.command("view"))
async def view(client, message: Message):
    if len(message.command) < 2:
        return await message.reply("❌ Nhập link video.")
    url = message.command[1]
    await message.reply(safe_request("GET", f"https://hoangdaixu.x10.bz/api/cronview.php?key=hoangdaixu&link={url}&type=view"))

@app.on_message(filters.command("insta"))
async def insta(client, message: Message):
    if len(message.command) < 2:
        return await message.reply("❌ Nhập username Instagram.")
    username = message.command[1]
    await message.reply(safe_request("GET", f"https://hoangdaixu.x10.bz/api/infoins.php?key=hoangdaixu&username={username}"))

@app.on_message(filters.command("zalo"))
async def zalo(client, message: Message):
    if len(message.command) < 2:
        return await message.reply("❌ Nhập số điện thoại.")
    sdt = message.command[1]
    await message.reply(safe_request("GET", f"https://hoangdaixu.x10.bz/api/zalo.php?key=hoangdaixu&sdt={sdt}"))

# CCCD & Passport
@app.on_message(filters.command("cccd"))
async def cccd(client, message: Message):
    await message.reply("🔖 Tạo CCCD ảo tại:\nhttps://hoangdaixu.x10.bz/cccd/")

@app.on_message(filters.command("passport"))
async def passport(client, message: Message):
    await message.reply("🛂 Tạo hộ chiếu ảo tại:\nhttps://hoangdaixu.x10.bz/passport/")

@app.on_message(filters.command("uptime"))
async def uptime(client, message: Message):
    uptime_seconds = int(time.time() - start_time)
    hours, remainder = divmod(uptime_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    await message.reply(f"⏱ Bot đã hoạt động: {hours} giờ {minutes} phút {seconds} giây.")

# Chạy bot
app.run()

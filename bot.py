import os
import zipfile
import shutil
import subprocess
import logging
import urllib.request
import tarfile
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from keep_alive import keep_alive

# === ✅ Cấu hình BOT ===
BOT_TOKEN = "6367532329:AAGJh1RnIa-UZGBUdzKHTy3lyKnB81NdqjM"

# === ✅ Cấu hình logging ===
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# === ✅ Hàm tự động setup Theos + SDK + Toolchain ===
def setup_theos():
    home_dir = os.path.expanduser("~")
    theos_path = os.path.join(home_dir, "theos")
    sdk_path = os.path.join(theos_path, "sdks", "iPhoneOS14.5.sdk")
    toolchain_bin = os.path.join(theos_path, "toolchain", "bin", "arm64-apple-darwin14-clang")

    print("🛠️ Đang kiểm tra & setup Theos...")

    # ✅ Clone repo nếu chưa có
    if not os.path.exists(os.path.join(theos_path, "make")):
        print("📦 Đang clone Theos...")
        subprocess.run(["git", "clone", "--recursive", "https://github.com/theos/theos.git", theos_path], check=True)
        subprocess.run(["git", "clone", "https://github.com/theos/sdks.git"], cwd=theos_path, check=True)
        subprocess.run(["git", "clone", "https://github.com/theos/lib.git"], cwd=theos_path, check=True)
        subprocess.run(["git", "clone", "https://github.com/theos/vendor.git"], cwd=theos_path, check=True)

    # ✅ Tải SDK nếu chưa có
    if not os.path.exists(sdk_path):
        print("📥 Đang tải iPhoneOS14.5.sdk...")
        try:
            os.makedirs(os.path.dirname(sdk_path), exist_ok=True)
            sdk_url = "https://github.com/theos/sdks/releases/download/latest/iPhoneOS14.5.sdk.tar.xz"
            sdk_tar = os.path.join(theos_path, "sdks", "iPhoneOS14.5.sdk.tar.xz")
            urllib.request.urlretrieve(sdk_url, sdk_tar)
            with tarfile.open(sdk_tar, "r:xz") as tar:
                tar.extractall(path=os.path.join(theos_path, "sdks"))
            os.remove(sdk_tar)
            print("✅ SDK đã được tải và giải nén.")
        except Exception as e:
            print(f"❌ Lỗi tải SDK: {e}")

    # ✅ Build toolchain nếu chưa có
    if not os.path.isfile(toolchain_bin):
        print("🔧 Đang build toolchain ARM...")
        try:
            subprocess.run(["make", "-C", os.path.join(theos_path, "toolchain")], check=True)
            print("✅ Toolchain ARM build thành công.")
        except subprocess.CalledProcessError as e:
            print(f"❌ Lỗi build toolchain: {e}")
    else:
        print("✅ Toolchain đã tồn tại.")

# === ✅ /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤖 Xin chào!\nGửi mình file `.zip` chứa Theos tweak project để mình build `.deb` cho bạn.")

# === ✅ Hàm build tweak
def build_theos_project(path: str) -> str:
    try:
        build_output = subprocess.check_output(
            ["make", "clean", "package"],
            cwd=path,
            stderr=subprocess.STDOUT,
            env=dict(os.environ, THEOS=os.path.expanduser("~/theos"))
        ).decode()

        for root, dirs, files in os.walk(path):
            for file in files:
                if file.endswith(".deb"):
                    return os.path.join(root, file)
        return "BUILD_OK_NO_DEB"

    except subprocess.CalledProcessError as e:
        error_path = os.path.join(path, "build_error.txt")
        with open(error_path, "w") as f:
            f.write(e.output.decode())
        return error_path

# === ✅ Xử lý file .zip
async def handle_zip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file = await update.message.document.get_file()
    file_name = update.message.document.file_name
    zip_path = f"uploads/{file_name}"

    os.makedirs("uploads", exist_ok=True)
    await file.download_to_drive(zip_path)

    try:
        extract_dir = zip_path.replace(".zip", "")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)

        if not os.path.exists(os.path.join(extract_dir, "Makefile")):
            await update.message.reply_text("❌ Không tìm thấy Makefile. Đây không phải project Theos hợp lệ.")
            return

        result = build_theos_project(extract_dir)

        if result.endswith(".deb"):
            await update.message.reply_text("✅ Build xong! Đây là file `.deb` của bạn:")
            await update.message.reply_document(document=open(result, "rb"))
        elif result.endswith(".txt"):
            await update.message.reply_text("❌ Build lỗi! Dưới đây là log lỗi:")
            await update.message.reply_document(document=open(result, "rb"))
        else:
            await update.message.reply_text("✅ Build xong nhưng không tìm thấy file `.deb`.")

    except Exception as e:
        await update.message.reply_text(f"❌ Lỗi xử lý file: {e}")
    finally:
        os.remove(zip_path)
        shutil.rmtree(extract_dir, ignore_errors=True)

# === ✅ Chạy bot
def main():
    keep_alive()
    setup_theos()

    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.Document.ZIP, handle_zip))

    print("🤖 Bot Theos Builder đang chạy...")
    app.run_polling()

if __name__ == "__main__":
    main()

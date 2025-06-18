import os
import zipfile
import shutil
import subprocess
import logging
import urllib.request
import tarfile

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from keep_alive import keep_alive  # Nếu chạy trên Replit hoặc Web server

# === CẤU HÌNH ===
BOT_TOKEN = "6367532329:AAGJh1RnIa-UZGBUdzKHTy3lyKnB81NdqjM"
ADMIN_ID = 5736655322  # 👑 ID Telegram của bạn (chỉ bạn được dùng /setup)
THEOS_DIR = os.path.expanduser("~/theos")
TOOLCHAIN_BIN = os.path.join(THEOS_DIR, "toolchain", "bin", "arm64-apple-darwin14-clang")
SDK_PATH = os.path.join(THEOS_DIR, "sdks", "iPhoneOS14.5.sdk")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# === CLONE GIT AN TOÀN ===
def safe_clone(repo_url, dest):
    if os.path.exists(dest):
        print(f"✅ Repo tồn tại: {dest}")
        return
    try:
        subprocess.run(["git", "clone", repo_url, dest], check=True)
        print(f"✅ Cloned: {repo_url}")
    except subprocess.CalledProcessError as e:
        print(f"❌ Lỗi clone {repo_url}: {e}")

# === SETUP THEOS ===
def setup_theos():
    print("🛠️ Bắt đầu cài đặt Theos...")
    if not os.path.exists(os.path.join(THEOS_DIR, "make")):
        safe_clone("https://github.com/theos/theos.git", THEOS_DIR)

    safe_clone("https://github.com/theos/sdks.git", os.path.join(THEOS_DIR, "sdks"))
    safe_clone("https://github.com/theos/lib.git", os.path.join(THEOS_DIR, "lib"))
    safe_clone("https://github.com/theos/vendor.git", os.path.join(THEOS_DIR, "vendor"))
    safe_clone("https://github.com/theos/toolchain.git", os.path.join(THEOS_DIR, "toolchain"))

    if not os.path.exists(SDK_PATH):
        print("📥 Đang tải iPhoneOS14.5.sdk...")
        try:
            sdk_url = "https://github.com/theos/sdks/releases/download/latest/iPhoneOS14.5.sdk.tar.xz"
            sdk_tar = os.path.join(THEOS_DIR, "sdks", "iPhoneOS14.5.sdk.tar.xz")
            urllib.request.urlretrieve(sdk_url, sdk_tar)
            with tarfile.open(sdk_tar, "r:xz") as tar:
                tar.extractall(path=os.path.join(THEOS_DIR, "sdks"))
            os.remove(sdk_tar)
            print("✅ Đã tải & giải nén SDK.")
        except Exception as e:
            print(f"❌ Lỗi tải SDK: {e}")

    if not os.path.isfile(TOOLCHAIN_BIN):
        print("🔧 Đang build toolchain...")
        try:
            subprocess.run(["make", "-C", os.path.join(THEOS_DIR, "toolchain")], check=True)
            print("✅ Build toolchain thành công.")
        except subprocess.CalledProcessError as e:
            print(f"❌ Lỗi build toolchain: {e}")
    else:
        print("✅ Toolchain đã sẵn sàng.")

# === /start ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤖 Gửi file `.zip` chứa Theos tweak. Mình sẽ build thành `.deb` cho bạn!")

# === /setup ===
async def setup_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("⛔ Bạn không có quyền dùng lệnh này.")
        return

    await update.message.reply_text("🛠️ Đang cài đặt Theos, vui lòng chờ...")
    try:
        setup_theos()
        await update.message.reply_text("✅ Setup Theos hoàn tất.")
    except Exception as e:
        await update.message.reply_text(f"❌ Lỗi setup: {e}")

# === BUILD TWEAK ===
def build_theos_project(path: str) -> str:
    try:
        subprocess.check_output(
            ["make", "clean", "package"],
            cwd=path,
            stderr=subprocess.STDOUT,
            env=dict(os.environ, THEOS=THEOS_DIR)
        )

        for root, dirs, files in os.walk(path):
            for file in files:
                if file.endswith(".deb"):
                    return os.path.join(root, file)

        return "BUILD_OK_NO_DEB"
    except subprocess.CalledProcessError as e:
        error_file = os.path.join(path, "build_error.txt")
        with open(error_file, "w") as f:
            f.write(e.output.decode())
        return error_file

# === XỬ LÝ FILE ZIP ===
async def handle_zip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file = await update.message.document.get_file()
    filename = update.message.document.file_name
    zip_path = f"uploads/{filename}"
    extract_path = zip_path.replace(".zip", "")

    os.makedirs("uploads", exist_ok=True)
    await file.download_to_drive(zip_path)

    await update.message.reply_text("🔧 Đang xử lý và build tweak của bạn, vui lòng chờ...")

    try:
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(extract_path)

        if not os.path.exists(os.path.join(extract_path, "Makefile")):
            await update.message.reply_text("❌ Không tìm thấy Makefile. Không phải Theos project.")
            return

        result = build_theos_project(extract_path)

        if result.endswith(".deb"):
            await update.message.reply_text("✅ Build thành công! Dưới đây là file .deb của bạn:")
            await update.message.reply_document(document=open(result, "rb"))
        elif result.endswith(".txt"):
            await update.message.reply_text("❌ Build lỗi! Gửi lại log lỗi:")
            await update.message.reply_document(document=open(result, "rb"))
        else:
            await update.message.reply_text("✅ Build xong nhưng không thấy file .deb.")

    except Exception as e:
        await update.message.reply_text(f"❌ Lỗi xử lý file: {e}")
    finally:
        try:
            os.remove(zip_path)
            shutil.rmtree(extract_path, ignore_errors=True)
        except:
            pass

# === MAIN ===
def main():
    keep_alive()
    setup_theos()  # Khởi tạo khi khởi động server

    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("setup", setup_command))
    app.add_handler(MessageHandler(filters.Document.ZIP, handle_zip))

    print("🚀 Bot đã sẵn sàng.")
    app.run_polling()

if __name__ == "__main__":
    main()

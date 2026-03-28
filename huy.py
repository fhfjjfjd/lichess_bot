import os, json, sys, subprocess, threading, argparse
from logger import log
from stats import Stats
from engine import Engine
from ai_manager import AIManager
from core import BotCore # Import BotCore directly
# from telegram_bot import main as run_telegram_bot # We will call this via subprocess if mode 5

# --- Global variables for flags and bot instance ---
bot_instance = None
client = None
account = None
engine = None
stats = None
ai = None
USE_AI_MANAGEMENT = False
USE_AI_MOVES = False
AUTO_CHALLENGE = False
selected_mode_for_direct_run = None # Will store '1' through '5'

# --- Helper Functions ---
def get_path(filename):
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)

def load_settings():
    path = get_path("settings.json")
    return json.load(open(path, encoding="utf-8"))

def reset_api_menu():
    cfg = load_settings()
    print("
" + "=" * 55)
    print("🔑 RESET / SETUP API:")
    print("=" * 55)
    print("  1. ♟️  Reset Lichess Token")
    print("  2. 🤖 Reset OpenRouter Key")
    print("  3. 📡 Reset Telegram Config")
    print("  4. ⬅️  Back")
    print("=" * 55)
    choice = input("Choose (1-4): ").strip()
    if choice == "1":
        path = get_path(cfg["lichess"]["token_file"])
        if os.path.exists(path): os.remove(path)
        log("🗑️ Removed old Lichess token.", "WARN")
    elif choice == "2":
        path = get_path(cfg["openrouter"]["key_file"])
        if os.path.exists(path): os.remove(path)
        log("🗑️ Removed OpenRouter Key.", "WARN")
    elif choice == "3":
        cfg["telegram"]["token"] = "NHẬP_TOKEN_CỦA_BẠN_TẠI_ĐÂY"
        cfg["telegram"]["chat_id"] = "NHẬP_ID_CỦA_BẠN_TẠI_ĐÂY"
        with open(get_path("settings.json"), "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=4, ensure_ascii=False)
        log("🗑️ Reset Telegram configuration.", "WARN")
    return

def setup_telegram_config():
    cfg = load_settings()
    changed = False
    if cfg["telegram"]["token"] == "NHẬP_TOKEN_CỦA_BẠN_TẠI_ĐÂY":
        cfg["telegram"]["token"] = input("🤖 Enter Telegram Bot Token: ").strip()
        changed = True
    if cfg["telegram"]["chat_id"] == "NHẬP_ID_CỦA_BẠN_TẠI_ĐÂY":
        cfg["telegram"]["chat_id"] = input("🆔 Enter your Telegram Chat ID: ").strip()
        changed = True
    if changed:
        with open(get_path("settings.json"), "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=4, ensure_ascii=False)
        log("✅ Saved Telegram configuration.", "INFO")

# --- Main execution logic ---
def main():
    global cfg, pending_challenge, bot_instance, USE_AI_MANAGEMENT, USE_AI_MOVES, AUTO_CHALLENGE
    
    parser = argparse.ArgumentParser(description="Lichess Bot Launcher")
    parser.add_argument('--mode', type=str, choices=['1', '2', '3', '4', '5'], help='Select bot mode (1-5) to run directly.')
    parser.add_argument('--start', action='store_true', help='Start the bot directly in the selected mode, bypassing the menu.')
    parser.add_argument('--reset-api', action='store_true', help='Trigger API reset menu.')
    parser.add_argument('--shutdown', action='store_true', help='Shut down the bot process.')
    
    args = parser.parse_args()

    if args.shutdown:
        log("👋 Shutting down bot process...", "INFO")
        sys.exit(0)

    if args.reset_api:
        reset_api_menu()
        sys.exit(0)

    # Scripts for modes 1-4 and Telegram mode 5
    mode_scripts = {
        "1": "mode1_smart_auto.py",
        "2": "mode2_ai_full.py",
        "3": "mode3_only_play.py",
        "4": "mode4_ai_passive.py",
        "5": "telegram_bot.py"
    }

    if args.start and args.mode:
        mode_choice = args.mode
        log(f"🚀 Starting bot directly in Mode {mode_choice}...")
        
        if mode_choice == "5": # Telegram mode
            script_path = get_path(mode_scripts[mode_choice])
            log(f"Launching Telegram bot script: {script_path}")
            try:
                # Run Telegram bot script as a separate process, blocking huy.py until it exits
                subprocess.run([sys.executable, script_path], cwd=BASE_DIR)
            except KeyboardInterrupt:
                log("Interrupted Telegram bot. Returning to main menu.", "INFO")
            except FileNotFoundError:
                log(f"❌ Error: Script '{script_path}' not found.", "ERROR")
            except Exception as e:
                log(f"❌ An error occurred: {e}", "ERROR")
        else: # Modes 1-4 run BotCore directly
            if run_bot_core(mode_choice): # Run BotCore instance directly
                log("BotCore run loop finished.")
            else:
                log("❌ Failed to start bot core. Returning to menu.", "ERROR")
        return # Exit main after direct start/run

    # --- Fallback to Interactive Menu ---
    while True:
        cfg = load_settings() # Reload settings for menu consistency
        print("
" + "=" * 55)
        print("🏠 MAIN MENU:")
        print("=" * 55)
        print("  1. 🤖 SMART AUTO   (Mode 1)")
        print("  2. 🧠 AI FULL      (Mode 2)")
        print("  3. ♟️  ONLY PLAY    (Mode 3)")
        print("  4. 🧠 AI PASSIVE   (Mode 4)")
        print("  5. 📡 TELEGRAM CONTROL (Mode 5)")
        print("  6. 🔄 Khởi động lại Bot")
        print("  7. 🔑 Reset / Cài đặt API")
        print("  8. ❌ Thoát")
        print("=" * 55)
        choice = input("Chọn (1-8): ").strip()
        
        scripts = {
            "1": "mode1_smart_auto.py",
            "2": "mode2_ai_full.py",
            "3": "mode3_only_play.py",
            "4": "mode4_ai_passive.py",
            "5": "telegram_bot.py"
        }
        
        if choice in scripts:
            script_name = scripts[choice]
            log(f"🚀 Khởi động {script_name}...")
            try:
                subprocess.run([sys.executable, get_path(script_name)], cwd=BASE_DIR)
            except KeyboardInterrupt:
                log("🔙 Quay lại Menu Chính...", "INFO")
            except FileNotFoundError:
                log(f"❌ Lỗi: Không tìm thấy script '{script_name}'.", "ERROR")
            except Exception as e:
                log(f"❌ Lỗi không xác định khi chạy script: {e}", "ERROR")
        elif choice == "6":
            log("🔄 Đang khởi động lại toàn bộ chương trình...", "INFO")
            os.execv(sys.executable, [sys.executable] + sys.argv)
        elif choice == "7":
            reset_api_menu()
        elif choice == "8":
            log("👋 Tạm biệt!", "INFO")
            break

if __name__ == "__main__":
    main()

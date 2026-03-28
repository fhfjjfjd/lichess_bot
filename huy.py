import os, json, sys, subprocess
from logger import log

def load_config():
    return json.load(open("settings.json", encoding="utf-8"))

def reset_api_menu():
    cfg = load_config()
    print("\n" + "=" * 55)
    print("🔑 RESET / CÀI ĐẶT API:")
    print("=" * 55)
    print("  1. ♟️  Reset Lichess Token")
    print("  2. 🤖 Reset OpenRouter Key")
    print("  3. ⬅️  Quay lại")
    print("=" * 55)
    choice = input("Chọn (1-3): ").strip()
    if choice == "1":
        if os.path.exists(cfg["lichess"]["token_file"]): os.remove(cfg["lichess"]["token_file"])
        log("🗑️ Đã xóa token Lichess.", "WARN")
    elif choice == "2":
        if os.path.exists(cfg["openrouter"]["key_file"]): os.remove(cfg["openrouter"]["key_file"])
        log("🗑️ Đã xóa OpenRouter Key.", "WARN")

def main():
    while True:
        print("\n" + "=" * 55)
        print("🏠 MENU CHÍNH:")
        print("=" * 55)
        print("  1. 🤖 SMART AUTO   (Mode 1)")
        print("  2. 🧠 AI FULL      (Mode 2)")
        print("  3. ♟️  ONLY PLAY    (Mode 3)")
        print("  4. 🧠 AI PASSIVE   (Mode 4)")
        print("  5. 🔄 Khởi động lại Bot")
        print("  6. 🔑 Reset / Cài đặt API")
        print("  7. ❌ Thoát")
        print("=" * 55)
        choice = input("Chọn (1-7): ").strip()
        
        scripts = {
            "1": "mode1_smart_auto.py",
            "2": "mode2_ai_full.py",
            "3": "mode3_only_play.py",
            "4": "mode4_ai_passive.py"
        }
        
        if choice in scripts:
            log(f"🚀 Khởi động {scripts[choice]}...")
            subprocess.run([sys.executable, scripts[choice]])
        elif choice == "5":
            log("🔄 Đang khởi động lại...", "INFO")
            os.execv(sys.executable, [sys.executable] + sys.argv)
        elif choice == "6":
            reset_api_menu()
        elif choice == "7":
            log("👋 Tạm biệt!", "INFO")
            break

if __name__ == "__main__":
    main()

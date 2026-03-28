import os, json, sys, subprocess
from logger import log

# Xác định thư mục gốc của dự án
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def get_path(filename):
    return os.path.join(BASE_DIR, filename)

def load_settings():
    path = get_path("settings.json")
    return json.load(open(path, encoding="utf-8"))

def reset_api_menu():
    cfg = load_settings()
    print("\n" + "=" * 55)
    print("🔑 RESET / CÀI ĐẶT API:")
    print("=" * 55)
    print("  1. ♟️  Reset Lichess Token")
    print("  2. 🤖 Reset OpenRouter Key")
    print("  3. ⬅️  Quay lại")
    print("=" * 55)
    choice = input("Chọn (1-3): ").strip()
    if choice == "1":
        path = get_path(cfg["lichess"]["token_file"])
        if os.path.exists(path): os.remove(path)
        log("🗑️ Đã xóa token Lichess.", "WARN")
    elif choice == "2":
        path = get_path(cfg["openrouter"]["key_file"])
        if os.path.exists(path): os.remove(path)
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
            script_path = get_path(scripts[choice])
            log(f"🚀 Khởi động {scripts[choice]}...")
            try:
                # Chạy script với thư mục làm việc (cwd) là thư mục gốc của bot
                subprocess.run([sys.executable, script_path], cwd=BASE_DIR)
            except KeyboardInterrupt:
                log("🔙 Đã dừng bot và quay lại Menu Chính.", "INFO")
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

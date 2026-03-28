import os, json, sys, subprocess, threading
from logger import log
from stats import Stats
from engine import Engine
from ai_manager import AIManager
from board_utils import moves_to_board, get_phase, format_move, is_endgame_draw

# Xác định thư mục gốc của dự án
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def get_path(filename):
    return os.path.join(BASE_DIR, filename)

def load_settings():
    path = get_path("settings.json")
    return json.load(open(path, encoding="utf-8"))

def reset_api_menu():
    cfg = load_settings()
    print("
" + "=" * 55)
    print("🔑 RESET / CÀI ĐẶT API:")
    print("=" * 55)
    print("  1. ♟️  Reset Lichess Token")
    print("  2. 🤖 Reset OpenRouter Key")
    print("  3. 📡 Reset Telegram Config")
    print("  4. ⬅️  Quay lại")
    print("=" * 55)
    choice = input("Chọn (1-4): ").strip()
    if choice == "1":
        path = get_path(cfg["lichess"]["token_file"])
        if os.path.exists(path): os.remove(path)
        log("🗑️ Đã xóa token Lichess.", "WARN")
    elif choice == "2":
        path = get_path(cfg["openrouter"]["key_file"])
        if osa.path.exists(path): os.remove(path)
        log("🗑️ Đã xóa OpenRouter Key.", "WARN")
    elif choice == "3":
        cfg["telegram"]["token"] = "NHẬP_TOKEN_CỦA_BẠN_TẠI_ĐÂY"
        cfg["telegram"]["chat_id"] = "NHẬP_ID_CỦA_BẠN_TẠI_ĐÂY"
        with open(get_path("settings.json"), "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=4, ensure_ascii=False)
        log("🗑️ Đã reset cấu hình Telegram.", "WARN")

def setup_telegram():
    cfg = load_settings()
    changed = False
    if cfg["telegram"]["token"] == "NHẬP_TOKEN_CỦA_BẠN_TẠI_ĐÂY":
        cfg["telegram"]["token"] = input("🤖 Nhập Telegram Bot Token: ").strip()
        changed = True
    if cfg["telegram"]["chat_id"] == "NHẬP_ID_CỦA_BẠN_TẠI_ĐÂY":
        cfg["telegram"]["chat_id"] = input("🆔 Nhập Telegram Chat ID của bạn: ").strip()
        changed = True
    if changed:
        with open(get_path("settings.json"), "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=4, ensure_ascii=False)
        log("✅ Đã lưu cấu hình Telegram.", "INFO")

def main():
    global cfg, pending_challenge
    while True:
        cfg = load_settings()
        print("
" + "=" * 55)
        print("🏠 MENU CHÍNH:")
        print("=" * 55)
        print("  1. 🤖 SMART AUTO   (Mode 1)")
        print("  2. 🧠 AI FULL      (Mode 2)")
        print("  3. ♟️  ONLY PLAY    (Mode 3)")
        print("  4. 🧠 AI PASSIVE   (Mode 4)")
        print("  5. 📡 TELEGRAM CONTROL (New!)")
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
        
        proc = None # Biến để lưu trữ tiến trình con
        if choice in scripts:
            script_path = get_path(scripts[choice])
            log(f"🚀 Khởi động {scripts[choice]}...")
            try:
                # Sử dụng Popen để chạy script con và có thể quản lý nó
                proc = subprocess.Popen([sys.executable, script_path], cwd=BASE_DIR)
                proc.wait() # Đợi cho script con kết thúc
            except KeyboardInterrupt:
                log("🔙 Quay lại Menu Chính...", "INFO")
                if proc: # Nếu có tiến trình con đang chạy
                    proc.terminate() # Gửi tín hiệu Terminate
                    proc.wait() # Chờ nó kết thúc
            except FileNotFoundError:
                log(f"❌ Lỗi: Không tìm thấy script '{script_path}'. Hãy kiểm tra lại.", "ERROR")
            except Exception as e:
                log(f"❌ Lỗi không xác định khi chạy script: {e}", "ERROR")
                if proc: # Đảm bảo tiến trình con bị đóng nếu có lỗi
                    proc.terminate()
                    proc.wait()
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

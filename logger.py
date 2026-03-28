from datetime import datetime
import os

# Xác định thư mục gốc của dự án
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_FILE = os.path.join(BASE_DIR, "bot.log")

COLORS = {
    "INFO": "\033[97m",
    "GAME": "\033[92m",
    "ENGINE": "\033[96m",
    "AI": "\033[95m",
    "CHALLENGE": "\033[93m",
    "EVENT": "\033[94m",
    "STATS": "\033[33m",
    "ERROR": "\033[91m",
    "WARN": "\033[93m",
    "CHAT": "\033[90m",
    "ANALYSIS": "\033[36m",
    "TOURNAMENT": "\033[35m",
}
RESET = "\033[0m"

def log(msg, level="INFO", save_to_file=True):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    color = COLORS.get(level, COLORS["INFO"])
    
    # In ra console với màu sắc
    print(f"{color}[{timestamp}] [{level:>10}] {msg}{RESET}")
    
    # Ghi vào file bot.log (không có mã màu ANSI)
    if save_to_file:
        try:
            with open(LOG_FILE, "a", encoding="utf-8") as f:
                f.write(f"[{timestamp}] [{level:>10}] {msg}\n")
        except:
            pass

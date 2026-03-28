from datetime import datetime

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

def log(msg, level="INFO"):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    color = COLORS.get(level, COLORS["INFO"])
    print(f"{color}[{timestamp}] [{level:>10}] {msg}{RESET}")

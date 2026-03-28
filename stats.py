import json
import os
from logger import log

# Xác định thư mục gốc của dự án
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATS_FILE = os.path.join(BASE_DIR, "stats.json")

class Stats:
    def __init__(self):
        self.data = {"games": 0, "wins": 0, "losses": 0, "draws": 0,
                     "resigns": 0, "ai_helps": 0, "moves_played": 0,
                     "fastest_win": 999, "longest_game": 0,
                     "opponents_beaten": [], "current_streak": 0, "best_streak": 0}
        self.load()

    def load(self):
        if os.path.exists(STATS_FILE):
            try:
                with open(STATS_FILE, encoding="utf-8") as f:
                    saved = json.load(f)
                    self.data.update(saved)
                log(f"📊 Đọc thống kê từ {STATS_FILE}", "STATS")
            except:
                pass

    def save(self):
        try:
            with open(STATS_FILE, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
        except:
            pass

    def add_game(self, result, opponent="", move_count=0):
        self.data["games"] += 1
        self.data["moves_played"] += move_count
        if result == "win":
            self.data["wins"] += 1
            self.data["current_streak"] += 1
            if self.data["current_streak"] > self.data["best_streak"]:
                self.data["best_streak"] = self.data["current_streak"]
            if move_count < self.data["fastest_win"] and move_count > 0:
                self.data["fastest_win"] = move_count
            if opponent and opponent not in self.data["opponents_beaten"]:
                self.data["opponents_beaten"].append(opponent)
        elif result == "loss":
            self.data["losses"] += 1
            self.data["current_streak"] = 0
        elif result == "draw":
            self.data["draws"] += 1
        if move_count > self.data["longest_game"]:
            self.data["longest_game"] = move_count
        self.save()

    def add_resign(self):
        self.data["resigns"] += 1
        self.save()

    def add_ai_help(self):
        self.data["ai_helps"] += 1
        self.save()

    def show(self):
        d = self.data
        total = d["games"]
        if total == 0:
            log("📊 Chưa có ván nào.", "STATS")
            return
        wr = d["wins"] / total * 100
        log(f"{'=' * 45}", "STATS")
        log(f"📊 THỐNG KÊ TỔNG HỢP", "STATS")
        log(f"{'=' * 45}", "STATS")
        log(f"  Tổng ván:        {total}", "STATS")
        log(f"  Thắng:           {d['wins']} ({wr:.1f}%)", "STATS")
        log(f"  Thua:            {d['losses']}", "STATS")
        log(f"  Hòa:             {d['draws']}", "STATS")
        log(f"  Bỏ cuộc:         {d['resigns']}", "STATS")
        log(f"  AI hỗ trợ:       {d['ai_helps']} lần", "STATS")
        log(f"  Tổng nước đi:    {d['moves_played']}", "STATS")
        log(f"  Thắng nhanh nhất:{d['fastest_win']} nước", "STATS")
        log(f"  Ván dài nhất:    {d['longest_game']} nước", "STATS")
        log(f"  Chuỗi thắng:     {d['current_streak']} (kỷ lục: {d['best_streak']})", "STATS")
        log(f"  Đối thủ đã hạ:   {len(d['opponents_beaten'])}", "STATS")
        log(f"{'=' * 45}", "STATS")

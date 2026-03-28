import subprocess
import chess
from logger import log

class Engine:
    def __init__(self, threads=5, hash_mb=300, skill=20, think_ms=3000,
                 min_think=500, max_think=8000, smart_time=True):
        self.think_ms = think_ms
        self.min_think = min_think
        self.max_think = max_think
        self.smart_time = smart_time
        self.skill = skill

        log("🔧 Khởi động Stockfish...")
        self.proc = subprocess.Popen(
            "stockfish",
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            universal_newlines=True
        )
        self._send("uci")
        self._wait_for("uciok")
        self._send(f"setoption name Threads value {threads}")
        self._send(f"setoption name Hash value {hash_mb}")
        self._send(f"setoption name Skill Level value {skill}")
        self._send("isready")
        self._wait_for("readyok")
        log(f"⚙️ Stockfish 18: Threads={threads} | Hash={hash_mb}MB | "
            f"Skill={skill} | Think={think_ms}ms", "ENGINE")

    def _send(self, cmd):
        self.proc.stdin.write(cmd + "\n")
        self.proc.stdin.flush()

    def _wait_for(self, token):
        while True:
            line = self.proc.stdout.readline().strip()
            if line == token:
                return

    def set_skill(self, skill):
        self.skill = skill
        self._send(f"setoption name Skill Level value {skill}")
        log(f"⚙️ Skill Level → {skill}", "ENGINE")

    def calc_think_time(self, board, my_time_ms=None):
        if not self.smart_time:
            return self.think_ms
        pieces = len(board.piece_map())
        # Khai cuộc: nghĩ ít
        if pieces >= 28:
            t = self.min_think
        # Trung cuộc: nghĩ nhiều
        elif pieces >= 14:
            t = self.think_ms
        # Tàn cuộc: nghĩ vừa
        else:
            t = int(self.think_ms * 0.7)
        # Nếu ít quân + thế cờ phức tạp → tăng thời gian
        if board.is_check():
            t = int(t * 1.5)
        # Giới hạn
        t = max(self.min_think, min(self.max_think, t))
        # Nếu có thời gian thực tế, quản lý
        if my_time_ms and my_time_ms < 30000:
            t = min(t, my_time_ms // 10)
        return t

    def get_best_move(self, moves_str, board=None):
        if board and self.smart_time:
            t = self.calc_think_time(board)
        else:
            t = self.think_ms
            
        # Sử dụng FEN để đảm bảo thế cờ luôn đồng bộ 100% với Stockfish
        if board:
            fen = board.fen()
            # Nếu là Chess960, cần báo cho Stockfish
            if board.chess960:
                self._send("setoption name UCI_Chess960 value true")
            else:
                self._send("setoption name UCI_Chess960 value false")
            self._send(f"position fen {fen}")
        else:
            self._send(f"position startpos moves {moves_str}" if moves_str else "position startpos")
            
        self._send(f"go movetime {t}")
        score = 0
        depth = 0
        best = None
        while True:
            line = self.proc.stdout.readline().strip()
            if "score cp" in line:
                try:
                    score = int(line.split("score cp ")[1].split()[0])
                except:
                    pass
            if "score mate" in line:
                try:
                    mate = int(line.split("score mate ")[1].split()[0])
                    score = 10000 * (1 if mate > 0 else -1)
                except:
                    pass
            if " depth " in line:
                try:
                    depth = int(line.split(" depth ")[1].split()[0])
                except:
                    pass
            if line.startswith("bestmove"):
                best = line.split()[1]
                break
        log(f"🧠 Stockfish: {best} | eval: {score/100:.1f} | depth: {depth} | time: {t}ms", "ENGINE")
        return best, score, depth

    def get_top_moves(self, moves_str, n=3):
        self._send(f"setoption name MultiPV value {n}")
        self._send(f"position startpos moves {moves_str}" if moves_str else "position startpos")
        self._send(f"go movetime {self.think_ms}")
        candidates = {}
        while True:
            line = self.proc.stdout.readline().strip()
            if " multipv " in line and " pv " in line:
                try:
                    pv_idx = int(line.split(" multipv ")[1].split()[0])
                    pv_moves = line.split(" pv ")[1]
                    s = 0
                    if "score cp" in line:
                        s = int(line.split("score cp ")[1].split()[0])
                    elif "score mate" in line:
                        m = int(line.split("score mate ")[1].split()[0])
                        s = 10000 * (1 if m > 0 else -1)
                    d = int(line.split(" depth ")[1].split()[0])
                    candidates[pv_idx] = {"move": pv_moves.split()[0], "score": s,
                                           "depth": d, "pv": pv_moves}
                except:
                    pass
            if line.startswith("bestmove"):
                break
        self._send("setoption name MultiPV value 1")
        return candidates

    def analyze_position(self, moves_str, time_ms=5000):
        self._send(f"position startpos moves {moves_str}" if moves_str else "position startpos")
        self._send(f"go movetime {time_ms}")
        info = {"score": 0, "depth": 0, "best": "", "pv": "", "nodes": 0}
        while True:
            line = self.proc.stdout.readline().strip()
            if "score cp" in line:
                try:
                    info["score"] = int(line.split("score cp ")[1].split()[0])
                except: pass
            if "score mate" in line:
                try:
                    m = int(line.split("score mate ")[1].split()[0])
                    info["score"] = 10000 * (1 if m > 0 else -1)
                except: pass
            if " depth " in line:
                try: info["depth"] = int(line.split(" depth ")[1].split()[0])
                except: pass
            if " nodes " in line:
                try: info["nodes"] = int(line.split(" nodes ")[1].split()[0])
                except: pass
            if " pv " in line:
                try: info["pv"] = line.split(" pv ")[1]
                except: pass
            if line.startswith("bestmove"):
                info["best"] = line.split()[1]
                break
        return info

    def quit(self):
        self._send("quit")
        self.proc.wait()

import os, json, random, time, threading, berserk
from logger import log
from stats import Stats
from engine import Engine
from ai_manager import AIManager
from telegram_manager import TelegramManager
from board_utils import moves_to_board, get_phase, format_move, is_endgame_draw

# Xác định thư mục gốc của dự án
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def get_path(filename):
    return os.path.join(BASE_DIR, filename)

def load_settings():
    path = get_path("settings.json")
    return json.load(open(path, encoding="utf-8"))

settings = load_settings()

class BotCore:
    def __init__(self, use_ai_mgmt=False, use_ai_moves=False, auto_challenge=False):
        self.use_ai_mgmt = use_ai_mgmt
        self.use_ai_moves = use_ai_moves
        self.auto_challenge = auto_challenge
        
        self.client = None
        self.account = None
        self.engine = None
        self.stats = Stats()
        self.ai = None
        
        # Tích hợp Telegram
        tg_cfg = settings.get("telegram", {})
        self.tg = TelegramManager(tg_cfg.get("token"), tg_cfg.get("chat_id"))
        
        self.active_games = set()
        self.pending_challenge = {"id": None, "time": 0, "target": ""}
        self.running = True
        self.last_search_time = 0

    def login(self):
        tf = get_path(settings["lichess"]["token_file"])
        while True:
            if os.path.exists(tf):
                with open(tf) as f: token = f.read().strip()
            else:
                token = input("🔑 Nhập Lichess Token: ").strip()
            session = berserk.TokenSession(token)
            self.client = berserk.Client(session=session)
            try:
                self.account = self.client.account.get()
                log(f"✅ Đăng nhập: {self.account['username']}")
                with open(tf, "w") as f: f.write(token)
                return True
            except Exception as e:
                log(f"❌ Token lỗi: {e}", "ERROR")
                if os.path.exists(tf): os.remove(tf)

    def init_engine(self):
        self.engine = Engine(
            threads=settings["stockfish"]["threads"], hash_mb=settings["stockfish"]["hash_mb"],
            skill=settings["stockfish"]["skill_level"], think_ms=settings["stockfish"]["think_time_ms"],
            min_think=settings["stockfish"]["min_think_ms"], max_think=settings["stockfish"]["max_think_ms"],
            smart_time=settings["bot"]["smart_time"]
        )
        if self.use_ai_mgmt:
            sp = f"Bạn là AI quản lý bot '{self.account['username']}' trên Lichess. Tiếng Việt."
            self.ai = AIManager(get_path(settings["openrouter"]["key_file"]), settings["openrouter"]["model"],
                               settings["openrouter"]["max_tokens"], sp)

    def safe_move(self, gid, move):
        for i in range(3):
            try:
                self.client.bots.make_move(gid, move)
                return True
            except Exception as e:
                err_msg = str(e)
                if "Not your turn" in err_msg: return True
                log(f"⚠️ Gửi nước {move} lỗi: {err_msg}", "ERROR")
                if "cannot move" in err_msg or "Illegal" in err_msg: return False
                time.sleep(1)
        return False

    def chat(self, gid, msg):
        if settings["bot"]["chat_enabled"]:
            try: self.client.bots.post_message(gid, msg)
            except: pass

    def smart_move(self, moves, board, total_moves):
        best, score, depth = self.engine.get_best_move(moves, board)
        if not self.use_ai_moves or not self.ai: return best, score, depth
        th, lo, mn = settings["bot"]["ai_help_threshold"]*100, settings["bot"]["ai_help_losing"]*100, settings["bot"]["ai_help_min_moves"]
        if total_moves >= mn and (abs(score) < th or score < lo):
            log(f"🆘 Thế cờ khó (eval={score/100:.1f}), hỏi AI...", "AI")
            cands = self.engine.get_top_moves(moves, 3)
            if cands:
                chosen = self.ai.choose_move(cands, moves, f"{score/100:.1f}")
                if chosen:
                    for c in cands.values():
                        if c['move'] == chosen:
                            log(f"🤖 AI chọn: {chosen}", "AI")
                            return chosen, c['score'], c['depth']
        return best, score, depth

    def play_game(self, gid):
        if gid in self.active_games: return
        self.active_games.add(gid)
        self.pending_challenge = {"id": None, "time": 0, "target": ""}
        
        game_url = f"https://lichess.org/{gid}"
        log(f"🎮 BẮT ĐẦU VÁN: {gid}", "GAME")
        
        my_color = opp_name = None
        move_num = last_score = 0
        last_played_len = -1
        initial_fen = None
        variant = "standard"

        try:
            if settings["bot"]["chat_enabled"]:
                try: self.client.bots.post_message(gid, settings["bot"]["chat_greeting"])
                except: pass
                
            for event in self.client.bots.stream_game_state(gid):
                if event['type'] == 'gameFull':
                    white = event['white']
                    my_color = 'white' if white.get('id', white.get('name', '')).lower() == self.account['id'].lower() else 'black'
                    opp = event['black'] if my_color == 'white' else event['white']
                    opp_name = opp.get('name', opp.get('id', '???'))
                    initial_fen, variant = event.get('initialFen'), event.get('variant', {}).get('key', 'standard')
                    
                    # Thông báo Telegram
                    self.tg.notify_game_start(gid, opp_name, opp.get('rating', '?'), game_url)
                    
                    log(f"♟️ {my_color} vs {opp_name} ({opp.get('rating', '?')}) | Variant: {variant}", "GAME")
                    if settings["bot"].get("show_game_url", True):
                        log(f"🔗 Link: {game_url}", "GAME")
                        log("⏳ Đợi 15s cho bạn vào xem...", "INFO")
                        time.sleep(15)

                    moves = event['state']['moves']
                    ml = moves.split() if moves else []
                    my_turn = (my_color == 'white' and len(ml) % 2 == 0) or (my_color == 'black' and len(ml) % 2 == 1)
                    if my_turn and len(ml) > last_played_len:
                        board = moves_to_board(moves, initial_fen, variant)
                        move_num += 1
                        best, score, _ = self.smart_move(moves, board, len(ml))
                        last_score, last_played_len = score, len(ml)
                        log(f"➡️ #{move_num} {format_move(board, best)} | eval: {score/100:.1f}", "GAME")
                        self.safe_move(gid, best)

                elif event['type'] == 'gameState':
                    moves = event['moves']
                    status = event.get('status', 'started')
                    if status != 'started':
                        result = "win" if event.get('winner') == my_color else "loss" if event.get('winner') else "draw"
                        log(f"🏁 Kết thúc: {status} ({len(moves.split())} nước)", "GAME")
                        
                        # Thông báo Telegram
                        self.tg.notify_game_end(status, result, len(moves.split()))
                        
                        if settings["bot"]["chat_enabled"]:
                            try: self.client.bots.post_message(gid, settings["bot"]["chat_gg"])
                            except: pass
                        break
                    ml = moves.split() if moves else []
                    my_turn = (my_color == 'white' and len(ml) % 2 == 0) or (my_color == 'black' and len(ml) % 2 == 1)
                    if not my_turn or len(ml) <= last_played_len: continue
                    board = moves_to_board(moves, initial_fen, variant)
                    if settings["bot"]["auto_resign"] and last_score < settings["bot"]["resign_score"] * 100 and len(ml) >= settings["bot"]["resign_min_moves"]:
                        log(f"🏳️ Resign (eval: {last_score/100:.1f})", "GAME")
                        if settings["bot"]["chat_enabled"]:
                            try: self.client.bots.post_message(gid, settings["bot"]["chat_resign"])
                            except: pass
                        try: self.client.bots.resign_game(gid)
                        except: pass
                        break
                    move_num += 1
                    best, score, _ = self.smart_move(moves, board, len(ml))
                    last_score, last_played_len = score, len(ml)
                    log(f"➡️ #{move_num} {format_move(board, best)} | eval: {score/100:.1f}", "GAME")
                    self.safe_move(gid, best)
        except Exception as e: log(f"❌ Lỗi ván: {e}", "ERROR")
        finally:
            self.active_games.discard(gid)
            if self.auto_challenge: threading.Thread(target=self.send_challenge).start()

    def handle_challenge(self, ch):
        cid, name = ch['id'], ch.get('challenger', {}).get('name', '???')
        rating, variant = ch.get('challenger', {}).get('rating', 0), ch.get('variant', {}).get('key', 'standard')
        speed = ch.get('speed', '?')
        log(f"📩 Thách đấu từ: {name} ({rating}) {variant} {speed}", "CHALLENGE")
        if name.lower() == self.account['username'].lower():
            try: self.client.bots.decline_challenge(cid)
            except: pass
            return
        if len(self.active_games) >= settings["challenge"]["max_concurrent_games"]:
            try: self.client.bots.decline_challenge(cid)
            except: pass
            return
        if self.use_ai_mgmt and self.ai:
            answer = self.ai.decide_challenge(name, rating, variant, speed, 0, 0)
            if answer and answer.startswith("DECLINE"):
                try: self.client.bots.decline_challenge(cid)
                except: pass
                log(f"❌ AI từ chối {name}", "CHALLENGE")
            else:
                try: self.client.bots.accept_challenge(cid)
                except: pass
                log(f"✅ AI chấp nhận {name}", "CHALLENGE")
        else:
            self.client.bots.accept_challenge(cid)
            log(f"✅ Chấp nhận {name}", "CHALLENGE")

    def send_challenge(self):
        if not self.auto_challenge or len(self.active_games) >= settings["challenge"]["max_concurrent_games"] or self.pending_challenge["id"]: return
        self.last_search_time = time.time()
        try:
            log("🔎 Đang tìm đối thủ bot online...", "CHALLENGE")
            bots = list(self.client.bots.get_online_bots(limit=30))
            opps = [b for b in bots if b['username'].lower() != self.account['username'].lower()]
            if not opps: return
            target = random.choice(opps)
            cl_limit, cl_inc = settings["challenge"]["default_clock_limit"], settings["challenge"]["default_clock_increment"]
            log(f"🎯 Thách đấu: {target['username']}...", "CHALLENGE")
            res = self.client.challenges.create(target['id'], rated=settings["challenge"]["rated"], clock_limit=cl_limit, clock_increment=cl_inc)
            self.pending_challenge = {"id": res['challenge']['id'], "time": time.time(), "target": target['username']}
        except: pass

    def timeout_monitor(self):
        last_log_time = 0
        while self.running:
            now = time.time()
            if self.auto_challenge:
                if self.pending_challenge["id"]:
                    elapsed = int(now - self.pending_challenge["time"])
                    if elapsed % 10 == 0 and elapsed != last_log_time:
                        log(f"⏳ Đợi {self.pending_challenge['target']}... ({40-elapsed}s còn lại)", "CHALLENGE")
                        last_log_time = elapsed
                    if elapsed >= 40:
                        log(f"⏰ Hủy thách đấu với {self.pending_challenge['target']}.", "CHALLENGE")
                        try: self.client.challenges.cancel(self.pending_challenge["id"])
                        except: pass
                        self.pending_challenge = {"id": None, "time": 0, "target": ""}
                        threading.Thread(target=self.send_challenge).start()
                elif not self.active_games and (now - self.last_search_time > 15):
                    self.send_challenge()
            time.sleep(1)

    def run(self):
        self.login()
        self.init_engine()
        threading.Thread(target=self.timeout_monitor, daemon=True).start()
        if self.auto_challenge: self.send_challenge()
        log("🚀 Bot đang lắng nghe sự kiện...", "INFO")
        try:
            for event in self.client.board.stream_incoming_events():
                if event['type'] == 'gameStart':
                    gid = event['game']['gameId']
                    threading.Thread(target=self.play_game, args=(gid,), daemon=True).start()
                elif event['type'] == 'challenge':
                    self.handle_challenge(event['challenge'])
                elif event['type'] in ('challengeDeclined', 'challengeCanceled'):
                    if self.pending_challenge["id"] == event.get('challenge', {}).get('id'):
                        self.pending_challenge = {"id": None, "time": 0, "target": ""}
                        if self.auto_challenge: threading.Thread(target=self.send_challenge).start()
        except KeyboardInterrupt:
            self.running = False
            log("👋 Dừng bot...", "INFO")
            if self.engine: self.engine.quit()

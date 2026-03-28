import os, json, random, time, threading, berserk
from logger import log
from stats import Stats
from engine import Engine
from ai_manager import AIManager
from board_utils import moves_to_board, get_phase, format_move, is_endgame_draw

# Tải cấu hình
def load_config():
    return json.load(open("config.json", encoding="utf-8"))

cfg = load_config()

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
        
        self.active_games = set()
        self.pending_challenge = {"id": None, "time": 0}

    def login(self):
        tf = cfg["lichess"]["token_file"]
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
            threads=cfg["stockfish"]["threads"], hash_mb=cfg["stockfish"]["hash_mb"],
            skill=cfg["stockfish"]["skill_level"], think_ms=cfg["stockfish"]["think_time_ms"],
            min_think=cfg["stockfish"]["min_think_ms"], max_think=cfg["stockfish"]["max_think_ms"],
            smart_time=cfg["bot"]["smart_time"]
        )
        if self.use_ai_mgmt:
            sp = f"Bạn là AI quản lý bot '{self.account['username']}' trên Lichess. Tiếng Việt chuyên nghiệp."
            self.ai = AIManager(cfg["openrouter"]["key_file"], cfg["openrouter"]["model"],
                               cfg["openrouter"]["max_tokens"], sp)

    def safe_move(self, gid, move):
        for i in range(3):
            try:
                self.client.bots.make_move(gid, move)
                return True
            except Exception as e:
                if "Not your turn" in str(e): return True
                log(f"⚠️ Gửi nước {move} lỗi: {e}", "ERROR")
                time.sleep(1)
        return False

    def chat(self, gid, msg):
        if cfg["bot"]["chat_enabled"]:
            try: self.client.bots.post_message(gid, msg)
            except: pass

    def smart_move(self, moves, board, total_moves):
        best, score, depth = self.engine.get_best_move(moves, board)
        if not self.use_ai_moves or not self.ai: return best, score, depth
        
        th, lo, mn = cfg["bot"]["ai_help_threshold"]*100, cfg["bot"]["ai_help_losing"]*100, cfg["bot"]["ai_help_min_moves"]
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
        self.pending_challenge = {"id": None, "time": 0}
        
        game_url = f"https://lichess.org/{gid}"
        log(f"🎮 BẮT ĐẦU VÁN: {gid}", "GAME")
        if cfg["bot"].get("show_game_url", True):
            log(f"🔗 Xem trực tiếp tại: {game_url}", "GAME")
        
        my_color = opp_name = None
        move_num = last_score = 0
        last_played_len = -1
        initial_fen = None
        variant = "standard"

        try:
            self.chat(gid, cfg["bot"]["chat_greeting"])
            for event in self.client.bots.stream_game_state(gid):
                if event['type'] == 'gameFull':
                    white = event['white']
                    my_color = 'white' if white.get('id', white.get('name', '')).lower() == self.account['id'].lower() else 'black'
                    opp = event['black'] if my_color == 'white' else event['white']
                    opp_name = opp.get('name', opp.get('id', '???'))
                    initial_fen, variant = event.get('initialFen'), event.get('variant', {}).get('key', 'standard')
                    log(f"♟️ {my_color} vs {opp_name} ({opp.get('rating', '?')})", "GAME")
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
                        self.stats.add_game("win" if event.get('winner') == my_color else "loss", opp_name, len(moves.split()))
                        log(f"🏁 {status} ({len(moves.split())} nước)", "GAME")
                        self.chat(gid, cfg["bot"]["chat_gg"])
                        if self.use_ai_mgmt and self.ai:
                            analysis = self.ai.analyze_game(moves, "win" if event.get('winner') == my_color else "loss", my_color)
                            if analysis: log(f"🔬 {analysis}", "ANALYSIS")
                        break
                    ml = moves.split() if moves else []
                    my_turn = (my_color == 'white' and len(ml) % 2 == 0) or (my_color == 'black' and len(ml) % 2 == 1)
                    if not my_turn or len(ml) <= last_played_len: continue
                    board = moves_to_board(moves, initial_fen, variant)
                    if cfg["bot"]["auto_resign"] and last_score < cfg["bot"]["resign_score"] * 100 and len(ml) >= cfg["bot"]["resign_min_moves"]:
                        log(f"🏳️ Resign (eval: {last_score/100:.1f})", "GAME")
                        self.chat(gid, cfg["bot"]["chat_resign"])
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
        log(f"📩 Thách đấu: {name} ({rating}) {variant} {speed}", "CHALLENGE")
        if len(self.active_games) >= cfg["challenge"]["max_concurrent_games"]:
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
        if not self.auto_challenge or len(self.active_games) >= cfg["challenge"]["max_concurrent_games"] or self.pending_challenge["id"]: return
        try:
            bots = list(self.client.bots.get_online_bots(limit=30))
            opps = [b for b in bots if b['id'] != self.account['id']]
            if not opps: return
            target = random.choice(opps)
            cl_limit, cl_inc = cfg["challenge"]["default_clock_limit"], cfg["challenge"]["default_clock_increment"]
            log(f"🎯 Thách đấu: {target['username']}...", "CHALLENGE")
            res = self.client.challenges.create(target['id'], rated=cfg["challenge"]["rated"], clock_limit=cl_limit, clock_increment=cl_inc)
            self.pending_challenge = {"id": res['challenge']['id'], "time": time.time()}
        except: pass

    def run(self):
        self.login()
        self.init_engine()
        if self.auto_challenge: threading.Thread(target=self.send_challenge).start()
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
                        self.pending_challenge = {"id": None, "time": 0}
                        if self.auto_challenge: threading.Thread(target=self.send_challenge).start()
                
                if self.auto_challenge and self.pending_challenge["id"]:
                    if time.time() - self.pending_challenge["time"] > 40:
                        log(f"⏰ Hủy thách đấu treo {self.pending_challenge['id']}", "CHALLENGE")
                        try: self.client.challenges.cancel(self.pending_challenge["id"])
                        except: pass
                        self.pending_challenge = {"id": None, "time": 0}
                        threading.Thread(target=self.send_challenge).start()
        except KeyboardInterrupt:
            log("👋 Dừng bot...", "INFO")
            if self.engine: self.engine.quit()

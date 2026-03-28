import os, json, random, time, threading, berserk
from logger import log
from stats import Stats
from engine import Engine
from ai_manager import AIManager
from board_utils import moves_to_board, get_phase, format_move, is_endgame_draw

# ==================== CẤU HÌNH ====================
cfg = json.load(open("config.json", encoding="utf-8"))

# Biến toàn cục
client = None
account = None
engine = None
stats = None
ai = None
USE_AI_MANAGEMENT = False
USE_AI_MOVES = False
AUTO_CHALLENGE = False

# ==================== ĐĂNG NHẬP ====================
def login():
    global client, account
    tf = cfg["lichess"]["token_file"]
    while True:
        if os.path.exists(tf):
            with open(tf) as f: token = f.read().strip()
            log("📂 Đọc token Lichess từ file...")
        else:
            token = input("🔑 Nhập Lichess Token mới: ").strip()
        
        session = berserk.TokenSession(token)
        client = berserk.Client(session=session)
        try:
            account = client.account.get()
            log(f"✅ Đăng nhập Lichess: {account['username']}")
            with open(tf, "w") as f: f.write(token)
            return
        except Exception as e:
            log(f"❌ Token lỗi: {e}", "ERROR")
            if os.path.exists(tf): os.remove(tf)

# ==================== RESET API ====================
def reset_api_menu():
    print("\n" + "=" * 55)
    print("🔑 RESET / CÀI ĐẶT API:")
    print("=" * 55)
    print("  1. ♟️  Reset Lichess Token")
    print("  2. 🤖 Reset OpenRouter Key")
    print("  3. ⬅️  Quay lại")
    print("=" * 55)
    choice = input("Chọn (1-3): ").strip()
    
    if choice == "1":
        tf = cfg["lichess"]["token_file"]
        if os.path.exists(tf): os.remove(tf)
        log("🗑️ Đã xóa token Lichess cũ. Hãy khởi động lại Bot để nhập mới.", "WARN")
    elif choice == "2":
        kf = cfg["openrouter"]["key_file"]
        if os.path.exists(kf): os.remove(kf)
        log("🗑️ Đã xóa OpenRouter Key cũ. Hãy khởi động lại Bot để nhập mới.", "WARN")
    return

# ==================== KHỞI TẠO BOT ====================
def start_bot_flow():
    global engine, stats, ai, USE_AI_MANAGEMENT, USE_AI_MOVES, AUTO_CHALLENGE
    
    login() # Đăng nhập trước

    print("\n" + "=" * 55)
    print("🎮 CHỌN CHẾ ĐỘ CHƠI:")
    print("=" * 55)
    print("  1. 🤖 SMART AUTO   — Tự động, Stockfish đánh, AI quản lý")
    print("  2. 🧠 AI FULL      — Tự động hoàn toàn, AI chọn nước đi")
    print("  3. ♟️  ONLY PLAY    — Chế độ thụ động, không dùng AI")
    print("  4. 🧠 AI PASSIVE   — Chế độ thụ động, AI hỗ trợ đánh")
    print("=" * 55)
    mode = input(f"Chọn (1-4) [{cfg['bot']['default_mode']}]: ").strip()
    if mode not in ("1", "2", "3", "4"):
        mode = str(cfg["bot"]["default_mode"])

    USE_AI_MANAGEMENT = mode in ("1", "2", "4")
    USE_AI_MOVES = mode in ("2", "4")
    AUTO_CHALLENGE = mode in ("1", "2")
    
    NAMES = {"1": "🤖 SMART AUTO", "2": "🧠 AI FULL", "3": "♟️  ONLY PLAY", "4": "🧠 AI PASSIVE"}
    log(f"🚀 Chế độ: {NAMES[mode]}")

    engine = Engine(
        threads=cfg["stockfish"]["threads"], hash_mb=cfg["stockfish"]["hash_mb"],
        skill=cfg["stockfish"]["skill_level"], think_ms=cfg["stockfish"]["think_time_ms"],
        min_think=cfg["bot"]["min_think_ms"], max_think=cfg["bot"]["max_think_ms"],
        smart_time=cfg["bot"]["smart_time"]
    )
    stats = Stats()
    if USE_AI_MANAGEMENT:
        sp = f"Bạn là bộ não quản lý bot cờ vua '{account['username']}' trên Lichess. Tiếng Việt."
        ai = AIManager(cfg["openrouter"]["key_file"], cfg["openrouter"]["model"],
                       cfg["openrouter"]["max_tokens"], sp)
    return True

# ==================== HÀM HỖ TRỢ ====================
active_games = set()
pending_challenge = {"id": None, "time": 0}

def safe_move(gid, move):
    for i in range(3):
        try:
            client.bots.make_move(gid, move)
            return True
        except Exception as e:
            if "Not your turn" in str(e): return True
            log(f"⚠️ Gửi nước lỗi (lần {i+1}): {e}", "ERROR")
            time.sleep(1)
    return False

def chat(gid, msg):
    if not cfg["bot"]["chat_enabled"]: return
    try: client.bots.post_message(gid, msg)
    except: pass

def get_result(event, my_color):
    status = event.get('status', '')
    winner = event.get('winner', '')
    if status in ('draw', 'stalemate') or not winner: return "draw"
    return "win" if winner == my_color else "loss"

def smart_move(moves, board, total_moves):
    best, score, depth = engine.get_best_move(moves, board)
    if not USE_AI_MOVES or not ai: return best, score, depth
    th, lo, mn = cfg["bot"]["ai_help_threshold"]*100, cfg["bot"]["ai_help_losing"]*100, cfg["bot"]["ai_help_min_moves"]
    if total_moves >= mn and (abs(score) < th or score < lo):
        log(f"🆘 Thế cờ khó (eval={score/100:.1f}), hỏi AI...", "AI")
        cands = engine.get_top_moves(moves, 3)
        if cands:
            chosen = ai.choose_move(cands, moves, f"{score/100:.1f}")
            if chosen:
                for c in cands.values():
                    if c['move'] == chosen:
                        log(f"🤖 AI chọn: {chosen}", "AI")
                        return chosen, c['score'], c['depth']
    return best, score, depth

def play_game(gid):
    if gid in active_games: return
    active_games.add(gid)
    global pending_challenge
    pending_challenge = {"id": None, "time": 0}
    log(f"🎮 Bắt đầu ván: {gid}", "GAME")
    my_color = opp_name = None
    move_num = last_score = 0
    last_played_len = -1
    initial_fen = None
    variant = "standard"

    try:
        chat(gid, cfg["bot"]["chat_greeting"])
        for event in client.bots.stream_game_state(gid):
            if event['type'] == 'gameFull':
                white = event['white']
                my_color = 'white' if white.get('id', white.get('name', '')).lower() == account['id'].lower() else 'black'
                opp = event['black'] if my_color == 'white' else event['white']
                opp_name = opp.get('name', opp.get('id', '???'))
                initial_fen, variant = event.get('initialFen'), event.get('variant', {}).get('key', 'standard')
                log(f"♟️ {my_color} vs {opp_name} ({opp.get('rating', '?')}) | Variant: {variant}", "GAME")
                moves = event['state']['moves']
                ml = moves.split() if moves else []
                my_turn = (my_color == 'white' and len(ml) % 2 == 0) or (my_color == 'black' and len(ml) % 2 == 1)
                if my_turn and len(ml) > last_played_len:
                    board = moves_to_board(moves, initial_fen, variant)
                    move_num += 1
                    best, score, _ = smart_move(moves, board, len(ml))
                    last_score, last_played_len = score, len(ml)
                    log(f"➡️ #{move_num} {format_move(board, best)} | eval: {score/100:.1f}", "GAME")
                    safe_move(gid, best)

            elif event['type'] == 'gameState':
                moves = event['moves']
                status = event.get('status', 'started')
                if status != 'started':
                    result = get_result(event, my_color)
                    mc = len(moves.split()) if moves else 0
                    stats.add_game(result, opp_name or "???", mc)
                    log(f"🏁 {status} → {result} ({mc} nước)", "GAME")
                    chat(gid, cfg["bot"]["chat_gg"])
                    if USE_AI_MANAGEMENT and ai:
                        analysis = ai.analyze_game(moves, result, my_color or "?")
                        if analysis: log(f"🔬 {analysis}", "ANALYSIS")
                    break
                ml = moves.split() if moves else []
                my_turn = (my_color == 'white' and len(ml) % 2 == 0) or (my_color == 'black' and len(ml) % 2 == 1)
                if not my_turn or len(ml) <= last_played_len: continue
                board = moves_to_board(moves, initial_fen, variant)
                if cfg["bot"]["auto_resign"] and last_score < cfg["bot"]["resign_score"] * 100 and len(ml) >= cfg["bot"]["resign_min_moves"]:
                    log(f"🏳️ Resign (eval: {last_score/100:.1f})", "GAME")
                    chat(gid, cfg["bot"]["chat_resign"])
                    try: client.bots.resign_game(gid)
                    except: pass
                    break
                if cfg["bot"]["auto_draw"] and is_endgame_draw(board) and len(ml) >= cfg["bot"]["draw_min_moves"]:
                    try: client.bots.offer_draw(gid)
                    except: pass
                move_num += 1
                best, score, _ = smart_move(moves, board, len(ml))
                last_score, last_played_len = score, len(ml)
                log(f"➡️ #{move_num} {format_move(board, best)} | eval: {score/100:.1f}", "GAME")
                safe_move(gid, best)
    except Exception as e: log(f"❌ Lỗi ván {gid}: {e}", "ERROR")
    finally:
        active_games.discard(gid)
        if AUTO_CHALLENGE: threading.Thread(target=send_challenge).start()

def handle_challenge(ch):
    cid, name = ch['id'], ch.get('challenger', {}).get('name', '???')
    rating, variant = ch.get('challenger', {}).get('rating', 0), ch.get('variant', {}).get('key', 'standard')
    speed, tl, inc = ch.get('speed', '?'), ch.get('timeControl', {}).get('limit', '?'), ch.get('timeControl', {}).get('increment', '?')
    log(f"📩 Thách đấu: {name} ({rating}) {variant} {speed}", "CHALLENGE")
    if len(active_games) >= cfg["challenge"]["max_concurrent_games"]:
        try: client.bots.decline_challenge(cid)
        except: pass
        return
    if USE_AI_MANAGEMENT and ai:
        answer = ai.decide_challenge(name, rating, variant, speed, tl, inc)
        if answer and answer.startswith("DECLINE"):
            try: client.bots.decline_challenge(cid)
            except: pass
            log(f"❌ AI từ chối {name}", "CHALLENGE")
        else:
            try: client.bots.accept_challenge(cid)
            except: pass
            log(f"✅ AI chấp nhận {name}", "CHALLENGE")
    else:
        av, mn, mx = cfg["challenge"]["accept_variants"], cfg["challenge"]["min_rating"], cfg["challenge"]["max_rating"]
        if variant in av and (isinstance(rating, str) or mn <= rating <= mx):
            try: client.bots.accept_challenge(cid)
            except: pass
            log(f"✅ Chấp nhận {name}", "CHALLENGE")
        else:
            try: client.bots.decline_challenge(cid)
            except: pass
            log(f"❌ Từ chối {name}", "CHALLENGE")

def send_challenge():
    global pending_challenge
    if not AUTO_CHALLENGE or len(active_games) >= cfg["challenge"]["max_concurrent_games"] or pending_challenge["id"]: return
    try:
        bots = list(client.bots.get_online_bots(limit=30))
        opps = [b for b in bots if b['id'] != account['id']]
        if not opps: return
        target = random.choice(opps)
        cl_limit, cl_inc = cfg["challenge"]["default_clock_limit"], cfg["challenge"]["default_clock_increment"]
        log(f"🎯 Thách đấu: {target['username']}...", "CHALLENGE")
        res = client.challenges.create(target['id'], rated=cfg["challenge"]["rated"], clock_limit=cl_limit, clock_increment=cl_inc)
        pending_challenge = {"id": res['challenge']['id'], "time": time.time()}
    except: pass

# ==================== MAIN ====================
def main():
    while True:
        print("\n" + "=" * 55)
        print("🏠 MENU CHÍNH:")
        print("=" * 55)
        print("  1. 🚀 Bắt đầu Bot (Chọn chế độ)")
        print("  2. 🔑 Reset / Cài đặt API")
        print("  3. ❌ Thoát")
        print("=" * 55)
        choice = input("Chọn (1-3): ").strip()
        
        if choice == "1":
            if start_bot_flow():
                # Vòng lặp sự kiện chính của Bot
                if AUTO_CHALLENGE: threading.Thread(target=send_challenge).start()
                while True:
                    try:
                        for event in client.board.stream_incoming_events():
                            if event['type'] == 'gameStart':
                                gid = event['game']['gameId']
                                threading.Thread(target=play_game, args=(gid,), daemon=True).start()
                            elif event['type'] == 'challenge':
                                handle_challenge(event['challenge'])
                            elif event['type'] in ('challengeDeclined', 'challengeCanceled'):
                                if pending_challenge["id"] == event.get('challenge', {}).get('id'):
                                    pending_challenge = {"id": None, "time": 0}
                                    if AUTO_CHALLENGE: threading.Thread(target=send_challenge).start()
                            if AUTO_CHALLENGE and pending_challenge["id"]:
                                if time.time() - pending_challenge["time"] > 40:
                                    log(f"⏰ Hủy thách đấu {pending_challenge['id']}", "CHALLENGE")
                                    try: client.challenges.cancel(pending_challenge["id"])
                                    except: pass
                                    pending_challenge = {"id": None, "time": 0}
                                    threading.Thread(target=send_challenge).start()
                    except KeyboardInterrupt:
                        log("👋 Tắt bot...", "INFO")
                        engine.quit()
                        return # Trở về menu chính hoặc thoát hoàn toàn
                    except Exception as e:
                        log(f"⚠️ Lỗi kết nối: {e} - Thử lại...", "ERROR")
                        time.sleep(5)
        elif choice == "2":
            reset_api_menu()
        elif choice == "3":
            log("👋 Tạm biệt!", "INFO")
            break

if __name__ == "__main__":
    main()

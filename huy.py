import os, json, random, time, threading, berserk
from logger import log
from stats import Stats
from engine import Engine
from ai_manager import AIManager
from board_utils import moves_to_board, get_phase, format_move, is_endgame_draw

# ==================== CẤU HÌNH ====================
cfg = json.load(open("config.json", encoding="utf-8"))
log("📂 Đọc config.json")

# ==================== ĐĂNG NHẬP ====================
def login():
    tf = cfg["lichess"]["token_file"]
    while True:
        if os.path.exists(tf):
            token = open(tf).read().strip()
            log("📂 Đọc token từ file...")
        else:
            token = input("Nhập token Lichess: ").strip()
        session = berserk.TokenSession(token)
        cl = berserk.Client(session=session)
        try:
            acc = cl.account.get()
            log(f"✅ Đăng nhập: {acc['username']}")
            open(tf, "w").write(token)
            return cl, acc
        except Exception as e:
            log(f"❌ Token lỗi: {e}", "ERROR")
            if os.path.exists(tf):
                os.remove(tf)

client, account = login()

# ==================== CHỌN CHẾ ĐỘ ====================
print("\n" + "=" * 55)
print("🎮 CHỌN CHẾ ĐỘ:")
print("=" * 55)
print("  1. 🎄 NOAI ĐẦY ĐỦ  — Tự động tất cả, không AI")
print("  2. 🤖 AI ĐẦY ĐỦ    — AI quyết định mọi thứ (Tự tìm ván)")
print("  3. ♟️  CHỈ CHƠI      — CHỈ CHỜ thách đấu, không AI")
print("  4. 🧠 AI CHỈ CHƠI   — CHỈ CHỜ thách đấu, AI hỗ trợ")
print("=" * 55)
mode = input(f"Chọn (1-4) [{cfg['bot']['default_mode']}]: ").strip()
if mode not in ("1", "2", "3", "4"):
    mode = str(cfg["bot"]["default_mode"])

USE_AI = mode in ("2", "4")
AUTO_CHALLENGE = mode in ("1", "2")
NAMES = {"1": "🎄 NOAI ĐẦY ĐỦ", "2": "🤖 AI ĐẦY ĐỦ",
         "3": "♟️  CHỈ CHƠI", "4": "🧠 AI CHỈ CHƠI"}
log(f"Chế độ: {NAMES[mode]}")

# ==================== KHỞI TẠO ====================
engine = Engine(
    threads=cfg["stockfish"]["threads"], hash_mb=cfg["stockfish"]["hash_mb"],
    skill=cfg["stockfish"]["skill_level"], think_ms=cfg["stockfish"]["think_time_ms"],
    min_think=cfg["stockfish"]["min_think_ms"], max_think=cfg["stockfish"]["max_think_ms"],
    smart_time=cfg["bot"]["smart_time"]
)
stats = Stats()
ai = None
if USE_AI:
    sp = f'Bạn là AI quản lý bot cờ vua "{account["username"]}". Trả lời ĐÚNG format, không thừa.'
    ai = AIManager(cfg["openrouter"]["key_file"], cfg["openrouter"]["model"],
                   cfg["openrouter"]["max_tokens"], sp)

# ==================== HÀM HỖ TRỢ ====================
active_games = set()
pending_challenge = {"id": None, "time": 0}

def safe_move(gid, move):
    for i in range(3):
        try:
            client.bots.make_move(gid, move)
            return True
        except Exception as e:
            # Nếu lỗi là "Không phải lượt của bạn", tức là nước đi đã được gửi rồi
            if "Not your turn" in str(e):
                return True
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

# ==================== NƯỚC ĐI THÔNG MINH ====================
def smart_move(moves, board, total_moves):
    best, score, depth = engine.get_best_move(moves, board)
    if not USE_AI or not ai: return best, score, depth

    th = cfg["bot"]["ai_help_threshold"] * 100
    lo = cfg["bot"]["ai_help_losing"] * 100
    mn = cfg["bot"]["ai_help_min_moves"]

    if total_moves >= mn and (abs(score) < th or score < lo):
        log(f"🆘 Thế cờ khó (eval={score/100:.1f}), hỏi AI...", "AI")
        cands = engine.get_top_moves(moves, 3)
        if cands:
            chosen = ai.choose_move(cands, moves, f"{score/100:.1f}")
            stats.add_ai_help()
            if chosen:
                for c in cands.values():
                    if c['move'] == chosen:
                        log(f"🤖 AI chọn: {chosen}", "AI")
                        return chosen, c['score'], c['depth']
    return best, score, depth

# ==================== CHƠI CỜ ====================
def play_game(gid):
    if gid in active_games: return
    active_games.add(gid)
    global pending_challenge
    pending_challenge = {"id": None, "time": 0}
    
    log(f"🎮 Bắt đầu ván: {gid}", "GAME")
    my_color = opp_name = None
    move_num = 0
    last_score = 0
    last_played_len = -1 # Tránh đánh 2 lần cùng 1 lượt
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
                initial_fen = event.get('initialFen')
                variant = event.get('variant', {}).get('key', 'standard')
                
                log(f"♟️ {my_color} vs {opp_name} ({opp.get('rating', '?')}) | Variant: {variant}", "GAME")
                moves = event['state']['moves']
                ml = moves.split() if moves else []
                
                my_turn = (my_color == 'white' and len(ml) % 2 == 0) or \
                          (my_color == 'black' and len(ml) % 2 == 1)
                
                if my_turn and len(ml) > last_played_len:
                    board = moves_to_board(moves, initial_fen, variant)
                    move_num += 1
                    best, score, _ = smart_move(moves, board, len(ml))
                    last_score = score
                    last_played_len = len(ml)
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
                    if USE_AI and ai:
                        analysis = ai.analyze_game(moves, result, my_color or "?")
                        if analysis: log(f"🔬 {analysis}", "ANALYSIS")
                    break

                ml = moves.split() if moves else []
                my_turn = (my_color == 'white' and len(ml) % 2 == 0) or \
                          (my_color == 'black' and len(ml) % 2 == 1)
                
                if not my_turn or len(ml) <= last_played_len:
                    continue

                board = moves_to_board(moves, initial_fen, variant)
                
                # Auto resign
                if cfg["bot"]["auto_resign"] and last_score < cfg["bot"]["resign_score"] * 100 \
                   and len(ml) >= cfg["bot"]["resign_min_moves"]:
                    log(f"🏳️ Resign (eval: {last_score/100:.1f})", "GAME")
                    chat(gid, cfg["bot"]["chat_resign"])
                    try: client.bots.resign_game(gid)
                    except: pass
                    break

                # Auto draw
                if cfg["bot"]["auto_draw"] and is_endgame_draw(board) and len(ml) >= cfg["bot"]["draw_min_moves"]:
                    try: client.bots.offer_draw(gid)
                    except: pass

                move_num += 1
                best, score, _ = smart_move(moves, board, len(ml))
                last_score = score
                last_played_len = len(ml)
                log(f"➡️ #{move_num} {format_move(board, best)} | eval: {score/100:.1f}", "GAME")
                safe_move(gid, best)

    except Exception as e:
        log(f"❌ Lỗi ván {gid}: {e}", "ERROR")
    finally:
        active_games.discard(gid)
        if AUTO_CHALLENGE:
            threading.Thread(target=send_challenge).start()

# ==================== THÁCH ĐẤU ====================
def handle_challenge(ch):
    cid = ch['id']
    name = ch.get('challenger', {}).get('name', '???')
    rating = ch.get('challenger', {}).get('rating', 0)
    variant = ch.get('variant', {}).get('key', 'standard')
    speed = ch.get('speed', '?')
    tl = ch.get('timeControl', {}).get('limit', '?')
    inc = ch.get('timeControl', {}).get('increment', '?')
    log(f"📩 Thách đấu: {name} ({rating}) {variant} {speed}", "CHALLENGE")

    if len(active_games) >= cfg["challenge"]["max_concurrent_games"]:
        try: client.bots.decline_challenge(cid)
        except: pass
        return

    if USE_AI and ai:
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
        av = cfg["challenge"]["accept_variants"]
        mn = cfg["challenge"]["min_rating"]
        mx = cfg["challenge"]["max_rating"]
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
    if not AUTO_CHALLENGE or len(active_games) >= cfg["challenge"]["max_concurrent_games"] or pending_challenge["id"]:
        return

    try:
        bots = list(client.bots.get_online_bots(limit=30))
        opps = [b for b in bots if b['id'] != account['id']]
        if not opps: return
        target = random.choice(opps)
        cl_limit, cl_inc = cfg["challenge"]["default_clock_limit"], cfg["challenge"]["default_clock_increment"]
        log(f"🎯 Thách đấu: {target['username']}...", "CHALLENGE")
        res = client.challenges.create(target['id'], rated=cfg["challenge"]["rated"],
                                       clock_limit=cl_limit, clock_increment=cl_inc)
        pending_challenge = {"id": res['challenge']['id'], "time": time.time()}
    except: pass

# ==================== MAIN ====================
print("\n" + "=" * 55)
log(f"🚀 BOT KHỞI ĐỘNG — {NAMES[mode]}")
print("=" * 55 + "\n")

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
        break
    except Exception as e:
        log(f"⚠️ Lỗi kết nối: {e} - Thử lại...", "ERROR")
        time.sleep(5)

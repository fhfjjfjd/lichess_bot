import telebot
import os, json, sys, threading, time
from core import BotCore, get_path, load_settings
from logger import log

# 1. Khởi tạo cấu hình Telegram
cfg = load_settings()
tg_token = cfg["telegram"]["token"]
admin_id = cfg["telegram"]["chat_id"]

if not tg_token or tg_token == "NHẬP_TOKEN_CỦA_BẠN_TẠI_ĐÂY":
    print("
" + "=" * 55) # Sử dụng '=' thay vì '!'
    print("  TELEGRAM BOT SETUP") # Dùng tiếng Anh cho nhất quán với README
    print("=" * 55)
    tg_token = input("🤖 Nhập Telegram Bot Token: ").strip()
    admin_id = input("🆔 Nhập Telegram Chat ID của bạn: ").strip()
    cfg["telegram"]["token"], cfg["telegram"]["chat_id"] = tg_token, admin_id
    with open(get_path("settings.json"), "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=4, ensure_ascii=False)
    log("✅ Đã lưu cấu hình Telegram.", "INFO")

bot = telebot.TeleBot(tg_token)
lichess_bot = None

HELP_TEXT = """
♟️ *LICHESS BOT CONTROL PANEL* ♟️

🚀 *Lệnh vận hành:*
/start - Bật bot (Chế độ tự động tìm ván).
/stop - Dừng bot đánh cờ (Vẫn giữ kết nối Telegram).
/cancel - Hủy lời mời thách đấu đang treo.
/shutdown - Tắt hoàn toàn chương trình bot (Dừng lạnh).

📊 *Lệnh thông tin & Dữ liệu:*
/status - Kiểm tra trạng thái hiện tại của bot.
/stats - Xem thống kê thắng/thua.
/resetstats - Xóa toàn bộ thống kê (Về 0).
/link - Lấy link ván đang đánh.
/log [N] - Lấy N dòng log gần nhất (mặc định 20).

⚙️ *Lệnh cấu hình:*
/setmode [1-4] - Đổi chế độ chơi của bot (ví dụ: /setmode 1).

❓ *Hỗ trợ:*
/help - Hiện bảng hướng dẫn này.
"""

def on_game_start_callback(gid, opponent, rating, url):
    try: bot.send_message(admin_id, f"🎮 *VÁN MỚI!*
👤 `{opponent}` ({rating})
🔗 {url}", parse_mode="Markdown")
    except: pass

def on_game_end_callback(status, result, mc):
    icon = "🎉" if result == "win" else "😔" if result == "loss" else "🤝"
    try: bot.send_message(admin_id, f"🏁 *KẾT THÚC!* {icon}
📊 `{status}`
🏆 *{result.upper()}*
🔢 `{mc}` nước", parse_mode="Markdown")
    except: pass

@bot.message_handler(commands=['help'])
def help_handler(message):
    if str(message.chat.id) == str(admin_id):
        bot.send_message(message.chat.id, HELP_TEXT, parse_mode="Markdown")

@bot.message_handler(commands=['start', 'run'])
def start_handler(message):
    global lichess_bot
    if str(message.chat.id) != str(admin_id): return
    if lichess_bot and lichess_bot.running:
        bot.reply_to(message, "⚠️ Bot đã đang chạy rồi!")
        return
    
    bot.reply_to(message, "🚀 Đang khởi động Lichess Bot...")
    lichess_bot = BotCore(use_ai_mgmt=True, use_ai_moves=False, auto_challenge=True)
    lichess_bot.on_game_start, lichess_bot.on_game_end = on_game_start_callback, on_game_end_callback
    threading.Thread(target=lichess_bot.run, daemon=True).start()
    bot.send_message(admin_id, "✅ Bot đã chạy và đang tìm đối thủ!")

@bot.message_handler(commands=['stop'])
def stop_handler(message):
    global lichess_bot
    if str(message.chat.id) != str(admin_id): return
    if lichess_bot:
        lichess_bot.running = False
        if lichess_bot.engine: lichess_bot.engine.quit()
        for t in threading.enumerate():
            if t.name.startswith('Thread-') or t.name.startswith('Dummy-'): 
                 t.join(timeout=0.1)
        lichess_bot = None
        bot.reply_to(message, "🛑 Đã dừng Lichess Bot.")
    else: bot.reply_to(message, "⚠️ Bot chưa chạy.")

@bot.message_handler(commands=['cancel'])
def cancel_handler(message):
    if str(message.chat.id) != str(admin_id): return
    if lichess_bot and lichess_bot.pending_challenge["id"]:
        try:
            lichess_bot.client.challenges.cancel(lichess_bot.pending_challenge["id"])
            bot.reply_to(message, f"🚫 Đã hủy thách đấu với `{lichess_bot.pending_challenge['target']}`.")
            lichess_bot.pending_challenge = {"id": None, "time": 0, "target": ""}
        except: bot.reply_to(message, "❌ Không thể hủy (có thể đối thủ đã nhận hoặc từ chối).")
    else: bot.reply_to(message, "ℹ️ Không có thách đấu nào đang treo.")

@bot.message_handler(commands=['resetstats'])
def resetstats_handler(message):
    if str(message.chat.id) != str(admin_id): return
    path = get_path("stats.json")
    if os.path.exacts("stats.json"):
        os.remove(path)
        log("🗑️ Đã xóa file thống kê cũ.", "WARN")
        if lichess_bot:
            from stats import Stats
            lichess_bot.stats = Stats()
        bot.reply_to(message, "✅ *Đã xóa toàn bộ thống kê.* Bot sẽ bắt đầu đếm lại từ ván sau!", parse_mode="Markdown")
    else: bot.reply_to(message, "ℹ️ Hiện chưa có dữ liệu thống kê để xóa.")

@bot.message_handler(commands=['shutdown'])
def shutdown_handler(message):
    if str(message.chat.id) != str(admin_id): return
    bot.send_message(admin_id, "🔌 *Đang tắt toàn bộ hệ thống...* Tạm biệt!", parse_mode="Markdown")
    if lichess_bot:
        lichess_bot.running = False
        if lichess_bot.engine: lichess_bot.engine.quit()
    os._exit(0)

@bot.message_handler(commands=['status'])
def status_handler(message):
    if str(message.chat.id) != str(admin_id): return
    if not lichess_bot: bot.reply_to(message, "🔴 Bot đang DỪNG.")
    else:
        s = "⚔️ Đang thi đấu" if lichess_bot.active_games else "🔎 Đang tìm ván"
        bot.reply_to(message, f"🟢 Bot đang CHẠY.
📊 Trạng thái: {s}")

@bot.message_handler(commands=['stats'])
def stats_handler(message):
    if str(message.chat.id) != str(admin_id): return
    from stats import Stats
    s = lichess_bot.stats if lichess_bot else Stats()
    d = s.data
    wr = (d["wins"] / d["games"] * 100) if d["games"] > 0 else 0
    msg = f"📊 *THỐNG KÊ:*

🔢 Tổng: `{d['games']}`
🏆 Thắng: `{d['wins']}` ({wr:.1f}%)
😔 Thua: `{d['losses']}`
🤝 Hòa: `{d['draws']}`
🔥 Chuỗi hiện tại: `{d['current_streak']}`"
    bot.send_message(admin_id, msg, parse_mode="Markdown")

@bot.message_handler(commands=['link'])
def link_handler(message):
    if str(message.chat.id) != str(admin_id): return
    if lichess_bot and lichess_bot.active_games:
        for gid in lichess_bot.active_games: bot.reply_to(message, f"🔗 https://lichess.org/{gid}")
    else: bot.reply_to(message, "❌ Không có ván nào đang diễn ra.")

if __name__ == "__main__":
    log("📡 Hệ thống Telegram đang chờ lệnh...")
    try: bot.send_message(admin_id, HELP_TEXT, parse_mode="Markdown")
    except Exception as e:
        log(f"❌ Không thể gửi tin nhắn chào mừng: {e}", "ERROR")
    bot.infinity_polling()

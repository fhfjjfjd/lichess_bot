import telebot
import os, json, sys, threading, time
from core import BotCore
from logger import log

# Load settings
with open("settings.json") as f:
    cfg = json.load(f)

tg_token = cfg["telegram"]["token"]
admin_id = cfg["telegram"]["chat_id"]

if tg_token == "NHẬP_TOKEN_CỦA_BẠN_TẠI_ĐÂY":
    print("❌ Lỗi: Bạn chưa nhập Telegram Token trong settings.json!")
    sys.exit(1)

bot = telebot.TeleBot(tg_token)
lichess_bot = None
bot_thread = None

def get_status_text():
    if not lichess_bot: return "🔴 Bot đang DỪNG."
    game_count = len(lichess_bot.active_games)
    status = "⚔️ Đang THI ĐẤU" if game_count > 0 else "🔎 Đang TÌM VÁN"
    return f"🟢 Bot đang CHẠY.\n📊 Trạng thái: {status}\n🎮 Số ván đang chơi: {game_count}"

@bot.message_handler(commands=['start', 'run'])
def start_handler(message):
    global lichess_bot, bot_thread
    if str(message.chat.id) != str(admin_id): return
    
    if lichess_bot and lichess_bot.running:
        bot.reply_to(message, "⚠️ Bot đã đang chạy rồi!")
        return
    
    bot.reply_to(message, "🚀 Đang khởi động Lichess Bot (Chế độ SMART AUTO)...")
    lichess_bot = BotCore(use_ai_mgmt=True, use_ai_moves=False, auto_challenge=True)
    bot_thread = threading.Thread(target=lichess_bot.run, daemon=True)
    bot_thread.start()
    bot.send_message(admin_id, "✅ Bot đã sẵn sàng và đang tìm đối thủ!")

@bot.message_handler(commands=['stop'])
def stop_handler(message):
    global lichess_bot
    if str(message.chat.id) != str(admin_id): return
    if lichess_bot:
        lichess_bot.running = False
        if lichess_bot.engine: lichess_bot.engine.quit()
        lichess_bot = None
        bot.reply_to(message, "🛑 Đã dừng Lichess Bot.")
    else:
        bot.reply_to(message, "⚠️ Bot chưa chạy.")

@bot.message_handler(commands=['status'])
def status_handler(message):
    if str(message.chat.id) != str(admin_id): return
    bot.reply_to(message, get_status_text())

@bot.message_handler(commands=['stats'])
def stats_handler(message):
    if str(message.chat.id) != str(admin_id): return
    if not lichess_bot:
        bot.reply_to(message, "⚠️ Hãy /start bot trước để xem thống kê.")
        return
    d = lichess_bot.stats.data
    total = d["games"]
    wr = (d["wins"] / total * 100) if total > 0 else 0
    msg = f"📊 *THỐNG KÊ BOT:*\n\n" \
          f"🔢 Tổng ván: `{total}`\n" \
          f"🏆 Thắng: `{d['wins']}` ({wr:.1f}%)\n" \
          f"😔 Thua: `{d['losses']}`\n" \
          f"🤝 Hòa: `{d['draws']}`\n" \
          f"🔥 Chuỗi thắng: `{d['current_streak']}`"
    bot.send_message(admin_id, msg, parse_mode="Markdown")

@bot.message_handler(commands=['help'])
def help_handler(message):
    msg = "🎮 *DANH SÁCH LỆNH ĐIỀU KHIỂN:*\n\n" \
          "/start - Khởi động bot\n" \
          "/stop - Dừng bot\n" \
          "/status - Kiểm tra trạng thái\n" \
          "/stats - Xem thống kê thắng thua\n" \
          "/help - Hiện bản hướng dẫn này"
    bot.send_message(message.chat.id, msg, parse_mode="Markdown")

if __name__ == "__main__":
    log("📡 Hệ thống điều khiển Telegram đang chờ lệnh...")
    bot.infinity_polling()

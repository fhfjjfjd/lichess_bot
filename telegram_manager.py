import telebot
import os, json
from logger import log

class TelegramManager:
    def __init__(self, token, chat_id):
        self.bot = telebot.TeleBot(token) if token and token != "NHẬP_TOKEN_CỦA_BẠN_TẠI_ĐÂY" else None
        self.chat_id = chat_id
        self.enabled = self.bot is not None

    def send_msg(self, text):
        if not self.enabled or not self.chat_id: return
        try:
            self.bot.send_message(self.chat_id, text, parse_mode="Markdown")
        except Exception as e:
            log(f"⚠️ Không thể gửi tin nhắn Telegram: {e}", "ERROR")

    def notify_game_start(self, gid, opponent, rating, url):
        msg = f"🎮 *VÁN ĐẤU MỚI BẮT ĐẦU!*\n\n" \
              f"👤 Đối thủ: `{opponent}` ({rating})\n" \
              f"🔗 Link: {url}\n\n" \
              f"🔥 Chúc bot may mắn!"
        self.send_msg(msg)

    def notify_game_end(self, status, result, mc):
        icon = "🎉" if result == "win" else "😔" if result == "loss" else "🤝"
        msg = f"🏁 *VÁN ĐẤU KẾT THÚC!* {icon}\n\n" \
              f"📊 Trạng thái: `{status}`\n" \
              f"🏆 Kết quả: *{result.upper()}*\n" \
              f"🔢 Số nước: `{mc}`"
        self.send_msg(msg)

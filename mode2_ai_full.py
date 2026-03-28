from core import BotCore

if __name__ == "__main__":
    # Chế độ 2: Tự động hoàn toàn, AI chọn nước đi (True, True, True)
    bot = BotCore(use_ai_mgmt=True, use_ai_moves=True, auto_challenge=True)
    bot.run()

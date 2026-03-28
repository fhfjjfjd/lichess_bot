from core import BotCore

if __name__ == "__main__":
    # Chế độ 1: Tự động, Stockfish đánh, AI quản lý (True, False, True)
    bot = BotCore(use_ai_mgmt=True, use_ai_moves=False, auto_challenge=True)
    bot.run()

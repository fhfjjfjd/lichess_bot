from core import BotCore

if __name__ == "__main__":
    # Chế độ 4: Chế độ thụ động, AI hỗ trợ đánh (True, True, False)
    bot = BotCore(use_ai_mgmt=True, use_ai_moves=True, auto_challenge=False)
    bot.run()

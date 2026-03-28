from core import BotCore

if __name__ == "__main__":
    # Chế độ 3: Chế độ thụ động, không dùng AI (False, False, False)
    bot = BotCore(use_ai_mgmt=False, use_ai_moves=False, auto_challenge=False)
    bot.run()

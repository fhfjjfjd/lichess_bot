# ♟️ Lichess Bot - Stockfish 18 + Gemini AI

An automated Lichess chess bot optimized for Termux (Android), Linux, and Windows. It integrates **Stockfish 18** and **Gemini AI** with **Telegram Remote Control**.

## 🌟 Key Features

- **Extreme Performance:** Powered by Stockfish 18 (8 threads, 400MB Hash).
- **AI Brain:** Uses Gemini 2.0 Flash for management and tactical assistance.
- **Telegram Control:** Remote control your bot via Telegram (start/stop/stats/links).
- **Auto-Installation:** Setup everything with a single command.
- **Smart Management:** Auto-cancels dead challenges and handles Chess960.

## 🚀 Quick Start (Recommended)

1. **Clone and Install:**
   ```bash
   git clone https://github.com/fhfjjfjd/lichess_bot
   cd lichess_bot
   pip install -r requirements.txt
   bash install.sh
   ```

2. **Run the Launcher:**
   ```bash
   python3 huy.py
   ```
   - Select **Mode 5 (Telegram Control)**.
   - The bot will automatically ask for your **Telegram Token** and **Chat ID** on the first run.

## 📱 Telegram Commands

- `/start` - Start the bot searching for games.
- `/stop` - Stop the bot.
- `/status` - Check current activity.
- `/stats` - View win/loss statistics.
- `/help` - Show command list.

## ⚙️ Settings (`settings.json`)

- `show_game_url`: Toggle live game link display (True/False).
- `save_log_file`: Toggle persistent logging to `bot.log`.
- `telegram`: Configure your bot token and chat ID.

## ⚠️ Important

- **BOT Account:** You **must** use a dedicated Lichess BOT account.
- **Upgrade:** Use `python3 upgrade_to_bot.py` to upgrade a clean account.

## 📜 License

MIT License.

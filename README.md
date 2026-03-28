# ♟️ Lichess Bot - Stockfish 18 + Gemini AI

An automated Lichess chess bot optimized for Termux (Android), Linux, and Windows. It integrates **Stockfish 18**, the world's strongest engine, and **Gemini AI** (via OpenRouter) for intelligent management and decision-making.

## 🌟 Key Features

- **High Performance:** Configured for 8 threads and 400MB Hash RAM for deep analysis.
- **AI Brain:** Uses Gemini 2.0 Flash for management and tactical assistance.
- **Interactive Menu System:**
  - **Start Bot:** Choose your preferred game mode (1-4).
  - **Restart:** Reload the application and configuration.
  - **Reset API:** Reset Lichess Token or OpenRouter Key.
  - **Telegram Control (Beta):** Control bot via Telegram commands.
- **Chess960 Support:** Full synchronization with Fischer Random variants.
- **Smart Challenge Management:** Automatically finds and challenges online bots; cancels dead requests after 40 seconds.

## 🚀 Quick Start

### Method 1: Automatic Installation (Recommended)

1. **On Termux / Linux:**
   ```bash
   git clone https://github.com/fhfjjfjd/lichess_bot
   cd lichess_bot
   bash install.sh
   ```

2. **On Windows:**
   - Download the repository and run `install.bat`.

---

### Method 2: Manual Setup

1. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Setup Tokens:**
   - Create `lichess.token` and `openrouter.key` files.
   - **Required Lichess Scopes:** `preference:read`, `email:read`, `challenge:read`, `challenge:write`, `bot:play`.
   - **Optional Scopes:** `challenge:bulk`, `tournament:write`, `team:read`, `team:write`, `puzzle:read`, `puzzle:write`, `racer:write`, `study:read`, `study:write`, `engine:read`, `engine:write`.

3. **Upgrade Account to BOT:**
   - **Warning:** Permanent and only for accounts with 0 games played.
   - Run `python3 upgrade_to_bot.py` and type `CONFIRM`.

4. **Run the Bot Launcher:**
   ```bash
   python3 huy.py
   ```
   - You will be presented with a main menu:
     - `1. SMART AUTO`
     - `2. AI FULL`
     - `3. ONLY PLAY`
     - `4. AI PASSIVE`
     - `5. TELEGRAM CONTROL (Beta)`
     - `6. Restart Bot`
     - `7. Reset API`
     - `8. Exit`

## ⚙️ Configuration (`settings.json`)

- `show_game_url`: Toggle live game link display in console (True/False).
- `save_log_file`: Toggle persistent logging to `bot.log` (True/False).
- `telegram`: Configure your bot token and chat ID.
- `training`: Settings for bot's self-improvement (enabled, analysis time, boost).

## ⚠️ Important

- **BOT Account:** You **must** use a dedicated Lichess BOT account.
- **Security:** Never share your token/key files.

## 📜 License

MIT License.

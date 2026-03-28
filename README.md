# ♟️ Lichess Bot - Stockfish 18 + Gemini AI

An automated Lichess chess bot optimized for Termux (Android), Linux, and Windows. It integrates the world's strongest engine, **Stockfish 18**, and **Gemini AI** (via OpenRouter) for intelligent decision-making and interaction with opponents.

## 🌟 Key Features

- **Extreme Performance:** Powered by Stockfish 18, capable of analyzing millions of positions per second.
- **AI Integration:** Uses Gemini 2.0 Flash to select optimal moves in complex positions and analyze games after they finish.
- **4 Flexible Game Modes:**
  1. `NOAI FULL`: Fully automated, uses pure Stockfish for all moves.
  2. `AI FULL`: Fully automated, AI assists in difficult tactical decisions.
  3. `ONLY PLAY`: Passive mode, waits for incoming challenges or your manual challenges on the web.
  4. `🧠 AI ONLY PLAY`: Passive mode with AI assistance for moves.
- **Chess960 Support:** Automatically detects and handles Fischer Random (Chess960) variants.
- **Smart Management:** Automatically cancels pending challenges if not accepted within 40 seconds.
- **Detailed Statistics:** Tracks win/loss ratios, win streaks, and AI effectiveness.

## 🛠️ System Requirements

- **OS:** Android (Termux), Linux, or Windows.
- **Language:** Python 3.10+.
- **Engine:** `stockfish` (Available in most package managers or from the Stockfish homepage).

## 🚀 Quick Start

### Method 1: Automatic Installation (Recommended)

1. **On Termux / Linux:**
   ```bash
   git clone https://github.com/fhfjjfjd/lichess_bot
   cd lichess_bot
   bash install.sh
   ```

2. **On Windows:**
   - Download the project.
   - Double-click the `install.bat` file.

---

### Method 2: Manual Installation

1. **Install required packages:**
   ```bash
   pkg install python git stockfish -y
   pip install berserk python-chess openai==0.28.1 requests
   ```

2. **Configure Authentication (Tokens):**
   - Create a `lichess.token` file: Paste your API Token from [Lichess API Settings](https://lichess.org/account/oauth/token).
   - **Required Scopes (Essential for Bot):**
     - `Read preferences` (`preference:read`)
     - `Read email address` (`email:read`)
     - `Read incoming challenges` (`challenge:read`)
     - `Create, accept, decline challenges` (`challenge:write`)
     - `Play games with the bot API` (`bot:play`)
   - **Optional Scopes (For Extended Features):**
     - `Create multiple challenges` (`challenge:bulk`)
     - `Create, update, and join tournaments` (`tournament:write`)
     - `Read private team info` (`team:read`)
     - `Join and leave teams` (`team:write`)
     - `Read puzzle activities` (`puzzle:read`)
     - `Solve puzzles` (`puzzle:write`)
     - `Create and join puzzle races` (`racer:write`)
     - `Read private studies and broadcasts` (`study:read`)
     - `Create, update, delete studies and broadcasts` (`study:write`)
     - `View and use external engines` (`engine:read`)
     - `Create and update external engines` (`engine:write`)
   - Create an `openrouter.key` file: Paste your API Key from [OpenRouter](https://openrouter.ai/).

3. **Upgrade to BOT Account:**
   - **IMPORTANT:** Upgrading to a BOT account is **permanent** and **irreversible**.
   - Your account **must not have played any games** prior to the upgrade. It is recommended to create a new account specifically for the bot.
   - Run the upgrade script:
     ```bash
     python3 upgrade_to_bot.py
     ```
   - Type `CONFIRM` when prompted to complete the process.

4. **Run the Bot:**
   ```bash
   python3 huy.py
   ```

## ⚙️ Configuration (`config.json`)

You can customize various parameters in `config.json`:
- `threads`: Number of CPU cores for Stockfish (Recommended: 2-4 on mobile).
- `think_time_ms`: Time Stockfish thinks for each move.
- `ai_help_threshold`: Position evaluation threshold for the bot to ask AI for help.
- `auto_resign`: Automatically resign when the position is too weak.

## ⚠️ Important Notes

- **BOT Account:** You **must** use a Lichess account upgraded to BOT mode. Using a normal user account will result in an immediate ban.
- **Security:** Never share your `lichess.token` and `openrouter.key` files with anyone.

## 📜 License

This project is released under the MIT License. Enjoy your experience with this pocket-sized "Grandmaster"!

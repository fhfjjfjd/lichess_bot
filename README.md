# ♟️ Lichess Bot - Stockfish 18 + Gemini AI

An automated Lichess chess bot optimized for Termux (Android), Linux, and Windows. It integrates **Stockfish 18**, the world's strongest engine, and **Gemini AI** (via OpenRouter) for intelligent management and decision-making.

## 🌟 Key Features

- **High Performance:** Configured for 8 threads and 400MB Hash RAM for deep analysis.
- **AI Management:** Uses Gemini 2.0 Flash to handle chat, analyze games, and decide on challenges.
- **4 Professional Game Modes:**
  1. `🤖 SMART AUTO`: Fully automated. Stockfish makes moves, AI manages interaction.
  2. `🧠 AI FULL`: Fully automated. AI assists in choosing moves in sharp positions.
  3. `♟️ ONLY PLAY`: Passive mode. Waits for challenges, pure Stockfish play.
  4. `🧠 AI PASSIVE`: Passive mode. Waits for challenges, AI assists in moves.
- **Interactive Menu System:**
  - **Start Bot:** Easily select your preferred mode.
  - **Restart:** Instantly reload the application and configuration.
  - **Reset API:** Securely wipe and re-enter Lichess or OpenRouter credentials.
- **Chess960 Support:** Full synchronization with Fischer Random variants.
- **Smart Challenge Management:** Automatically finds and challenges online bots; cancels dead requests after 40 seconds.

## 🛠️ System Requirements

- **OS:** Android (Termux), Linux, or Windows.
- **Language:** Python 3.10+.
- **Engine:** `stockfish` (Installed via `pkg install stockfish` on Termux).

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
   pip install berserk python-chess openai==0.28.1 requests
   ```

2. **Setup Tokens:**
   - Create `lichess.token` and `openrouter.key` files in the root folder.
   - **Required Scopes:** `preference:read`, `email:read`, `challenge:read`, `challenge:write`, `bot:play`.

3. **Upgrade Account to BOT:**
   - **Warning:** Permanent and only for accounts with 0 games played.
   - Run `python3 upgrade_to_bot.py` and type `CONFIRM`.

4. **Run the Bot:**
   ```bash
   python3 huy.py
   ```

## ⚙️ Performance Configuration (`settings.json`)

The bot is pre-configured for high-end mobile performance:
- `threads`: 8
- `hash_mb`: 400
- `think_time_ms`: 3000

## 📜 License

Distributed under the MIT License.

@echo off
TITLE Lichess Bot Installer (Windows)
echo 🚀 Bat dau cai dat Lichess Bot cho Windows...

echo 📦 Dang cai dat cac thu vien Python...
python -m pip install --upgrade pip
pip install berserk python-chess openai==0.28.1 requests

if not exist lichess.token (
    echo 🔑 Tao file lichess.token...
    type nul > lichess.token
)

if not exist openrouter.key (
    echo 🔑 Tao file openrouter.key...
    type nul > openrouter.key
)

echo.
echo ✅ CAI DAT HOAN TAT!
echo -------------------------------------------------------
echo 1. Paste your Lichess Token into 'lichess.token'
echo    (Required scopes: preference:read, email:read, challenge:read, challenge:write, bot:play)
echo 2. Paste your OpenRouter Key into 'openrouter.key'
echo 3. Dam bao ban da tai Stockfish.exe va de trong PATH
echo 4. Chay bot bang lenh: python huy.py
echo -------------------------------------------------------
pause

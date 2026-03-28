#!/bin/bash
# Lichess Bot Auto Installer (Linux/Termux)

echo "🚀 Bắt đầu cài đặt Lichess Bot..."

# Kiểm tra môi trường Termux
if [ -d "/data/data/com.termux" ]; then
    echo "📱 Phát hiện môi trường Termux. Đang cập nhật gói hệ thống..."
    pkg update && pkg upgrade -y
    pkg install python stockfish git -y
else
    echo "🐧 Phát hiện môi trường Linux. Đang kiểm tra các gói cần thiết..."
    # Kiểm tra python3
    if ! command -v python3 &> /dev/null; then
        echo "❌ Lỗi: Chưa cài đặt python3. Vui lòng cài đặt trước."
        exit 1
    fi
    # Kiểm tra stockfish
    if ! command -v stockfish &> /dev/null; then
        echo "⚠️ Cảnh báo: Chưa tìm thấy 'stockfish' trong hệ thống. Vui lòng cài đặt bằng trình quản lý gói của bạn (ví dụ: sudo apt install stockfish)."
    fi
fi

echo "📦 Đang cài đặt các thư viện Python..."
pip install --upgrade pip
pip install berserk python-chess openai==0.28.1 requests

# Thiết lập file bí mật nếu chưa có
if [ ! -f "lichess.token" ]; then
    echo "🔑 Tạo file lichess.token..."
    touch lichess.token
fi

if [ ! -f "openrouter.key" ]; then
    echo "🔑 Tạo file openrouter.key..."
    touch openrouter.key
fi

echo ""
echo "✅ CÀI ĐẶT HOÀN TẤT!"
echo "-------------------------------------------------------"
echo "1. Paste your Lichess Token into 'lichess.token'"
echo "   Required Scopes:"
echo "   - Essential: preference:read, email:read, challenge:read, challenge:write, bot:play"
echo "   - Extended: challenge:bulk, tournament:write, team:read, team:write, puzzle:read,"
echo "               puzzle:write, racer:write, study:read, study:write, engine:read, engine:write"
echo "2. Paste your OpenRouter Key into 'openrouter.key'"
echo "3. Chạy bot bằng lệnh: python3 huy.py"
echo "-------------------------------------------------------"

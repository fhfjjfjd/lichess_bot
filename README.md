# ♟️ Lichess Bot - Stockfish 18 + Gemini AI

Một bot chơi cờ vua tự động trên Lichess được tối ưu hóa cho môi trường Termux (Android), tích hợp công cụ mạnh nhất thế giới **Stockfish 18** và trí tuệ nhân tạo **Gemini AI** (thông qua OpenRouter) để đưa ra các quyết định thông minh và giao tiếp với đối thủ.

## 🌟 Tính năng nổi bật

- **Engine cực mạnh:** Sử dụng Stockfish 18 (bản mới nhất) với khả năng phân tích hàng triệu nước đi/giây.
- **Tích hợp AI:** Sử dụng Gemini 2.0 Flash để chọn nước đi tối ưu trong các thế cờ khó và phân tích ván đấu sau khi kết thúc.
- **4 Chế độ chơi linh hoạt:**
  1. `NOAI ĐẦY ĐỦ`: Tự động tìm ván và đánh bằng Stockfish thuần túy.
  2. `AI ĐẦY ĐỦ`: Tự động tìm ván, AI tham gia quyết định mọi nước đi khó.
  3. `CHỈ CHƠI`: Chế độ thụ động, chỉ chờ người khác thách đấu hoặc bạn tự thách đấu trên web.
  4. `🧠 AI CHỈ CHƠI`: Chế độ thụ động nhưng có AI hỗ trợ đánh hộ.
- **Hỗ trợ Chess960:** Tự động nhận diện và xử lý biến thể cờ vua Fischer Random.
- **Quản lý thông minh:** Tự động hủy thách đấu nếu đối thủ không nhận lời sau 40 giây.
- **Thống kê chi tiết:** Theo dõi tỉ lệ thắng/thua, chuỗi thắng, và hiệu quả của AI.

## 🛠️ Yêu cầu hệ thống

- **Hệ điều hành:** Android (Termux) hoặc Linux.
- **Ngôn ngữ:** Python 3.10+.
- **Thư viện:** `berserk`, `python-chess`, `openai==0.28.1`, `requests`.
- **Engine:** `stockfish` (Cài đặt qua `pkg install stockfish`).

## 🚀 Cài đặt nhanh

1. **Cài đặt các gói cần thiết:**
   ```bash
   pkg update && pkg upgrade
   pkg install python git stockfish -y
   pip install berserk python-chess openai==0.28.1 requests
   ```

2. **Cấu hình mã xác thực (Tokens):**
   - Tạo file `lichess.token`: Dán mã API Token từ [Lichess API Settings](https://lichess.org/account/oauth/token) (Cần quyền: `Read preferences`, `Read email address`, `Play games with the bot API`, `Read incoming challenges`).
   - Tạo file `openrouter.key`: Dán mã API Key từ [OpenRouter](https://openrouter.ai/).

3. **Chạy Bot:**
   ```bash
   python3 huy.py
   ```

## ⚙️ Cấu hình (`config.json`)

Bạn có thể tùy chỉnh các thông số trong file `config.json`:
- `threads`: Số nhân CPU cho Stockfish (Khuyên dùng: 2-4 trên điện thoại).
- `think_time_ms`: Thời gian Stockfish suy nghĩ cho mỗi nước đi.
- `ai_help_threshold`: Độ khó của thế cờ để bot bắt đầu hỏi AI.
- `auto_resign`: Tự động xin thua khi thế cờ quá yếu (tránh lãng phí thời gian).

## ⚠️ Lưu ý quan trọng

- **Tài khoản BOT:** Bạn **bắt buộc** phải sử dụng tài khoản Lichess đã được nâng cấp lên chế độ BOT. Nếu dùng tài khoản người dùng bình thường, bạn sẽ bị khóa tài khoản ngay lập tức.
- **Bảo mật:** Tuyệt đối không bao giờ chia sẻ file `lichess.token` và `openrouter.key` cho bất kỳ ai.

## 📜 Giấy phép

Dự án này được phát hành dưới giấy phép mã nguồn mở. Chúc bạn có những trải nghiệm tuyệt vời với "Đại kiện tướng" bỏ túi này!

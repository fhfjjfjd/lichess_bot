import openai
import os
from logger import log

class AIManager:
    def __init__(self, key_file, model, max_tokens, system_prompt):
        self.model = model
        self.max_tokens = max_tokens
        self.system_prompt = system_prompt
        self.key = None
        
        # Thiết lập OpenRouter làm base URL cho OpenAI SDK
        openai.api_base = "https://openrouter.ai/api/v1"
        
        if os.path.exists(key_file):
            with open(key_file) as f:
                self.key = f.read().strip()
        else:
            self.key = input("Nhập OpenRouter API key: ").strip()
            with open(key_file, "w") as f:
                f.write(self.key)
            log("🔑 Đã lưu OpenRouter key.", "AI")
        
        if self.key:
            openai.api_key = self.key

    def ask(self, prompt):
        if not self.key:
            log("AI lỗi: Không tìm thấy API Key", "ERROR")
            return None
        try:
            log(f"🤖 Đang hỏi AI ({self.model})...", "AI")
            
            # Sử dụng OpenAI SDK để gọi OpenRouter
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.max_tokens,
                timeout=20  # Tăng timeout một chút cho ổn định
            )
            
            content = response.choices[0].message.content
            if content:
                log(f"🤖 AI: {content.strip()[:50]}...", "AI") # Log ngắn gọn
                return content.strip()
            else:
                log("AI trả về rỗng", "WARN")
                return None
                
        except openai.error.RateLimitError:
            log("AI lỗi: Bị giới hạn (Rate Limit). Thử model khác hoặc chờ chút.", "ERROR")
        except openai.error.AuthenticationError:
            log("AI lỗi: Sai API Key.", "ERROR")
        except Exception as e:
            log(f"AI lỗi: {e}", "ERROR")
        return None

    def choose_move(self, candidates, moves_str, score_str):
        if not candidates: return None
        move_list = moves_str.split() if moves_str else []
        cand_text = "\n".join([
            f"  {i}. {c['move']} (eval: {c['score']/100:.1f})"
            for i, c in candidates.items()
        ])
        prompt = f"""Thế cờ hiện tại (sau {len(move_list)} nước): eval = {score_str}

Stockfish đề xuất {len(candidates)} nước:
{cand_text}

Chọn nước tốt nhất. Chỉ trả lời đúng nước đi (ví dụ: e2e4)"""
        answer = self.ask(prompt)
        if answer:
            # Lấy từ đầu tiên trong câu trả lời (phòng trường hợp AI nói dông dài)
            chosen = answer.strip().split()[0].lower()
            valid = [c['move'] for c in candidates.values()]
            if chosen in valid:
                return chosen
        return None

    def decide_challenge(self, challenger, rating, variant, speed, time_limit, increment):
        prompt = f"""Có thách đấu đến:
- Người thách: {challenger} (rating: {rating})
- Variant: {variant}
- Tốc độ: {speed} ({time_limit}s + {increment}s)

Hãy quyết định ACCEPT hoặc DECLINE.
Chỉ trả lời đúng format: ACCEPT|lý do hoặc DECLINE|lý do"""
        return self.ask(prompt)

    def choose_challenge_config(self):
        prompt = """Hãy chọn cấu hình cho một ván đấu mới.
Trả lời đúng format: THỜI_GIAN|TĂNG_GIỜ|MÀU
- THỜI_GIAN: số giây (60, 120, 180, 300, 600, 900)
- TĂNG_GIỜ: increment giây (0, 1, 2, 3, 5)
- MÀU: white hoặc black hoặc random
Ví dụ: 180|2|random"""
        return self.ask(prompt)

    def analyze_game(self, moves_str, result, my_color):
        prompt = f"""Phân tích ván cờ vừa xong:
- Tôi chơi quân: {my_color}
- Kết quả: {result}
- Các nước đi: {moves_str}

Phân tích ngắn gọn (3-5 dòng): điểm mạnh, sai lầm, cải thiện."""
        return self.ask(prompt)

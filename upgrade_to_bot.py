import berserk
from logger import log

def upgrade():
    try:
        with open("lichess.token", "r") as f:
            token = f.read().strip()
        
        if not token:
            log("❌ Lỗi: File lichess.token đang trống!", "ERROR")
            return
            
        session = berserk.TokenSession(token)
        client = berserk.Client(session=session)
        
        # Thử lấy thông tin tài khoản hiện tại
        acc = client.account.get()
        username = acc['username']
        
        if acc.get('title') == 'BOT':
            log(f"✅ Tài khoản {username} ĐÃ LÀ BOT RỒI. Bạn không cần làm gì thêm.", "INFO")
            return

        print("\n" + "!" * 55)
        print(f"⚠️  CẢNH BÁO: NÂNG CẤP TÀI KHOẢN '{username}' LÊN BOT")
        print("!" * 55)
        print("- Tài khoản này sẽ KHÔNG THỂ chơi cờ thủ công như người bình thường.")
        print("- Bạn KHÔNG THỂ quay lại chế độ người chơi bình thường sau khi nâng cấp.")
        print("- Bạn PHẢI sử dụng bot để thi đấu.")
        print("!" * 55)
        
        confirm = input(f"\nBạn có chắc chắn muốn nâng cấp '{username}' lên BOT không? (nhập 'CONFIRM' để đồng ý): ")
        
        if confirm == "CONFIRM":
            log(f"🚀 Đang gửi yêu cầu nâng cấp lên BOT cho {username}...", "INFO")
            try:
                # Lệnh API chính thức để nâng cấp tài khoản lên BOT
                client.bots.upgrade_account()
                log(f"🎉 CHÚC MỪNG! Tài khoản {username} hiện đã chính thức trở thành BOT.", "INFO")
            except Exception as e:
                log(f"❌ Lỗi nâng cấp: {e}", "ERROR")
                log("Hỗ trợ: Kiểm tra xem tài khoản này đã từng chơi ván nào chưa. Tài khoản BOT mới nên là tài khoản sạch (chưa chơi ván nào).", "WARN")
        else:
            log("🚫 Đã hủy yêu cầu nâng cấp.", "WARN")
            
    except Exception as e:
        log(f"❌ Lỗi xác thực: {e}", "ERROR")

if __name__ == "__main__":
    upgrade()

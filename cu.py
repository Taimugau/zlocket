import json
import threading
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from websocket import WebSocketApp

PORT = 10000

# ================== Biến toàn cục ==================
latestResult = {
    "Ket_qua": "Chưa có kết quả",
    "Phien": 0,
    "Tong": 0,
    "Xuc_xac_1": 0,
    "Xuc_xac_2": 0,
    "Xuc_xac_3": 0,
    "id": "@sg205rika"
}

lastEventId = 19

# ================== WebSocket ==================
WS_URL = "wss://websocket.atpman.net/websocket"
HEADERS = [
    "Host: websocket.atpman.net",
    "Origin: https://play.789club.sx",
    "User-Agent: Mozilla/5.0",
    "Accept-Encoding: gzip, deflate, br, zstd",
    "Accept-Language: vi-VN,vi;q=0.9",
    "Pragma: no-cache",
    "Cache-Control: no-cache"
]

# ----- Đăng nhập bằng tài khoản mới -----
LOGIN_MESSAGE = [
    1,
    "MiniGame",
    "wanglin2019aaand",      # user mới
    "WamgLin2091",           # pass mới
    {
        "info": "{\"ipAddress\":\"113.185.45.88\",\"wsToken\":\"eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJnZW5kZXIiOjAsImNhblZpZXdTdGF0IjpmYWxzZSwiZGlzcGxheU5hbWUiOiJlbXlldTE3ODljbHVuIiwiYm90IjowLCJpc01lcmNoYW50IjpmYWxzZSwidmVyaWZpZWRCYW5rQWNjb3VudCI6ZmFsc2UsInBsYXlFdmVudExvYmJ5IjpmYWxzZSwiY3VzdG9tZXJJZCI6NjU3NjU3NjksImFmZklkIjoiNzg5IiwiYmFubmVkIjpmYWxzZSwiYnJhbmQiOiI3ODkuY2x1YiIsInRpbWVzdGFtcCI6MTc2NjQ3MDk1NTY4OCwibG9ja0dhbWVzIjpbXSwiYW1vdW50IjowLCJsb2NrQ2hhdCI6ZmFsc2UsInBob25lVmVyaWZpZWQiOmZhbHNlLCJpcEFkZHJlc3MiOiIxMTMuMTg1LjQ1Ljg4IiwibXV0ZSI6ZmFsc2UsImF2YXRhciI6Imh0dHBzOi8vYXBpLnhldWkuaW8vaW1hZ2VzL2F2YXRhci9hdmF0YXJfMjUucG5nIiwicGxhdGZvcm1JZCI6NSwidXNlcklkIjoiMjFkMTUxMjEtYjIzOC00ZDIyLTgzMTMtNGI3YjYwN2VhZjIxIiwicmVnVGltZSI6MTc2NjQ3MDkzMDEwNCwicGhvbmUiOiIiLCJkZXBvc2l0IjpmYWxzZSwidXNlcm5hbWUiOiJTOF93YW5nbGluMjAxOWFhYW5kIn0.F5jr6g1BPGMQ-5EPRdck-PDvVDXcahyGySOFSjyNEuE\",\"locale\":\"vi\",\"userId\":\"21d15121-b238-4d22-8313-4b7b607eaf21\",\"username\":\"S8_wanglin2019aaand\",\"timestamp\":1766470955689,\"refreshToken\":\"34ed90232de44567aec7d4752b021717.e8cd9e15f74c42fb8bd491e395d73ab1\"}",
        "signature": "55A3202A0554F20C01D09CD018386265C93B292E843BE3722766912A8F01ACF50E9574D88D52FAFDABEBD4794D3306C87021EF3DD6B25DA102872D23C7C31A0F1D3EB99C0714968A64F6C40335726EB999F1CEAE49BC0954EABA48189E1BBE61BD40C898CA4D683DA76E24386F4431772D05BC8142DAEBFA90E27A9C250A5ED3"
    }
]

SUBSCRIBE_TX_RESULT = [6, "MiniGame", "taixiuUnbalancedPlugin", {"cmd": 2000}]
SUBSCRIBE_LOBBY = [6, "MiniGame", "lobbyPlugin", {"cmd": 10001}]

def print_json_pretty(data, label=""):
    """Hàm in JSON đẹp với định dạng dễ đọc"""
    if label:
        print(f"\n{'='*50}")
        print(f"📋 {label}")
        print(f"{'='*50}")
    
    try:
        if isinstance(data, dict) or isinstance(data, list):
            formatted = json.dumps(data, indent=2, ensure_ascii=False)
            print(formatted)
        else:
            print(data)
    except:
        print(data)

def on_open(ws):
    print("✅ Đã kết nối WebSocket")
    print(f"📤 Gửi login message...")
    print_json_pretty(LOGIN_MESSAGE, "LOGIN MESSAGE")
    
    ws.send(json.dumps(LOGIN_MESSAGE))

    def run():
        time.sleep(1)
        print(f"📤 Đăng ký nhận kết quả Tài/Xỉu...")
        ws.send(json.dumps(SUBSCRIBE_TX_RESULT))
        
        print(f"📤 Đăng ký nhận thông tin Lobby...")
        ws.send(json.dumps(SUBSCRIBE_LOBBY))

        while True:
            time.sleep(10)
            ws.send("2")  # ping
            ws.send(json.dumps(SUBSCRIBE_TX_RESULT))
            ws.send(json.dumps([7, "Simms", lastEventId, 0, {"id": 0}]))

    threading.Thread(target=run, daemon=True).start()

def on_message(ws, message):
    global latestResult, lastEventId
    
    try:
        # Hiển thị toàn bộ message nhận được
        print_json_pretty(f"📥 NHẬN MESSAGE: {message[:500]}...", "RAW MESSAGE")
        
        data = json.loads(message)
        
        # Hiển thị message đã parse
        print_json_pretty(data, "PARSED MESSAGE")
        
        # Kiểm tra và xử lý lastEventId
        if isinstance(data, list):
            if len(data) >= 3 and data[0] == 7 and data[1] == "Simms" and isinstance(data[2], int):
                old_id = lastEventId
                lastEventId = data[2]
                print(f"🆔 Cập nhật lastEventId: {old_id} → {lastEventId}")
            
            # Xử lý dữ liệu kết quả Tài/Xỉu
            if len(data) >= 2 and isinstance(data[1], dict):
                msg_data = data[1]
                
                # Kết quả Tài/Xỉu
                if msg_data.get("cmd") == 2006:
                    sid = msg_data.get("sid")
                    d1 = msg_data.get("d1", 0)
                    d2 = msg_data.get("d2", 0)
                    d3 = msg_data.get("d3", 0)
                    
                    tong = d1 + d2 + d3
                    ketqua = "Tài" if tong >= 11 else "Xỉu"
                    
                    latestResult = {
                        "Ket_qua": ketqua,
                        "Phien": sid,
                        "Tong": tong,
                        "Xuc_xac_1": d1,
                        "Xuc_xac_2": d2,
                        "Xuc_xac_3": d3,
                        "id": "@sg205rika"
                    }
                    
                    print("🎲 CẬP NHẬT KẾT QUẢ:")
                    print_json_pretty(latestResult)
                
                # Thông tin lobby
                elif msg_data.get("cmd") == 10001:
                    print("🏛️ NHẬN THÔNG TIN LOBBY")
                
                # Thông tin khác
                else:
                    cmd = msg_data.get("cmd")
                    if cmd:
                        print(f"📊 Nhận command: {cmd}")
        
        # Xử lý message là dict
        elif isinstance(data, dict):
            print("📄 Message là dictionary")
            
    except json.JSONDecodeError as e:
        print(f"❌ Lỗi parse JSON: {e}")
        print(f"📄 Nội dung message: {message[:200]}")
    except Exception as e:
        print(f"❌ Lỗi xử lý message: {str(e)}")
        import traceback
        traceback.print_exc()

def on_close(ws, close_status_code, close_msg):
    print("🔌 WebSocket đóng.")
    print(f"   Mã đóng: {close_status_code}")
    print(f"   Thông điệp: {close_msg}")
    print("   Kết nối lại sau 5s...")
    time.sleep(5)
    start_ws()

def on_error(ws, error):
    print("❌ Lỗi WebSocket:")
    print_json_pretty(error, "ERROR DETAILS")

def start_ws():
    print("🔄 Bắt đầu kết nối WebSocket...")
    ws = WebSocketApp(
        WS_URL,
        header=HEADERS,
        on_open=on_open,
        on_message=on_message,
        on_close=on_close,
        on_error=on_error
    )
    ws.run_forever()

# ================== HTTP SERVER ==================
class MyHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        # Tắt log mặc định của HTTP server
        pass
    
    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        if self.path == "/taixiu":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps(latestResult).encode("utf-8"))
            
            # Log khi có request
            print(f"🌐 HTTP Request: {self.path} - Trả về kết quả hiện tại")
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"Khong tim thay")

def start_http():
    server = HTTPServer(("0.0.0.0", PORT), MyHandler)
    print(f"🌐 HTTP Server chạy tại http://localhost:{PORT}/taixiu")
    server.serve_forever()

# ================== RUN ==================
if __name__ == "__main__":
    print("🚀 Khởi động hệ thống...")
    print(f"📝 Tài khoản: wanglin2019aaand")
    print(f"🔑 Mật khẩu: WamgLin2091")
    print(f"🌐 IP: 113.185.45.88")
    print("-" * 50)
    
    threading.Thread(target=start_ws, daemon=True).start()
    start_http()

"""
TOOL FAKE SPAM SMS OTP – HIỂN THỊ GIẢ LẬP GIAO DIỆN SPAM
Không gửi request thật – chỉ hiển thị giao diện giả như đang spam
Dùng để prank / scare / demo
"""
import os
import sys
import time
import random
import threading
from datetime import datetime

# ============================================================
# CẤU HÌNH
# ============================================================
SERVICES = [
    "MOMO", "ZALOPAY", "VIETTEL_MONEY", "VNPAY", "SHOPEEPAY",
    "SHOPEE", "LAZADA", "TIKI", "SENDO", "FPT_SHOP",
    "TGDD", "DMX", "BHX", "GRAB", "BE",
    "GOJEK", "BAEMIN", "AHAMOVE", "LOSHIP", "GHN",
    "VIETTEL_POST", "MY_VIETTEL", "MY_VNPT", "VHOME",
    "VIETCOMBANK", "BIDV", "TECHCOMBANK", "MBBANK", "ACB",
    "VPBANK", "TPBANK", "SACOMBANK", "MSB", "OCB",
    "SHB", "FECREDIT", "HOMECREDIT", "VNPT_MONEY",
    "VINFANS", "AEON", "PHUCLONG", "KINGFOLD", "TV360",
    "VUIHOC", "FPT_PLAY", "GALAXY_PLAY",
]

COLORS = {
    "GREEN":  "\033[92m",
    "RED":    "\033[91m",
    "YELLOW": "\033[93m",
    "CYAN":   "\033[96m",
    "MAGENTA":"\033[95m",
    "WHITE":  "\033[97m",
    "RESET":  "\033[0m",
    "BOLD":   "\033[1m",
}

# ============================================================
# BIẾN TOÀN CỤC
# ============================================================
running = True
success_count = {}
fail_count = {}
total_sent = 0
total_success = 0
total_fail = 0
lock = threading.Lock()

# ============================================================
# HÀM HIỂN THỊ
# ============================================================
def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_banner(phone, duration, speed, threads):
    clear()
    banner = f"""
{COLORS['CYAN']}{COLORS['BOLD']}
  ╔══════════════════════════════════════════════════════════╗
  ║        TOOL FAKE SPAM SMS OTP – VIETNAM EDITION          ║
  ║        MÔ PHỎNG SPAM – KHÔNG GỬI REQUEST THẬT            ║
  ╚══════════════════════════════════════════════════════════╝
{COLORS['RESET']}
  {COLORS['YELLOW']}[*] MỤC TIÊU    : {phone}{COLORS['RESET']}
  {COLORS['YELLOW']}[*] THỜI GIAN   : {duration}s{COLORS['RESET']}
  {COLORS['YELLOW']}[*] TỐC ĐỘ      : {speed} ({threads} luồng){COLORS['RESET']}
  {COLORS['YELLOW']}[*] DỊCH VỤ     : {len(SERVICES)} services{COLORS['RESET']}
  {COLORS['RED']}[!] GIẢ LẬP – KHÔNG GỬI OTP THẬT{COLORS['RESET']}
{COLORS['RESET']}
"""
    print(banner)

def print_stats(elapsed):
    """In bảng thống kê động"""
    global total_sent, total_success, total_fail
    with lock:
        ts = total_sent
        tsc = total_success
        tf = total_fail
    rate = ts / elapsed if elapsed > 0 else 0
    pct = (tsc / ts * 100) if ts > 0 else 0

    # Chỉ hiển thị top dịch vụ có hoạt động
    active_services = []
    with lock:
        for name in sorted(success_count.keys(), key=lambda x: success_count.get(x,0)+fail_count.get(x,0), reverse=True)[:15]:
            sc = success_count.get(name, 0)
            fc = fail_count.get(name, 0)
            if sc + fc > 0:
                active_services.append((name, sc, fc))

    sys.stdout.write("\033[H")  # Đưa con trỏ về đầu terminal
    sys.stdout.write("\033[J")  # Xóa từ con trỏ đến cuối
    print_banner(sys.argv[1] if len(sys.argv) > 1 else "09xxxxxxx", "", "", "")
    print(f"  {'='*55}")
    print(f"  [{(datetime.now().strftime('%H:%M:%S'))}] ĐÃ GỬI: {ts} | "
          f"{COLORS['GREEN']}✅ {tsc}{COLORS['RESET']} | "
          f"{COLORS['RED']}❌ {tf}{COLORS['RESET']} | "
          f"{COLORS['YELLOW']}📊 {pct:.1f}%{COLORS['RESET']} | "
          f"{COLORS['CYAN']}⚡ {rate:.1f}/s{COLORS['RESET']}")
    print(f"  {'='*55}")

    for name, sc, fc in active_services:
        bar_len = 20
        filled = int(sc / max(1, sc+fc) * bar_len)
        bar = f"{COLORS['GREEN']}{'█'*filled}{COLORS['RED']}{'░'*(bar_len-filled)}{COLORS['RESET']}"
        print(f"  {name:18s} [{bar}] {COLORS['GREEN']}OK={sc:4d}{COLORS['RESET']} {COLORS['RED']}FAIL={fc:4d}{COLORS['RESET']}")

    # Log giả lập đang chạy
    print(f"\n  {COLORS['MAGENTA']}[LOG GIẢ LẬP]{COLORS['RESET']}")
    fake_messages = [
        f"  [✓] Gửi OTP {random.choice(SERVICES)} → {random.choice(['09'+''.join(random.choices('0123456789',k=8)) for _ in range(1)])} | {random.randint(200,2000)}ms",
        f"  [✓] SMS OTP {random.choice(SERVICES)} đã gửi | {random.randint(150,800)}ms",
        f"  [~] Đang kết nối {random.choice(['Vietcombank','MOMO','ZaloPay','Shopee'])} API... {random.randint(300,1500)}ms",
        f"  [✓] Xác thực thành công | Response 200 | {random.randint(100,500)}ms",
        f"  [~] Retry {random.choice(['Grab','Be','Baemin'])} lần {random.randint(1,3)}... {random.randint(500,2000)}ms",
    ]
    for _ in range(3):
        print(random.choice(fake_messages))

    sys.stdout.flush()

# ============================================================
# HÀM GIẢ LẬP GỬI OTP
# ============================================================
def fake_send_otp(service_name):
    """Giả lập gửi 1 OTP – thành công ~85%"""
    global total_sent, total_success, total_fail

    with lock:
        total_sent += 1

    # Giả lập thời gian gửi
    delay = random.uniform(0.05, 0.3)
    time.sleep(delay)

    # 85% tỉ lệ thành công
    if random.random() < 0.85:
        with lock:
            success_count[service_name] = success_count.get(service_name, 0) + 1
            total_success += 1
    else:
        with lock:
            fail_count[service_name] = fail_count.get(service_name, 0) + 1
            total_fail += 1

def worker(service_name, end_time):
    """Mỗi worker chạy liên tục 1 service"""
    while time.time() < end_time and running:
        fake_send_otp(service_name)
        # Random delay nhỏ giữa các lần gửi
        time.sleep(random.uniform(0.01, 0.05))

def progress_animation(end_time):
    """Hiệu ứng loading..."""
    chars = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"
    i = 0
    while time.time() < end_time and running:
        sys.stdout.write(f"\r  {COLORS['CYAN']}[{chars[i%len(chars)]}] ĐANG SPAM...{COLORS['RESET']}")
        sys.stdout.flush()
        i += 1
        time.sleep(0.1)
    sys.stdout.write("\r" + " "*50 + "\r")

# ============================================================
# MAIN
# ============================================================
def main():
    global running, total_sent, total_success, total_fail, success_count, fail_count

    clear()
    print(f"{COLORS['CYAN']}{COLORS['BOLD']}")
    print("""
  ╔══════════════════════════════════════════════════════════╗
  ║        TOOL FAKE SPAM SMS OTP – VIETNAM EDITION          ║
  ║        MÔ PHỎNG SPAM – KHÔNG GỬI REQUEST THẬT            ║
  ║        CHỈ DÙNG ĐỂ PRANK / SCARE / DEMO                  ║
  ╚══════════════════════════════════════════════════════════╝
    """)
    print(f"{COLORS['RESET']}")

    # --- INPUT ---
    phone = input(f"  {COLORS['YELLOW']}[?] NHẬP SỐ ĐIỆN THOẠI MỤC TIÊU: {COLORS['RESET']}").strip()
    if not phone:
        phone = "09xxxxxxxxx"

    try:
        duration = int(input(f"  {COLORS['YELLOW']}[?] THỜI GIAN SPAM (giây, mặc định 60): {COLORS['RESET']}") or "60")
    except:
        duration = 60

    print(f"\n  {COLORS['YELLOW']}[?] CHỌN TỐC ĐỘ SPAM (GIẢ LẬP):{COLORS['RESET']}")
    print(f"      1. MAX    – ~500 OTP/s (cực nhanh)")
    print(f"      2. HIGH   – ~200 OTP/s")
    print(f"      3. NORMAL – ~50 OTP/s")
    print(f"      4. LOW    – ~10 OTP/s")

    speed_input = input(f"  {COLORS['YELLOW']}      Chọn (1-4, Enter=MAX): {COLORS['RESET']}").strip()
    speed_map = {
        "1": ("MAX", 500, 100),
        "2": ("HIGH", 200, 50),
        "3": ("NORMAL", 50, 20),
        "4": ("LOW", 10, 5),
    }
    speed_name, rate, threads = speed_map.get(speed_input, ("MAX", 500, 100))

    # Reset biến
    total_sent = 0
    total_success = 0
    total_fail = 0
    success_count = {}
    fail_count = {}
    running = True

    # --- MÀN HÌNH BẮT ĐẦU ---
    clear()
    print(f"""
{COLORS['CYAN']}{COLORS['BOLD']}
  ╔══════════════════════════════════════════════════════════╗
  ║        TOOL FAKE SPAM SMS OTP – VIETNAM EDITION          ║
  ╚══════════════════════════════════════════════════════════╝
{COLORS['RESET']}
  {COLORS['YELLOW']}📱 MỤC TIÊU    : {phone}{COLORS['RESET']}
  {COLORS['YELLOW']}⏱️  THỜI GIAN   : {duration} giây{COLORS['RESET']}
  {COLORS['YELLOW']}⚡ TỐC ĐỘ      : {speed_name} (~{rate} OTP/s){COLORS['RESET']}
  {COLORS['YELLOW']}🧵 SỐ LUỒNG    : {threads}{COLORS['RESET']}
  {COLORS['YELLOW']}📦 DỊCH VỤ     : {len(SERVICES)}{COLORS['RESET']}
  {COLORS['RED']}[!] GIẢ LẬP – KHÔNG GỬI OTP THẬT [!]{COLORS['RESET']}
""")
    input(f"  {COLORS['GREEN']}[!] Nhấn ENTER để BẮT ĐẦU SPAM...{COLORS['RESET']}")

    # --- BẮT ĐẦU SPAM ---
    clear()
    start_time = time.time()
    end_time = start_time + duration

    # Khởi chạy worker threads
    all_threads = []
    for _ in range(threads):
        svc = random.choice(SERVICES)
        t = threading.Thread(target=worker, args=(svc, end_time), daemon=True)
        t.start()
        all_threads.append(t)

    # Thread hiển thị stats
    stats_thread = threading.Thread(target=progress_animation, args=(end_time,), daemon=True)
    stats_thread.start()

    # Vòng lặp hiển thị chính
    try:
        while time.time() < end_time and running:
            elapsed = time.time() - start_time
            print_stats(elapsed)
            time.sleep(0.2)  # Cập nhật 5 lần/giây
    except KeyboardInterrupt:
        running = False
        print(f"\n\n  {COLORS['RED']}[!] ĐÃ DỪNG BỞI NGƯỜI DÙNG!{COLORS['RESET']}")

    running = False
    elapsed = time.time() - start_time

    # Chờ các thread kết thúc
    time.sleep(0.5)

    # --- TỔNG KẾT ---
    with lock:
        ts = total_sent
        tsc = total_success
        tf = total_fail

    clear()
    print(f"""
{COLORS['CYAN']}{COLORS['BOLD']}
  ╔══════════════════════════════════════════════════════════╗
  ║                   KẾT THÚC SPAM                          ║
  ╚══════════════════════════════════════════════════════════╝
{COLORS['RESET']}
  {COLORS['YELLOW']}📱 MỤC TIÊU       : {phone}{COLORS['RESET']}
  {COLORS['YELLOW']}⏱️  TỔNG THỜI GIAN : {elapsed:.1f} giây{COLORS['RESET']}
  {COLORS['YELLOW']}📤 TỔNG SMS ĐÃ GỬI: {ts}{COLORS['RESET']}
  {COLORS['GREEN']}✅ THÀNH CÔNG      : {tsc} ({tsc/max(1,ts)*100:.1f}%){COLORS['RESET']}
  {COLORS['RED']}❌ THẤT BẠI        : {tf} ({tf/max(1,ts)*100:.1f}%){COLORS['RESET']}
  {COLORS['CYAN']}⚡ TỐC ĐỘ TR.BÌNH : {ts/elapsed:.1f} OTP/s{COLORS['RESET']}

  {COLORS['MAGENTA']}[*] ĐÂY LÀ TOOL GIẢ LẬP – KHÔNG CÓ OTP NÀO ĐƯỢC GỬI THẬT{COLORS['RESET']}
""")

    input(f"\n  {COLORS['YELLOW']}Nhấn ENTER để thoát...{COLORS['RESET']}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{COLORS['RED']}[!] Đã thoát.{COLORS['RESET']}")
    except Exception as e:
        print(f"\n{COLORS['RED']}[!] Lỗi: {e}{COLORS['RESET']}")

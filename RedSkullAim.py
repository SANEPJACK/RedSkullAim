"""
pyinstaller --onefile --noconsole --icon "img/redaim.ico" --add-data "img\\redaim.ico;img" --add-data "img\\background.png;img" RedSkullAim.py

pyinstaller --clean --noconfirm RedSkullAim_obf.spec

python RedSkullAim.py

Hotkey screen-watcher for PBApp window.

ปุ่มลัดทั้งหมดจะแสดงบนหน้าต่าง “เลือกความละเอียดหน้าจอ” (เปิดด้วย Insert)

โปรแกรมจะจับภาพเฉพาะกรอบที่เลือกและตรวจพิกเซลสีแดง หากเจอจะกดเมาส์/คีย์บอร์ดตามโหมดที่เลือก
"""

import time
import sys
import ctypes
import threading
import os
import winreg
import subprocess
from datetime import datetime, timedelta, timezone
from urllib.parse import quote

import keyboard
import mouse
import cv2
import numpy as np
import mss
import win32gui
import winsound
import tkinter as tk
from tkinter import ttk, messagebox
import requests
import certifi

# กันกรณี onefile: แตกไฟล์ไว้ใน sys._MEIPASS
if getattr(sys, 'frozen', False):
    base = getattr(sys, '_MEIPASS', '')
    candidate = os.path.join(base, 'certifi', 'cacert.pem')
    if os.path.exists(candidate):
        os.environ['SSL_CERT_FILE'] = candidate
        os.environ['REQUESTS_CA_BUNDLE'] = candidate
    else:
        # fallback ใช้ path ของ certifi โดยตรง
        os.environ['SSL_CERT_FILE'] = certifi.where()
        os.environ['REQUESTS_CA_BUNDLE'] = certifi.where()
else:
    os.environ['SSL_CERT_FILE'] = certifi.where()
    os.environ['REQUESTS_CA_BUNDLE'] = certifi.where()

# ---------- ตั้งค่าทั่วไป ----------
ICON_PATH = os.path.join(os.path.dirname(__file__), "img", "redaim.ico")
BACKGROUND_IMAGE_PATH = os.path.join(os.path.dirname(__file__), "img", "background.png")
TH_TZ = timezone(timedelta(hours=7))
EXPIRE_DATE = datetime(2026, 2, 28, tzinfo=TH_TZ)
PROGRAM_NAME = "redaim"

FIREBASE_DB_URL = "https://redskull-8888-default-rtdb.asia-southeast1.firebasedatabase.app"

FIREBASE_AUTH_TOKEN = ""  # leave empty if database rules are public
DEFAULT_TRIAL_DAYS = 3
license_plan = None

RESOLUTION_PRESETS = {
    "1920x1080": {"top": 0, "left": 960, "width": 40, "height": 540},
    "1440x1080": {"top": 0, "left": 720, "width": 40, "height": 540},
    "1760x990": {"top": 0, "left": 840, "width": 40, "height": 525},
    "1680x1050": {"top": 0, "left": 683, "width": 40, "height": 400},
    "1366x768": {"top": 0, "left": 640, "width": 40, "height": 384},
    "1280x768": {"top": 0, "left": 640, "width": 40, "height": 384},
    "1280x720": {"top": 0, "left": 640, "width": 40, "height": 360},
    "1024x768": {"top": 0, "left": 512, "width": 40, "height": 384},
}

# ---------- ตัวแปรสถานะ ----------
selected_region = {}
current_function = None
is_paused = False


# ---------- ฟังก์ชันยูทิล ----------
def message_box(title: str, text: str):
    ctypes.windll.user32.MessageBoxW(0, text, title, 0)


def check_internet_connection() -> bool:
    try:
        flags = ctypes.c_uint()
        return bool(ctypes.windll.wininet.InternetGetConnectedState(ctypes.byref(flags), 0))
    except Exception:
        return False

def get_confirm_token(response):
    for key, value in response.cookies.items():
        if key.startswith("download_warning"):
            return value
    return None


def save_response_content(response, destination):
    chunk_size = 32768
    with open(destination, "wb") as f:
        for chunk in response.iter_content(chunk_size):
            if chunk:
                f.write(chunk)



def now_in_th():
    """Return current datetime in Thailand timezone."""
    return datetime.now(TH_TZ)


def format_dt_ad(dt: datetime) -> str:
    """Format datetime using Gregorian year regardless of OS locale."""
    dt_th = dt.astimezone(TH_TZ)
    return f"{dt_th.day:02d}/{dt_th.month:02d}/{dt_th.year:04d} {dt_th.hour:02d}:{dt_th.minute:02d}"


def iso_th(dt: datetime) -> str:
    """ISO8601 string in Thai time (+07:00) with seconds precision."""
    return dt.astimezone(TH_TZ).replace(microsecond=0).isoformat()


def load_background_image():
    """Return Tk PhotoImage from BACKGROUND_IMAGE_PATH (if present)."""
    try:
        if os.path.exists(BACKGROUND_IMAGE_PATH):
            return tk.PhotoImage(file=BACKGROUND_IMAGE_PATH)
    except Exception as e:
        print(f"????????????????????????: {e}")
    return None

# ---------- Firebase license check ----------
def get_machine_uuid():
    """Return Windows machine GUID as the device UUID."""
    try:
        access = winreg.KEY_READ
        # ensure we read 64-bit view even when python is 32-bit
        if hasattr(winreg, "KEY_WOW64_64KEY"):
            access |= winreg.KEY_WOW64_64KEY
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\\Microsoft\\Cryptography", 0, access) as key:
            value, _ = winreg.QueryValueEx(key, "MachineGuid")
            if value:
                return str(value).strip()
    except Exception as exc:
        print(f"Failed to read MachineGuid from registry: {exc}")

    # fallback 1: WMIC
    try:
        output = subprocess.check_output(["wmic", "csproduct", "get", "uuid"], text=True, timeout=5, creationflags=0x08000000)
        parts = [p.strip() for p in output.splitlines() if p.strip() and p.strip().lower() != "uuid"]
        if parts:
            return parts[0]
    except Exception as exc:
        print(f"Failed to read UUID via WMIC: {exc}")

    # fallback 2: GetCurrentHwProfile
    try:
        class HW_PROFILE_INFO(ctypes.Structure):
            _fields_ = [
                ("dwDockInfo", ctypes.c_ulong),
                ("szHwProfileGuid", ctypes.c_wchar * 39),
                ("szHwProfileName", ctypes.c_wchar * 80),
            ]

        info = HW_PROFILE_INFO()
        if ctypes.windll.user32.GetCurrentHwProfileW(ctypes.byref(info)):
            guid = info.szHwProfileGuid.strip("{}").strip()
            if guid:
                return guid
    except Exception as exc:
        print(f"Failed to read UUID via GetCurrentHwProfile: {exc}")

    return None


def build_firebase_customer_url(uuid: str) -> str:
    base_url = FIREBASE_DB_URL.rstrip("/")
    path = f"/customers/{quote(uuid)}.json"
    if FIREBASE_AUTH_TOKEN and "YOUR_DB_AUTH_TOKEN" not in FIREBASE_AUTH_TOKEN:
        return f"{base_url}{path}?auth={FIREBASE_AUTH_TOKEN}"
    return base_url + path


def _parse_iso_datetime(value: str):
    if not value:
        return None
    try:
        if value.endswith("Z"):
            value = value[:-1] + "+00:00"
        dt = datetime.fromisoformat(value)
        if dt.tzinfo is None:
            return dt.replace(tzinfo=TH_TZ)
        return dt.astimezone(TH_TZ)
    except Exception:
        return None


def fetch_or_create_customer(uuid: str) -> dict:
    if not FIREBASE_DB_URL or "your-project-id" in FIREBASE_DB_URL:
        raise RuntimeError("FirebaseDbUrl is not configured")

    url = build_firebase_customer_url(uuid)
    response = requests.get(url, timeout=8)
    if response.ok and response.text.strip() not in ("", "null"):
        return response.json()

    now_th = now_in_th()
    expiry_th = now_th + timedelta(days=DEFAULT_TRIAL_DAYS)
    payload = {
        "name": "ผู้ใช้ทดสอบ",
        "plan": "free",
        "status": True,
        "program": PROGRAM_NAME,
        "createdAt": iso_th(now_th),
        "expiry": iso_th(expiry_th),
    }
    put_response = requests.put(url, json=payload, timeout=8)
    put_response.raise_for_status()
    return payload


def check_firebase_license():
    global EXPIRE_DATE, license_plan

    raw_uuid = get_machine_uuid()
    if not raw_uuid:
        messagebox.showerror("ไม่พบรหัสเครื่อง", "ไม่สามารถอ่าน Machine UUID ได้")
        sys.exit()
    uuid = f"{raw_uuid}-aim"
    display_uuid = raw_uuid

    try:
        customer = fetch_or_create_customer(uuid)
    except Exception as exc:
        messagebox.showerror("Connection Error", f"ไม่สามารถเชื่อมต่อเซิร์ฟเวอร์ได้\n{exc}")
        sys.exit()

    if not customer.get("status", False):
        messagebox.showerror(
            "Access Denied",
            f"ไม่ได้รับอนุญาตให้ใช้งาน\nรหัสสมาชิกของคุณคือ:\n{display_uuid}\nโปรดติดต่อแอดมิน",
        )
        sys.exit()

    plan = str(customer.get("plan", "")).lower()
    license_plan = plan or "unknown"

    if plan == "member":
        EXPIRE_DATE = datetime(2099, 1, 1, tzinfo=TH_TZ)
        messagebox.showinfo("สถานะโปรแกรม", f"ได้รับอนุญาต (สมาชิก: {customer.get('name', 'ไม่ระบุ')})")
        return

    if plan == "free":
        expiry_dt = _parse_iso_datetime(customer.get("expiry", ""))
        if expiry_dt is None:
            messagebox.showerror("Error", "รูปแบบวันหมดอายุไม่ถูกต้อง")
            sys.exit()
        EXPIRE_DATE = expiry_dt
        messagebox.showinfo(
            "สถานะโปรแกรม",
            f"Free ทดลองถึง {format_dt_ad(expiry_dt)} (UUID: {display_uuid})",
        )
        return

    messagebox.showerror("Error", f"รูปแบบแผนไม่รองรับ: {plan}")
    sys.exit()


def check_expiration():
    if license_plan == "member":
        return
    today = now_in_th()
    if today > EXPIRE_DATE:
        message_box("โปรแกรมหมดอายุ", "หมดอายุการใช้งานแล้ว")
        sys.exit()


def show_time_remaining():
    if license_plan == "member":
        return
    now = now_in_th()
    remaining = EXPIRE_DATE - now
    if remaining.total_seconds() > 0:
        days = remaining.days
        hours, remainder = divmod(remaining.seconds, 3600)
        minutes, _ = divmod(remainder, 60)
        messagebox.showinfo(
            "เวลาคงเหลือ",
            f"ใช้งานได้อีก {days} วัน {hours} ชม. {minutes} นาที\n(หมดอายุ {format_dt_ad(EXPIRE_DATE)})",
        )
    else:
        check_expiration()


def monitor_internet(root):
    def check_loop():
        while True:
            if not check_internet_connection():
                messagebox.showerror(
                    "ขาดการเชื่อมต่อ",
                    "ไม่พบการเชื่อมต่ออินเทอร์เน็ต โปรแกรมจะปิดตัวลง",
                )
                root.destroy()
                sys.exit()
            time.sleep(5)

    threading.Thread(target=check_loop, daemon=True).start()


def select_resolution():
    """แสดงหน้าต่างเลือกขนาดกรอบจับภาพ."""

    def on_select():
        global selected_region
        choice = combo.get()
        selected_region = RESOLUTION_PRESETS.get(choice, {})
        root.destroy()

    root = tk.Tk()
    root.title("RedSkull aim color PB")
    root.geometry("300x200")
    root.configure(bg="#f0f4f7")

    bg_img = load_background_image()
    if bg_img:
        bg_label = tk.Label(root, image=bg_img)
        bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        root._bg_image = bg_img  # กัน GC

    try:
        root.iconbitmap(ICON_PATH)
    except Exception:
        pass  # ไฟล์ไอคอนไม่สำคัญต่อการทำงานหลัก

    style = ttk.Style()
    style.theme_use("clam")
    style.configure("TLabel", font=("Segoe UI", 11), background="#f0f4f7")
    style.configure("TButton", font=("Segoe UI", 10), padding=6)
    style.configure("TCombobox", padding=4)

    
    ttk.Label(
        root,
        text="F1 กล | F2 ซอง | F3 ซองบัพ | F4 ซองเบ \n"
             "F5 สไน | F6 สไนบัพ | F7 สไนเบ \n"
             "F8 Kar98TSR | F9 Kar98TSRบัพ | F10 Kar98TSRเบ \n"
             "F11 พัก | F12 ปิด | Insert เลือกขนาดกรอบ",
        justify="center",
        font=("Segoe UI", 8),
        background="#f0f4f7",
        foreground="#444",
        wraplength=280,
    ).pack(pady=(0, 10))
    ttk.Label(root, text="เลือกความละเอียดหน้าจอ").pack(pady=(15, 6))
    combo = ttk.Combobox(root, values=list(RESOLUTION_PRESETS.keys()), state="readonly", width=25)
    combo.current(0)
    combo.pack(pady=5)
    ttk.Button(root, text="ยืนยัน", command=on_select).pack(pady=12)

    monitor_internet(root)
    root.mainloop()


# ---------- จับภาพ / ตรวจสี ----------
def find_game_window():
    hwnd = win32gui.FindWindow("PBApp", None)
    return hwnd if hwnd != 0 else None


def get_window_rect(hwnd):
    rect = win32gui.GetWindowRect(hwnd)
    return {"top": rect[1], "left": rect[0], "width": rect[2] - rect[0], "height": rect[3] - rect[1]}


def capture_screen(region):
    with mss.mss() as sct:
        img = sct.grab(region)
        img_np = np.array(img)
        return cv2.cvtColor(img_np, cv2.COLOR_BGRA2BGR)


def detect_red_pixel_bgr(img):
    lower_red = np.array([0, 0, 255])
    upper_red = np.array([0, 0, 255])
    red_mask = cv2.inRange(img, lower_red, upper_red)
    return np.any(red_mask)


def _region_from_window(hwnd):
    if not selected_region:
        return None
    window_rect = get_window_rect(hwnd)
    return {
        "top": window_rect["top"] + selected_region["top"],
        "left": window_rect["left"] + selected_region["left"],
        "width": selected_region["width"],
        "height": selected_region["height"],
    }


# ---------- โหมดต่าง ๆ ----------
def AR():
    hwnd = find_game_window()
    if hwnd is None:
        return
    region = _region_from_window(hwnd)
    if not region:
        return
    img = capture_screen(region)
    if detect_red_pixel_bgr(img):
        mouse.press("left")
        time.sleep(0.01)
        mouse.release("left")


def SG():
    hwnd = find_game_window()
    if hwnd is None:
        return
    region = _region_from_window(hwnd)
    if not region:
        return
    img = capture_screen(region)
    if detect_red_pixel_bgr(img):
        mouse.press("left")
        time.sleep(0.02)
        mouse.release("left")
        keyboard.press("q")
        mouse.wheel(1)
        time.sleep(0.02)
        keyboard.release("q")
        keyboard.press("q")
        mouse.wheel(-1)
        time.sleep(0.45)
        keyboard.release("q")


def SGBUFF():
    hwnd = find_game_window()
    if hwnd is None:
        return
    region = _region_from_window(hwnd)
    if not region:
        return
    img = capture_screen(region)
    if detect_red_pixel_bgr(img):
        mouse.press("left")
        time.sleep(0.02)
        mouse.release("left")
        keyboard.press("q")
        mouse.wheel(1)
        time.sleep(0.02)
        keyboard.release("q")
        keyboard.press("q")
        mouse.wheel(-1)
        time.sleep(0.41)
        keyboard.release("q")


def SGBERET():
    hwnd = find_game_window()
    if hwnd is None:
        return
    region = _region_from_window(hwnd)
    if not region:
        return
    img = capture_screen(region)
    if detect_red_pixel_bgr(img):
        mouse.press("left")
        time.sleep(0.02)
        mouse.release("left")
        keyboard.press("q")
        mouse.wheel(1)
        time.sleep(0.02)
        keyboard.release("q")
        keyboard.press("q")
        mouse.wheel(-1)
        time.sleep(0.30)
        keyboard.release("q")


def SNIPER():
    hwnd = find_game_window()
    if hwnd is None:
        return
    region = _region_from_window(hwnd)
    if not region:
        return
    img = capture_screen(region)
    if detect_red_pixel_bgr(img):
        mouse.press("right")
        time.sleep(0.04)
        mouse.press("left")
        time.sleep(0.02)
        mouse.release("right")
        mouse.release("left")
        keyboard.press("q")
        mouse.wheel(1)
        time.sleep(0.02)
        keyboard.release("q")
        keyboard.press("q")
        mouse.wheel(-1)
        time.sleep(0.67)
        keyboard.release("q")


def SNIPERBUFF():
    hwnd = find_game_window()
    if hwnd is None:
        return
    region = _region_from_window(hwnd)
    if not region:
        return
    img = capture_screen(region)
    if detect_red_pixel_bgr(img):
        mouse.press("right")
        time.sleep(0.04)
        mouse.press("left")
        time.sleep(0.02)
        mouse.release("right")
        mouse.release("left")
        keyboard.press("q")
        mouse.wheel(1)
        time.sleep(0.02)
        keyboard.release("q")
        keyboard.press("q")
        mouse.wheel(-1)
        time.sleep(0.61)
        keyboard.release("q")


def SNIPERBERET():
    hwnd = find_game_window()
    if hwnd is None:
        return
    region = _region_from_window(hwnd)
    if not region:
        return
    img = capture_screen(region)
    if detect_red_pixel_bgr(img):
        mouse.press("right")
        time.sleep(0.04)
        mouse.press("left")
        time.sleep(0.02)
        mouse.release("right")
        mouse.release("left")
        keyboard.press("q")
        mouse.wheel(1)
        time.sleep(0.02)
        keyboard.release("q")
        keyboard.press("q")
        mouse.wheel(-1)
        time.sleep(0.45)
        keyboard.release("q")


def KAR98():
    hwnd = find_game_window()
    if hwnd is None:
        return
    region = _region_from_window(hwnd)
    if not region:
        return
    img = capture_screen(region)
    if detect_red_pixel_bgr(img):
        mouse.press("right")
        time.sleep(0.02)
        mouse.press("left")
        time.sleep(0.02)
        mouse.release("right")
        mouse.release("left")
        keyboard.press("q")
        mouse.wheel(1)
        time.sleep(0.02)
        keyboard.release("q")
        keyboard.press("q")
        mouse.wheel(-1)
        time.sleep(0.56)
        keyboard.release("q")


def KAR98BUFF():
    hwnd = find_game_window()
    if hwnd is None:
        return
    region = _region_from_window(hwnd)
    if not region:
        return
    img = capture_screen(region)
    if detect_red_pixel_bgr(img):
        mouse.press("right")
        time.sleep(0.02)
        mouse.press("left")
        time.sleep(0.02)
        mouse.release("right")
        mouse.release("left")
        keyboard.press("q")
        mouse.wheel(1)
        time.sleep(0.02)
        keyboard.release("q")
        keyboard.press("q")
        mouse.wheel(-1)
        time.sleep(0.52)
        keyboard.release("q")


def KAR98BERET():
    hwnd = find_game_window()
    if hwnd is None:
        return
    region = _region_from_window(hwnd)
    if not region:
        return
    img = capture_screen(region)
    if detect_red_pixel_bgr(img):
        mouse.press("right")
        time.sleep(0.02)
        mouse.press("left")
        time.sleep(0.02)
        mouse.release("right")
        mouse.release("left")
        keyboard.press("q")
        mouse.wheel(1)
        time.sleep(0.02)
        keyboard.release("q")
        keyboard.press("q")
        mouse.wheel(-1)
        time.sleep(0.38)
        keyboard.release("q")


# ---------- คุมฮอตคีย์ ----------
def is_insert_only_pressed() -> bool:
    """Return True when the dedicated Insert key is pressed (ignore numpad 0)."""
    return any(
        event.name == "insert" and not getattr(event, "is_keypad", False)
        for event in keyboard._pressed_events.values()
    )


def check_keys():
    global is_paused, current_function
    if keyboard.is_pressed("F1"):
        current_function = AR
        is_paused = False
        print("AR started.")
        winsound.Beep(300, 200)
        time.sleep(0.15)
    if keyboard.is_pressed("F2"):
        current_function = SG
        is_paused = False
        print("SG started.")
        winsound.Beep(300, 200)
        time.sleep(0.15)
    if keyboard.is_pressed("F3"):
        current_function = SGBUFF
        is_paused = False
        print("SGBUFF started.")
        winsound.Beep(300, 200)
        time.sleep(0.15)
    if keyboard.is_pressed("F4"):
        current_function = SGBERET
        is_paused = False
        print("SGBERET started.")
        winsound.Beep(300, 200)
        time.sleep(0.15)
    if keyboard.is_pressed("F5"):
        current_function = SNIPER
        is_paused = False
        print("SNIPER started.")
        winsound.Beep(300, 200)
        time.sleep(0.15)
    if keyboard.is_pressed("F6"):
        current_function = SNIPERBUFF
        is_paused = False
        print("SNIPERBUFF started.")
        winsound.Beep(300, 200)
        time.sleep(0.15)
    if keyboard.is_pressed("F7"):
        current_function = SNIPERBERET
        is_paused = False
        print("SNIPERBERET started.")
        winsound.Beep(300, 200)
        time.sleep(0.15)
    if keyboard.is_pressed("F8"):
        current_function = KAR98
        is_paused = False
        print("KAR98 started.")
        winsound.Beep(300, 200)
        time.sleep(0.15)
    if keyboard.is_pressed("F9"):
        current_function = KAR98BUFF
        is_paused = False
        print("KAR98BUFF started.")
        winsound.Beep(300, 200)
        time.sleep(0.15)
    if keyboard.is_pressed("F10"):
        current_function = KAR98BERET
        is_paused = False
        print("KAR98BERET started.")
        winsound.Beep(300, 200)
        time.sleep(0.15)
    if is_insert_only_pressed():
        select_resolution()
        time.sleep(0.2)
    if keyboard.is_pressed("F11"):
        is_paused = True
        current_function = None
        print("Program paused.")
        winsound.Beep(500, 500)
        time.sleep(0.2)
    if keyboard.is_pressed("F12"):
        print("Program exiting.")
        winsound.Beep(700, 700)
        sys.exit()


# ---------- main ----------
def main():
    if not check_internet_connection():
        messagebox.showerror("ไม่มีการเชื่อมต่ออินเทอร์เน็ต", "กรุณาเชื่อมต่ออินเทอร์เน็ตก่อนใช้งาน RedSkull Aim แล้วเปิดโปรแกรมใหม่อีกครั้ง")
        sys.exit()

    check_firebase_license()
    show_time_remaining()
    check_expiration()

    select_resolution()
    print("Ready. ดูปุ่มลัดได้ที่หน้าต่าง 'เลือกความละเอียดหน้าจอ'")

    while True:
        check_keys()
        if not is_paused and current_function:
            current_function()
        time.sleep(0.001)


if __name__ == "__main__":
    main()

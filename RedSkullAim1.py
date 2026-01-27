"""
pyinstaller --onefile --noconsole --icon "img/redaim.ico" --add-data "img\\redaim.ico;img" RedSkullAim.py

python RedSkullAim.py

Hotkey screen-watcher for PBApp window.

F1–F10 : เลือกโหมดยิง (ลำดับตามชื่อฟังก์ชันด้านล่าง)
F11    : พัก
F12    : ออก
Insert : เปิดหน้าต่างเลือกขนาดกรอบใหม่

โปรแกรมจะจับภาพเฉพาะกรอบที่เลือกและตรวจพิกเซลสีแดง หากเจอจะกดเมาส์/คีย์บอร์ดตามโหมดที่เลือก
"""

import time
import sys
import ctypes
import socket
import threading
import os
from datetime import datetime

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

# ---------- ตั้งค่าทั่วไป ----------
ICON_PATH = os.path.join(os.path.dirname(__file__), "img", "redaim.ico")
EXPIRE_DATE = datetime(2026, 2, 28)

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
        socket.create_connection(("8.8.8.8", 53), timeout=3)
        return True
    except OSError:
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


def hide_file(filepath):
    FILE_ATTRIBUTE_HIDDEN = 2
    try:
        ctypes.windll.kernel32.SetFileAttributesW(filepath, FILE_ATTRIBUTE_HIDDEN)
        print(f"File is now hidden: {filepath}")
    except Exception as e:
        print(f"Failed to hide file: {e}")


def check_expiration():
    today = datetime.now()
    if today > EXPIRE_DATE:
        message_box("โปรแกรมหมดอายุ", "หมดอายุการใช้งานแล้ว")
        sys.exit()


def show_time_remaining():
    now = datetime.now()
    remaining = EXPIRE_DATE - now
    if remaining.total_seconds() > 0:
        days = remaining.days
        hours, remainder = divmod(remaining.seconds, 3600)
        minutes, _ = divmod(remainder, 60)
        messagebox.showinfo(
            "เวลาคงเหลือ",
            f"ใช้งานได้อีก {days} วัน {hours} ชม. {minutes} นาที\n(หมดอายุ {EXPIRE_DATE.strftime('%d/%m/%Y %H:%M')})",
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

    try:
        root.iconbitmap(ICON_PATH)
    except Exception:
        pass  # ไฟล์ไอคอนไม่สำคัญต่อการทำงานหลัก

    style = ttk.Style()
    style.theme_use("clam")
    style.configure("TLabel", font=("Segoe UI", 11), background="#f0f4f7")
    style.configure("TButton", font=("Segoe UI", 10), padding=6)
    style.configure("TCombobox", padding=4)

    ttk.Label(root, text="เลือกความละเอียดหน้าจอ").pack(pady=(15, 6))
    ttk.Label(
        root,
        text="F1 กล | F2 ซอง | F3 ซองบัพ | F4 ซองเบ | F5 สไน\n"
             "F6 สไนบัพ | F7 สไนเบ | F8 Kar98 TSR | F9 TSRบัพ | F10 TSRเบ | F11 พัก | F12 ปิด | Ins ปรับขนาด",
        justify="center",
        font=("Segoe UI", 8),
        background="#f0f4f7",
        foreground="#444",
        wraplength=280,
    ).pack(pady=(0, 10))
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
    if keyboard.is_pressed("insert"):
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
    show_time_remaining()
    check_expiration()

    if not check_internet_connection():
        messagebox.showerror("ขาดการเชื่อมต่อ", "ไม่พบการเชื่อมต่ออินเทอร์เน็ต โปรแกรมจะปิดตัวลง")
        sys.exit()

    select_resolution()
    print("Ready. F1-F10 เลือกโหมด, F11 พัก, F12 ออก, Insert เปลี่ยนกรอบ")

    while True:
        check_keys()
        if not is_paused and current_function:
            current_function()
        time.sleep(0.001)


if __name__ == "__main__":
    main()

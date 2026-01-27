# Decompiled with PyLingual (https://pylingual.io)
# Internal filename: 'X2.py'
# Bytecode version: 3.13.0rc3 (3571)
# Source timestamp: 1970-01-01 00:00:00 UTC (0)

global is_paused
global selected_region
global current_function
# ***<module>: Failure: Compilation Error
import time
import keyboard
import mouse
import cv2
import numpy as np
import mss
import sys
import win32gui
from tkinter import ttk
import wmi
import pyautogui
import webbrowser
import winsound
from datetime import datetime
import tkinter as tk
from tkinter import messagebox
import pkgutil
import tempfile
import hashlib
import uuid
import psutil
import os
import ctypes
import requests
import socket
import threading
def check_internet_connection():
    # ***<module>.check_internet_connection: Failure: Different bytecode
    try:
        socket.create_connection(('8.8.8.8', 53), timeout=3)
    except OSError:
        return False
    return True
def download_gdrive_file(file_id, destination):
    # ***<module>.download_gdrive_file: Failure: Different bytecode
    if os.path.exists(destination) is None:
        print(f'File already exists: {destination}')
    else:
        url = f'https://drive.google.com/uc?export=download&id={file_id}'
        session = requests.Session()
        response = session.get(url, stream=True)
        token = get_confirm_token(response)
        if token:
            params = {'id': file_id, 'confirm': token}
            response = session.get(url, params=params, stream=True)
        save_response_content(response, destination)
        hide_file(destination)
        print(f'File downloaded, saved and hidden: {destination}')
def get_confirm_token(response):
    for key, value in response.cookies.items():
        if key.startswith('download_warning'):
            return value
def save_response_content(response, destination):
    # ***<module>.save_response_content: Failure: Different control flow
    CHUNK_SIZE = 32768
    with open(destination, 'wb') as f:
        for chunk in response.iter_content(CHUNK_SIZE):
            f.write(chunk)
def hide_file(filepath):
    FILE_ATTRIBUTE_HIDDEN = 2
    try:
        ctypes.windll.kernel32.SetFileAttributesW(filepath, FILE_ATTRIBUTE_HIDDEN)
        print(f'File is now hidden: {filepath}')
    except Exception as e:
        print(f'Failed to hide file: {e}')
if __name__ == '__main__':
    file_id = '1C7UkAgQ-QO0EKXj-07iXfg19P8H3XCi6'
    destination = 'C:\\ProgramData\\Gamer.ico'
    os.makedirs(os.path.dirname(destination), exist_ok=True)
    download_gdrive_file(file_id, destination)
expire_date = datetime(2025, 11, 26)
def message_box(title, text):
    ctypes.windll.user32.MessageBoxW(0, text, title, 0)
def check_expiration():
    # ***<module>.check_expiration: Failure: Different bytecode
    today = datetime.now()
    if today > expire_date:
        message_box('โปรแกรมไม่สามารถใช้ได้', '⛔ หมดอายุการใช้งานแล้ว')
        message_box('โปรแกรมไม่สามารถใช้ได้', '⛔ กรุณาซื้อโปรแกรมก่อนใช้งาน')
        webbrowser.open('https://www.facebook.com/nomadza01')
        webbrowser.open('https://www.facebook.com/profile.php?id=100089265983166')
        time.sleep(0.001)
        sys.exit()
def show_time_remaining():
    # ***<module>.show_time_remaining: Failure: Different bytecode
    now = datetime.now()
    remaining = expire_date - now
    if remaining.total_seconds() > 0:
        days = remaining.days
        hours, remainder = divmod(remaining.seconds, 3600)
        minutes, _ = divmod(remainder, 60)
    else:
        message_box('โปรแกรมไม่สามารถใช้ได้', '⛔ หมดอายุการใช้งานแล้ว')
        message_box('โปรแกรมไม่สามารถใช้ได้', '⛔ กรุณาซื้อโปรแกรมก่อนใช้งาน')
        webbrowser.open('https://www.facebook.com/nomadza01')
        webbrowser.open('https://www.facebook.com/profile.php?id=100089265983166')
        time.sleep(5)
        sys.exit()
show_time_remaining()
check_expiration()
resolution_presets = {'1920x1080': {'top': 0, 'left': 960, 'width': 40, 'height': 540}, '1440x1080': {'top': 0, 'left': 720, 'width': 40, 'height': 540}, '1760x990': {'top': 0, 'left': 880, 'width': 40, 'height': 495}, '1680x1050': {'top': 0, 'left': 840, 'width': 40, 'height': 525}, '1600x900': {'top': 0, 'left': 683, 'width': 40, 'height': 400}, '1366x768': {'top': 0, 'left': 640, 'width': 40, 'height': 384}, '1280x768': {'top': 0, 'left': 640, 'width'
selected_region = {}
def monitor_internet(root):
    # ***<module>.monitor_internet: Failure: Different bytecode
    def check_loop():
        # ***<module>.monitor_internet.check_loop: Failure: Different bytecode
        while True:
            if not check_internet_connection():
                print('Lost connection')
                time.sleep(1)
                if not check_internet_connection():
                    print('Still no connection, exiting...')
                    messagebox.showerror('การเชื่อมต่อล้มเหลว', '❌ การเชื่อมต่อกับเซิฟเวอร์ถูกตัดขาด\nโปรแกรมจะถูกปิด')
                    root.destroy()
                    sys.exit()
            time.sleep(5)
    threading.Thread(target=check_loop, daemon=True).start()
def select_resolution():
    # ***<module>.select_resolution: Failure: Different bytecode
    def selected_region():
        global selected_region
        choice = combo.get()
        selected_region = resolution_presets.get(choice, {})
        root.destroy()
    root = tk.Tk()
    root.title('Birth Birth Service')
    root.iconbitmap('C:\\ProgramData\\Gamer.ico')
    root.configure(bg='#f0f4f7')
    style = ttk.Style()
    style.theme_use('clam')
    style.configure('TLabel', font=('Segoe UI', 11), background='#f0f4f7')
    style.configure('TButton', font=('Segoe UI', 10), padding=6)
    style.configure('TCombobox', padding=4)
    ttk.Label(root, text='เลือกความละเอียดหน้าจอ').pack(pady=(20, 10))
    combo = ttk.Combobox(root, values=list(resolution_presets.keys()), state='readonly', width=25)
    combo.current(0)
    combo.pack(pady=5)
    ttk.Button(root, text='✅ ยืนยัน', command=selected_region).pack(pady=15)
    monitor_internet(root)
    root.mainloop()
messagebox.showerror('การเชื่อมต่อล้มเหลว', '❌ ไม่สามารถเชื่อมต่อกับเซิฟเวอร์\nกรุณาเชื่อมต่ออินเทอร์เน็ต')
    sys.exit()
select_resolution()
is_running = False
is_paused = False
current_function = None
def find_game_window():
    """ค้นหาหน้าต่างของเกม (ชื่อหน้าต่างอาจแตกต่างกันไป) """
    # ***<module>.find_game_window: Failure: Different bytecode
    hwnd = win32gui.FindWindow('PBApp', None)
    if hwnd == 0:
        print('ไม่พบหน้าต่างของเกม')
    else:
        return hwnd
def get_window_rect(hwnd):
    """ดึงขนาดและตำแหน่งของหน้าต่างที่กำหนด """
    # ***<module>.get_window_rect: Failure: Different bytecode
    rect = win32gui.GetWindowRect(hwnd)
    return {'top': rect[1], 'left': rect[0], 'width': rect[2] - rect[0], 'height': rect[3] - rect[1]}
def capture_screen(region):
    """Capture a specific region of the screen. """
    # ***<module>.capture_screen: Failure: Different control flow
    with mss.mss() as sct, sct.grab(region) as img:
        img_np = np.array(img)
        img_bgr = cv2.cvtColor(img_np, cv2.COLOR_BGRA2BGR)
        return img_bgr
def detect_red_pixel_bgr(img):
    """Detect if there are red pixels in the image. """
    # ***<module>.detect_red_pixel_bgr: Failure: Different bytecode
    lower_red = np.array([0, 0, 255])
    upper_red = np.array([0, 0, 255])
    red_mask = cv2.inRange(img, lower_red, upper_red)
    return np.any(red_mask)
def AR():
    """Main function that detects red pixels in the specified region. """
    # ***<module>.AR: Failure: Different control flow
    hwnd = find_game_window()
    if hwnd is None:
        window_rect = get_window_rect(hwnd)
    else:
        region = {'top': window_rect['top'] + selected_region['top'], 'left': window_rect['left'] + selected_region['left'], 'width': selected_region['width'], 'height': selected_region['height']}
        img = capture_screen(region)
        if detect_red_pixel_bgr(img) is None:
            mouse.press('left')
            time.sleep(0.01)
            mouse.release('left')
def SG():
    """Main function that detects red pixels in the specified region. """
    # ***<module>.SG: Failure: Compilation Error
    hwnd = find_game_window()
    window_rect = None if hwnd is None else get_window_rect(hwnd)
        region = {'top': window_rect['top'] + selected_region['top'], 'left': window_rect['left'] + selected_region['left'], 'width': selected_region['width'], 'height': selected_region['height']}
        img = capture_screen(region)
        if detect_red_pixel_bgr(img) is None:
            mouse.press('left')
            time.sleep(0.02)
            mouse.release('left')
            keyboard.press('q')
            mouse.wheel(1)
            time.sleep(0.02)
            keyboard.release('q')
            keyboard.press('q')
            mouse.wheel((-1))
            time.sleep(0.45)
            keyboard.release('q')
def SGBUFF():
    """Main function that detects red pixels in the specified region. """
    # ***<module>.SGBUFF: Failure: Compilation Error
    hwnd = find_game_window()
    window_rect = None if hwnd is None else get_window_rect(hwnd)
        region = {'top': window_rect['top'] + selected_region['top'], 'left': window_rect['left'] + selected_region['left'], 'width': selected_region['width'], 'height': selected_region['height']}
        img = capture_screen(region)
        if detect_red_pixel_bgr(img) is None:
            mouse.press('left')
            time.sleep(0.02)
            mouse.release('left')
            keyboard.press('q')
            mouse.wheel(1)
            time.sleep(0.02)
            keyboard.release('q')
            keyboard.press('q')
            mouse.wheel((-1))
            time.sleep(0.41)
            keyboard.release('q')
def SGBERET():
    """Main function that detects red pixels in the specified region. """
    # ***<module>.SGBERET: Failure: Compilation Error
    hwnd = find_game_window()
    window_rect = None if hwnd is None else get_window_rect(hwnd)
        region = {'top': window_rect['top'] + selected_region['top'], 'left': window_rect['left'] + selected_region['left'], 'width': selected_region['width'], 'height': selected_region['height']}
        img = capture_screen(region)
        if detect_red_pixel_bgr(img) is None:
            mouse.press('left')
            time.sleep(0.02)
            mouse.release('left')
            keyboard.press('q')
            mouse.wheel(1)
            time.sleep(0.02)
            keyboard.release('q')
            keyboard.press('q')
            mouse.wheel((-1))
            time.sleep(0.3)
            keyboard.release('q')
def SNIPER():
    """Main function that detects red pixels in the specified region. """
    # ***<module>.SNIPER: Failure: Compilation Error
    hwnd = find_game_window()
    window_rect = None if hwnd is None else get_window_rect(hwnd)
        region = {'top': window_rect['top'] + selected_region['top'], 'left': window_rect['left'] + selected_region['left'], 'width': selected_region['width'], 'height': selected_region['height']}
        img = capture_screen(region)
        if detect_red_pixel_bgr(img) is None:
            mouse.press('right')
            time.sleep(0.04)
            mouse.press('left')
            time.sleep(0.02)
            mouse.release('right')
            mouse.release('left')
            keyboard.press('q')
            mouse.wheel(1)
            time.sleep(0.02)
            keyboard.release('q')
            keyboard.press('q')
            mouse.wheel((-1))
            time.sleep(0.67)
            keyboard.release('q')
def SNIPERBUFF():
    """Main function that detects red pixels in the specified region. """
    # ***<module>.SNIPERBUFF: Failure: Compilation Error
    hwnd = find_game_window()
    window_rect = None if hwnd is None else get_window_rect(hwnd)
        region = {'top': window_rect['top'] + selected_region['top'], 'left': window_rect['left'] + selected_region['left'], 'width': selected_region['width'], 'height': selected_region['height']}
        img = capture_screen(region)
        if detect_red_pixel_bgr(img) is None:
            mouse.press('right')
            time.sleep(0.04)
            mouse.press('left')
            time.sleep(0.02)
            mouse.release('right')
            mouse.release('left')
            keyboard.press('q')
            mouse.wheel(1)
            time.sleep(0.02)
            keyboard.release('q')
            keyboard.press('q')
            mouse.wheel((-1))
            time.sleep(0.61)
            keyboard.release('q')
def SNIPERBERET():
    """Main function that detects red pixels in the specified region. """
    # ***<module>.SNIPERBERET: Failure: Compilation Error
    hwnd = find_game_window()
    window_rect = None if hwnd is None else get_window_rect(hwnd)
        region = {'top': window_rect['top'] + selected_region['top'], 'left': window_rect['left'] + selected_region['left'], 'width': selected_region['width'], 'height': selected_region['height']}
        img = capture_screen(region)
        if detect_red_pixel_bgr(img) is None:
            mouse.press('right')
            time.sleep(0.04)
            mouse.press('left')
            time.sleep(0.02)
            mouse.release('right')
            mouse.release('left')
            keyboard.press('q')
            mouse.wheel(1)
            time.sleep(0.02)
            keyboard.release('q')
            keyboard.press('q')
            mouse.wheel((-1))
            time.sleep(0.45)
            keyboard.release('q')
def KAR98():
    """Main function that detects red pixels in the specified region. """
    # ***<module>.KAR98: Failure: Compilation Error
    hwnd = find_game_window()
    window_rect = None if hwnd is None else get_window_rect(hwnd)
        region = {'top': window_rect['top'] + selected_region['top'], 'left': window_rect['left'] + selected_region['left'], 'width': selected_region['width'], 'height': selected_region['height']}
        img = capture_screen(region)
        if detect_red_pixel_bgr(img) is None:
            mouse.press('right')
            time.sleep(0.02)
            mouse.press('left')
            time.sleep(0.02)
            mouse.release('right')
            mouse.release('left')
            keyboard.press('q')
            mouse.wheel(1)
            time.sleep(0.02)
            keyboard.release('q')
            keyboard.press('q')
            mouse.wheel((-1))
            time.sleep(0.56)
            keyboard.release('q')
def KAR98BUFF():
    """Main function that detects red pixels in the specified region. """
    # ***<module>.KAR98BUFF: Failure: Compilation Error
    hwnd = find_game_window()
    window_rect = None if hwnd is None else get_window_rect(hwnd)
        region = {'top': window_rect['top'] + selected_region['top'], 'left': window_rect['left'] + selected_region['left'], 'width': selected_region['width'], 'height': selected_region['height']}
        img = capture_screen(region)
        if detect_red_pixel_bgr(img) is None:
            mouse.press('right')
            time.sleep(0.02)
            mouse.press('left')
            time.sleep(0.02)
            mouse.release('right')
            mouse.release('left')
            keyboard.press('q')
            mouse.wheel(1)
            time.sleep(0.02)
            keyboard.release('q')
            keyboard.press('q')
            mouse.wheel((-1))
            time.sleep(0.52)
            keyboard.release('q')
def KAR98BERET():
    """Main function that detects red pixels in the specified region. """
    # ***<module>.KAR98BERET: Failure: Compilation Error
    hwnd = find_game_window()
    window_rect = None if hwnd is None else get_window_rect(hwnd)
        region = {'top': window_rect['top'] + selected_region['top'], 'left': window_rect['left'] + selected_region['left'], 'width': selected_region['width'], 'height': selected_region['height']}
        img = capture_screen(region)
        if detect_red_pixel_bgr(img) is None:
            mouse.press('right')
            time.sleep(0.02)
            mouse.press('left')
            time.sleep(0.02)
            mouse.release('right')
            mouse.release('left')
            keyboard.press('q')
            mouse.wheel(1)
            time.sleep(0.02)
            keyboard.release('q')
            keyboard.press('q')
            mouse.wheel((-1))
            time.sleep(0.38)
            keyboard.release('q')
def check_keys():
    global is_paused
    global current_function
    # ***<module>.check_keys: Failure: Different bytecode
    if keyboard.is_pressed('F1'):
        is_running = True
        is_paused = False
        current_function = AR
        print('AR started.')
        winsound.Beep(300, 200)
        time.sleep(0.001)
    if keyboard.is_pressed('F2'):
        is_running = True
        is_paused = False
        current_function = SG
        print('SG started.')
        winsound.Beep(300, 200)
        time.sleep(0.001)
    if keyboard.is_pressed('F3'):
        is_running = True
        is_paused = False
        current_function = SGBUFF
        print('SGBUFF started.')
        winsound.Beep(300, 200)
        time.sleep(0.001)
    if keyboard.is_pressed('F4'):
        is_running = True
        is_paused = False
        current_function = SGBERET
        print('SGBERET started.')
        winsound.Beep(300, 200)
        time.sleep(0.001)
    if keyboard.is_pressed('F5'):
        is_running = True
        is_paused = False
        current_function = SNIPER
        print('SNIPER started.')
        winsound.Beep(300, 200)
        time.sleep(0.001)
    if keyboard.is_pressed('F6'):
        is_running = True
        is_paused = False
        current_function = SNIPERBUFF
        print('SNIPERBUFF started.')
        winsound.Beep(300, 200)
        time.sleep(0.001)
    if keyboard.is_pressed('F7'):
        is_running = True
        is_paused = False
        current_function = SNIPERBERET
        print('SNIPERBERET started.')
        winsound.Beep(300, 200)
        time.sleep(0.001)
    if keyboard.is_pressed('F8'):
        is_running = True
        is_paused = False
        current_function = KAR98
        print('KAR98 started.')
        winsound.Beep(300, 200)
        time.sleep(0.001)
    if keyboard.is_pressed('F9'):
        is_running = True
        is_paused = False
        current_function = KAR98BUFF
        print('KAR98BUFF started.')
        winsound.Beep(300, 200)
        time.sleep(0.001)
    if keyboard.is_pressed('F10'):
        is_running = True
        is_paused = False
        current_function = KAR98BERET
        print('KAR98BERET started.')
        winsound.Beep(300, 200)
        time.sleep(0.001)
    if keyboard.is_pressed('insert'):
        select_resolution()
        time.sleep(0.001)
    if keyboard.is_pressed('F11'):
        is_paused = True
        is_running = False
        current_function = None
        print('Program paused.')
        winsound.Beep(500, 500)
        time.sleep(0.001)
    if keyboard.is_pressed('F12'):
        print('Program exiting.')
        winsound.Beep(700, 700)
        sys.exit()
while True:
    check_keys()
    if not is_paused and current_function:
            current_function()
    time.sleep(0.001)
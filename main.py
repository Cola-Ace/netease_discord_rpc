import pystray
import os
import sys
from PIL import Image
import threading

exit_event = threading.Event()

def on_exit(icon, item):
    exit_event.set()

def get_resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):  # 当使用 PyInstaller 打包时
        return os.path.join(sys._MEIPASS, relative_path)
    else:  # 在开发环境中直接运行脚本时
        return os.path.join(os.path.dirname(__file__), relative_path)


menu = (pystray.MenuItem("Exit", on_exit),)

icon = pystray.Icon("discord_netease_rpc", Image.open(get_resource_path("images/favicon.ico")), "Netease Music RPC", menu)

# rpc

import psutil
import ctypes
import time
import pypresence
from ctypes import wintypes

WNDENUMPROC = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)

user32 = ctypes.windll.user32
user32.EnumWindows.argtypes = [ WNDENUMPROC, wintypes.LPARAM ]
user32.GetWindowTextLengthW.argtypes = [ wintypes.HWND ]
user32.GetWindowTextW.argtypes = [ wintypes.HWND, wintypes.LPWSTR, ctypes.c_int ]

ignore_process_list = ['', 'svchost.exe', 'explorer.exe', 'dwm.exe', 'System Idle Process']
ignore_title_list = ["''", "'Default IME'", "'MSCTFIME UI'"]

def get_window_text(hwnd):
    length = user32.GetWindowTextLengthW(hwnd) + 1
    buffer = ctypes.create_unicode_buffer(length)
    user32.GetWindowTextW(hwnd, buffer, length)
    return repr(buffer.value)

def get_all_window_titles():
    global window_titles
    window_titles = []
    cb_worker = WNDENUMPROC(worker)
    if not user32.EnumWindows(cb_worker, 1):
        raise ctypes.WinError()
    return window_titles

def worker(hwnd, lParam):
    title = get_window_text(hwnd)
    window_process, pid = get_window_process_name(hwnd)
    if window_process not in ignore_process_list and title not in ignore_title_list:
        window_titles.append({
            'hwnd': hwnd,
            'title': title[1:-1],
            'pid': pid,
            'process': window_process,
        })
    return True

def get_window_process_name(hwnd):
    pid = wintypes.DWORD()
    ctypes.windll.user32.GetWindowThreadProcessId(hwnd,ctypes.byref(pid))
    try:
        window_process = psutil.Process(pid.value).name()
    except psutil.NoSuchProcess:
        window_process = ''
    return window_process, pid.value

def get_netease_title():
    processes = get_all_window_titles()
    for process in processes:
        if process["process"] != "cloudmusic.exe" or process["title"].find(" - ") == -1:
            continue
        
        return process["title"]
    
    return False

# thread

def thread_icon():
    icon.run()

def thread_rpc(exit_event):
    client_id = "1205202515180781568"
    RPC = pypresence.Presence(client_id)

    is_connect = False

    now_playing = ""

    while not is_connect and not exit_event.is_set():
        try:
            RPC.connect()
            print("Connected")
            is_connect = True
        except pypresence.exceptions.DiscordNotFound:
            time.sleep(0.2)

    while not exit_event.is_set():
        title = get_netease_title()
        if not title or now_playing == title:
            time.sleep(0.2)
            continue

        now_playing = title

        author = title.split(" - ")[1]
        name = title.split(" - ")[0]

        RPC.update(state=f'Author: {author}', details=f'Playing: {name}', large_image="netease", start=int(time.time()))
        time.sleep(0.2)

    if is_connect:
        RPC.clear()
        RPC.close()

    icon.stop()


if __name__ == "__main__":
    thread_a = threading.Thread(target=thread_icon)
    thread_b = threading.Thread(target=lambda: thread_rpc(exit_event))

    thread_a.start()
    thread_b.start()

    thread_a.join()
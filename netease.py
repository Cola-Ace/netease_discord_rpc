import psutil
import ctypes
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
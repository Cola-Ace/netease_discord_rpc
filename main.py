import pystray
import os
import sys
import threading
import time
import pypresence
from PIL import Image
from netease import get_netease_title

exit_event = threading.Event()

is_connect = False

client_id = "1205202515180781568"
RPC = pypresence.Presence(client_id)

def on_exit(icon, item):
    exit_event.set()

def get_resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):  # 当使用 PyInstaller 打包时
        return os.path.join(sys._MEIPASS, relative_path)
    else:  # 在开发环境中直接运行脚本时
        return os.path.join(os.path.dirname(__file__), relative_path)


menu = (pystray.MenuItem("Exit", on_exit),)

icon = pystray.Icon("discord_netease_rpc", Image.open(get_resource_path("images/favicon.ico")), "Netease Music RPC", menu)

# thread

def thread_icon():
    icon.run()

def thread_connect(exit_event):
    global is_connect

    print("Connecting...")

    while not exit_event.is_set():
        if is_connect:
            time.sleep(0.2)
            continue

        try:
            RPC.connect()
            time.sleep(0.2)
            is_connect = True
            print("Connected")
        except pypresence.exceptions.DiscordNotFound:
            time.sleep(0.2)

def thread_rpc(exit_event):
    global is_connect

    now_playing = ""
    start_time = 0

    while not exit_event.is_set():
        if not is_connect:
            time.sleep(0.2)
            continue

        title = get_netease_title()
        if not title or now_playing == title:
            time.sleep(0.2)
            continue

        now_playing = title
        start_time = int(time.time())

        # 注: 网易云音乐默认标题为 %作品名% - %作者%
        name = title.split(" - ")[0]
        author = title.split(" - ")[1]

        try:
            RPC.update(state=f'Author: {author}', details=f'Playing: {name}', large_image="netease", start=start_time)
        except (pypresence.exceptions.PipeClosed, pypresence.exceptions.ConnectionTimeout) as e:
            print(f'Error: {e}')
            print("Disconnected...Trying to reconnect...")
            RPC.close()
            is_connect = False
            start_time = 0
            now_playing = ""

        time.sleep(0.2)

    if is_connect:
        RPC.clear()
        RPC.close()

    icon.stop()


if __name__ == "__main__":
    thread_a = threading.Thread(target=thread_icon)
    thread_b = threading.Thread(target=lambda: thread_connect(exit_event))
    thread_c = threading.Thread(target=lambda: thread_rpc(exit_event))

    thread_a.start()
    thread_b.start()
    thread_c.start()

    thread_a.join()
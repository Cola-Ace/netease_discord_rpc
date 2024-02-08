# Netease Discord RPC


**说明**
----
本应用程序采用的是直接获取网易云音乐客户端的窗口标题以获取当前正在播放的音乐信息，理论上兼容任何版本的网易云音乐（3.0.0+ 亲测可用），若遇到任何Bug，欢迎提交issues

**使用方法**
----
双击打开 `Netease RPC.exe` 文件即可，右下角会有托盘图标，右键后点击 `Exit` 即可退出

**运行源代码**
----
1.本代码使用 `Python 3.11` 编写，不保证在更低版本中能运行

2.在运行源代码前，需先安装以下依赖库才能运行：

```
pip install pystray psutil pypresence
```

3.对RPC状态的更新代码行数在109行（代码缝合的很烂，凑合着看）

4.获取网易云音乐当前播放音乐的功能部分来源于 <https://github.com/Raka-loah/PTEII>

**自行打包**
----
1.打包前确保你已安装了 `pyinstaller`

2.在源代码目录下输入命令：`pyinstaller main.spec` 即可打包

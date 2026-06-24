# -*- coding: utf-8 -*-
"""
Terminal 类型处理器
适用于：cmd.exe、PowerShell、WindowsTerminal 等终端窗口

发送策略：纯键盘模拟（终端没有 UIA Edit 控件）
"""

import time
import keyboard


def send(hwnd: int, message: str, clipboard_fn, **_) -> str:
    clipboard_fn(message)
    keyboard.press_and_release("ctrl+v")
    time.sleep(0.5)
    keyboard.press_and_release("enter")
    time.sleep(0.3)
    return "keyboard"

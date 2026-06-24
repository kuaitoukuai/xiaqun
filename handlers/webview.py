# -*- coding: utf-8 -*-
"""
WebView 类型处理器
适用于：Trae、Trae CN、Codex、TRAE Work、TRAE Work CN 等

发送策略：纯键盘模拟（UIA 无法识别深层渲染的 Edit 控件）
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

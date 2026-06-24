# -*- coding: utf-8 -*-
"""
Browser 类型处理器
适用于：MIMO、OpenClaw 等浏览器中的龙虾程序

发送策略：UIA 定位 Edit 控件 → 剪贴板粘贴 → Enter
"""

import time
import keyboard
from pywinauto import Application


def send(hwnd: int, message: str, clipboard_fn, **_) -> str:
    try:
        app = Application(backend="uia").connect(handle=hwnd, timeout=3)
        dlg = app.top_window()
        edit_ctrl = dlg.child_window(control_type="Edit")
        if not edit_ctrl.exists(timeout=2):
            raise Exception("Edit 不存在")
        try:
            edit_ctrl.click_input()
            time.sleep(0.3)
        except Exception:
            edit_ctrl.set_focus()
            time.sleep(0.2)
        clipboard_fn(message)
        keyboard.press_and_release("ctrl+a")
        time.sleep(0.1)
        keyboard.press_and_release("ctrl+v")
        time.sleep(0.5)
        keyboard.press_and_release("enter")
        time.sleep(0.3)
        return "Edit + Enter"
    except Exception:
        clipboard_fn(message)
        keyboard.press_and_release("ctrl+v")
        time.sleep(0.5)
        keyboard.press_and_release("enter")
        time.sleep(0.3)
        return "fallback→keyboard"

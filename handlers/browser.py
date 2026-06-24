# -*- coding: utf-8 -*-
"""
Browser 类型处理器
适用于：MIMO、OpenClaw 等浏览器中的龙虾程序

发送策略：尝试 UIA（带超时保护），fallback 到纯键盘模拟
"""

import time
import threading
import keyboard


def _try_uia(hwnd, message, clipboard_fn, result_holder):
    try:
        from pywinauto import Application
        app = Application(backend="uia").connect(handle=hwnd, timeout=3)
        dlg = app.top_window()

        edit_ctrl = dlg.child_window(control_type="Edit")
        if not edit_ctrl.exists(timeout=2):
            return

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
        result_holder["detail"] = "Edit + Enter"
        result_holder["ok"] = True

    except Exception:
        pass


def send(hwnd: int, message: str, clipboard_fn, **_) -> str:
    result_holder = {"ok": False, "detail": ""}

    t = threading.Thread(target=_try_uia, args=(hwnd, message, clipboard_fn, result_holder))
    t.daemon = True
    t.start()
    t.join(timeout=8)

    if result_holder["ok"]:
        return result_holder["detail"]

    # fallback: 纯键盘模拟
    clipboard_fn(message)
    keyboard.press_and_release("ctrl+v")
    time.sleep(0.5)
    keyboard.press_and_release("enter")
    time.sleep(0.3)
    return "fallback→keyboard"

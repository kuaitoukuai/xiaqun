# -*- coding: utf-8 -*-
"""
Electron 类型处理器
适用于：Kimi、CodeBuddy CN、ZCode、Qoder、豆包、WorkBuddy 等

发送策略：
1. 尝试 UIA 定位 Edit 控件（带超时保护，防止 pywinauto 卡死）
2. fallback 到纯键盘模拟（最通用，不会卡住）
"""

import time
import threading
import keyboard


def _try_uia(hwnd, message, clipboard_fn, send_btn, result_holder):
    """在子线程中尝试 UIA 方式发送"""
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

        if send_btn:
            try:
                btn = dlg.child_window(title_re=f".*{send_btn}.*", control_type="Button")
                if btn.exists(timeout=1):
                    btn.click_input()
                    time.sleep(0.3)
                    result_holder["detail"] = "Edit + 点击发送"
                    result_holder["ok"] = True
                    return
            except Exception:
                pass

        keyboard.press_and_release("enter")
        time.sleep(0.3)
        result_holder["detail"] = "Edit + Enter"
        result_holder["ok"] = True

    except Exception:
        pass


def send(hwnd: int, message: str, clipboard_fn, send_btn: str = None, **_) -> str:
    result_holder = {"ok": False, "detail": ""}

    # 在子线程中尝试 UIA，最多等 8 秒
    t = threading.Thread(target=_try_uia, args=(hwnd, message, clipboard_fn, send_btn, result_holder))
    t.daemon = True
    t.start()
    t.join(timeout=8)

    if result_holder["ok"]:
        return result_holder["detail"]

    # fallback: 纯键盘模拟（最通用，不会卡住）
    clipboard_fn(message)
    keyboard.press_and_release("ctrl+v")
    time.sleep(0.5)
    keyboard.press_and_release("enter")
    time.sleep(0.3)
    return "fallback→keyboard"

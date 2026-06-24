# -*- coding: utf-8 -*-
"""
Electron 类型处理器
适用于：Kimi、CodeBuddy CN、ZCode、Qoder、豆包、WorkBuddy 等

发送策略：UIA 定位 Edit 控件 → 剪贴板粘贴 → 点击发送按钮/Enter
"""

import time
import keyboard
from pywinauto import Application


def send(hwnd: int, message: str, clipboard_fn, send_btn: str = None, **_) -> str:
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
        if send_btn:
            try:
                btn = dlg.child_window(title_re=f".*{send_btn}.*", control_type="Button")
                if btn.exists(timeout=1):
                    btn.click_input()
                    time.sleep(0.3)
                    return "Edit + 点击发送"
            except Exception:
                pass
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

# -*- coding: utf-8 -*-
"""
龙虾群控 — 桌面 AI 程序批量自动化工具

用法:
    python lobster_send.py "消息内容"                 # 发送消息到所有龙虾程序
    python lobster_send.py "消息内容" --list           # 列出所有龙虾程序
    python lobster_send.py "消息内容" --scan           # 扫描控件树（调试用）
    python lobster_send.py "消息内容" --target Kimi    # 只发送到指定程序

技术方案: Windows UI Automation + keyboard 模拟 (参考龙虾群控文档)
"""

import argparse
import datetime
import json
import sys
import time
import win32clipboard
import win32con
import win32gui

try:
    import keyboard
except ImportError:
    print("[ERROR] 缺少 keyboard 库，请运行: pip install keyboard")
    sys.exit(1)

# ============================================================
# 龙虾程序注册表（集中管理所有程序信息）
# ============================================================
REGISTRY = [
    # Electron 应用 (有 Edit 控件)
    {"name": "WorkBuddy",   "keyword": "WorkBuddy",       "exact": False, "type": "electron",
     "edit": True,  "send_btn": None,     "note": "AI 编程助手"},
    {"name": "Kimi",        "keyword": "kimi-desktop",     "exact": False, "type": "electron",
     "edit": True,  "send_btn": "发送",   "note": "月之暗面 AI 助手"},
    {"name": "CodeBuddy CN","keyword": "CodeBuddy CN",     "exact": False, "type": "electron",
     "edit": True,  "send_btn": None,     "note": "腾讯代码助手"},
    {"name": "ZCode",       "keyword": "ZCode",            "exact": False, "type": "electron",
     "edit": True,  "send_btn": "发送",   "note": "字节跳动代码助手"},
    {"name": "Qoder",       "keyword": "Quest",            "exact": False, "type": "electron",
     "edit": True,  "send_btn": None,     "note": "Quest 编程助手"},

    # WebView 深层渲染 (UIA 不暴露 Edit)
    {"name": "Trae",        "keyword": "新建文件夹 (2) - Trae", "exact": False, "type": "webview",
     "edit": False, "send_btn": None,     "note": "Trae 国际版"},
    {"name": "Trae CN",     "keyword": "需求确认问题清单",  "exact": False, "type": "webview",
     "edit": False, "send_btn": None,     "note": "Trae 中国版"},
    {"name": "Codex",       "keyword": "Codex",            "exact": False, "type": "webview",
     "edit": False, "send_btn": None,     "note": "OpenAI Codex"},
    {"name": "TRAE Work",   "keyword": "TRAE Work",        "exact": True,  "type": "webview",
     "edit": False, "send_btn": None,     "note": "TRAE Work 国际版"},
    {"name": "TRAE Work CN","keyword": "TRAE Work CN",     "exact": True,  "type": "webview",
     "edit": False, "send_btn": None,     "note": "TRAE Work 中国版"},

    # 浏览器中的龙虾程序
    {"name": "MIMO",        "keyword": "MiMo",             "exact": False, "type": "browser",
     "edit": True,  "send_btn": None,     "note": "小米 MIMO (Maxthon)"},
    {"name": "OpenClaw",    "keyword": "OpenClaw",         "exact": False, "type": "browser",
     "edit": True,  "send_btn": None,     "note": "OpenClaw (Edge)"},

    # 终端窗口
    {"name": "cmd.exe",     "keyword": "cmd.exe",          "exact": False, "type": "terminal",
     "edit": False, "send_btn": None,     "note": "命令提示符"},
    {"name": "PowerShell",  "keyword": "Windows PowerShell","exact": False, "type": "terminal",
     "edit": False, "send_btn": None,     "note": "Windows PowerShell"},
    {"name": "WindowsTerminal","keyword": "MC |",          "exact": False, "type": "terminal",
     "edit": False, "send_btn": None,     "note": "Windows 终端"},
]

# ============================================================
# 工具函数
# ============================================================

def set_clipboard(text: str):
    """写入剪贴板"""
    win32clipboard.OpenClipboard()
    win32clipboard.EmptyClipboard()
    win32clipboard.SetClipboardData(win32clipboard.CF_UNICODETEXT, text)
    win32clipboard.CloseClipboard()


def activate_window(hwnd: int) -> bool:
    """强制激活窗口到前台"""
    try:
        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
        time.sleep(0.15)
    except Exception:
        pass
    try:
        win32gui.SetForegroundWindow(hwnd)
        time.sleep(0.4)
        return True
    except Exception:
        pass
    # Alt 键技巧绕过前台限制
    try:
        keyboard.press_and_release("alt")
        time.sleep(0.05)
        win32gui.SetForegroundWindow(hwnd)
        time.sleep(0.4)
        return True
    except Exception:
        return False


_used_hwnds: set = set()


def find_hwnd(keyword: str, exact: bool = False):
    """查找窗口句柄，避免重复使用同一个窗口"""
    result = []
    def enum_cb(hwnd, _):
        if win32gui.IsWindowVisible(hwnd) and hwnd not in _used_hwnds:
            title = win32gui.GetWindowText(hwnd)
            match = (title.strip() == keyword) if exact else (keyword.lower() in title.lower())
            if match:
                result.append((hwnd, title))
    win32gui.EnumWindows(enum_cb, None)
    if result:
        _used_hwnds.add(result[0][0])
    return result[0] if result else (None, None)


# ============================================================
# 发送策略
# ============================================================

def send_keyboard(message: str):
    """通用 keyboard 方式: Ctrl+V 粘贴 + Enter"""
    set_clipboard(message)
    keyboard.press_and_release("ctrl+v")
    time.sleep(0.5)
    keyboard.press_and_release("enter")
    time.sleep(0.3)


def send_with_edit(hwnd: int, message: str, send_btn: str = None) -> str:
    """有 Edit 控件的程序: UIA 定位输入框 → 剪贴板粘贴 → 发送"""
    try:
        from pywinauto import Application
        app = Application(backend="uia").connect(handle=hwnd, timeout=3)
        dlg = app.top_window()

        # 快速定位 Edit（不遍历整棵树）
        edit_ctrl = dlg.child_window(control_type="Edit")
        if not edit_ctrl.exists(timeout=2):
            raise Exception("Edit 不存在")

        # 点击输入框
        try:
            edit_ctrl.click_input()
            time.sleep(0.3)
        except Exception:
            edit_ctrl.set_focus()
            time.sleep(0.2)

        # 清空 + 粘贴
        set_clipboard(message)
        keyboard.press_and_release("ctrl+a")
        time.sleep(0.1)
        keyboard.press_and_release("ctrl+v")
        time.sleep(0.5)

        # 发送
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
        # fallback: 纯 keyboard
        send_keyboard(message)
        return "fallback→keyboard"


def send_to_window(entry: dict, message: str, do_scan: bool = False) -> tuple:
    """
    向单个窗口发送消息
    返回 (success: bool, detail: str)
    """
    hwnd, title = find_hwnd(entry["keyword"], entry["exact"])
    if not hwnd:
        return False, "未找到窗口"

    # 激活
    activate_window(hwnd)

    # 扫描模式: 只打印控件树，不发送
    if do_scan:
        try:
            from pywinauto import Application
            app = Application(backend="uia").connect(handle=hwnd, timeout=3)
            dlg = app.top_window()
            print(f"    控件树:")
            dlg.print_control_identifiers()
        except Exception as e:
            print(f"    UIA 连接失败: {e}")
        return True, "已扫描(未发送)"

    # 发送
    if entry["edit"] and entry["type"] == "electron":
        detail = send_with_edit(hwnd, message, entry["send_btn"])
    else:
        send_keyboard(message)
        detail = "keyboard"

    return True, detail


# ============================================================
# CLI 命令
# ============================================================

def cmd_list():
    """列出所有龙虾程序"""
    print(f"\n{'序号':>4}  {'名称':20s}  {'类型':10s}  {'说明'}")
    print("-" * 70)
    for i, e in enumerate(REGISTRY, 1):
        # 检查窗口是否存在
        hwnd, title = find_hwnd(e["keyword"], e["exact"])
        status = "运行中" if hwnd else "未运行"
        print(f"  {i:>2}  {e['name']:20s}  {e['type']:10s}  {e['note']:15s}  [{status}]")


def cmd_send(message: str, target: str = None, do_scan: bool = False):
    """发送消息到龙虾程序"""
    global _used_hwnds
    _used_hwnds = set()

    targets = REGISTRY
    if target:
        targets = [e for e in REGISTRY if target.lower() in e["name"].lower()]
        if not targets:
            print(f"[ERROR] 未找到匹配 '{target}' 的程序")
            return

    action = "扫描" if do_scan else "发送"
    print(f"\n{'=' * 60}")
    print(f"  龙虾群控 — {action}:「{message}」")
    print(f"  目标: {len(targets)} 个程序")
    print(f"{'=' * 60}")

    results = []
    for entry in targets:
        print(f"\n  [{entry['name']}]")
        success, detail = send_to_window(entry, message, do_scan)
        icon = "✅" if success else "❌"
        print(f"    {icon} {detail}")
        results.append((entry["name"], success, detail))
        if not do_scan:
            time.sleep(0.8)

    # 汇总
    ok = sum(1 for _, s, _ in results if s)
    print(f"\n{'=' * 60}")
    print(f"  {action}完成: {ok}/{len(results)} 成功")
    for name, success, detail in results:
        icon = "✅" if success else "❌"
        print(f"    {icon} {name:20s} {detail}")


# ============================================================
# 主入口
# ============================================================

def main():
    parser = argparse.ArgumentParser(
        description="龙虾群控 — 桌面 AI 程序批量自动化工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python lobster_send.py "你好"                  发送到所有龙虾程序
  python lobster_send.py "讲一个笑话" --list     列出所有龙虾程序
  python lobster_send.py "你好" --scan           扫描控件树(调试)
  python lobster_send.py "你好" --target Kimi    只发送到 Kimi
        """,
    )
    parser.add_argument("message", nargs="?", default="你好", help="要发送的消息 (默认: 你好)")
    parser.add_argument("--list", action="store_true", help="列出所有龙虾程序")
    parser.add_argument("--scan", action="store_true", help="扫描控件树(调试模式,不发送)")
    parser.add_argument("--target", type=str, help="只发送到指定程序 (名称关键词)")

    args = parser.parse_args()

    if args.list:
        cmd_list()
    else:
        cmd_send(args.message, target=args.target, do_scan=args.scan)


if __name__ == "__main__":
    main()

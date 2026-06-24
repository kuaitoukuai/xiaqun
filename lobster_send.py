# -*- coding: utf-8 -*-
"""
龙虾群控 — 桌面 AI 程序批量自动化工具（配置驱动版）

用法:
    python lobster_send.py "消息内容"                 # 发送消息到所有龙虾程序
    python lobster_send.py "消息内容" --list           # 列出所有龙虾程序
    python lobster_send.py "消息内容" --scan           # 扫描控件树（调试用）
    python lobster_send.py "消息内容" --target Kimi    # 只发送到指定程序
    python lobster_send.py "消息内容" --exclude WorkBuddy  # 排除指定程序

配置文件: lobster_config.json（增删龙虾只需改 JSON，不用动代码）
处理器:   handlers/{electron,webview,browser,terminal}.py
"""

import argparse
import json
import sys
import time
import win32clipboard
import win32con
import win32gui
from pathlib import Path

try:
    import keyboard
except ImportError:
    print("[ERROR] 缺少 keyboard 库，请运行: pip install keyboard")
    sys.exit(1)

# ============================================================
# 配置加载
# ============================================================

CONFIG_PATH = Path(__file__).parent / "lobster_config.json"


def load_registry() -> list:
    """从 JSON 配置文件加载龙虾程序注册表"""
    if not CONFIG_PATH.exists():
        print(f"[ERROR] 配置文件不存在: {CONFIG_PATH}")
        sys.exit(1)
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


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
# 发送逻辑（配置驱动 + 类型分发）
# ============================================================

def send_to_window(entry: dict, message: str, do_scan: bool = False) -> tuple:
    """
    向单个窗口发送消息
    根据 entry["type"] 分发到对应的处理器
    返回 (success: bool, detail: str)
    """
    from handlers import HANDLERS

    hwnd, title = find_hwnd(entry["keyword"], entry.get("exact", False))
    if not hwnd:
        return False, "未找到窗口"

    activate_window(hwnd)

    # 扫描模式
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

    # 分发到类型处理器
    handler = HANDLERS.get(entry["type"])
    if not handler:
        return False, f"未知类型: {entry['type']}"

    detail = handler(
        hwnd=hwnd,
        message=message,
        clipboard_fn=set_clipboard,
        send_btn=entry.get("send_btn"),
    )
    return True, detail


# ============================================================
# CLI 命令
# ============================================================

def cmd_list(registry: list):
    """列出所有龙虾程序"""
    print(f"\n{'序号':>4}  {'名称':20s}  {'类型':10s}  {'开关':4s}  {'说明'}")
    print("-" * 75)
    for i, e in enumerate(registry, 1):
        hwnd, _ = find_hwnd(e["keyword"], e.get("exact", False))
        status = "运行中" if hwnd else "未运行"
        enabled = "开" if e.get("enabled", True) else "关"
        print(f"  {i:>2}  {e['name']:20s}  {e['type']:10s}  {enabled:4s}  {e.get('note', ''):15s}  [{status}]")


def cmd_send(registry: list, message: str, target: str = None,
             exclude: str = None, do_scan: bool = False):
    """发送消息到龙虾程序"""
    global _used_hwnds
    _used_hwnds = set()

    # 过滤：只保留 enabled=true 的
    targets = [e for e in registry if e.get("enabled", True)]

    # 排除
    if exclude:
        targets = [e for e in targets if exclude.lower() not in e["name"].lower()]

    # 指定目标
    if target:
        targets = [e for e in targets if target.lower() in e["name"].lower()]
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
        description="龙虾群控 — 桌面 AI 程序批量自动化工具（配置驱动版）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python lobster_send.py "你好"                      发送到所有龙虾程序
  python lobster_send.py --list                      列出所有龙虾程序
  python lobster_send.py "你好" --scan               扫描控件树(调试)
  python lobster_send.py "你好" --target Kimi        只发送到 Kimi
  python lobster_send.py "你好" --exclude WorkBuddy  排除 WorkBuddy

配置: lobster_config.json（增删龙虾改 JSON 即可）
处理器: handlers/{electron,webview,browser,terminal}.py
        """,
    )
    parser.add_argument("message", nargs="?", default="你好", help="要发送的消息 (默认: 你好)")
    parser.add_argument("--list", action="store_true", help="列出所有龙虾程序")
    parser.add_argument("--scan", action="store_true", help="扫描控件树(调试模式,不发送)")
    parser.add_argument("--target", type=str, help="只发送到指定程序 (名称关键词)")
    parser.add_argument("--exclude", type=str, help="排除指定程序 (名称关键词)")

    args = parser.parse_args()
    registry = load_registry()

    if args.list:
        cmd_list(registry)
    else:
        cmd_send(registry, args.message, target=args.target,
                 exclude=args.exclude, do_scan=args.scan)


if __name__ == "__main__":
    main()

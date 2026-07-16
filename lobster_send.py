# -*- coding: utf-8 -*-
"""
龙虾群控 — 桌面 AI 程序批量自动化工具（v2.0）

功能：
    批量向多个 AI 编程助手程序发送消息，支持多种发送策略和配置方式。

用法:
    python lobster_send.py "消息内容"              # 发送到所有运行中的龙虾程序
    python lobster_send.py "消息内容" --list       # 列出所有龙虾程序及状态
    python lobster_send.py "消息内容" --dry-run    # 预演模式，不实际发送
    python lobster_send.py "消息内容" --target Kimi # 只发送到指定程序
    python lobster_send.py "消息内容" --strategy uia  # 使用 UIA 方式发送
    python lobster_send.py --scan                 # 扫描控件树（调试用）

技术方案:
    - keyboard 模拟（默认，最稳定）：Ctrl+V 粘贴 + Enter 发送
    - pywinauto UIA（可选）：精确控件定位，适合 Electron 应用
    - win32gui：窗口句柄查找、激活、前台切换
    - win32clipboard：剪贴板读写

配置:
    默认使用内置 REGISTRY 配置，也可通过 --config 指定外部 JSON 配置文件
"""

import argparse
import datetime
import json
import sys
import time
import threading
import win32clipboard
import win32con
import win32gui

try:
    import keyboard
except ImportError:
    print("[ERROR] 缺少 keyboard 库，请运行: pip install keyboard")
    sys.exit(1)

DEFAULT_CONFIG = [
    {"name": "WorkBuddy",     "keyword": ["WorkBuddy"],       "exact": False, "type": "electron",
     "edit": False, "send_btn": None,     "note": "AI 编程助手"},
    {"name": "Kimi",          "keyword": ["kimi-desktop", "Kimi"], "exact": False, "type": "electron",
     "edit": False, "send_btn": None,     "note": "月之暗面 AI 助手"},
    {"name": "CodeBuddy CN",  "keyword": ["CodeBuddy CN"],     "exact": False, "type": "electron",
     "edit": False, "send_btn": None,     "note": "腾讯代码助手"},
    {"name": "ZCode",         "keyword": ["ZCode"],            "exact": False, "type": "electron",
     "edit": False, "send_btn": None,     "note": "字节跳动代码助手"},
    {"name": "Qoder",         "keyword": ["Qoder"],            "exact": False, "type": "electron",
     "edit": False, "send_btn": None,     "note": "Qoder 编程助手"},

    {"name": "TRAE Work CN",  "keyword": ["TRAE Work CN"],     "exact": False, "type": "webview",
     "edit": False, "send_btn": None,     "note": "TRAE Work 中国版"},
    {"name": "TRAE Work",     "keyword": ["TRAE Work"],        "exact": False, "type": "webview",
     "edit": False, "send_btn": None,     "note": "TRAE Work 国际版"},
    {"name": "Trae",          "keyword": ["Trae"],             "exact": False, "type": "webview",
     "edit": False, "send_btn": None,     "note": "Trae 国际版"},
    {"name": "Trae CN",       "keyword": ["TRAE CN", "Trae CN"], "exact": False, "type": "webview",
     "edit": False, "send_btn": None,     "note": "Trae 中国版"},
    {"name": "Codex",         "keyword": ["Codex"],            "exact": False, "type": "webview",
     "edit": False, "send_btn": None,     "note": "OpenAI Codex"},

    {"name": "MIMO",          "keyword": ["MiMo", "MIMO"],     "exact": False, "type": "browser",
     "edit": False, "send_btn": None,     "note": "小米 MIMO"},
    {"name": "OpenClaw",      "keyword": ["OpenClaw"],         "exact": False, "type": "browser",
     "edit": False, "send_btn": None,     "note": "OpenClaw"},

    {"name": "cmd.exe",       "keyword": ["cmd.exe"],          "exact": False, "type": "terminal",
     "edit": False, "send_btn": None,     "note": "命令提示符"},
    {"name": "PowerShell",    "keyword": ["Windows PowerShell", "PowerShell"], "exact": False, "type": "terminal",
     "edit": False, "send_btn": None,     "note": "Windows PowerShell"},
    {"name": "WindowsTerminal", "keyword": ["Windows Terminal", "WT"], "exact": False, "type": "terminal",
     "edit": False, "send_btn": None,     "note": "Windows 终端"},
]

_used_hwnds: set = set()


def set_clipboard(text: str):
    win32clipboard.OpenClipboard()
    win32clipboard.EmptyClipboard()
    win32clipboard.SetClipboardData(win32clipboard.CF_UNICODETEXT, text)
    win32clipboard.CloseClipboard()


def activate_window(hwnd: int) -> bool:
    try:
        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
        time.sleep(0.2)
    except Exception:
        pass

    for _ in range(3):
        try:
            win32gui.SetForegroundWindow(hwnd)
            time.sleep(0.5)
            return True
        except Exception:
            time.sleep(0.3)

    try:
        keyboard.press_and_release("alt")
        time.sleep(0.05)
        win32gui.SetForegroundWindow(hwnd)
        time.sleep(0.5)
        return True
    except Exception:
        return False


def find_hwnd(keywords, exact=False):
    if isinstance(keywords, str):
        keywords = [keywords]
    result = []

    def enum_cb(hwnd, _):
        if win32gui.IsWindowVisible(hwnd) and hwnd not in _used_hwnds:
            title = win32gui.GetWindowText(hwnd)
            if not title:
                return
            for kw in keywords:
                match = (title.strip() == kw) if exact else (kw.lower() in title.lower())
                if match:
                    result.append((hwnd, title))
                    return

    win32gui.EnumWindows(enum_cb, None)
    if result:
        _used_hwnds.add(result[0][0])
    return result[0] if result else (None, None)


def send_keyboard(message: str):
    set_clipboard(message)
    time.sleep(0.1)
    keyboard.press_and_release("ctrl+v")
    time.sleep(0.5)
    keyboard.press_and_release("enter")
    time.sleep(0.3)


def _uia_send_impl(hwnd, message, send_btn):
    from pywinauto import Application
    app = Application(backend="uia").connect(handle=hwnd, timeout=3)
    dlg = app.top_window()

    edit_ctrl = dlg.child_window(control_type="Edit")
    if not edit_ctrl.exists(timeout=2):
        raise Exception("Edit 控件不存在")

    try:
        edit_ctrl.click_input()
        time.sleep(0.3)
    except Exception:
        edit_ctrl.set_focus()
        time.sleep(0.2)

    set_clipboard(message)
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
                return "UIA + 点击发送"
        except Exception:
            pass

    keyboard.press_and_release("enter")
    time.sleep(0.3)
    return "UIA + Enter"


def send_with_uia(hwnd: int, message: str, send_btn: str = None, timeout: int = 15) -> str:
    result = {"success": False, "detail": ""}

    def worker():
        try:
            result["detail"] = _uia_send_impl(hwnd, message, send_btn)
            result["success"] = True
        except Exception as e:
            result["detail"] = f"UIA失败: {str(e)}"

    thread = threading.Thread(target=worker)
    thread.daemon = True
    thread.start()
    thread.join(timeout=timeout)

    if thread.is_alive():
        return "UIA超时，切换为keyboard"

    if result["success"]:
        return result["detail"]

    send_keyboard(message)
    return f"{result['detail']} → fallback→keyboard"


def send_to_window(entry: dict, message: str, strategy: str = "keyboard",
                   do_scan: bool = False, dry_run: bool = False) -> tuple:
    hwnd, title = find_hwnd(entry["keyword"], entry["exact"])
    if not hwnd:
        return False, "未找到窗口"

    if dry_run:
        return True, f"[预演] 找到窗口: {title}"

    if not activate_window(hwnd):
        return False, "窗口激活失败"

    if do_scan:
        result = {"success": False, "detail": ""}

        def scan_worker():
            try:
                from pywinauto import Application
                app = Application(backend="uia").connect(handle=hwnd, timeout=5)
                dlg = app.top_window()
                print(f"    [控件树开始]")
                dlg.print_control_identifiers()
                print(f"    [控件树结束]")
                result["success"] = True
                result["detail"] = "已扫描"
            except Exception as e:
                result["detail"] = f"UIA连接失败: {e}"

        thread = threading.Thread(target=scan_worker)
        thread.daemon = True
        thread.start()
        thread.join(timeout=30)

        if thread.is_alive():
            return True, "扫描超时"
        return result["success"], result["detail"]

    if strategy == "uia" and entry["edit"]:
        detail = send_with_uia(hwnd, message, entry["send_btn"])
    else:
        send_keyboard(message)
        detail = "keyboard"

    return True, detail


def cmd_list(registry):
    print(f"\n{'序号':>4}  {'名称':18s}  {'类型':10s}  {'说明':20s}  {'状态'}")
    print("-" * 80)
    global _used_hwnds
    _used_hwnds = set()
    for i, e in enumerate(registry, 1):
        hwnd, title = find_hwnd(e["keyword"], e["exact"])
        status = f"运行中 ({title})" if hwnd else "未运行"
        print(f"  {i:>2}  {e['name']:18s}  {e['type']:10s}  {e['note']:20s}  [{status}]")


def cmd_send(message: str, registry, target: str = None, strategy: str = "keyboard",
             do_scan: bool = False, dry_run: bool = False, retry: int = 0,
             output_json: bool = False, log_file: str = None):
    global _used_hwnds
    _used_hwnds = set()

    targets = registry
    if target:
        targets = [e for e in registry if target.lower() in e["name"].lower()]
        if not targets:
            if output_json:
                print(json.dumps({"success": False, "error": f"未找到匹配 '{target}' 的程序"}))
            else:
                print(f"[ERROR] 未找到匹配 '{target}' 的程序")
            return

    action = "扫描" if do_scan else ("预演" if dry_run else "发送")
    results = []
    log_lines = []

    if not output_json:
        print(f"\n{'=' * 70}")
        print(f"  龙虾群控 — {action}:「{message}」")
        print(f"  策略: {strategy} | 目标: {len(targets)} 个程序")
        print(f"{'=' * 70}")

    for entry in targets:
        if not output_json:
            print(f"\n  [{entry['name']}]")

        success = False
        detail = ""
        for attempt in range(retry + 1):
            s, d = send_to_window(entry, message, strategy, do_scan, dry_run)
            if s:
                success = s
                detail = d
                break
            if attempt < retry:
                if not output_json:
                    print(f"    重试 {attempt + 1}/{retry}...")
                time.sleep(1)
                detail = d

        results.append({
            "name": entry["name"],
            "success": success,
            "detail": detail,
            "type": entry["type"],
        })

        if not output_json:
            icon = "✅" if success else "❌"
            print(f"    {icon} {detail}")

        if not do_scan:
            time.sleep(0.8)

    ok_count = sum(1 for r in results if r["success"])

    if log_file:
        log_entry = {
            "timestamp": datetime.datetime.now().isoformat(),
            "action": action,
            "message": message,
            "strategy": strategy,
            "results": results,
        }
        try:
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
        except Exception as e:
            if not output_json:
                print(f"\n[WARN] 日志写入失败: {e}")

    if output_json:
        print(json.dumps({
            "success": ok_count == len(results),
            "total": len(results),
            "success_count": ok_count,
            "results": results,
        }, ensure_ascii=False, indent=2))
    else:
        print(f"\n{'=' * 70}")
        print(f"  {action}完成: {ok_count}/{len(results)} 成功")
        for r in results:
            icon = "✅" if r["success"] else "❌"
            print(f"    {icon} {r['name']:18s} {r['detail']}")


def load_config(config_path: str):
    if not config_path:
        return DEFAULT_CONFIG
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
        return config
    except Exception as e:
        print(f"[WARN] 加载配置文件失败: {e}，使用默认配置")
        return DEFAULT_CONFIG


def main():
    parser = argparse.ArgumentParser(
        description="龙虾群控 — 桌面 AI 程序批量自动化工具（v2.0）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python lobster_send.py "你好"                           # 发送到所有运行中的龙虾程序
  python lobster_send.py "讲一个笑话" --list              # 列出所有龙虾程序及状态
  python lobster_send.py "你好" --dry-run                 # 预演模式，不实际发送
  python lobster_send.py "你好" --target Kimi             # 只发送到 Kimi
  python lobster_send.py "你好" --strategy uia            # 使用 UIA 方式发送
  python lobster_send.py --scan --target WorkBuddy        # 扫描控件树(调试)
  python lobster_send.py "你好" --retry 2                 # 失败时重试2次
  python lobster_send.py "你好" --config config.json      # 使用外部配置文件
  python lobster_send.py "你好" --json                    # JSON格式输出
  python lobster_send.py "你好" --log lobster.log         # 记录日志到文件
        """,
    )
    parser.add_argument("message", nargs="?", default="你好", help="要发送的消息 (默认: 你好)")
    parser.add_argument("--list", action="store_true", help="列出所有龙虾程序及状态")
    parser.add_argument("--scan", action="store_true", help="扫描控件树(调试模式,不发送)")
    parser.add_argument("--target", type=str, help="只发送到指定程序 (名称关键词)")
    parser.add_argument("--strategy", type=str, default="keyboard",
                        choices=["keyboard", "uia"], help="发送策略")
    parser.add_argument("--dry-run", action="store_true", help="预演模式，不实际发送")
    parser.add_argument("--retry", type=int, default=0, help="失败时重试次数")
    parser.add_argument("--config", type=str, help="外部 JSON 配置文件路径")
    parser.add_argument("--json", action="store_true", help="JSON格式输出")
    parser.add_argument("--log", type=str, help="日志文件路径")

    args = parser.parse_args()

    registry = load_config(args.config)

    if args.list:
        cmd_list(registry)
    else:
        cmd_send(
            args.message,
            registry,
            target=args.target,
            strategy=args.strategy,
            do_scan=args.scan,
            dry_run=args.dry_run,
            retry=args.retry,
            output_json=args.json,
            log_file=args.log,
        )


if __name__ == "__main__":
    main()

# -*- coding: utf-8 -*-
"""
龙虾群控 — 类型处理器包

按程序类型（electron/webview/browser/terminal）分发发送逻辑。
新增类型时，只需在此目录添加新文件并在 HANDLERS 中注册。
"""
from . import electron, webview, browser, terminal

HANDLERS = {
    "electron": electron.send,
    "webview":  webview.send,
    "browser":  browser.send,
    "terminal": terminal.send,
}

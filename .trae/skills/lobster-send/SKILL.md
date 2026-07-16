---
name: "lobster-send"
description: "龙虾群控桌面自动化工具 — 批量向多个 AI 编程助手程序（WorkBuddy、Kimi、Trae、Codex 等）发送消息。当用户要求向多个龙虾类程序发送消息、批量控制桌面 AI 软件、或测试龙虾程序自动化时调用此 Skill。"
---

# 龙虾群控 — 桌面 AI 程序批量自动化（v2.0）

## 概述

基于 Windows UI Automation + keyboard 模拟方案，实现对桌面上所有龙虾类 AI 编程助手程序的批量自动化控制。支持多种发送策略、配置方式和输出格式。

## 依赖安装

```bash
pip install pywinauto pywin32 keyboard
```

## 主程序

主程序位于项目根目录: `lobster_send.py`

### 基本用法

```bash
# 发送消息到所有运行中的龙虾程序
python lobster_send.py "你好"

# 列出所有龙虾程序及其运行状态
python lobster_send.py --list

# 扫描控件树（调试模式，不发送）
python lobster_send.py --scan --target WorkBuddy

# 只发送到指定程序
python lobster_send.py "你好" --target Kimi
python lobster_send.py "讲一个笑话" --target Trae
```

### 高级用法

```bash
# 预演模式，不实际发送
python lobster_send.py "你好" --dry-run

# 使用 UIA 方式发送（精确控件定位）
python lobster_send.py "你好" --strategy uia

# 失败时重试2次
python lobster_send.py "你好" --retry 2

# 使用外部配置文件
python lobster_send.py "你好" --config config.json

# JSON格式输出（便于程序调用）
python lobster_send.py "你好" --json

# 记录日志到文件
python lobster_send.py "你好" --log lobster.log
```

## 支持的程序列表

| 类型 | 程序 | 说明 |
|------|------|------|
| Electron | WorkBuddy | AI 编程助手 |
| Electron | Kimi | 月之暗面 AI 助手 |
| Electron | CodeBuddy CN | 腾讯代码助手 |
| Electron | ZCode | 字节跳动代码助手 |
| Electron | Qoder | Qoder 编程助手 |
| WebView | Trae / Trae CN | Trae 国际版/中国版 |
| WebView | Codex | OpenAI Codex |
| WebView | TRAE Work / TRAE Work CN | TRAE Work |
| 浏览器 | MIMO | 小米 MIMO |
| 浏览器 | OpenClaw | OpenClaw |
| 终端 | cmd.exe / PowerShell / WindowsTerminal | 命令行窗口 |

## 技术方案

### 发送策略

1. **keyboard（默认，最稳定）**: 剪贴板 Ctrl+V 粘贴 → Enter 发送
2. **UIA（可选）**: pywinauto 精确定位 Edit 控件 → 剪贴板粘贴 → 发送按钮/Enter

### 核心原理

- **keyboard 库**: 模拟全局键盘事件，适用于所有类型窗口
- **pywinauto (UIA 后端)**: 遍历 Windows UI Automation 控件树，定位 Edit/Button 控件
- **win32clipboard**: 剪贴板读写，实现文字粘贴
- **win32gui**: 窗口句柄查找、激活、前台切换
- **threading**: UIA 操作超时保护，避免程序卡死

### 关键发现

- `set_edit_text()` 和 `type_keys()` 对 Electron/WebView 应用**无效**
- 必须通过 **Ctrl+V 剪贴板粘贴**触发 Electron 的 paste 事件
- **keyboard 直接模拟**是最通用方案，适用于所有程序类型
- WebView 深层渲染的程序（Trae/Codex）UIA 无法识别 Edit，只能用 keyboard
- pywinauto 的 `connect()` 和 `click_input()` 在某些环境下会卡死，需要超时保护

## 文件结构

```
lobster_send.py            主程序（统一入口，v2.0）
龙虾群控.docx              原始技术文档
龙虾群控测试报告_v2.docx    测试报告
.trae/skills/lobster-send/  Skill 目录
```

## 扩展新程序

### 方式1：修改内置配置

在 `lobster_send.py` 的 `DEFAULT_CONFIG` 列表中添加新条目:

```python
{"name": "新程序名", "keyword": ["关键词1", "关键词2"], "exact": False, "type": "electron",
 "edit": False, "send_btn": None, "note": "说明"},
```

### 方式2：外部配置文件

创建 `config.json`:

```json
[
  {"name": "新程序名", "keyword": ["关键词"], "exact": false, "type": "electron",
   "edit": false, "send_btn": null, "note": "说明"}
]
```

使用: `python lobster_send.py "消息" --config config.json`

### 字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| `name` | str | 程序显示名称 |
| `keyword` | str/list | 窗口标题关键词（支持多个） |
| `exact` | bool | 是否精确匹配窗口标题 |
| `type` | str | electron / webview / browser / terminal |
| `edit` | bool | 是否尝试用 UIA 定位 Edit 控件 |
| `send_btn` | str/None | 发送按钮名称（None 表示用 Enter） |
| `note` | str | 程序说明 |

## v2.0 新增功能

- ✅ **超时保护**: UIA 操作使用 threading 超时机制，防止程序卡死
- ✅ **默认 keyboard**: 默认使用最稳定的 keyboard 方式发送
- ✅ **预演模式**: `--dry-run` 预览发送目标，不实际发送
- ✅ **重试机制**: `--retry N` 失败时自动重试 N 次
- ✅ **多关键词**: 支持为每个程序配置多个关键词
- ✅ **配置文件**: 支持外部 JSON 配置文件
- ✅ **JSON 输出**: `--json` 便于程序调用和集成
- ✅ **日志记录**: `--log` 记录发送结果到文件
- ✅ **激活重试**: 窗口激活失败时自动重试 3 次

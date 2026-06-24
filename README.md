# 虾群 (XiaQun) v0.1.0

一个使用Python程序、skill调用句柄批量控制多种AI龙虾软件、cmd的工具

## 功能特性

- 支持多个主流AI平台
- 批量提问功能
- 自动打开浏览器标签页
- 支持自定义AI页面
- 简单易用的GUI界面

## 支持的AI平台

| 网址 | 中文名称 |
|------|----------|
| kimi.moonshot.cn | Kimi |
| metaso.cn | 秘塔搜索 |
| wenxiaobai.com | 问小白 |
| deepseek.com | DeepSeek |
| yuanbao.tencent.com | 腾讯元宝 |
| zhida.zhihu.com | 知乎直答 |
| qwen.ai | Qwen |
| claude.ai | Claude |
| www.n.cn | 纳米AI搜索 |
| www.google.com | 谷歌 |
| gemini.google.com | 谷歌Gemini |
| x.com | X-Grok |
| chatgpt.com | ChatGPT |
| chatglm.cn | 智谱清言 |
| tongyi.aliyun.com | 通义千问 |
| www.doubao.com | 豆包 |
| yiyan.baidu.com | 文心一言 |
| chat.baidu.com | 百度搜索 |

## 代码逻辑文档

### 项目架构

```
xiaqun/
├── main.py                 # 主程序入口
├── src/
│   ├── __init__.py         # 包初始化
│   ├── browser_controller.py  # 浏览器控制模块
│   ├── ai_manager.py       # AI平台管理模块
│   └── gui.py              # GUI界面模块
├── requirements.txt        # Python依赖
├── LICENSE                 # MIT许可证
└── README.md              # 项目说明
```

### 核心模块说明

#### 1. BrowserController（浏览器控制器）
- **功能**: 管理浏览器标签页和自动化操作
- **支持浏览器**: Chrome、Firefox、Edge
- **主要方法**:
  - `start_browser()`: 启动浏览器
  - `open_url(url, new_tab)`: 打开URL
  - `get_tabs()`: 获取所有标签页
  - `switch_to_tab(handle)`: 切换标签页
  - `close_tab(handle)`: 关闭标签页
  - `close_browser()`: 关闭浏览器

#### 2. AIManager（AI管理器）
- **功能**: 管理AI平台和提问逻辑
- **平台配置**: 使用AIPlatform类存储平台信息
- **主要方法**:
  - `get_platforms()`: 获取所有AI平台
  - `get_platform_by_name(name)`: 根据名称获取平台
  - `submit_question(browser_controller, platform, question)`: 向指定平台提交问题
  - `submit_to_all_platforms(browser_controller, question)`: 向所有平台提交问题

#### 3. XiaQunGUI（GUI界面）
- **功能**: 提供用户交互界面
- **界面元素**:
  - 浏览器选择（Chrome/Firefox/Edge）
  - 控制按钮（启动浏览器/检查标签/关闭浏览器）
  - 提问输入区域
  - AI平台选择列表
  - 提交按钮（提交所有AI/提交当前AI）

### 工作流程

1. **初始化阶段**
   - 用户启动程序
   - GUI界面加载
   - AI管理器加载平台配置

2. **浏览器控制**
   - 用户选择浏览器类型
   - 点击"启动浏览器"按钮
   - 程序启动对应的浏览器驱动

3. **AI平台管理**
   - 用户在GUI中查看AI平台列表
   - 选择要提问的平台
   - 输入问题内容

4. **提问提交**
   - 程序打开选中的AI平台页面
   - 自动输入问题内容
   - 点击提交按钮
   - 支持批量提交到多个平台

5. **结果处理**
   - 程序显示提交状态
   - 用户可以在浏览器中查看回答

### 技术实现细节

#### 浏览器自动化
- 使用Selenium WebDriver进行浏览器控制
- 支持多种浏览器驱动（ChromeDriver、GeckoDriver、EdgeDriver）
- 使用WebDriver Manager自动管理驱动版本

#### AI平台交互
- 使用CSS选择器定位页面元素
- 支持自定义输入框和提交按钮选择器
- 自动等待页面加载完成

#### GUI设计
- 使用Tkinter构建图形界面
- 支持多线程操作，避免界面冻结
- 提供友好的用户交互体验

### 配置说明

#### AI平台配置
每个AI平台通过AIPlatform类配置：
```python
AIPlatform(
    name="平台名称",
    url="平台URL",
    input_selector="输入框CSS选择器",
    submit_selector="提交按钮CSS选择器"
)
```

#### 浏览器配置
支持三种浏览器类型：
- Chrome: 使用ChromeDriver
- Firefox: 使用GeckoDriver  
- Edge: 使用EdgeDriver

### 扩展指南

#### 添加新的AI平台
1. 在AIManager的`_load_default_platforms()`方法中添加新的AIPlatform配置
2. 配置平台的URL、输入框选择器和提交按钮选择器
3. 测试平台交互是否正常

#### 自定义功能
1. 修改GUI界面布局
2. 添加新的控制按钮
3. 扩展提问功能（如定时提问、模板提问等）

## 安装依赖

```bash
pip install -r requirements.txt
```

## 使用方法

1. 运行程序：
   ```bash
   python main.py
   ```

2. 打开浏览器，访问AI页面并登录账号

3. 点击"检查已打开标签"确认标签页正确

4. 输入提问内容，点击"提交所有AI"或"当前AI"

## 联系方式

- **作者微信**: 
  ![作者微信](images/author.jpg)
  
- **微信群**: 
  ![微信群](images/wechat-group.jpg)

## 开发计划

- [ ] 支持更多AI平台
- [ ] 添加批量处理功能
- [ ] 支持自定义提问模板
- [ ] 添加结果导出功能
- [ ] 支持多语言界面

## 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 版本历史

### v0.1.0 (2026-06-24)
- 初始版本发布
- 支持18个主流AI平台
- 实现浏览器控制功能
- 实现GUI用户界面
- 添加MIT开源许可证

## 致谢

感谢所有为这个项目做出贡献的开发者！

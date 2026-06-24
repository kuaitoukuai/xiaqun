# 虾群 (XiaQun)

一个使用Python程序、skill调用句柄批量控制多种AI龙虾软件、cmd的工具

## 功能特性

- 支持18个主流AI平台
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

## 项目结构

```
xiaqun/
├── README.md
├── LICENSE
├── requirements.txt
├── main.py
└── src/
    ├── __init__.py
    ├── browser_controller.py
    ├── ai_manager.py
    └── gui.py
```

## 开发计划

- [ ] 支持更多AI平台
- [ ] 添加批量处理功能
- [ ] 支持自定义提问模板
- [ ] 添加结果导出功能
- [ ] 支持多语言界面

## 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 联系方式

- GitHub: [kuaitoukuai](https://github.com/kuaitoukuai)
- QQ群: 1037524108

## 致谢

感谢所有为这个项目做出贡献的开发者！

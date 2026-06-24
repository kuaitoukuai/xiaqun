"""
AI管理器模块
负责管理AI平台和提问逻辑
"""

import time
import logging
from typing import List, Dict, Optional
from selenium.webdriver.common.by import By

logger = logging.getLogger(__name__)


class AIPlatform:
    """AI平台类"""
    
    def __init__(self, name: str, url: str, input_selector: str, submit_selector: str):
        """
        初始化AI平台
        
        Args:
            name: 平台名称
            url: 平台URL
            input_selector: 输入框选择器
            submit_selector: 提交按钮选择器
        """
        self.name = name
        self.url = url
        self.input_selector = input_selector
        self.submit_selector = submit_selector


class AIManager:
    """AI管理器类"""
    
    def __init__(self):
        """初始化AI管理器"""
        self.platforms = self._load_default_platforms()
        
    def _load_default_platforms(self) -> List[AIPlatform]:
        """
        加载默认AI平台配置
        
        Returns:
            List[AIPlatform]: AI平台列表
        """
        return [
            AIPlatform(
                name="Kimi",
                url="https://kimi.moonshot.cn",
                input_selector="textarea",
                submit_selector="button[type='submit']"
            ),
            AIPlatform(
                name="秘塔搜索",
                url="https://metaso.cn",
                input_selector="textarea",
                submit_selector="button[type='submit']"
            ),
            AIPlatform(
                name="问小白",
                url="https://wenxiaobai.com",
                input_selector="textarea",
                submit_selector="button[type='submit']"
            ),
            AIPlatform(
                name="DeepSeek",
                url="https://deepseek.com",
                input_selector="textarea",
                submit_selector="button[type='submit']"
            ),
            AIPlatform(
                name="腾讯元宝",
                url="https://yuanbao.tencent.com",
                input_selector="textarea",
                submit_selector="button[type='submit']"
            ),
            AIPlatform(
                name="知乎直答",
                url="https://zhida.zhihu.com",
                input_selector="textarea",
                submit_selector="button[type='submit']"
            ),
            AIPlatform(
                name="Qwen",
                url="https://qwen.ai",
                input_selector="textarea",
                submit_selector="button[type='submit']"
            ),
            AIPlatform(
                name="Claude",
                url="https://claude.ai",
                input_selector="textarea",
                submit_selector="button[type='submit']"
            ),
            AIPlatform(
                name="纳米AI搜索",
                url="https://www.n.cn",
                input_selector="textarea",
                submit_selector="button[type='submit']"
            ),
            AIPlatform(
                name="谷歌",
                url="https://www.google.com",
                input_selector="textarea[name='q']",
                submit_selector="input[type='submit']"
            ),
            AIPlatform(
                name="谷歌Gemini",
                url="https://gemini.google.com",
                input_selector="textarea",
                submit_selector="button[type='submit']"
            ),
            AIPlatform(
                name="X-Grok",
                url="https://x.com",
                input_selector="textarea",
                submit_selector="button[type='submit']"
            ),
            AIPlatform(
                name="ChatGPT",
                url="https://chatgpt.com",
                input_selector="textarea",
                submit_selector="button[type='submit']"
            ),
            AIPlatform(
                name="智谱清言",
                url="https://chatglm.cn",
                input_selector="textarea",
                submit_selector="button[type='submit']"
            ),
            AIPlatform(
                name="通义千问",
                url="https://tongyi.aliyun.com",
                input_selector="textarea",
                submit_selector="button[type='submit']"
            ),
            AIPlatform(
                name="豆包",
                url="https://www.doubao.com",
                input_selector="textarea",
                submit_selector="button[type='submit']"
            ),
            AIPlatform(
                name="文心一言",
                url="https://yiyan.baidu.com",
                input_selector="textarea",
                submit_selector="button[type='submit']"
            ),
            AIPlatform(
                name="百度搜索",
                url="https://chat.baidu.com",
                input_selector="textarea",
                submit_selector="button[type='submit']"
            )
        ]
    
    def get_platforms(self) -> List[AIPlatform]:
        """
        获取所有AI平台
        
        Returns:
            List[AIPlatform]: AI平台列表
        """
        return self.platforms
    
    def get_platform_by_name(self, name: str) -> Optional[AIPlatform]:
        """
        根据名称获取AI平台
        
        Args:
            name: 平台名称
            
        Returns:
            Optional[AIPlatform]: AI平台对象
        """
        for platform in self.platforms:
            if platform.name == name:
                return platform
        return None
    
    def submit_question(self, browser_controller, platform: AIPlatform, question: str) -> bool:
        """
        向指定AI平台提交问题
        
        Args:
            browser_controller: 浏览器控制器
            platform: AI平台
            question: 问题内容
            
        Returns:
            bool: 是否成功提交
        """
        try:
            # 打开平台URL
            if not browser_controller.open_url(platform.url):
                return False
            
            # 等待页面加载
            time.sleep(3)
            
            # 输入问题
            if not browser_controller.input_text(By.CSS_SELECTOR, platform.input_selector, question):
                return False
            
            # 点击提交按钮
            if not browser_controller.click_element(By.CSS_SELECTOR, platform.submit_selector):
                return False
            
            logger.info(f"成功向 {platform.name} 提交问题")
            return True
            
        except Exception as e:
            logger.error(f"向 {platform.name} 提交问题失败: {e}")
            return False
    
    def submit_to_all_platforms(self, browser_controller, question: str) -> Dict[str, bool]:
        """
        向所有AI平台提交问题
        
        Args:
            browser_controller: 浏览器控制器
            question: 问题内容
            
        Returns:
            Dict[str, bool]: 各平台提交结果
        """
        results = {}
        for platform in self.platforms:
            results[platform.name] = self.submit_question(browser_controller, platform, question)
        return results

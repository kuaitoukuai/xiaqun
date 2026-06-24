"""
浏览器控制器模块
负责管理浏览器标签页和自动化操作
"""

import time
import logging
from typing import List, Dict, Optional
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager

logger = logging.getLogger(__name__)


class BrowserController:
    """浏览器控制器类"""
    
    def __init__(self, browser_type: str = "chrome"):
        """
        初始化浏览器控制器
        
        Args:
            browser_type: 浏览器类型 (chrome, firefox, edge)
        """
        self.browser_type = browser_type.lower()
        self.driver = None
        self.tabs = {}
        
    def start_browser(self) -> bool:
        """
        启动浏览器
        
        Returns:
            bool: 是否成功启动
        """
        try:
            if self.browser_type == "chrome":
                service = ChromeService(ChromeDriverManager().install())
                self.driver = webdriver.Chrome(service=service)
            elif self.browser_type == "firefox":
                service = FirefoxService(GeckoDriverManager().install())
                self.driver = webdriver.Firefox(service=service)
            elif self.browser_type == "edge":
                service = EdgeService(EdgeChromiumDriverManager().install())
                self.driver = webdriver.Edge(service=service)
            else:
                logger.error(f"不支持的浏览器类型: {self.browser_type}")
                return False
                
            logger.info(f"成功启动 {self.browser_type} 浏览器")
            return True
            
        except Exception as e:
            logger.error(f"启动浏览器失败: {e}")
            return False
    
    def open_url(self, url: str, new_tab: bool = True) -> bool:
        """
        打开URL
        
        Args:
            url: 要打开的URL
            new_tab: 是否在新标签页中打开
            
        Returns:
            bool: 是否成功打开
        """
        try:
            if new_tab:
                self.driver.execute_script(f"window.open('{url}', '_blank');")
            else:
                self.driver.get(url)
                
            time.sleep(2)  # 等待页面加载
            logger.info(f"成功打开URL: {url}")
            return True
            
        except Exception as e:
            logger.error(f"打开URL失败: {e}")
            return False
    
    def get_tabs(self) -> List[Dict]:
        """
        获取所有标签页信息
        
        Returns:
            List[Dict]: 标签页信息列表
        """
        try:
            tabs = []
            for handle in self.driver.window_handles:
                self.driver.switch_to.window(handle)
                title = self.driver.title
                url = self.driver.current_url
                tabs.append({
                    'handle': handle,
                    'title': title,
                    'url': url
                })
            return tabs
            
        except Exception as e:
            logger.error(f"获取标签页失败: {e}")
            return []
    
    def switch_to_tab(self, handle: str) -> bool:
        """
        切换到指定标签页
        
        Args:
            handle: 标签页句柄
            
        Returns:
            bool: 是否成功切换
        """
        try:
            self.driver.switch_to.window(handle)
            logger.info(f"成功切换到标签页: {handle}")
            return True
            
        except Exception as e:
            logger.error(f"切换标签页失败: {e}")
            return False
    
    def close_tab(self, handle: str) -> bool:
        """
        关闭指定标签页
        
        Args:
            handle: 标签页句柄
            
        Returns:
            bool: 是否成功关闭
        """
        try:
            self.driver.switch_to.window(handle)
            self.driver.close()
            logger.info(f"成功关闭标签页: {handle}")
            return True
            
        except Exception as e:
            logger.error(f"关闭标签页失败: {e}")
            return False
    
    def close_browser(self) -> bool:
        """
        关闭浏览器
        
        Returns:
            bool: 是否成功关闭
        """
        try:
            if self.driver:
                self.driver.quit()
                logger.info("成功关闭浏览器")
            return True
            
        except Exception as e:
            logger.error(f"关闭浏览器失败: {e}")
            return False
    
    def wait_for_element(self, by: By, value: str, timeout: int = 10) -> Optional[object]:
        """
        等待元素出现
        
        Args:
            by: 定位方式
            value: 定位值
            timeout: 超时时间
            
        Returns:
            Optional[object]: 元素对象
        """
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, value))
            )
            return element
            
        except Exception as e:
            logger.error(f"等待元素超时: {e}")
            return None
    
    def input_text(self, by: By, value: str, text: str) -> bool:
        """
        输入文本
        
        Args:
            by: 定位方式
            value: 定位值
            text: 要输入的文本
            
        Returns:
            bool: 是否成功输入
        """
        try:
            element = self.wait_for_element(by, value)
            if element:
                element.clear()
                element.send_keys(text)
                logger.info(f"成功输入文本: {text}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"输入文本失败: {e}")
            return False
    
    def click_element(self, by: By, value: str) -> bool:
        """
        点击元素
        
        Args:
            by: 定位方式
            value: 定位值
            
        Returns:
            bool: 是否成功点击
        """
        try:
            element = self.wait_for_element(by, value)
            if element:
                element.click()
                logger.info(f"成功点击元素: {value}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"点击元素失败: {e}")
            return False

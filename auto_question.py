#!/usr/bin/env python3
"""
虾群自动化提问脚本
自动向所有AI平台提问指定问题
"""

import sys
import os
import time
import logging
from pathlib import Path

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.browser_controller import BrowserController
from src.ai_manager import AIManager

def setup_logging():
    """设置日志配置"""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler("auto_question.log", encoding="utf-8")
        ]
    )

def main():
    """主函数"""
    setup_logging()
    logger = logging.getLogger(__name__)
    
    logger.info("启动虾群自动化提问脚本")
    
    # 获取问题内容
    if len(sys.argv) > 1:
        question = " ".join(sys.argv[1:])
    else:
        question = "现在时间多少？"
    
    logger.info(f"问题内容: {question}")
    
    # 创建浏览器控制器和AI管理器
    browser_controller = BrowserController("chrome")
    ai_manager = AIManager()
    
    try:
        # 启动浏览器
        logger.info("启动浏览器...")
        if not browser_controller.start_browser():
            logger.error("启动浏览器失败")
            return
        
        logger.info("浏览器启动成功")
        
        # 向所有AI平台提问
        logger.info("开始向所有AI平台提问...")
        results = ai_manager.submit_to_all_platforms(browser_controller, question)
        
        # 统计结果
        success_count = sum(1 for success in results.values() if success)
        total_count = len(results)
        
        logger.info(f"提问完成！成功 {success_count}/{total_count} 个平台")
        
        # 显示详细结果
        for platform, success in results.items():
            status = "成功" if success else "失败"
            logger.info(f"  {platform}: {status}")
        
        # 等待用户查看结果
        logger.info("请在浏览器中查看各平台的回答")
        logger.info("按Enter键关闭浏览器...")
        input()
        
    except KeyboardInterrupt:
        logger.info("程序被用户中断")
    except Exception as e:
        logger.error(f"程序运行出错: {e}")
        raise
    finally:
        # 关闭浏览器
        logger.info("关闭浏览器...")
        browser_controller.close_browser()
        logger.info("程序退出")

if __name__ == "__main__":
    main()

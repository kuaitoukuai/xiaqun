#!/usr/bin/env python3
"""
虾群 (XiaQun) - 批量AI提问工具
主程序入口
"""

import sys
import os
import logging
from pathlib import Path

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.gui import XiaQunGUI
from src.browser_controller import BrowserController
from src.ai_manager import AIManager


def setup_logging():
    """设置日志配置"""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler("xiaqun.log", encoding="utf-8")
        ]
    )


def main():
    """主函数"""
    setup_logging()
    logger = logging.getLogger(__name__)
    
    logger.info("启动虾群 - 批量AI提问工具")
    
    try:
        # 创建并运行GUI
        app = XiaQunGUI()
        app.run()
        
    except KeyboardInterrupt:
        logger.info("程序被用户中断")
    except Exception as e:
        logger.error(f"程序运行出错: {e}")
        raise
    finally:
        logger.info("程序退出")


if __name__ == "__main__":
    main()

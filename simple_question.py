#!/usr/bin/env python3
"""
虾群简化版提问脚本
直接向所有AI平台提问
"""

import sys
import os
import time
from pathlib import Path

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.browser_controller import BrowserController
from src.ai_manager import AIManager

def main():
    """主函数"""
    print("虾群 - 批量AI提问工具")
    print("=" * 50)
    
    # 获取问题内容
    if len(sys.argv) > 1:
        question = " ".join(sys.argv[1:])
    else:
        question = "现在时间多少？"
    
    print(f"问题内容: {question}")
    print("=" * 50)
    
    # 创建浏览器控制器和AI管理器
    browser_controller = BrowserController("chrome")
    ai_manager = AIManager()
    
    try:
        # 启动浏览器
        print("启动浏览器...")
        if not browser_controller.start_browser():
            print("❌ 启动浏览器失败")
            return
        
        print("✅ 浏览器启动成功")
        
        # 向所有AI平台提问
        print("开始向所有AI平台提问...")
        results = ai_manager.submit_to_all_platforms(browser_controller, question)
        
        # 统计结果
        success_count = sum(1 for success in results.values() if success)
        total_count = len(results)
        
        print(f"提问完成！成功 {success_count}/{total_count} 个平台")
        
        # 显示详细结果
        for platform, success in results.items():
            status = "✅ 成功" if success else "❌ 失败"
            print(f"  {platform}: {status}")
        
        print("=" * 50)
        print("请在浏览器中查看各平台的回答")
        print("按Enter键关闭浏览器...")
        input()
        
    except KeyboardInterrupt:
        print("\n程序被用户中断")
    except Exception as e:
        print(f"❌ 程序运行出错: {e}")
        raise
    finally:
        # 关闭浏览器
        print("关闭浏览器...")
        browser_controller.close_browser()
        print("程序退出")

if __name__ == "__main__":
    main()

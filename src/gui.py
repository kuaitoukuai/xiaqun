"""
GUI界面模块
提供用户交互界面
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
from typing import List, Dict
from .browser_controller import BrowserController
from .ai_manager import AIManager, AIPlatform


class XiaQunGUI:
    """虾群GUI界面类"""
    
    def __init__(self):
        """初始化GUI界面"""
        self.root = tk.Tk()
        self.root.title("虾群 - 批量AI提问工具")
        self.root.geometry("800x600")
        
        self.browser_controller = None
        self.ai_manager = AIManager()
        
        self._setup_ui()
        
    def _setup_ui(self):
        """设置UI界面"""
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 标题
        title_label = ttk.Label(main_frame, text="虾群 - 批量AI提问工具", font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # 浏览器选择
        browser_frame = ttk.LabelFrame(main_frame, text="浏览器选择", padding="10")
        browser_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.browser_var = tk.StringVar(value="chrome")
        ttk.Radiobutton(browser_frame, text="Chrome", variable=self.browser_var, value="chrome").grid(row=0, column=0, padx=5)
        ttk.Radiobutton(browser_frame, text="Firefox", variable=self.browser_var, value="firefox").grid(row=0, column=1, padx=5)
        ttk.Radiobutton(browser_frame, text="Edge", variable=self.browser_var, value="edge").grid(row=0, column=2, padx=5)
        
        # 控制按钮
        control_frame = ttk.Frame(main_frame)
        control_frame.grid(row=2, column=0, columnspan=3, pady=(0, 10))
        
        ttk.Button(control_frame, text="启动浏览器", command=self._start_browser).grid(row=0, column=0, padx=5)
        ttk.Button(control_frame, text="检查已打开标签", command=self._check_tabs).grid(row=0, column=1, padx=5)
        ttk.Button(control_frame, text="关闭浏览器", command=self._close_browser).grid(row=0, column=2, padx=5)
        
        # 提问区域
        question_frame = ttk.LabelFrame(main_frame, text="提问内容", padding="10")
        question_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.question_text = scrolledtext.ScrolledText(question_frame, height=5, width=70)
        self.question_text.grid(row=0, column=0, columnspan=3)
        
        # 提交按钮
        submit_frame = ttk.Frame(main_frame)
        submit_frame.grid(row=4, column=0, columnspan=3, pady=(0, 10))
        
        ttk.Button(submit_frame, text="提交所有AI", command=self._submit_all).grid(row=0, column=0, padx=5)
        ttk.Button(submit_frame, text="提交当前AI", command=self._submit_current).grid(row=0, column=1, padx=5)
        
        # AI平台选择
        platform_frame = ttk.LabelFrame(main_frame, text="AI平台选择", padding="10")
        platform_frame.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.platform_listbox = tk.Listbox(platform_frame, height=6, selectmode=tk.MULTIPLE)
        self.platform_listbox.grid(row=0, column=0, columnspan=3, sticky=(tk.W, tk.E))
        
        # 加载AI平台
        self._load_platforms()
        
        # 状态栏
        self.status_var = tk.StringVar(value="就绪")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E))
        
        # 配置网格权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        
    def _load_platforms(self):
        """加载AI平台列表"""
        platforms = self.ai_manager.get_platforms()
        for platform in platforms:
            self.platform_listbox.insert(tk.END, platform.name)
    
    def _start_browser(self):
        """启动浏览器"""
        browser_type = self.browser_var.get()
        self.browser_controller = BrowserController(browser_type)
        
        if self.browser_controller.start_browser():
            self.status_var.set(f"已启动 {browser_type} 浏览器")
            messagebox.showinfo("成功", f"已启动 {browser_type} 浏览器")
        else:
            messagebox.showerror("错误", f"启动 {browser_type} 浏览器失败")
    
    def _check_tabs(self):
        """检查已打开的标签页"""
        if not self.browser_controller:
            messagebox.showerror("错误", "请先启动浏览器")
            return
        
        tabs = self.browser_controller.get_tabs()
        if tabs:
            tab_info = "\n".join([f"{tab['title']} - {tab['url']}" for tab in tabs])
            messagebox.showinfo("已打开的标签页", f"共有 {len(tabs)} 个标签页:\n\n{tab_info}")
        else:
            messagebox.showinfo("提示", "没有已打开的标签页")
    
    def _close_browser(self):
        """关闭浏览器"""
        if self.browser_controller:
            self.browser_controller.close_browser()
            self.browser_controller = None
            self.status_var.set("浏览器已关闭")
            messagebox.showinfo("成功", "浏览器已关闭")
        else:
            messagebox.showinfo("提示", "没有正在运行的浏览器")
    
    def _submit_all(self):
        """提交问题到所有AI平台"""
        if not self.browser_controller:
            messagebox.showerror("错误", "请先启动浏览器")
            return
        
        question = self.question_text.get("1.0", tk.END).strip()
        if not question:
            messagebox.showerror("错误", "请输入问题内容")
            return
        
        # 在新线程中执行提交
        threading.Thread(target=self._submit_all_thread, args=(question,), daemon=True).start()
    
    def _submit_all_thread(self, question: str):
        """在新线程中提交问题到所有AI平台"""
        self.status_var.set("正在提交问题到所有AI平台...")
        results = self.ai_manager.submit_to_all_platforms(self.browser_controller, question)
        
        success_count = sum(1 for success in results.values() if success)
        total_count = len(results)
        
        self.root.after(0, lambda: messagebox.showinfo("完成", f"提交完成！成功 {success_count}/{total_count} 个平台"))
        self.root.after(0, lambda: self.status_var.set(f"提交完成！成功 {success_count}/{total_count} 个平台"))
    
    def _submit_current(self):
        """提交问题到选中的AI平台"""
        if not self.browser_controller:
            messagebox.showerror("错误", "请先启动浏览器")
            return
        
        question = self.question_text.get("1.0", tk.END).strip()
        if not question:
            messagebox.showerror("错误", "请输入问题内容")
            return
        
        selected_indices = self.platform_listbox.curselection()
        if not selected_indices:
            messagebox.showerror("错误", "请选择至少一个AI平台")
            return
        
        selected_platforms = []
        for index in selected_indices:
            platform_name = self.platform_listbox.get(index)
            platform = self.ai_manager.get_platform_by_name(platform_name)
            if platform:
                selected_platforms.append(platform)
        
        # 在新线程中执行提交
        threading.Thread(target=self._submit_current_thread, args=(question, selected_platforms), daemon=True).start()
    
    def _submit_current_thread(self, question: str, platforms: List[AIPlatform]):
        """在新线程中提交问题到选中的AI平台"""
        self.status_var.set("正在提交问题到选中的AI平台...")
        results = {}
        
        for platform in platforms:
            results[platform.name] = self.ai_manager.submit_question(self.browser_controller, platform, question)
        
        success_count = sum(1 for success in results.values() if success)
        total_count = len(results)
        
        self.root.after(0, lambda: messagebox.showinfo("完成", f"提交完成！成功 {success_count}/{total_count} 个平台"))
        self.root.after(0, lambda: self.status_var.set(f"提交完成！成功 {success_count}/{total_count} 个平台"))
    
    def run(self):
        """运行GUI界面"""
        self.root.mainloop()

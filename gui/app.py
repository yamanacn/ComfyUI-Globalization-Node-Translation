#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
GUI 应用程序模块
处理用户界面和拖拽功能
"""

import os
import tkinter as tk
from tkinter import ttk, messagebox
import logging
from core.file_handler import FileHandler
from core.node_parser import NodeParser
from core.config_manager import ConfigManager
import json
from translation_service.translation_service import TranslationService
import asyncio
import threading
import nest_asyncio
import shutil

# 初始化 nest_asyncio 以支持嵌套事件循环
nest_asyncio.apply()

class App:
    """GUI 应用程序类"""
    
    def __init__(self, master):
        """初始化应用"""
        self.master = master
        self.folders = []  # 存储选择的文件夹路径
        self.is_stopped = False  # 翻译停止标志
        self.loop = asyncio.new_event_loop()  # 创建事件循环
        self.translation_mode = tk.StringVar(value='chinese_only')  # 默认选择中文翻译
        
        # 初始化配置管理器
        self.config_manager = ConfigManager()
        
        # 设置窗口样式
        self.setup_styles()
        
        # 创建主框架
        main_frame = ttk.Frame(master, padding="10")
        main_frame.grid(row=0, column=0, sticky='nsew')
        main_frame.grid_columnconfigure(0, weight=1)
        
        # 设置各个区域
        self.setup_api_section(main_frame)  # API设置区域
        self.setup_folder_section(main_frame)  # 文件夹选择区域
        self.setup_action_section(main_frame)  # 操作区域
        self.setup_log_section(main_frame)  # 日志区域
        self.setup_translation_mode_section(main_frame)  # 新增翻译模式设置
        
        # 加载配置
        self.load_config()
        
    def setup_window(self):
        """设置主窗口"""
        self.master.title("ComfyUI 节点翻译工具 - By OLDX")
        self.master.minsize(1000, 600)
        
        # 配置网格权重，使界面可以自适应调整
        self.master.grid_rowconfigure(0, weight=1)
        self.master.grid_columnconfigure(0, weight=1)
        
    def setup_styles(self):
        """设置控件样式"""
        style = ttk.Style()
        
        # 设置主题
        style.theme_use('clam')  # 使用 clam 主题作为基础
        
        # 设置标签框架样式
        style.configure('Custom.TLabelframe', padding=15)
        style.configure('Custom.TLabelframe.Label', font=('微软雅黑', 10, 'bold'))
        
        # 设置按钮样式
        style.configure('Custom.TButton',
                       padding=5,
                       font=('微软雅黑', 9))
        
        # 设置输入框样式
        style.configure('Custom.TEntry',
                       padding=5)
                       
        # 设置主要按钮样式
        style.configure('Primary.TButton',
                       padding=5,
                       font=('微软雅黑', 9, 'bold'))
        
    def setup_api_section(self, parent):
        """设置 API 区域"""
        api_frame = ttk.LabelFrame(
            parent,
            text="API 设置",
            style='Custom.TLabelframe'
        )
        api_frame.grid(row=0, column=0, sticky='ew', pady=(0, 15))
        api_frame.grid_columnconfigure(1, weight=1)
        api_frame.grid_columnconfigure(3, weight=1)
        
        # API Key 输入框
        ttk.Label(api_frame, text="API Key:").grid(row=0, column=0, padx=(0, 5), sticky='w')
        self.api_key_entry = ttk.Entry(api_frame, style='Custom.TEntry')
        self.api_key_entry.grid(row=0, column=1, sticky='ew', padx=5)
        
        # Model ID 输入框
        ttk.Label(api_frame, text="Model ID:").grid(row=0, column=2, padx=(15, 5), sticky='w')
        self.model_id_entry = ttk.Entry(api_frame, style='Custom.TEntry')
        self.model_id_entry.grid(row=0, column=3, sticky='ew', padx=5)
        
        # API 操作按钮
        btn_frame = ttk.Frame(api_frame)
        btn_frame.grid(row=0, column=4, padx=(15, 0))
        
        ttk.Button(
            btn_frame,
            text="保存配置",
            command=self.save_config,
            style='Custom.TButton'
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            btn_frame,
            text="测试 API",
            command=self.test_api,
            style='Custom.TButton'
        ).pack(side=tk.LEFT, padx=5)
        
    def setup_folder_section(self, parent):
        """设置文件处理区域"""
        file_frame = ttk.LabelFrame(
            parent,
            text="文件处理",
            style='Custom.TLabelframe'
        )
        file_frame.grid(row=1, column=0, sticky='nsew', pady=(0, 15))
        file_frame.grid_columnconfigure(0, weight=1)
        file_frame.grid_rowconfigure(1, weight=1)
        
        # 拖拽提示
        ttk.Label(
            file_frame,
            text="将文件夹拖拽到下方区域",
            font=('微软雅黑', 9)
        ).grid(row=0, column=0, pady=(0, 5))
        
        # 文件列表区域
        list_frame = ttk.Frame(file_frame)
        list_frame.grid(row=1, column=0, sticky='nsew')
        list_frame.grid_columnconfigure(0, weight=1)
        list_frame.grid_rowconfigure(0, weight=1)
        
        self.folder_listbox = tk.Listbox(
            list_frame,
            height=6,
            font=('微软雅黑', 9)
        )
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.folder_listbox.yview)
        self.folder_listbox.configure(yscrollcommand=scrollbar.set)
        
        self.folder_listbox.grid(row=0, column=0, sticky='nsew')
        scrollbar.grid(row=0, column=1, sticky='ns')
        
        # 绑定拖拽事件
        self.folder_listbox.drop_target_register('DND_Files')
        self.folder_listbox.dnd_bind('<<Drop>>', self.on_drop)
        
    def setup_log_section(self, parent):
        """设置日志区域"""
        log_frame = ttk.LabelFrame(
            parent,
            text="处理日志",
            style='Custom.TLabelframe'
        )
        log_frame.grid(row=2, column=0, sticky='nsew', pady=(0, 15))
        log_frame.grid_columnconfigure(0, weight=1)
        log_frame.grid_rowconfigure(0, weight=1)
        
        # 日志文本框
        self.log_text = tk.Text(
            log_frame,
            height=8,
            font=('微软雅黑', 9),
            wrap=tk.WORD
        )
        scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        
        self.log_text.grid(row=0, column=0, sticky='nsew', padx=(0, 2))
        scrollbar.grid(row=0, column=1, sticky='ns')
        
    def setup_action_section(self, parent):
        """设置操作区域"""
        action_frame = ttk.Frame(parent)
        action_frame.grid(row=3, column=0, sticky='ew')
        action_frame.grid_columnconfigure(1, weight=1)
        
        # 操作按钮
        btn_frame = ttk.Frame(action_frame)
        btn_frame.grid(row=0, column=1, sticky='e')
        
        ttk.Button(
            btn_frame,
            text="开始解析",
            command=self.start_parse,
            style='Primary.TButton'
        ).pack(side=tk.LEFT, padx=5)
        
        self.translate_btn = ttk.Button(
            btn_frame,
            text="开始翻译",
            command=self.start_translation,
            style='Primary.TButton'
        )
        self.translate_btn.pack(side=tk.LEFT, padx=5)
        
        self.stop_btn = ttk.Button(
            btn_frame,
            text="终止翻译",
            command=self.stop_translation,
            state='disabled',
            style='Custom.TButton'
        )
        self.stop_btn.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            btn_frame,
            text="打开检测结果",
            command=self.open_results_folder,
            style='Custom.TButton'
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            btn_frame,
            text="清空文件夹",
            command=self.clear_folders,
            style='Custom.TButton'
        ).pack(side=tk.LEFT, padx=5)

    def on_drop(self, event):
        """处理文件夹拖拽事件"""
        file_paths = self.master.tk.splitlist(event.data)
        for path in file_paths:
            if os.path.isdir(path) and path not in self.folders:
                self.folders.append(path)
                self.folder_listbox.insert(tk.END, path)
                self.log_message(f"已添加文件夹: {path}")
                
    def clear_folders(self):
        """清空已添加的文件夹"""
        if not self.folders:
            messagebox.showinfo("提示", "没有需要清空的文件夹！")
            return
            
        if messagebox.askyesno("确认", "确定要清空所有已添加的文件夹吗？"):
            self.folders.clear()
            self.folder_listbox.delete(0, tk.END)
            self.log_message("已清空所有文件夹")
                
    def start_parse(self):
        """开始解析节点"""
        if self.translation_mode.get() == 'global_translation':
            self._parse_global_translation()
        else:
            self._parse_chinese_only()

    def run_translation(self):
        """在新线程中运行翻译任务"""
        asyncio.run(self.start_translation())

    def open_results_folder(self):
        """打开检测结果文件夹"""
        if not self.folders:
            messagebox.showwarning("警告", "请先添加文件夹！")
            return
        
        # 假设结果文件夹在第一个文件夹下的 locales/zh 目录
        results_folder = os.path.join(self.folders[0], "locales", "zh")
        if os.path.exists(results_folder):
            os.startfile(results_folder)
        else:
            messagebox.showerror("错误", "未找到检测结果文件夹！")

    def start_translation(self):
        """开始翻译任务"""
        if not self.folders:
            messagebox.showwarning("警告", "请先添加文件夹！")
            return
        
        api_key = self.api_key_entry.get()
        model_id = self.model_id_entry.get()
        
        if not api_key or not model_id:
            messagebox.showwarning("警告", "请填写 API Key 和 Model ID！")
            return
        
        self.is_stopped = False
        self.translate_btn.configure(state='disabled')
        self.stop_btn.configure(state='normal')
        
        # 在新线程中运行翻译操作
        threading.Thread(target=self._run_translation_thread, daemon=True).start()

    def _run_translation_thread(self):
        """在新线程中运行翻译操作"""
        try:
            api_key = self.api_key_entry.get()
            model_id = self.model_id_entry.get()
            
            # 遍历所有文件夹
            for folder in self.folders:
                if self.is_stopped:
                    self.log_message("翻译任务已终止")
                    break
                
                self.log_message(f"\n开始处理文件夹: {folder}")
                
                # 获取中文版本的路径
                zh_path = os.path.join(folder, "locales", "zh", "nodeDefs.json")
                if not os.path.exists(zh_path):
                    self.log_message(f"错误：未找到文件: {zh_path}")
                    continue

                # 读取原始文件
                with open(zh_path, 'r', encoding='utf-8') as f:
                    json_data = json.load(f)

                if self.translation_mode.get() == 'global_translation':
                    # 全球化翻译模式
                    self.log_message("\n开始全球化翻译流程...")
                    
                    # 第1步：复制文件
                    shutil.copy(zh_path, os.path.join(folder, "locales", "zh", "ru_nodeDefs.json"))
                    if self.is_stopped:
                        self.log_message("翻译任务已终止")
                        break
                    shutil.copy(zh_path, os.path.join(folder, "locales", "zh", "ja_nodeDefs.json"))
                    if self.is_stopped:
                        self.log_message("翻译任务已终止")
                        break
                    shutil.copy(zh_path, os.path.join(folder, "locales", "zh", "ko_nodeDefs.json"))
                    if self.is_stopped:
                        self.log_message("翻译任务已终止")
                        break
                    shutil.copy(zh_path, os.path.join(folder, "locales", "zh", "fr_nodeDefs.json"))
                    if self.is_stopped:
                        self.log_message("翻译任务已终止")
                        break
                    self.log_message("已复制 nodeDefs.json 到各语言文件")
                    
                    # 第2步：按顺序提交翻译
                    languages = [
                        ("zh", "system_prompt_text.txt"),
                        ("ru", "system_prompt_text_ru.txt"),
                        ("ja", "system_prompt_text_ja.txt"),
                        ("ko", "system_prompt_text_ko.txt"),
                        ("fr", "system_prompt_text_fr.txt")
                    ]
                    
                    for lang, prompt_file in languages:
                        if self.is_stopped:
                            self.log_message("翻译任务已终止")
                            break
                        try:
                            # 重新初始化翻译服务
                            translation_service = TranslationService(api_key, model_id)
                            self.log_message(f"\n开始 {lang} 翻译...")
                            
                            # 重新加载提示词
                            current_prompt = self.reload_prompt(lang)
                            if not current_prompt:
                                self.log_message(f"错误：{lang} 提示词为空，跳过此语言")
                                continue
                            
                            # 打印当前提示词到终端
                            self.log_message(f"当前 {lang} 提示词内容预览: {current_prompt[:200]}...")
                            
                            # 获取对应的文件路径
                            target_file = "nodeDefs.json" if lang == "zh" else f"{lang}_nodeDefs.json"
                            target_path = os.path.join(folder, "locales", "zh", target_file)
                            
                            # 读取目标文件
                            with open(target_path, 'r', encoding='utf-8') as f:
                                target_data = json.load(f)
                            
                            # 执行翻译
                            success, translated_data = asyncio.run(
                                translation_service.translate(target_data, current_prompt)
                            )
                            
                            if success and translated_data:
                                # 保存翻译结果
                                with open(target_path, 'w', encoding='utf-8') as f:
                                    json.dump(translated_data, f, ensure_ascii=False, indent=2)
                                self.log_message(f"{lang} 翻译完成，已保存到: {target_path}")
                            else:
                                self.log_message(f"{lang} 翻译失败")
                                
                        except Exception as e:
                            self.log_message(f"{lang} 翻译过程中出错: {str(e)}")
                            continue
                            
                    self.log_message("\n全球化翻译完成！")
                    
                    # 第3步：将翻译后的文件复制到对应的语言目录
                    self.log_message("\n开始复制翻译文件到对应语言目录...")
                    languages = ["ru", "ja", "ko", "fr"]
                    for lang in languages:
                        if self.is_stopped:
                            self.log_message("文件复制任务已终止")
                            break
                            
                        try:
                            # 源文件和目标文件路径
                            source_file = os.path.join(folder, "locales", "zh", f"{lang}_nodeDefs.json")
                            target_dir = os.path.join(folder, "locales", lang)
                            target_file = os.path.join(target_dir, "nodeDefs.json")
                            
                            # 确保目标目录存在
                            os.makedirs(target_dir, exist_ok=True)
                            
                            # 复制文件
                            shutil.copy2(source_file, target_file)
                            self.log_message(f"已将 {lang} 的翻译结果复制到: {target_file}")
                            
                        except Exception as e:
                            self.log_message(f"复制 {lang} 翻译文件时出错: {str(e)}")
                            continue
                    
                    self.log_message("\n所有翻译文件复制完成！")
                    
                    # 第4步：清理临时翻译文件
                    self.log_message("\n开始清理临时翻译文件...")
                    temp_files = ["ru_nodeDefs.json", "ja_nodeDefs.json", "ko_nodeDefs.json", "fr_nodeDefs.json"]
                    for temp_file in temp_files:
                        if self.is_stopped:
                            self.log_message("清理任务已终止")
                            break
                            
                        try:
                            temp_file_path = os.path.join(folder, "locales", "zh", temp_file)
                            if os.path.exists(temp_file_path):
                                os.remove(temp_file_path)
                                self.log_message(f"已删除临时文件: {temp_file}")
                        except Exception as e:
                            self.log_message(f"删除临时文件 {temp_file} 时出错: {str(e)}")
                            continue
                    
                    self.log_message("\n临时文件清理完成！")
                    
                else:
                    # 仅中文翻译模式
                    try:
                        self.log_message("\n开始中文翻译...")
                        current_prompt = self.reload_prompt("zh")
                        if not current_prompt:
                            self.log_message("错误：中文提示词为空，终止翻译")
                            continue
                            
                        self.log_message(f"提示词内容预览: {current_prompt[:200]}...")
                        
                        # 初始化翻译服务
                        translation_service = TranslationService(api_key, model_id)
                        
                        # 执行翻译
                        success, translated_data = asyncio.run(
                            translation_service.translate(json_data, current_prompt)
                        )
                        
                        if success and translated_data:
                            # 保存翻译结果
                            with open(zh_path, 'w', encoding='utf-8') as f:
                                json.dump(translated_data, f, ensure_ascii=False, indent=2)
                            self.log_message(f"中文翻译完成，已保存到: {zh_path}")
                        else:
                            self.log_message("中文翻译失败")
                            
                    except Exception as e:
                        self.log_message(f"中文翻译过程中出错: {str(e)}")
                
        except Exception as e:
            error_msg = f"翻译过程中发生错误: {str(e)}"
            self.master.after(0, lambda: self.log_message(error_msg))
            self.master.after(0, lambda: messagebox.showerror("错误", error_msg))
        finally:
            self.is_stopped = True
            self.master.after(0, self._reset_translation_buttons)

    def reload_prompt(self, lang: str) -> str:
        """加载指定语言的提示词
        
        Args:
            lang: 语言代码
        
        Returns:
            str: 提示词内容
        """
        if lang == "zh":
            import importlib
            import prompts.system_prompts
            importlib.reload(prompts.system_prompts)
            from prompts.system_prompts import SYSTEM_PROMPT
            self.log_message("已重新加载中文提示词")
            return SYSTEM_PROMPT
        else:
            prompt_file = f"system_prompt_text_{lang}.txt"
            prompt_path = os.path.join("prompts", prompt_file)
            try:
                with open(prompt_path, 'r', encoding='utf-8') as f:
                    current_prompt = f.read().strip()
                self.log_message(f"已加载 {lang} 提示词")
                return current_prompt
            except Exception as e:
                self.log_message(f"加载 {lang} 提示词失败: {str(e)}")
                return ""

    def _reset_translation_buttons(self):
        """重置翻译相关按钮状态"""
        self.translate_btn.configure(state='normal')
        self.stop_btn.configure(state='disabled')

    def log_message(self, message: str):
        """添加日志消息
        
        Args:
            message: 日志消息
        """
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)  # 滚动到最后一行
        logging.info(message)

    def save_config(self):
        """保存配置"""
        api_key = self.api_key_entry.get()
        model_id = self.model_id_entry.get()
        
        if not api_key or not model_id:
            messagebox.showwarning("警告", "请填写 API Key 和 Model ID！")
            return
            
        self.config_manager.save_config(api_key, model_id)
        messagebox.showinfo("成功", "配置已保存！")
        
    def load_config(self):
        """加载配置"""
        config = self.config_manager.load_config()
        if config:
            # 清除现有内容
            self.api_key_entry.delete(0, tk.END)
            self.model_id_entry.delete(0, tk.END)
            
            # 插入配置值
            self.api_key_entry.insert(0, config.get("api_key", "").strip())
            self.model_id_entry.insert(0, config.get("model_id", "").strip())
            logging.info("已加载配置")

    def test_api(self):
        """测试 API 连接"""
        api_key = self.api_key_entry.get()
        model_id = self.model_id_entry.get()
        
        if not api_key or not model_id:
            messagebox.showwarning("警告", "请填写 API Key 和 Model ID！")
            return
            
        self.log_message("开始测试 API 连接...")
        
        # 在新线程中运行测试
        threading.Thread(target=self._run_api_test, args=(api_key, model_id)).start()
        
    def _run_api_test(self, api_key: str, model_id: str):
        """在新线程中运行 API 测试
        
        Args:
            api_key: API 密钥
            model_id: 模型 ID
        """
        try:
            # 初始化翻译服务
            translation_service = TranslationService(api_key, model_id)
            
            # 准备测试数据
            test_data = {"test": "Who are you?"}
            
            # 执行测试
            result = self.loop.run_until_complete(translation_service.translate_batch(test_data))
            
            if result:
                self.master.after(0, lambda: self.log_message("API 测试成功！"))
                self.master.after(0, lambda: self.log_message(f"API 响应: {json.dumps(result, ensure_ascii=False)}"))
                self.master.after(0, lambda: messagebox.showinfo("成功", "API 连接测试成功！"))
            else:
                self.master.after(0, lambda: self.log_message("API 测试失败：未收到有效响应"))
                self.master.after(0, lambda: messagebox.showerror("错误", "API 测试失败：未收到有效响应"))
                
        except Exception as e:
            error_msg = f"API 测试失败: {str(e)}"
            self.master.after(0, lambda: self.log_message(error_msg))
            self.master.after(0, lambda: messagebox.showerror("错误", error_msg))

    def setup_translation_mode_section(self, parent):
        """设置翻译模式选择区域"""
        mode_frame = ttk.LabelFrame(parent, text="翻译模式", style='Custom.TLabelframe')
        mode_frame.grid(row=0, column=1, sticky='ew', pady=(0, 15))
        
        # 仅中文翻译选项
        ttk.Radiobutton(mode_frame, text="仅中文翻译", variable=self.translation_mode, value='chinese_only').grid(row=0, column=0, padx=5, sticky='w')
        # 全球化翻译选项
        ttk.Radiobutton(mode_frame, text="全球化翻译", variable=self.translation_mode, value='global_translation').grid(row=0, column=1, padx=5, sticky='w')

    def _parse_global_translation(self):
        """解析全局翻译"""
        try:
            # 1. 首先按照 V1 的逻辑生成 zh/nodeDefs.json
            self._parse_chinese_only()  # 调用原有的中文解析逻辑
            
            # 2. 定义其他语言列表
            other_languages = ["ru", "ko", "ja", "fr", "en"]
            
            # 3. 遍历所有文件夹
            for folder in self.folders:
                # 获取中文版本的 nodeDefs.json 路径
                zh_nodeDefs_path = os.path.join(folder, "locales", "zh", "nodeDefs.json")
                
                # 确保中文版本存在
                if not os.path.exists(zh_nodeDefs_path):
                    self.log_message(f"错误：未找到中文版本的 nodeDefs.json: {zh_nodeDefs_path}")
                    continue
                    
                # 4. 为其他语言创建目录并复制文件
                for lang_code in other_languages:
                    try:
                        # 创建语言目录
                        lang_dir = os.path.join(folder, "locales", lang_code)
                        os.makedirs(lang_dir, exist_ok=True)
                        
                        # 复制中文版本到该语言目录
                        target_path = os.path.join(lang_dir, "nodeDefs.json")
                        shutil.copy2(zh_nodeDefs_path, target_path)
                        
                        self.log_message(f"已创建 {lang_code} 语言文件: {target_path}")
                    except Exception as e:
                        self.log_message(f"处理 {lang_code} 语言时出错: {str(e)}")
            
            self.log_message("全球化翻译文件生成完成！")
        except Exception as e:
            error_msg = f"全球化翻译处理出错: {str(e)}"
            self.log_message(error_msg)
            messagebox.showerror("错误", error_msg)

    def _parse_chinese_only(self):
        """解析中文翻译"""
        if not self.folders:
            messagebox.showwarning("警告", "请先添加文件夹！")
            return
            
        total_folders = len(self.folders)
        for folder in self.folders:
            try:
                self.log_message(f"开始解析文件夹: {folder}")
                
                # 扫描 Python 文件
                python_files = FileHandler.scan_plugin_folder(folder)
                self.log_message(f"找到 {len(python_files)} 个 Python 文件")
                
                # 解析每个文件
                all_nodes = {}
                for file_path in python_files:
                    try:
                        nodes = NodeParser.parse_file(file_path)
                        if nodes:
                            all_nodes.update(nodes)
                    except Exception as e:
                        self.log_message(f"解析文件失败 {file_path}: {str(e)}")
                
                if all_nodes:
                    # 保存节点信息
                    output_file = FileHandler.save_node_info(all_nodes, folder)
                    self.log_message(f"节点信息已保存到: {output_file}")
                    total_nodes = len(all_nodes)
                    categories = set(node['category'] for node in all_nodes.values())
                    self.log_message(f"总共解析到 {total_nodes} 个节点，类别: {', '.join(categories)}")
                else:
                    self.log_message("未找到任何节点信息")
                
            except Exception as e:
                error_msg = f"处理文件夹时出错: {str(e)}"
                self.log_message(f"错误: {error_msg}")
                messagebox.showerror("错误", error_msg)
                
        # 所有文件夹解析完成后弹出提示
        messagebox.showinfo("成功", f"成功解析 {total_folders} 个文件夹！")
        
        # 移除自动开始翻译的部分
        # threading.Thread(target=self.run_translation).start()

    def _generate_nodeDefs_for_language(self, folder: str, lang_code: str):
        """为指定语言生成 nodeDefs.json 文件"""
        node_info = NodeParser.parse_folder(folder)  # 假设有一个方法可以解析文件夹
        output_file = os.path.join(folder, "locales", lang_code, "nodeDefs.json")
        
        # 保存生成的节点信息
        FileHandler.save_node_info(node_info, output_file)
        self.log_message(f"{lang_code} 的 nodeDefs.json 已生成: {output_file}")

    def stop_translation(self):
        """终止翻译任务"""
        if not self.is_stopped:
            self.is_stopped = True  # 设置停止标志
            self.log_message("正在终止翻译...")
            self.stop_btn.configure(state='disabled')
            self.translate_btn.configure(state='normal')
            
            # 这里可以添加其他需要在停止时执行的逻辑，例如清理资源等
            self.log_message("翻译任务已终止")
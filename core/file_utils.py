"""
文件操作工具类
处理文件扫描、读写等操作
"""

import os
import json
import logging
from typing import List, Dict, Optional

class FileUtils:
    """文件工具类"""
    
    @staticmethod
    def scan_python_files(folder_path: str) -> List[str]:
        """扫描目录下的所有 Python 文件
        
        Args:
            folder_path: 要扫描的文件夹路径
            
        Returns:
            List[str]: Python 文件路径列表
        """
        if not os.path.exists(folder_path):
            raise FileNotFoundError(f"文件夹不存在: {folder_path}")
            
        if not os.path.isdir(folder_path):
            raise NotADirectoryError(f"路径不是文件夹: {folder_path}")
            
        python_files = []
        
        # 遍历文件夹
        for root, _, files in os.walk(folder_path):
            for file in files:
                if file.endswith('.py') or file == '__init__.py':
                    file_path = os.path.join(root, file)
                    python_files.append(file_path)
                    logging.info(f"找到Python文件: {file_path}")
                    
        return python_files
        
    @staticmethod
    def ensure_dir(dir_path: str) -> None:
        """确保目录存在，不存在则创建
        
        Args:
            dir_path: 目录路径
        """
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
            
    @staticmethod
    def save_json(data: Dict, file_path: str, ensure_ascii: bool = False) -> None:
        """保存 JSON 文件
        
        Args:
            data: 要保存的数据
            file_path: 文件路径
            ensure_ascii: 是否确保 ASCII 编码
        """
        # 确保目标目录存在
        os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
        
        # 保存文件
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=ensure_ascii, indent=2)
            
    @staticmethod
    def load_json(file_path: str) -> Dict:
        """加载 JSON 文件
        
        Args:
            file_path: JSON 文件路径
            
        Returns:
            Dict: 加载的数据
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文件不存在: {file_path}")
            
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
            
    @staticmethod
    def get_output_dir(base_path: str, plugin_path: str) -> str:
        """获取插件的输出目录路径
        
        Args:
            base_path: 基础路径
            plugin_path: 插件路径
            
        Returns:
            str: 输出目录路径
        """
        # 获取插件名称
        plugin_name = os.path.basename(plugin_path.rstrip(os.path.sep))
        
        # 创建输出目录
        output_dir = os.path.join(plugin_path, "locales", "zh")
        os.makedirs(output_dir, exist_ok=True)
        
        return output_dir 
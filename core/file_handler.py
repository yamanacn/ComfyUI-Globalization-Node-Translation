"""
文件处理模块
处理文件扫描和 JSON 操作
"""

import os
import json
import logging
from typing import List, Dict

class FileHandler:
    """文件处理类"""
    
    @staticmethod
    def scan_plugin_folder(folder_path: str) -> List[str]:
        """扫描插件文件夹中的所有 Python 文件
        
        Args:
            folder_path: 插件文件夹路径
            
        Returns:
            List[str]: Python 文件路径列表
        """
        if not os.path.exists(folder_path):
            raise FileNotFoundError(f"文件夹不存在: {folder_path}")
            
        python_files = []
        # 遍历文件夹
        for root, _, files in os.walk(folder_path):
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    python_files.append(file_path)
                    logging.info(f"找到Python文件: {file_path}")
                    
        return python_files
        
    @staticmethod
    def save_node_info(node_info: Dict, folder_path: str) -> str:
        """保存节点信息到 JSON 文件
        
        Args:
            node_info: 节点信息字典
            folder_path: 插件文件夹路径
            
        Returns:
            str: JSON 文件路径
        """
        # 创建 locales/zh 目录
        output_dir = os.path.join(folder_path, "locales", "zh")
        os.makedirs(output_dir, exist_ok=True)
        
        # 保存 JSON 文件
        output_file = os.path.join(output_dir, "nodeDefs.json")
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(node_info, f, ensure_ascii=False, indent=2)
            
        logging.info(f"节点信息已保存到: {output_file}")

        # 清除 category 字段
        with open(output_file, 'r+', encoding='utf-8') as f:
            data = json.load(f)
            for key in data.keys():
                if 'category' in data[key]:
                    del data[key]['category']
            f.seek(0)  # 移动到文件开头
            json.dump(data, f, ensure_ascii=False, indent=2)
            f.truncate()  # 截断文件，去掉多余的内容

        return output_file 
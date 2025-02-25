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
        
        # 清理数据，移除不需要的字段
        cleaned_data = {}
        for key, value in node_info.items():
            node_data = {}
            # 只保留需要的字段
            if "display_name" in value:
                node_data["display_name"] = value["display_name"]
            if "inputs" in value:
                node_data["inputs"] = value["inputs"]
            if "outputs" in value:
                node_data["outputs"] = value["outputs"]
            cleaned_data[key] = node_data
        
        # 保存 JSON 文件
        output_file = os.path.join(output_dir, "nodeDefs.json")
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(cleaned_data, f, ensure_ascii=False, indent=2)
            
        logging.info(f"节点信息已保存到: {output_file}")
        return output_file 
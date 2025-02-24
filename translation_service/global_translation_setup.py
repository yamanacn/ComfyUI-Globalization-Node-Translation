"""
全球化翻译设置功能
处理生成多语言 nodeDefs.json 文件的功能
"""

import os
from core.file_handler import FileHandler
from core.node_parser import NodeParser

class GlobalTranslationSetup:
    """全球化翻译设置类"""
    
    def __init__(self, folders: list):
        """初始化全球化翻译设置
        
        Args:
            folders: 文件夹列表
        """
        self.folders = folders
        
    def setup_translation_folders(self):
        """设置翻译文件夹并生成 nodeDefs.json"""
        languages = ["zh", "ru", "ko", "ja", "fr", "en"]
        
        for folder in self.folders:
            for lang in languages:
                lang_dir = os.path.join(folder, "locales", lang)
                os.makedirs(lang_dir, exist_ok=True)  # 创建语言目录
                
                # 生成 nodeDefs.json
                nodeDefs_path = os.path.join(lang_dir, "nodeDefs.json")
                node_info = NodeParser.parse_folder(folder)  # 假设有一个方法可以解析文件夹
                FileHandler.save_node_info(node_info, lang_dir)
                print(f"{lang} 语言的 nodeDefs.json 已生成: {nodeDefs_path}")
        
        print("所有语言的 nodeDefs.json 文件已生成！") 
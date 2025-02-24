"""
配置管理模块
处理配置文件的读写操作
"""

import os
import json
import logging
from typing import Dict, Optional

class ConfigManager:
    """配置管理类"""
    
    def __init__(self):
        """初始化配置管理器"""
        # 使用用户主目录下的隐藏目录保存配置
        self.config_dir = os.path.join(os.path.expanduser("~"), ".comfyui_translator")
        self.config_file = os.path.join(self.config_dir, "config.json")
        self._ensure_config_dir()
        
    def _ensure_config_dir(self):
        """确保配置目录存在"""
        if not os.path.exists(self.config_dir):
            os.makedirs(self.config_dir)
            logging.info(f"创建配置目录: {self.config_dir}")
            
    def save_config(self, api_key: str, model_id: str) -> None:
        """保存配置
        
        Args:
            api_key: API 密钥
            model_id: 模型 ID
        """
        config = {
            "api_key": api_key,
            "model_id": model_id
        }
        
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            logging.info(f"配置已保存到: {self.config_file}")
        except Exception as e:
            logging.error(f"保存配置失败: {str(e)}")
            
    def load_config(self) -> Optional[Dict[str, str]]:
        """加载配置
        
        Returns:
            Optional[Dict[str, str]]: 配置信息，如果文件不存在则返回 None
        """
        if not os.path.exists(self.config_file):
            logging.info("配置文件不存在")
            return None
            
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            logging.info(f"已从 {self.config_file} 加载配置")
            return config
        except Exception as e:
            logging.error(f"加载配置失败: {str(e)}")
            return None 
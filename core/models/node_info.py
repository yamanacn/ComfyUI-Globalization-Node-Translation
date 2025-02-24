"""
节点信息数据模型
用于存储和管理节点的基本信息
"""

from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class NodeInfo:
    """节点信息数据类"""
    name: str
    title: str
    category: str = ""
    function: str = ""
    inputs: Dict[str, str] = None
    outputs: Dict[str, str] = None
    widgets: Dict[str, str] = None
    
    def __post_init__(self):
        """初始化后处理"""
        self.inputs = self.inputs or {}
        self.outputs = self.outputs or {}
        self.widgets = self.widgets or {}
        
    def to_dict(self) -> Dict:
        """转换为字典格式"""
        return {
            "name": self.name,
            "title": self.title,
            "category": self.category,
            "function": self.function,
            "inputs": self.inputs,
            "outputs": self.outputs,
            "widgets": self.widgets
        }
        
    @classmethod
    def from_dict(cls, data: Dict) -> 'NodeInfo':
        """从字典创建实例"""
        return cls(
            name=data.get("name", ""),
            title=data.get("title", ""),
            category=data.get("category", ""),
            function=data.get("function", ""),
            inputs=data.get("inputs", {}),
            outputs=data.get("outputs", {}),
            widgets=data.get("widgets", {})
        )

    def validate(self) -> bool:
        """验证节点信息的完整性
        
        Returns:
            bool: 是否有效
        """
        return bool(self.name and self.title and self.inputs and self.outputs) 
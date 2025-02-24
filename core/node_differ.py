"""
节点差异比较器
用于比较不同版本节点的差异
"""

import os
from typing import Dict, List, Tuple
from .models.node_info import NodeInfo
from .file_utils import FileUtils

class NodeDiffer:
    """节点差异比较器"""
    
    @staticmethod
    def compare_nodes(old_nodes: Dict[str, NodeInfo], new_nodes: Dict[str, NodeInfo]) -> Tuple[Dict[str, NodeInfo], List[str], List[str]]:
        """比较两个版本的节点，找出新增和删除的节点
        
        Args:
            old_nodes: 旧版本节点字典
            new_nodes: 新版本节点字典
            
        Returns:
            Tuple[Dict[str, NodeInfo], List[str], List[str]]: (新增节点字典, 新增节点名称列表, 删除节点名称列表)
        """
        added_nodes = {}
        added_node_names = []
        removed_node_names = []
        
        # 创建旧节点的基础名称集合
        old_base_names = {NodeDiffer._get_base_name(name) for name in old_nodes.keys()}
        
        # 遍历新节点
        for name, node in new_nodes.items():
            # 获取新节点的基础名称
            new_base_name = NodeDiffer._get_base_name(name)
            
            # 如果基础名称不在旧节点中，认为是新增的
            if new_base_name not in old_base_names:
                added_nodes[name] = node
                added_node_names.append(name)

        # 检查旧节点中是否有不在新节点中的节点
        for name in old_nodes.keys():
            if name not in new_nodes:
                removed_node_names.append(name)
        
        return added_nodes, added_node_names, removed_node_names
        
    @staticmethod
    def _get_base_name(node_name: str) -> str:
        """获取节点的基础名称
        
        Args:
            node_name: 完整节点名称
            
        Returns:
            str: 基础名称
        """
        # 移除所有标点符号和多余空格
        name = node_name.replace(":", " ").replace("-", " ").replace("_", " ")
        # 分割成单词并重新组合
        words = [word.strip() for word in name.split() if word.strip()]
        return " ".join(words)
        
    @staticmethod
    def save_added_nodes(added_nodes: Dict[str, NodeInfo], output_path: str) -> str:
        """保存新增节点到文件
        
        Args:
            added_nodes: 新增节点字典
            output_path: 输出路径
            
        Returns:
            str: 输出文件路径
        """
        if not added_nodes:
            return ""
            
        # 转换为字典格式
        nodes_dict = {name: node.to_dict() for name, node in added_nodes.items()}
        
        # 保存文件
        output_file = os.path.join(output_path, "added_nodes.json")
        FileUtils.save_json(nodes_dict, output_file)
        
        return output_file 
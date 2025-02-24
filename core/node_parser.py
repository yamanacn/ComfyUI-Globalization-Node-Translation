"""
节点解析模块
用于解析 ComfyUI 节点信息
"""

import ast
import os
import logging
from typing import Dict, Optional, Any, List, Tuple

class NodeParser:
    """节点解析器"""
    
    @staticmethod
    def parse_file(file_path: str) -> Dict[str, Dict]:
        """解析单个 Python 文件中的节点信息"""
        nodes_info = {}
        
        try:
            # 读取并解析文件
            with open(file_path, 'r', encoding='utf-8') as f:
                tree = ast.parse(f.read())
                
            # 获取文件级别的映射
            node_mappings = NodeParser._get_node_mappings(tree)
            display_mappings = NodeParser._get_display_mappings(tree)
            
            # 解析每个类定义
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    # 检查是否是 ComfyUI 节点类
                    if NodeParser._is_comfy_node(node):
                        class_name = node.name
                        # 使用注册名称作为键
                        registered_name = NodeParser._get_registered_name(class_name, node_mappings)
                        node_info = NodeParser._parse_node_class(node, registered_name, display_mappings)
                        if node_info:
                            nodes_info[registered_name] = node_info
                            logging.info(f"成功解析节点: {registered_name}")
                            
        except Exception as e:
            logging.error(f"解析文件失败 {file_path}: {str(e)}")
            
        return nodes_info
        
    @staticmethod
    def _is_comfy_node(class_node: ast.ClassDef) -> bool:
        """检查是否是 ComfyUI 节点类"""
        has_input_types = False
        has_return_types = False
        
        for item in class_node.body:
            if isinstance(item, ast.FunctionDef) and item.name == "INPUT_TYPES":
                has_input_types = True
            elif isinstance(item, ast.Assign):
                for target in item.targets:
                    if isinstance(target, ast.Name) and target.id == "RETURN_TYPES":
                        has_return_types = True
                        
        return has_input_types or has_return_types
        
    @staticmethod
    def _get_node_mappings(tree: ast.AST) -> Dict[str, str]:
        """获取 NODE_CLASS_MAPPINGS"""
        mappings = {}
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id == "NODE_CLASS_MAPPINGS":
                        if isinstance(node.value, ast.Dict):
                            for key, value in zip(node.value.keys, node.value.values):
                                if isinstance(key, ast.Str) and isinstance(value, ast.Name):
                                    mappings[value.id] = key.s
        return mappings
        
    @staticmethod
    def _get_display_mappings(tree: ast.AST) -> Dict[str, str]:
        """获取 NODE_DISPLAY_NAME_MAPPINGS"""
        mappings = {}
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id == "NODE_DISPLAY_NAME_MAPPINGS":
                        if isinstance(node.value, ast.Dict):
                            for key, value in zip(node.value.keys, node.value.values):
                                if isinstance(key, ast.Str) and isinstance(value, ast.Str):
                                    mappings[key.s] = value.s
        return mappings
        
    @staticmethod
    def _get_registered_name(class_name: str, mappings: Dict[str, str]) -> str:
        """获取节点的注册名称"""
        for cls, name in mappings.items():
            if cls == class_name:
                return name
        return class_name
        
    @staticmethod
    def _parse_node_class(class_node: ast.ClassDef, node_key: str, display_mappings: Dict[str, str]) -> Optional[Dict]:
        """解析节点类定义"""
        node_info = {
            "display_name": display_mappings.get(node_key, node_key),
            "inputs": {},
            "outputs": {},
            "category": ""  # 添加 category 字段
        }
        
        return_types = []
        return_names = []
        
        for item in class_node.body:
            # 解析输入类型
            if isinstance(item, ast.FunctionDef) and item.name == "INPUT_TYPES":
                input_types = NodeParser._parse_input_types(item)
                if input_types:
                    node_info["inputs"] = input_types
                    
            # 解析返回类型和名称
            elif isinstance(item, ast.Assign):
                for target in item.targets:
                    if isinstance(target, ast.Name):
                        if target.id == "RETURN_TYPES":
                            return_types = NodeParser._extract_value(item.value)
                        elif target.id == "RETURN_NAMES":
                            return_names = NodeParser._extract_value(item.value)
                        elif target.id == "CATEGORY":  # 提取 CATEGORY
                            node_info["category"] = NodeParser._extract_value(item.value)
                            
        # 处理输出信息
        if return_types:
            # 如果没有 RETURN_NAMES，使用 RETURN_TYPES 的小写形式
            if not return_names:
                return_names = [t.lower() for t in return_types]
                
            # 生成输出字典
            outputs = {}
            for name in return_names:
                outputs[name] = {"name": name}
            node_info["outputs"] = outputs
            
        return node_info
        
    @staticmethod
    def _parse_input_types(method_node: ast.FunctionDef) -> Dict:
        """解析输入类型方法"""
        inputs = {}
        
        # 查找方法中的返回语句
        for node in ast.walk(method_node):
            if isinstance(node, ast.Return) and isinstance(node.value, ast.Dict):
                # 解析 required 和 optional 输入
                for key, value in zip(node.value.keys, node.value.values):
                    if isinstance(key, ast.Str):
                        if key.s in ["required", "optional"]:
                            if isinstance(value, ast.Dict):
                                for input_key, _ in zip(value.keys, value.values):
                                    if isinstance(input_key, ast.Str):
                                        input_name = input_key.s
                                        inputs[input_name] = {"name": input_name}
                                        
        return inputs
        
    @staticmethod
    def _extract_value(node: ast.AST) -> Any:
        """提取 AST 节点的值"""
        if isinstance(node, ast.Str):
            return node.s
        elif isinstance(node, ast.Num):
            return node.n
        elif isinstance(node, ast.List):
            return [NodeParser._extract_value(item) for item in node.elts]
        elif isinstance(node, ast.Tuple):
            return tuple(NodeParser._extract_value(item) for item in node.elts)
        elif isinstance(node, ast.Dict):
            return {
                NodeParser._extract_value(k): NodeParser._extract_value(v)
                for k, v in zip(node.keys, node.values)
            }
        elif isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Constant):
            return node.value
        return None 

    @staticmethod
    def parse_folder(folder_path: str) -> Dict[str, Dict]:
        """解析指定文件夹中的所有 Python 文件
        
        Args:
            folder_path: 要解析的文件夹路径
            
        Returns:
            Dict[str, Dict]: 解析出的节点信息字典
        """
        nodes_info = {}
        
        # 遍历文件夹中的所有文件
        for root, _, files in os.walk(folder_path):
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    file_nodes = NodeParser.parse_file(file_path)
                    nodes_info.update(file_nodes)  # 合并节点信息
        
        return nodes_info 
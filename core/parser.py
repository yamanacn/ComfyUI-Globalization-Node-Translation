#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
节点解析器
用于解析ComfyUI插件文件夹中的节点信息
"""

import os
import ast
import json

class NodeParser:
    """ComfyUI节点解析器类"""
    
    def __init__(self, plugin_path: str):
        """初始化节点解析器
        
        Args:
            plugin_path: 插件目录路径
        """
        self.plugin_path = plugin_path
        self.node_info = {}
        
    def parse_folder(self, folder_path):
        """
        解析指定文件夹中的所有Python文件
        
        Args:
            folder_path: 插件文件夹路径
        """
        # 首先解析__init__.py获取节点映射
        init_file = os.path.join(folder_path, "__init__.py")
        if os.path.exists(init_file):
            self.parse_init_file(init_file)
            
        # 遍历所有Python文件
        for root, _, files in os.walk(folder_path):
            for file in files:
                if file.endswith(".py") and file != "__init__.py":
                    file_path = os.path.join(root, file)
                    self.parse_file(file_path)
                    
        # 保存解析结果
        self.save_results(folder_path)
        
    def parse_init_file(self, file_path):
        """
        解析__init__.py文件获取节点映射
        
        Args:
            file_path: __init__.py文件路径
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            tree = ast.parse(f.read())
            
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id == "NODE_CLASS_MAPPINGS":
                        if isinstance(node.value, ast.Dict):
                            for key, value in zip(node.value.keys, node.value.values):
                                if isinstance(key, ast.Str) and isinstance(value, ast.Name):
                                    self.node_info[value.id] = {
                                        "node_name": key.s,
                                        "category": "",
                                        "input_types": {},
                                        "return_types": [],
                                        "function": ""
                                    }
                                    
    def parse_file(self, file_path):
        """
        解析Python文件中的节点类定义
        
        Args:
            file_path: Python文件路径
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            tree = ast.parse(f.read())
            
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name in self.node_info:
                self.parse_class(node)
                
    def parse_class(self, class_node):
        """
        解析类定义，提取节点信息
        
        Args:
            class_node: AST类定义节点
        """
        node_info = self.node_info[class_node.name]
        
        for node in class_node.body:
            # 解析类别
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id == "CATEGORY":
                        if isinstance(node.value, ast.Str):
                            node_info["category"] = node.value.s
                            
            # 解析输入类型
            elif isinstance(node, ast.FunctionDef) and node.name == "INPUT_TYPES":
                node_info["input_types"] = self.extract_return_value(node)
                
            # 解析返回类型
            elif isinstance(node, ast.FunctionDef) and node.name == "RETURN_TYPES":
                node_info["return_types"] = self.extract_return_value(node)
                
            # 解析函数名
            elif isinstance(node, ast.FunctionDef) and node.name != "INPUT_TYPES" and node.name != "RETURN_TYPES":
                node_info["function"] = node.name
                
    def extract_return_value(self, func_node):
        """
        提取函数的返回值
        
        Args:
            func_node: AST函数定义节点
            
        Returns:
            解析后的返回值
        """
        for node in func_node.body:
            if isinstance(node, ast.Return):
                return self.extract_value(node.value)
        return None
        
    def extract_value(self, node):
        """
        递归提取AST节点的值
        
        Args:
            node: AST节点
            
        Returns:
            解析后的Python值
        """
        if isinstance(node, ast.Str):
            return node.s
        elif isinstance(node, ast.Num):
            return node.n
        elif isinstance(node, ast.List) or isinstance(node, ast.Tuple):
            return [self.extract_value(item) for item in node.elts]
        elif isinstance(node, ast.Dict):
            return {
                self.extract_value(key): self.extract_value(value)
                for key, value in zip(node.keys, node.values)
            }
        elif isinstance(node, ast.Name):
            # 简单处理，返回变量名
            return node.id
        return None
        
    def save_results(self, folder_path):
        """
        保存解析结果到JSON文件
        
        Args:
            folder_path: 插件文件夹路径
        """
        # 创建locales/zh目录
        output_dir = os.path.join(folder_path, "locales", "zh")
        os.makedirs(output_dir, exist_ok=True)
        
        # 保存JSON文件
        output_file = os.path.join(output_dir, "nodeDefs.json")
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.node_info, f, ensure_ascii=False, indent=2) 
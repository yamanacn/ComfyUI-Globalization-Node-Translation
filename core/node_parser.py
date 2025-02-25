"""
节点解析模块
用于解析 ComfyUI 节点信息
"""

import ast
import os
import logging
from typing import Dict, Optional, Any, List, Tuple, Set

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
            
            # 创建类名到父类的映射
            inheritance_map, class_defs = NodeParser._get_class_inheritance(tree)
            
            # 解析每个类定义
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    # 检查是否是 ComfyUI 节点类
                    if NodeParser._is_comfy_node(node, inheritance_map, class_defs) or node.name in node_mappings:
                        class_name = node.name
                        # 使用注册名称作为键
                        registered_name = NodeParser._get_registered_name(class_name, node_mappings)
                        # 获取父类信息
                        parent_info = NodeParser._get_parent_info(node, inheritance_map, class_defs)
                        node_info = NodeParser._parse_node_class(node, registered_name, display_mappings, parent_info)
                        if node_info:
                            nodes_info[registered_name] = node_info
                            logging.info(f"成功解析节点: {registered_name}")
                            
        except Exception as e:
            logging.error(f"解析文件失败 {file_path}: {str(e)}")
            
        return nodes_info
        
    @staticmethod
    def _get_class_inheritance(tree: ast.AST) -> Dict[str, List[str]]:
        """获取类的继承关系"""
        inheritance_map = {}
        # 先收集所有类定义
        class_defs = {}
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                class_defs[node.name] = node
                parent_classes = []
                for base in node.bases:
                    if isinstance(base, ast.Name):
                        parent_classes.append(base.id)
                inheritance_map[node.name] = parent_classes
        return inheritance_map, class_defs

    @staticmethod
    def _get_parent_info(class_node: ast.ClassDef, inheritance_map: Dict[str, List[str]], class_defs: Dict[str, ast.ClassDef]) -> Dict:
        """获取父类的输入输出信息"""
        parent_info = {
            "inputs": {},
            "outputs": {},
            "category": "",
            "function": ""
        }
        
        def get_parent_data(class_name: str, visited: Set[str]):
            if class_name in visited:
                return
            visited.add(class_name)
            
            # 获取父类列表
            parent_classes = inheritance_map.get(class_name, [])
            for parent in parent_classes:
                if parent in class_defs:
                    parent_node = class_defs[parent]
                    # 解析父类的输入类型
                    for item in parent_node.body:
                        if isinstance(item, ast.FunctionDef) and item.name == "INPUT_TYPES":
                            input_types = NodeParser._parse_input_types(item)
                            if input_types:
                                parent_info["inputs"].update(input_types)
                        elif isinstance(item, ast.FunctionDef) and item.name not in ["INPUT_TYPES", "__init__"]:
                            # 解析父类方法的参数
                            method_params = NodeParser._parse_method_parameters(item)
                            for param_name, param_type in method_params.items():
                                if param_name not in parent_info["inputs"]:
                                    parent_info["inputs"][param_name] = {"name": param_name}
                        elif isinstance(item, ast.Assign):
                            for target in item.targets:
                                if isinstance(target, ast.Name):
                                    if target.id == "RETURN_TYPES":
                                        return_types = NodeParser._extract_value(item.value)
                                        if return_types:
                                            outputs = {}
                                            for rt in return_types:
                                                name = rt.lower()
                                                outputs[name] = {"name": name}
                                            parent_info["outputs"].update(outputs)
                                    elif target.id == "CATEGORY":
                                        parent_info["category"] = NodeParser._extract_value(item.value)
                                    elif target.id == "FUNCTION":
                                        parent_info["function"] = NodeParser._extract_value(item.value)
                    
                    # 递归处理父类的父类
                    get_parent_data(parent, visited)
                    
        visited = set()
        get_parent_data(class_node.name, visited)
        return parent_info

    @staticmethod
    def _is_comfy_node(class_node: ast.ClassDef, inheritance_map: Dict[str, List[str]], class_defs: Dict[str, ast.ClassDef]) -> bool:
        """检查是否是 ComfyUI 节点类
        
        检测规则（按优先级排序）：
        1. 原始规则：有 INPUT_TYPES 方法或 RETURN_TYPES 属性
        2. 映射规则：类在 NODE_CLASS_MAPPINGS 中
        3. 继承规则：父类是节点类
        4. 组合规则：
           - 有 CATEGORY 且有 FUNCTION
           - 有 RETURN_TYPES 且有 FUNCTION
           - 类名以 Node 结尾且有 CATEGORY 或 FUNCTION
           - 有 RETURN_NAMES 且有 RETURN_TYPES
        """
        # 检查当前类的属性
        has_input_types = False
        has_return_types = False
        has_category = False
        has_function = False
        has_return_names = False
        
        # 检查类名是否以 Node 结尾
        is_node_class = class_node.name.endswith('Node')
        
        # 检查类的所有属性和方法
        for item in class_node.body:
            if isinstance(item, ast.FunctionDef):
                if item.name == "INPUT_TYPES":
                    has_input_types = True
                elif item.name == "FUNCTION":
                    has_function = True
            elif isinstance(item, ast.Assign):
                for target in item.targets:
                    if isinstance(target, ast.Name):
                        if target.id == "RETURN_TYPES":
                            has_return_types = True
                        elif target.id == "CATEGORY":
                            has_category = True
                        elif target.id == "FUNCTION":
                            has_function = True
                        elif target.id == "RETURN_NAMES":
                            has_return_names = True
        
        # 1. 原始规则：保持原有的基本检测逻辑
        if has_input_types or has_return_types:
            return True
            
        # 2. 继承规则：检查父类
        def check_parent_class(class_name: str, visited: Set[str]) -> bool:
            if class_name in visited:
                return False
            visited.add(class_name)
            
            parent_classes = inheritance_map.get(class_name, [])
            for parent in parent_classes:
                if parent in class_defs:
                    parent_node = class_defs[parent]
                    # 递归检查父类是否满足节点条件
                    if NodeParser._is_comfy_node(parent_node, inheritance_map, class_defs):
                        return True
            return False
            
        # 3. 组合规则：检查多个属性组合
        has_valid_combination = any([
            has_category and has_function,  # 有类别和功能
            has_return_types and has_function,  # 有返回类型和功能
            is_node_class and (has_category or has_function),  # Node类且有类别或功能
            has_return_names and has_return_types,  # 有返回名称和类型
            has_category and has_return_types,  # 有类别和返回类型
            has_input_types and has_function,  # 有输入类型和功能
        ])
        
        # 检查父类的继承关系
        visited = set()
        has_valid_parent = check_parent_class(class_node.name, visited)
        
        # 返回所有检测结果的组合
        return any([
            has_input_types,  # 原始规则1
            has_return_types,  # 原始规则2
            has_valid_parent,  # 继承规则
            has_valid_combination,  # 组合规则
        ])
        
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
    def _parse_node_class(class_node: ast.ClassDef, node_key: str, display_mappings: Dict[str, str], parent_info: Dict) -> Optional[Dict]:
        """解析节点类定义"""
        node_info = {
            "display_name": display_mappings.get(node_key, node_key),
            "inputs": parent_info.get("inputs", {}),
            "outputs": parent_info.get("outputs", {}),
            "category": parent_info.get("category", "")
        }
        
        # 解析类属性和方法
        for item in class_node.body:
            # 解析输入类型
            if isinstance(item, ast.FunctionDef):
                if item.name == "INPUT_TYPES":
                    input_types = NodeParser._parse_input_types(item)
                    if input_types:
                        node_info["inputs"].update(input_types)
                elif item.name not in ["INPUT_TYPES", "__init__"]:
                    # 解析其他方法的参数
                    method_params = NodeParser._parse_method_parameters(item)
                    for param_name, param_type in method_params.items():
                        if param_name not in node_info["inputs"]:
                            node_info["inputs"][param_name] = {"name": param_name}
                    
            # 解析类属性
            elif isinstance(item, ast.Assign):
                for target in item.targets:
                    if isinstance(target, ast.Name):
                        if target.id == "RETURN_TYPES":
                            return_types = NodeParser._extract_value(item.value)
                            if return_types:
                                outputs = {}
                                for rt in return_types:
                                    name = rt.lower()
                                    outputs[name] = {"name": name}
                                node_info["outputs"] = outputs
                        elif target.id == "CATEGORY":
                            node_info["category"] = NodeParser._extract_value(item.value)
                        elif target.id == "FUNCTION":
                            node_info["function"] = NodeParser._extract_value(item.value)
                            
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
    def _parse_method_parameters(method_node: ast.FunctionDef) -> Dict[str, str]:
        """解析方法参数
        
        Args:
            method_node: 方法的 AST 节点
            
        Returns:
            Dict[str, str]: 参数名到参数类型的映射
        """
        params = {}
        
        # 跳过 self 参数
        args = method_node.args.args[1:] if method_node.args.args else []
        
        for arg in args:
            param_name = arg.arg
            # 获取参数类型注解
            if arg.annotation:
                if isinstance(arg.annotation, ast.Name):
                    param_type = arg.annotation.id
                elif isinstance(arg.annotation, ast.Attribute):
                    param_type = f"{arg.annotation.value.id}.{arg.annotation.attr}"
                else:
                    param_type = "Any"
            else:
                param_type = "Any"
                
            params[param_name] = param_type
            
        return params
        
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
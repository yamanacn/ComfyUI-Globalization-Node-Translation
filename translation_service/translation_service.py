"""
翻译服务模块
处理与火山引擎 API 的所有交互
"""

import os
import json
import logging
import sys
from typing import List, Callable, Optional, Tuple, Dict
from prompts.system_prompts import SYSTEM_PROMPT
from openai import OpenAI

class TranslationService:
    """翻译服务类"""
    
    def __init__(self, api_key: str, model_id: str):
        """初始化翻译服务"""
        self.api_key = api_key.strip()  # 清理 API Key
        self.model_id = model_id
        self.base_url = "https://ark.cn-beijing.volces.com/api/v3"
        self.is_stopped = False
        self.temp_translation_file = "temp_translations.json"
        self.translation_map = {}
        
        # 初始化 OpenAI 客户端
        self.client = OpenAI(
            base_url=self.base_url,
            api_key=self.api_key
        )
        
        # 配置日志
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s [%(levelname)s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        print("\n正在加载系统提示词...")
        # 检查系统提示词
        self.system_prompt = SYSTEM_PROMPT
        if not self.system_prompt:
            print("\033[91m系统提示词加载失败！\033[0m")  # 红色文字
            logging.error("系统提示词加载失败")
        else:
            print("\033[92m系统提示词加载成功！\033[0m")  # 绿色文字
            logging.info("系统提示词加载成功")
        print()  # 添加空行
        
        print("系统提示词:", json.dumps(self.system_prompt, ensure_ascii=False, indent=2))
        
    def save_temp_translations(self, data: dict) -> None:
        """保存临时翻译结果
        
        Args:
            data: 翻译结果数据
        """
        try:
            with open(self.temp_translation_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logging.info(f"临时翻译结果已保存到: {self.temp_translation_file}")
        except Exception as e:
            logging.error(f"保存临时翻译结果失败: {str(e)}")

    def create_translation_map(self, json_data: dict) -> dict:
        """从临时翻译文件创建映射字典"""
        try:
            with open(self.temp_translation_file, 'r', encoding='utf-8') as f:
                temp_data = json.load(f)
            
            translation_map = {}
            # 遍历所有节点
            for node_data in temp_data.values():
                # 处理 display_name
                if "display_name" in node_data:
                    display_name = node_data["display_name"]
                    # 提取映射关系（这里需要根据实际情况调整提取逻辑）
                    if "(" in display_name:
                        base_name = display_name.split("(")[0].strip()
                        translation_map[base_name.split(": ")[-1]] = base_name.split(": ")[-1]
                
                # 处理 inputs
                if "inputs" in node_data:
                    for input_data in node_data["inputs"].values():
                        if "name" in input_data:
                            translation_map[input_data["name"]] = input_data["name"]
                
                # 处理 outputs
                if "outputs" in node_data:
                    for output_data in node_data["outputs"].values():
                        if "name" in output_data:
                            translation_map[output_data["name"]] = output_data["name"]
            
            logging.info(f"已创建映射字典，包含 {len(translation_map)} 个映射关系")
            return translation_map
            
        except Exception as e:
            logging.error(f"创建映射字典失败: {str(e)}")
            return {}

    def extract_terms(self, json_data: dict) -> List[str]:
        """提取需要翻译的词条"""
        terms = []
        
        for node_name, node_data in json_data.items():
            # 提取 display_name
            if "display_name" in node_data:
                display_name = node_data['display_name']
                terms.append(f"{display_name} -> {display_name}")
            
            # 提取 inputs
            if "inputs" in node_data:
                for input_key, input_value in node_data["inputs"].items():
                    if "name" in input_value:
                        name = input_value["name"]
                        terms.append(f"{name} -> {name}")
            
            # 提取 outputs
            if "outputs" in node_data:
                for output_key, output_value in node_data["outputs"].items():
                    if "name" in output_value:
                        name = output_value["name"]
                        terms.append(f"{name} -> {name}")
        
        return terms

    def parse_translation(self, original_text: str, translated_text: str) -> Dict[str, str]:
        """解析翻译结果"""
        translation_map = {}
        
        # 分割原文和译文
        original_lines = original_text.strip().split('\n')
        translated_lines = translated_text.strip().split('\n')
        
        # 创建映射
        for orig, trans in zip(original_lines, translated_lines):
            if '->' in orig and '->' in trans:
                orig_key = orig.split('->')[0].strip()  # 使用箭头前的值作为key
                trans_value = trans.split('->')[1].strip()
                translation_map[orig_key] = trans_value
        
        return translation_map

    def apply_translations(self, json_data: dict, translation_map: Dict[str, str]) -> dict:
        """应用翻译结果"""
        result = json_data.copy()
        
        for node_name, node_data in result.items():
            # 翻译 display_name
            if "display_name" in node_data:
                orig = node_data["display_name"]
                node_data["display_name"] = translation_map.get(orig, orig)
            
            # 翻译 inputs
            if "inputs" in node_data:
                for input_data in node_data["inputs"].values():
                    if "name" in input_data:
                        orig = input_data["name"]
                        input_data["name"] = translation_map.get(orig, orig)
            
            # 翻译 outputs
            if "outputs" in node_data:
                for output_data in node_data["outputs"].values():
                    if "name" in output_data:
                        orig = output_data["name"]
                        output_data["name"] = translation_map.get(orig, orig)
        
        return result

    async def translate(self, json_data: dict, system_prompt: str = None) -> Tuple[bool, dict]:
        """翻译完整的JSON数据
        
        Args:
            json_data: 要翻译的JSON数据
            system_prompt: 系统提示词，如果为None则使用默认提示词
            
        Returns:
            Tuple[bool, dict]: (是否成功, 翻译结果)
        """
        try:
            # 提取需要翻译的词条
            terms = self.extract_terms(json_data)
            if not terms:
                return False, {"error": "没有找到需要翻译的内容"}
            
            logging.info(f"共提取到 {len(terms)} 个待翻译词条")
            
            # 直接翻译所有词条
            success, result = await self.translate_batch(terms, system_prompt)
            if success:
                # 解析翻译结果
                translation_map = self.parse_translation('\n'.join(terms), result)
                
                # 应用翻译结果
                translated_data = self.apply_translations(json_data, translation_map)
                logging.info("翻译成功完成")
                return True, translated_data
            else:
                error_msg = f"翻译失败: {result}"
                logging.error(error_msg)
                return False, {"error": error_msg}
            
        except Exception as e:
            error_msg = f"翻译过程发生错误: {str(e)}"
            logging.error(error_msg)
            return False, {"error": error_msg}

    async def translate_batch(self, terms: List[str], system_prompt: str = None) -> Tuple[bool, str]:
        """翻译一批词条
        
        Args:
            terms: 待翻译的词条列表
            system_prompt: 系统提示词，如果为None则使用默认提示词
            
        Returns:
            Tuple[bool, str]: (是否成功, 翻译结果)
        """
        try:
            # 确定使用的系统提示词
            current_prompt = system_prompt if system_prompt else self.system_prompt
            
            # 打印当前使用的系统提示词
            print("\n当前使用的系统提示词:")
            print("-" * 50)
            print(current_prompt)
            print("-" * 50)
            
            # 创建流式请求
            stream = self.client.chat.completions.create(
                model=self.model_id,
                messages=[
                    {"role": "system", "content": current_prompt},
                    {"role": "user", "content": "\n".join(terms)}
                ],
                temperature=0.8,
                max_tokens=12000,
                stream=True
            )
            
            # 收集响应
            full_response = ""
            print("\n开始接收翻译响应...\n")
            
            for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    full_response += content
                    print(content, end="", flush=True)
            
            print("\n\n翻译响应接收完成\n")
            
            return True, full_response.strip()
            
        except Exception as e:
            error_msg = f"翻译请求失败: {str(e)}"
            logging.error(error_msg)
            return False, error_msg

    def extract_translatable_parts(self, original_data: dict) -> str:
        """提取需要翻译的部分并保存到临时文件"""
        translatable_parts = []
        
        for node_name, node_data in original_data.items():
            # 提取 display_name
            if "display_name" in node_data:
                translatable_parts.append(node_data["display_name"])
                
            # 提取 inputs
            if "inputs" in node_data:
                for input_key, input_value in node_data["inputs"].items():
                    if "name" in input_value:
                        translatable_parts.append(input_value["name"])

            # 提取 outputs
            if "outputs" in node_data:
                for output_key, output_value in node_data["outputs"].items():
                    if "name" in output_value:
                        translatable_parts.append(output_value["name"])

        # 去重
        translatable_parts = list(set(translatable_parts))
        
        # 保存到临时文件
        temp_file_path = "temp_translatable_parts.txt"
        with open(temp_file_path, 'w', encoding='utf-8') as f:
            for term in translatable_parts:
                f.write(f"· {term}\n")
            
        logging.info(f"提取的可翻译部分已保存到: {temp_file_path}")
        logging.info(f"提取的可翻译部分: \n" + "\n".join([f"·{term}" for term in translatable_parts]))
        return temp_file_path 

    def extract_translatable_content(self, nodeDefs_path: str) -> None:
        """从 nodeDefs.json 中提取需要翻译的内容并保存为 daifanyi.json
        
        Args:
            nodeDefs_path: nodeDefs.json 的路径
        """
        try:
            with open(nodeDefs_path, 'r', encoding='utf-8') as f:
                node_data = json.load(f)
            
            terms = set()  # 使用集合去重
            for node_name, node_info in node_data.items():
                # 提取 display_name
                if "display_name" in node_info:
                    display_name = node_info['display_name']
                    terms.add(f"{display_name} -> {display_name}")
                
                # 提取 inputs 中的 name
                if "inputs" in node_info:
                    for input_value in node_info['inputs'].values():
                        if "name" in input_value:
                            name = input_value['name']
                            terms.add(f"{name} -> {name}")
                
                # 提取 outputs 中的 name
                if "outputs" in node_info:
                    for output_value in node_info['outputs'].values():
                        if "name" in output_value:
                            name = output_value['name']
                            terms.add(f"{name} -> {name}")
            
            # 转换为列表并排序，确保输出顺序一致
            terms_list = sorted(list(terms))
            
            # 保存为 daifanyi.json
            with open("daifanyi.json", 'w', encoding='utf-8') as f:
                json.dump(terms_list, f, ensure_ascii=False, indent=2)
            
            logging.info(f"已提取 {len(terms_list)} 个待翻译词条并保存为 daifanyi.json")
            
        except Exception as e:
            logging.error(f"提取内容时出错: {str(e)}")
            raise

    def apply_translations_to_nodeDefs(self, nodeDefs_path: str) -> None:
        """将翻译结果应用到 nodeDefs.json
        
        Args:
            nodeDefs_path: nodeDefs.json 的路径
        """
        try:
            # 读取原始 nodeDefs.json
            with open(nodeDefs_path, 'r', encoding='utf-8') as f:
                node_data = json.load(f)
            
            # 读取翻译结果
            with open("yifanyi.json", 'r', encoding='utf-8') as f:
                translations = json.load(f)
            
            # 创建映射字典
            translation_map = {}
            for line in translations:
                if "->" in line:
                    original, translated = line.split("->")
                    translation_map[original.strip()] = translated.strip()
            
            # 应用翻译
            for node_name, node_info in node_data.items():
                # 更新 display_name
                if "display_name" in node_info:
                    orig = node_info["display_name"]
                    if orig in translation_map:
                        node_info["display_name"] = translation_map[orig]
                
                # 更新 inputs
                if "inputs" in node_info:
                    for input_value in node_info["inputs"].values():
                        if "name" in input_value:
                            orig = input_value["name"]
                            if orig in translation_map:
                                input_value["name"] = translation_map[orig]
                
                # 更新 outputs
                if "outputs" in node_info:
                    for output_value in node_info["outputs"].values():
                        if "name" in output_value:
                            orig = output_value["name"]
                            if orig in translation_map:
                                output_value["name"] = translation_map[orig]
            
            # 保存更新后的 nodeDefs.json
            with open(nodeDefs_path, 'w', encoding='utf-8') as f:
                json.dump(node_data, f, ensure_ascii=False, indent=2)
            
            logging.info("已将翻译结果应用到 nodeDefs.json")
            
        except Exception as e:
            logging.error(f"应用翻译结果时出错: {str(e)}")
            raise

if __name__ == '__main__':
    # 直接调用提取翻译内容的功能
    service = TranslationService(api_key='your_api_key', model_id='your_model_id')  # 替换为实际的 API Key 和模型 ID
    service.extract_translatable_content('nodeDefs.json')
"""
系统提示词文件
用于规范翻译结果
"""

import os
import logging

def load_system_prompt():
    """加载系统提示词
    
    Returns:
        str: 系统提示词内容
    """
    try:
        # 获取当前文件所在目录的绝对路径
        current_dir = os.path.dirname(os.path.abspath(__file__))
        prompt_file = os.path.join(current_dir, 'system_prompt_text.txt')
        
        with open(prompt_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        return content
            
    except Exception as e:
        logging.error(f"加载系统提示词失败: {str(e)}")
        # 返回一个基本的系统提示词作为后备
        return "你是一个专业的 ComfyUI 节点翻译专家。请将提供的节点信息从英文翻译成中文，保持 JSON 格式不变。"

# 加载系统提示词
SYSTEM_PROMPT = load_system_prompt() 
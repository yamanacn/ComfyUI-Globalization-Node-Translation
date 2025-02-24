import ast
import json
from core.node_parser import NodeParser
from core.models.node_info import NodeInfo

NODE_DISPLAY_NAME_MAPPINGS = {
    "LayerMask: HumanPartsUltra": "LayerMask: Human Parts Ultra(Advance)"
}

class NodeConverter:
    @staticmethod
    def extract_node_info(node_class, node_name):
        """提取节点信息"""
        node_info = {}

        # 显示名称
        display_name = NODE_DISPLAY_NAME_MAPPINGS.get(node_name)

        # 输入信息
        input_types = node_class.INPUT_TYPES()
        inputs = {}
        for param_name, param_info in input_types["required"].items():
            inputs[param_name] = {
                "name": param_name
            }

        # 构建节点信息字典
        node_info[node_name] = {
            "display_name": display_name,
            "inputs": inputs
        }

        return node_info

    @staticmethod
    def convert_node_info(node_class):
        """转换节点信息为指定的 JSON 结构"""
        # 暂存节点信息
        temp_node_info = NodeConverter.extract_node_info(node_class, node_class.NODE_NAME)

        # 输出信息提取
        output_names = node_class.RETURN_NAMES
        outputs = {}
        for i, output_name in enumerate(output_names):
            outputs[output_name] = {
                "name": output_name
            }

        # 生成符合要求的 JSON 格式
        result = {
            node_class.NODE_NAME: {
                "display_name": temp_node_info[node_class.NODE_NAME]["display_name"],
                "inputs": temp_node_info[node_class.NODE_NAME]["inputs"],
                "outputs": outputs
            }
        }

        return result

# 示例用法
# node_info = NodeConverter.convert_node_info(LS_HumanPartsUltra)
# print(json.dumps(node_info, ensure_ascii=False, indent=4)) 
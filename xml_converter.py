# -*- coding: UTF-8 -*-
"""
__Author__ = "MakiNaruto"
__Mail__: "become006@gamil.com"
__Created__ = "2024/02/01"
__Description__ = ""
"""

from collections import deque
from xml.dom.minidom import Element

from config.js_format import JsConfig
from xml_operation import get_children


def converter(code_type='js'):
    if code_type.lower() in ['js', 'javascript']:
        config = JsConfig
    else:
        raise Exception('未完成该类型的代码转换')

    class XmlConverter(config):
        def __init__(self):
            super().__init__()

        def format_node(self, node: Element):
            node_type = node.getAttribute('node_type')
            format_type = node.getAttribute('function_type')
            if node_type == 'list':
                son_nodes = get_children(node)
                if node.nodeName == 'params':
                    new_son_nodes = []
                    for index, son_node in enumerate(son_nodes):
                        new_son_nodes.append(son_node)
                        if index < len(son_nodes) - 1:
                            new_son_nodes.append(',')
                    son_nodes = ['('] + new_son_nodes + [')']
            else:
                if format_type.endswith('Declaration'):
                    parser = self.declaration
                elif format_type.endswith('Expression'):
                    parser = self.expression
                elif format_type.endswith('Statement'):
                    parser = self.statement
                else:
                    parser = self.other
                son_nodes = parser.get_sub_children(node, format_type)
            return son_nodes

        def tree_node_convert_code(self, node: Element):
            task_queue = deque([node])
            code = ""

            while task_queue:
                node = task_queue.popleft()

                if isinstance(node, str):
                    code += node
                else:
                    children = self.format_node(node)
                    children.reverse()
                    task_queue.extendleft(children)

            return code

    return XmlConverter()

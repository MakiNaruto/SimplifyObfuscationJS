# -*- coding: UTF-8 -*-
"""
__Author__ = "MakiNaruto"
__Mail__: "become006@gamil.com"
__Created__ = "2024/02/01"
__Description__ = ""
"""

from typing import Union
from collections import deque

from config.js_format import JsConfig
from xml_operation import (get_single_node_by_path,
                           get_node_value,
                           get_node_by_path,
                           get_children)


def converter(code_type='js'):
    if code_type.lower() in ['js', 'javascript']:
        Config = JsConfig
    else:
        raise Exception('未完成该类型的代码转换')

    class XmlConverter(Config):
        def __init__(self):
            super().__init__()

        def format_node(self, node):
            node_type = node.getAttribute('node_type')
            format_type = node.getAttribute('function_type')
            if node_type == 'list':
                son_nodes = get_children(node)
            else:
                if format_type.endswith('Declaration'):
                    path = self.declaration.get_path(node, format_type)
                elif format_type.endswith('Expression'):
                    path = self.expression.get_path(node, format_type)
                elif format_type.endswith('Statement'):
                    path = self.statement.get_path(node, format_type)
                else:
                    path = self.statement.get_path(node, format_type)

                son_nodes = self.expand_expression_with_path(node, path)
            return son_nodes

        def expand_expression_with_path(self, node, path_template: Union[list[str], str]):
            """
            @param node: 节点
            @param path_template: 节点
            @return:
            """
            assert isinstance(path_template, (list, str)), "预期外的数据类型"
            if isinstance(path_template, str):
                expand_nodes = get_single_node_by_path(node, f'{node.nodeName}{path_template}')
            else:
                expand_nodes = []
                for node_path in path_template:
                    if node_path.startswith('/'):
                        sub_node = get_single_node_by_path(node, f'{node.nodeName}{node_path}')
                    else:
                        sub_node = node_path
                    expand_nodes.append(sub_node)

            return expand_nodes

        def expand_expression_list_format(self, node_list, insert_model, insert_sequence='head',
                                          fill_str=None, template=None, skip_head=0, skip_tail=0):
            """
            @param node_list: 要进行格式化整理的节点列表
            @param insert_model: 格式化模式: mid | template
            @param insert_sequence: 插入方式, 从头向尾插入还是从尾向头插入: head | tail
            @param fill_str: 处于 mid_insert 格式化模式下的填充类型
            @param template: 按照模板格式进行填充
            @param skip_head: 跳过开头n个元素插入
            @param skip_tail: 跳过结尾n个元素插入
            @return: 格式化后的list信息

            """
            assert insert_model in ['head', 'tail'], '非预期的插入模式'
            if insert_model == 'mid':
                for i in range(len(node_list) - skip_tail, skip_head - 1, -1):
                    node_list.insert(i, fill_str)

            elif insert_model == 'template':
                assert template, '传入的自定义格式化信息为空'
                assert isinstance(template, list), '数据格式非期待的list类型'
                assert len(template) <= (len(node_list) + 1 - skip_head - skip_tail), '插入模板长度超出范围或移动头尾导致无法插入'
                assert insert_model in ['head', 'tail'], '非预期的插入模式'
                node_list_index = len(node_list)
                template_index = 1
                if insert_sequence == 'head':
                    skip_tail = len(node_list) - skip_head - len(template) + 1

                while template_index <= len(template) and node_list_index >= 0:
                    node_list.insert(node_list_index - skip_tail, template[-template_index])
                    template_index += 1
                    node_list_index -= 1
            return node_list

        def single_node_convert_code(self, node):
            if not node:
                return ''
            if isinstance(node, str):
                return node
            # if node.nodeName in ['left', 'right', 'object', 'property', 'argument']:
            leaf_type_nodes = get_node_by_path(node, f'{node.nodeName}/type')
            if len(leaf_type_nodes) == 1:
                type_node = leaf_type_nodes[0]
                type_text_node = get_single_node_by_path(type_node, f'{type_node.nodeName}/#text', return_value=True)
                if type_text_node == 'Identifier':
                    leaf = get_single_node_by_path(node, f'{node.nodeName}/name/#text', return_value=True)
                    return leaf
                if type_text_node in ['Literal', 'NumericLiteral']:
                    leaf = get_single_node_by_path(node, f'{node.nodeName}/value/#text', return_value=True)
                    return leaf
            elif len(node.childNodes) == 1:
                leaf_node = node.childNodes[0]
                return get_node_value(leaf_node)

        def tree_node_convert_code(self, node):
            task_queue = deque([node])
            code = ""

            while task_queue:
                node = task_queue.popleft()
                if not node:
                    continue
                res = self.single_node_convert_code(node)
                if not res:
                    children = self.format_node(node)
                    children.reverse()
                    task_queue.extendleft(children)
                else:
                    code += res
            return code
    return XmlConverter()

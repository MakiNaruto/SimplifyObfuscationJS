# -*- coding: UTF-8 -*-
"""
__Author__ = "MakiNaruto"
__Mail__: "become006@gamil.com"
__Created__ = "2024/04/18"
__Description__ = "转换为代码所需的配置文件模板"
"""

import re
from xml_operation import *


class NodeGetter:
    def get_path(self, node: Element, function_name, path_name: str):
        param = {"node": node, "path_name": path_name}
        model, path = eval(f"self.{function_name}(**param)")
        return path

    def get_sub_children(self, node: Element, path_name: str):
        expand_nodes = []

        if is_leaf(node):
            sub_node = get_single_node_by_path(node, f'{node.nodeName}/#text', return_value=True)
            expand_nodes.append(sub_node)
            return expand_nodes

        function_name = re.sub('Declaration$|Expression$|Statement$', '', path_name).lower()
        function_name += '_format'
        path_template = self.get_path(node, function_name, path_name)
        for node_path in path_template:
            # 路径信息均以 / 开头
            if node_path.startswith('/'):
                sub_node = get_single_node_by_path(node, f'{node.nodeName}{node_path}')
                param = {"get_child": True, "node": sub_node, "path_name": node_path}
                is_path_template, children = eval(f"self.{function_name}(**param)")
                if is_path_template:
                    expand_nodes.append(sub_node)
                else:
                    expand_nodes.extend(children)
            else:
                expand_nodes.append(node_path)
        if is_parenthesized(node):
            expand_nodes = ['('] + expand_nodes + [')']
        return expand_nodes

    def expand_expression_list_format(self, node_list: List[Element], insert_model: str, insert_sequence: str = 'head',
                                      fill_str: str = None, template: List[str] = None, skip_head=0, skip_tail=0):
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
        if not fill_str:
            fill_str = ''
        if insert_model == 'mid':
            for i in range(len(node_list) - skip_tail, skip_head - 1, -1):
                node_list.insert(i, fill_str)
        elif insert_model == 'template':
            assert insert_sequence in ['head', 'tail'], '非预期的插入模式'
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


class BaseDeclaration(NodeGetter):
    def function_format(self, *args, **kwargs):
        return True, ['function ', '/id', '()', '/body']


class BaseExpression(NodeGetter):
    def array_format(self, *args, **kwargs):
        return True, ['[', '/elements', ']']

    def assignment_format(self, *args, **kwargs):
        return True, ['/left', ' ', '/operator', ' ', '/right']

    def binary_format(self, *args, **kwargs):
        return True, ['/left', ' ', '/operator', ' ', '/right']

    def logical_format(self, *args, **kwargs):
        return True, ['/left', ' ', '/operator', ' ', '/right']

    def conditional_format(self, *args, **kwargs):
        return True, ['/test', ' ? ', '/consequent', ' : ', '/alternate']

    def sequence_format(self, *args, **kwargs):
        # 获取转换模板格式
        if kwargs.get('get_child'):
            # 获取孩子节点并进行优化
            node: Element = kwargs.get('node')
            path_name = kwargs.get('path_name')
            children = node.childNodes
            if path_name == '/expressions':
                self.expand_expression_list_format(children, insert_model='mid', fill_str=', ', skip_head=1, skip_tail=1)
                return False, children
        return True, ['/expressions']

    def unary_format(self, *args, **kwargs):
        return True, ['/operator', '/argument']

    def update_format(self, *args, **kwargs):
        return True, ['/operator', ' ', '/argument']

    def function_format(self, *args, **kwargs):
        return True, ['function()', '/body']

    def member_format(self, *args, **kwargs):
        node: Element = kwargs.get('node')
        condition_path = '/computed/#text'
        condition = 'str({}) == "True"'
        node_condition_value = get_single_node_by_path(node, f'{node.nodeName}{condition_path}', return_value=True)
        if eval(condition.format(node_condition_value)):
            path = ['/object', '[', '/property', ']']
        else:
            path = ['/object', '.', '/property']
        return True, path


class BaseStatement(NodeGetter):
    def block_format(self, *args, **kwargs):
        # 获取转换模板格式
        if kwargs.get('get_child'):
            # 获取孩子节点并进行优化
            node: Element = kwargs.get('node')
            path_name = kwargs.get('path_name')
            children = node.childNodes
            if path_name == '/body':
                self.expand_expression_list_format(children, insert_model='mid', fill_str=';', skip_head=1, skip_tail=1)
                return False, children
        return True, ['{', '/body', '}']

    def if_format(self, *args, **kwargs):
        node: Element = kwargs.get('node')
        condition_path = '/alternate'
        node_condition_value = get_single_node_by_path(node, f'{node.nodeName}{condition_path}')
        if node_condition_value:
            path = ['if(', '/test', '){', '/consequent', '}']
        else:
            path = ['if(', '/test', '){', '/consequent', '}', 'else{', '/alternate', '}']
        return True, path

    def expression_format(self, *args, **kwargs):
        return True, ['/expression']


class BaseOther(NodeGetter):
    def identifier_format(self, *args, **kwargs):
        return True, ['/name']

    def literal_format(self, *args, **kwargs):
        return True, ['/value']

    def numericliteral_format(self, *args, **kwargs):
        return True, ['/value']

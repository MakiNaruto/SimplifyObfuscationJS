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


class BaseDeclaration(NodeGetter):
    def function_format(self, *args, **kwargs):
        return True, ['function ', '/id', '()', '/body']


class BaseExpression(NodeGetter):
    def array_format(self, *args, **kwargs):
        return True, ['[', '/elements', ']']

    def arrowfunction_format(self, *args, **kwargs):
        return True, ['/params', '=>', '/body']

    def assignment_format(self, *args, **kwargs):
        return True, ['/left', ' ', '/operator', ' ', '/right']

    def binary_format(self, *args, **kwargs):
        return True, ['/left', ' ', '/operator', ' ', '/right']

    def call_format(self, *args, **kwargs):
        return True, ['/callee', '(', '/arguments', ')']

    def class_format(self, *args, **kwargs):
        return True, ['class', '/id', '{', '/body', '}']

    def conditional_format(self, *args, **kwargs):
        return True, ['/test', ' ? ', '/consequent', ' : ', '/alternate']

    def function_format(self, *args, **kwargs):
        return True, ['function()', '/body']

    def logical_format(self, *args, **kwargs):
        return True, ['/left', ' ', '/operator', ' ', '/right']

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

    def new_format(self, *args, **kwargs):
        return True, ['new ', '/callee', '(', '/arguments', ')']

    def object_format(self, *args, **kwargs):
        return True, ['/properties']

    def sequence_format(self, *args, **kwargs):
        # 获取转换模板格式
        if kwargs.get('get_child'):
            # 获取孩子节点并进行优化
            node: Element = kwargs.get('node')
            path_name = kwargs.get('path_name')
            children = node.childNodes
            if path_name == '/expressions':
                format_children = expand_expression_list_format(children, insert_model='mid', fill_info=', ')
                return False, format_children
        return True, ['/expressions']

    def tagged_template_format(self, *args, **kwargs):
        return True, ['/tag', '`', '/quasi', '`']

    def this_format(self, *args, **kwargs):
        return True, ['this']

    def unary_format(self, *args, **kwargs):
        return True, ['/operator', '/argument']

    def update_format(self, *args, **kwargs):
        return True, ['/operator', ' ', '/argument']

    def yield_format(self, *args, **kwargs):
        return True, ['yield', ' ', '/argument']


class BaseStatement(NodeGetter):
    def block_format(self, *args, **kwargs):
        # 获取转换模板格式
        if kwargs.get('get_child'):
            # 获取孩子节点并进行优化
            node: Element = kwargs.get('node')
            path_name = kwargs.get('path_name')
            children = node.childNodes
            if path_name == '/body':
                format_children = expand_expression_list_format(children, insert_model='mid', fill_info=';')
                return False, format_children
        return True, ['{', '/body', '}']

    def break_format(self, *args, **kwargs):
        return True, ['break']

    def continue_format(self, *args, **kwargs):
        return True, ['continue']

    def debugger_format(self, *args, **kwargs):
        return True, ['debugger']

    def dowhile_format(self, *args, **kwargs):
        return True, ['do {', '/body', '} while(', '/test', ')']

    def expression_format(self, *args, **kwargs):
        return True, ['/expression']

    def forin_format(self, *args, **kwargs):
        return True, ['for (', '/left', ' in ', '/right', ')', '{', '/body', '}']

    def forof_format(self, *args, **kwargs):
        return True, ['for (', '/left', ' in ', '/right', ')', '{', '/body', '}']

    def for_format(self, *args, **kwargs):
        return True, ['for (', '/init', ';', '/test', ';', '/update', ')', '{', '/body', '}']

    def if_format(self, *args, **kwargs):
        node: Element = kwargs.get('node')
        condition_path = '/alternate'
        node_condition_value = get_single_node_by_path(node, f'{node.nodeName}{condition_path}')
        if node_condition_value:
            path = ['if(', '/test', '){', '/consequent', '}']
        else:
            path = ['if(', '/test', '){', '/consequent', '}', 'else{', '/alternate', '}']
        return True, path

    def labeled_format(self, *args, **kwargs):
        return True, ['label', ': ', '/body']

    def return_format(self, *args, **kwargs):
        return True, ['return ', '/argument']

    def switch_format(self, *args, **kwargs):
        return True, ['switch(', '/discriminant', ')', '{', '/cases', '}']

    def throw_format(self, *args, **kwargs):
        return True, ['throw  ', '/argument']

    def try_format(self, *args, **kwargs):
        return True, ['try ', '/block ', '/handler']


class BaseOther(NodeGetter):
    def classbody_format(self, *args, **kwargs):
        return True, ['/body']

    def identifier_format(self, *args, **kwargs):
        return True, ['/name']

    def literal_format(self, *args, **kwargs):
        return True, ['/value']

    def numericliteral_format(self, *args, **kwargs):
        return True, ['/value']

    def property_format(self, *args, **kwargs):
        return True, ['/key', ':', '/value']

    def templateliteral_format(self, *args, **kwargs):
        return True, ['/expression', '/quasis']

    def switchcase_format(self, *args, **kwargs):
        return True, ['case: ', '/test', '/consequent']

    def stringliteral_format(self, *args, **kwargs):
        return True, ['/value']

    def catchclause_format(self, *args, **kwargs):
        return True, ['catch(', '/param', ')', '/body']
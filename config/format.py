# -*- coding: UTF-8 -*-
"""
__Author__ = "MakiNaruto"
__Mail__: "become006@gamil.com"
__Created__ = "2024/04/18"
__Description__ = "转换为代码所需的配置文件模板"
"""


from xml_operation import *


class BaseDeclaration:
    def get_path(self, node, path_name: str):
        inner_func = path_name.replace('Declaration', '_format').lower()
        param = {"node": node, "path_name": path_name}
        path = eval(f"self.{inner_func}(**param)")
        return path

    def function_format(self, *args, **kwargs):
        return ['function ', '/id', '()', '/body']


class BaseExpression:
    def get_path(self, node, path_name: str):
        inner_func = path_name.replace('Expression', '_format').lower()
        param = {"node": node, "path_name": path_name}
        path = eval(f"self.{inner_func}(**param)")
        return path

    def array_format(self, *args, **kwargs):
        return ['[', '/elements', ']']

    def assignment_format(self, *args, **kwargs):
        return ['/left', ' ', '/operator', ' ', '/right']

    def binary_format(self, *args, **kwargs):
        return ['/left', ' ', '/operator', ' ', '/right']

    def logical_format(self, *args, **kwargs):
        return ['/left', ' ', '/operator', ' ', '/right']

    def conditional_format(self, *args, **kwargs):
        return ['/test', ' ? ', '/consequent', ' : ', '/alternate']

    def sequence_format(self, *args, **kwargs):
        return ['/expressions']

    def unary_format(self, *args, **kwargs):
        return ['/operator', '/argument']

    def update_format(self, *args, **kwargs):
        return ['/operator', ' ', '/argument']

    def function_format(self, *args, **kwargs):
        return ['function()', '/body']

    def member_format(self, *args, **kwargs):
        node = kwargs.get('node')
        condition_path = '/computed/#text'
        condition = 'str({}) == "True"'
        node_condition_value = get_single_node_by_path(node, f'{node.nodeName}{condition_path}', return_value=True)
        if eval(condition.format(node_condition_value)):
            path = ['/object', '[', '/property', ']']
        else:
            path = ['/object', '.', '/property']
        return path


class BaseStatement:
    def get_path(self, node, path_name: str):
        inner_func = path_name.replace('Statement', '_format').lower()
        param = {"node": node, "path_name": path_name}
        path = eval(f"self.{inner_func}(**param)")
        return path

    def block_format(self, *args, **kwargs):
        return ['{', '/body', '}']

    def if_format(self, *args, **kwargs):
        node = kwargs.get('node')
        condition_path = '/alternate'
        node_condition_value = get_single_node_by_path(node, f'{node.nodeName}{condition_path}')
        if node_condition_value:
            path = ['if(', '/test', '){', '/consequent', '}']
        else:
            path = ['if(', '/test', '){', '/consequent', '}', 'else{', '/alternate', '}']
        return path

    def expression_format(self, *args, **kwargs):
        return ['/expression']


class BaseOther:
    def get_path(self, node, path_name: str):
        inner_func = f'{path_name}_format'.lower()
        param = {"node": node, "path_name": path_name}
        path = eval(f"self.{inner_func}(**param)")
        return path

    def identifier_format(self, *args, **kwargs):
        return '/name'

    def literal_format(self, *args, **kwargs):
        return '/value'

    def numericliteral_format(self, *args, **kwargs):
        return '/value'

# -*- coding: UTF-8 -*-
"""
__Author__ = "MakiNaruto"
__Mail__: "become006@gamil.com"
__Created__ = "2024/04/18"
__Description__ = "转换为代码所需的配置文件模板"
"""


from xml_operation import *


class Declaration:
    def get_path(self, node, path_name: str):
        inner_func = path_name.replace('Declaration', '_format').lower()
        path = eval(f"self.{inner_func}(node={node}, path_name='{path_name}')")
        return path


class Expression:
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
        return ['/operator', ' ', '/argument']

    def update_format(self, *args, **kwargs):
        return ['/operator', ' ', '/argument']

    def function_format(self, *args, **kwargs):
        return '/body'

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


class Statement:
    def get_path(self, node, path_name: str):
        inner_func = path_name.replace('Statement', '_format').lower()
        path = eval(f"self.{inner_func}(node=node, path_name=path_name)")
        return path

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


class Other:
    def get_path(self, node, path_name: str):
        inner_func = path_name.replace('Other', '_format').lower()
        path = eval(f"self.{inner_func}(node={node}, path_name='{path_name}')")
        return path

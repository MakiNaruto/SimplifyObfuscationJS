# -*- coding: UTF-8 -*-
"""
__Author__ = "MakiNaruto"
__Mail__: "become006@gamil.com"
__Created__ = "2024/02/01"
__Description__ = "单元测试"
"""

from code_convert import *
from unittest import TestCase
from xml_converter import converter
from xml_operation import search_node_by_attribute, assignment_conditional_convert, get_single_node_by_path


def code_converter(code):
    code = format_javascript_code(code)
    code = code.replace('\\', '#-#')

    ast = javascript_to_json(code, convert_method='nodejs', node_path='/usr/local/bin/node')
    xml_tree = json_to_xml(ast)
    json_out_put = xml_to_json(xml_tree)
    return ast, json_out_put, xml_tree


class Test(TestCase):
    def test_xml_convert_checker(self):
        """ xml转换为json结构完整性测试 """
        with open('files/fireyejs.js', 'r') as fr:
            javascript_code = fr.read()
        ast, json_out_put, xml_tree = code_converter(javascript_code)
        json_out_put = deep_sort_json(json_out_put)
        ast = deep_sort_json(ast)
        self.assertEqual(json_out_put, ast)

    def test_trans_assignment_bottom(self):
        """ 三目表达式赋值到底层测试 """
        javascript_code = 'r = a < 1 ? W < N.length ? 128 : 3 : D < T.length ? 9 : 12'
        target_code = 'a < 1 ? W < N.length ? r = 128 : r = 3 : D < T.length ? r = 9 : r = 12'
        _, _, xml_tree = code_converter(javascript_code)
        # 单元测试 3
        root = xml_tree.documentElement
        assignment_conditional_convert(root)
        ce_node = search_node_by_attribute(root, search_list=['ConditionalExpression'], attribute_name='function_type')[0]
        conv = converter()
        res = conv.tree_node_convert_code(ce_node)
        self.assertEqual(res, target_code)

    def test_recover(self):
        """ 代码转换为树结构后, 还原回代码形式的完整性测试 """
        conv = converter()
        javascript_code_list = ['void (13 == St)', '!function() {a,b,c}', 'function e() {a,b,c}', '!function() {a;b;c;!function() {d;e;f}}']
        for javascript_code in javascript_code_list:
            _, _, xml_tree = code_converter(javascript_code)
            root = xml_tree.documentElement
            all_nodes = get_single_node_by_path(root, f'{root.nodeName}/program/body').childNodes
            for node in all_nodes:
                conv_res = conv.tree_node_convert_code(node)
                self.assertEqual(conv_res.replace(' ', ''), javascript_code.replace(' ', ''))


if __name__ == '__main__':
    pass

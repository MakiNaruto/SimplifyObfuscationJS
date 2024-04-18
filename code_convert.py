# -*- coding: UTF-8 -*-
"""
__Author__ = "MakiNaruto"
__Mail__: "become006@gamil.com"
__Created__ = "2024/02/01"
__Description__ = "js代码 在 ast、json、xml之间的相互转换"
"""


import re
import json
import subprocess
import pyjsparser
from typing import Any
from copy import deepcopy
from xml.dom import minidom
import xml.etree.ElementTree as ET


def json_to_etree(dict_info: dict):
    """
    将json对象转换为xml结构中的etree树。
    @param dict_info: 字典结构
    """
    function_types = {
                        'ArrayExpression', 'ArrowFunctionExpression', 'AssignmentExpression', 'BinaryExpression',
                        'CallExpression', 'ClassExpression', 'ConditionalExpression', 'FunctionExpression', 'LogicalExpression',
                        'MemberExpression', 'NewExpression', 'ObjectExpression', 'SequenceExpression',
                        'TaggedTemplateExpression', 'ThisExpression', 'UnaryExpression', 'UpdateExpression', 'YieldExpression',

                        'BlockStatement', 'BreakStatement', 'ContinueStatement', 'DebuggerStatement',
                        'DoWhileStatement', 'EmptyStatement', 'ExpressionStatement', 'ForInStatement',
                        'ForOfStatement', 'ForStatement', 'FunctionDeclaration', 'IfStatement', 'LabeledStatement',
                        'ReturnStatement', 'SwitchStatement', 'ThrowStatement', 'TryStatement',
                        'WhileStatement', 'WithStatement',

                        'ClassDeclaration', 'Declaration', 'ExportAllDeclaration', 'ExportDeclaration',
                        'ExportDefaultDeclaration', 'ExportNamedDeclaration', 'FunctionDeclaration', 'ImportDeclaration', 'VariableDeclaration',

                        'Literal', 'Super', 'Identifier', 'ImportSpecifier', 'Program', 'MetaProperty',
                        'Statement', 'StatementListItem', 'AssignmentPattern', 'BindingPattern'
                    }

    root = ET.Element('root')
    stack = [[root, dict_info, None]]
    while stack:
        node, traversal_value, father_node = stack.pop()

        node.set("node_type", type(traversal_value).__name__)

        if isinstance(traversal_value, str):
            if not traversal_value:
                traversal_value = 'None-Str'
            if traversal_value in function_types:
                father_node.set("function_type", traversal_value)
            node.text = traversal_value
        elif isinstance(traversal_value, dict):
            for key, info in traversal_value.items():
                sub_node = ET.Element(key)
                sub_node.set("node_type", type(info).__name__)
                node.append(sub_node)
                stack.append([sub_node, info, node])
        elif isinstance(traversal_value, list):
            if not traversal_value:
                node.text = str(traversal_value)
            else:
                for info in traversal_value:
                    sub_node = ET.Element('sub_node')
                    sub_node.set("node_type", type(info).__name__)
                    node.append(sub_node)
                    stack.append([sub_node, info, node])
        else:
            node.text = str(traversal_value)
            if node.text.endswith('.0'):
                node.text = node.text[:-2]
                node.set("node_type", 'int')

    return root


def xml_to_json(root) -> dict:
    """
    将xml转换为json格式
    @param root: minidom解析的树结构
    """
    all_dict = {}
    stack = [[node, all_dict] for node in root.documentElement.childNodes]

    while stack:
        node, current_dict = stack.pop()

        if node.hasChildNodes():
            sub_dict, is_text_node = update_json_tree(node, current_dict)
            if not is_text_node:
                stack.extend([[sub_node, sub_dict] for sub_node in node.childNodes])
        else:
            if node.nodeType == 3:
                if isinstance(current_dict, dict):
                    if node.nodeValue:
                        current_dict.update({node.nodeName: node.nodeValue})
                    else:
                        current_dict.update({node.nodeName: ""})
            else:
                current_dict.update({node.nodeName: node.nodeValue})

    return all_dict


def javascript_to_xml(js_code: str, write_file: str = '', convert_method='nodejs', node_path='') -> tuple[Any, Any]:
    """
    将js代码转换为xml文件
    @param node_path:
    @param convert_method: js转ast的方式, [nodejs | pyjsparser]。
    @param js_code: js代码
    @param write_file: 生成的xml内容写入到指定的文件中。
    """
    if convert_method == 'nodejs':
        # ` 符号在转换中会出现异常, 进行替换处理
        js_code = re.sub('`', '#--', js_code)
        js_exec = f"""
        const parser = require('@babel/parser');

        const code = `{js_code}`;
        const ast = parser.parse(code, {{
            sourceType: 'module',
        }});

        const astJson = JSON.stringify(ast, (key, value) => {{
            if (key === 'start' || key === 'end' || key === 'loc') {{
                return undefined;
            }}
            return value;
        }}, 2);
        console.log(astJson);
        """

        result = subprocess.run([node_path, '-e', js_exec], capture_output=True, text=True)

        ast_json = result.stdout.strip()
        ast_json = json.loads(ast_json)
    else:
        ast_json = pyjsparser.parse(js_code)

    convert_xml_tree = json_to_etree(deepcopy(ast_json))
    convert_xml_tree = ET.ElementTree(convert_xml_tree)
    xml_string = minidom.parseString(ET.tostring(convert_xml_tree.getroot(), encoding='unicode'))
    if write_file:
        with open(write_file, 'w') as fw:
            fw.write(xml_string.toprettyxml(indent="  "))
    return ast_json, xml_string


def update_json_tree(node, json_node: dict) -> tuple[Any, bool]:
    """
    xml 转换为 json时, 帮助生成子树结构的方式
    @param node: 要转换为json的根节点
    @param json_node: 要更新内容的json节点信息。
    """
    text_node = False
    if node.getAttribute('node_type') == 'list':
        current_node_value = []
    elif node.getAttribute('node_type') == 'dict':
        current_node_value = {}
    else:
        current_node_value = node.childNodes[0].data

        if current_node_value == 'False':
            current_node_value = False
        if current_node_value == 'True':
            current_node_value = True
        if current_node_value == 'None':
            current_node_value = None
        if current_node_value == 'None-Str':
            current_node_value = ""

        if node.getAttribute('node_type') in {'bool', 'int', 'float', 'list', 'tuple'}:
            current_node_value = eval(node.childNodes[0].data)

        text_node = True

    if isinstance(json_node, list):
        if node.nodeName == 'sub_node':
            json_node.append({})
        else:
            json_node.append({node.nodeName: current_node_value})
        json_data = json_node[-1]
    else:
        json_node.update({node.nodeName: current_node_value})
        json_data = json_node[node.nodeName]

    return json_data, text_node


def deep_sort_json(obj: dict):
    """
    将json对象进行全层级排序。
    @param obj:
    """
    if isinstance(obj, dict):
        # 如果是字典，递归地对字典的键进行排序
        sorted_dict = {}
        for key in sorted(obj.keys()):
            sorted_dict[key] = deep_sort_json(obj[key])
        return sorted_dict
    elif isinstance(obj, list):
        # 如果是列表，先将列表内容以字符串形式排序，再递归排序
        sorted_list = sorted(obj, key=str)
        sorted_list = [deep_sort_json(item) for item in sorted_list]
        sorted_list = sorted(sorted_list, key=str)
        return sorted_list
    elif isinstance(obj, tuple):
        # 如果是列表，先将列表内容以字符串形式排序，再递归排序
        sorted_list = sorted(obj, key=str)
        sorted_list = tuple([deep_sort_json(item) for item in sorted_list])
        sorted_list = sorted(sorted_list, key=str)
        sorted_list = tuple(sorted_list)
        return sorted_list
    else:
        # 如果是其他类型，直接返回
        return obj


def format_javascript_code(input_string: str) -> str:
    """
    将js代码内部的 \\u \\x 信息进行特殊处理。
    @param input_string:
    """
    decoded_string = re.sub('\\\\u', lambda x: x.group().replace('\\u', '#$$#u'), input_string)
    decoded_string = re.sub('\\\\x', lambda x: x.group().replace('\\x', '#$$#x'), decoded_string)
    return decoded_string


def verify_json_consistency(json1: dict, json2: dict, show_diff=False, shift_range=100) -> bool:
    """
    校验两个无序json是否完全一致。
    @param json1: 用于对比的json1
    @param json2: 用于对比的json2
    @param show_diff: 若两边结果不一致，则将不同的地方结果打印。
    @param shift_range: 若对比的两个json不同，则展示不同处的地方左右范围。
    """
    json1 = deep_sort_json(json1)
    json2 = deep_sort_json(json2)

    if show_diff:
        json_1 = json.dumps(json1, ensure_ascii=False).replace('\n', '')
        json_2 = json.dumps(json2, ensure_ascii=False).replace('\n', '')

        index = 0
        while json_1[index] == json_2[index]:
            index += 1

        print(json_1[index - shift_range: index + shift_range])
        print(json_2[index - shift_range: index + shift_range])

    return json1 == json2

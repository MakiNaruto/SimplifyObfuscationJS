# -*- coding: UTF-8 -*-
"""
__Author__ = "MakiNaruto"
__Mail__: "become006@gamil.com"
__Created__ = "2024/02/01"
__Description__ = "xml 节点树的处理方法"
"""

from copy import deepcopy
from collections import deque
from xml.dom.minidom import Element
from typing import List, Set, Union
from xml.dom.minidom import Document


def get_node_by_path(node: Element, path: str) -> List[Element]:
    """
    对当前的节点进行路径查找, 通过指定路径进行子树的搜索。
    @param node: minidom解析的树型节点。
    @param path: 节点的完整路径，以'/'分割，如 'path/to/.../target_node'
    """
    stack = [[node, deque(path.split('/'))]]
    res = []
    while stack:
        curr_node, path_list = stack.pop()
        if not path_list:
            continue
        current_path = path_list.popleft()
        if curr_node.nodeName == current_path:
            if not path_list:
                res.append(curr_node)
            for sub_node in curr_node.childNodes:
                stack.append([sub_node, deepcopy(path_list)])
    return res


def get_single_node_by_path(node: Element, path: str, return_value: bool = False) -> Union[str, Element]:
    nodes = get_node_by_path(node, path)
    if len(nodes) == 1:
        leaf = nodes[0]
        if return_value:
            leaf_value = get_node_value(leaf)
            return leaf_value
        else:
            return leaf


def get_children(node: Element) -> List[Element]:
    """获取除叶子节外点的子节点"""
    nodes = list()
    for child in node.childNodes:
        if child.nodeType not in [3, 4, 10, 12]:
            nodes.append(child)
    return nodes


def get_node_children_tags(node: Element) -> Set[str]:
    """ 获取节点所有的儿子节点标签名称。 """
    return {sub_node.nodeName for sub_node in get_children(node)}


def get_node_value(node: Element) -> str:
    """ 获取节点存储的文本值 """
    leaf_node = [3, 4, 10, 12]
    if node.nodeType in leaf_node:
        return node.nodeValue


def is_leaf(node: Element) -> bool:
    res = get_single_node_by_path(node, f'{node.nodeName}/#text', return_value=True)
    return True if res else False


def is_parenthesized(node: Element) -> bool:
    res = get_single_node_by_path(node, f'{node.nodeName}/extra/parenthesized/#text', return_value=True)
    return True if res == 'True' else False


def search_node_by_name(node: Element, search_list: list) -> List[Element]:
    """
    深度搜索获取特定节点类型的节点。
    @param node: minidom解析的树型根节点。
    @param search_list: 搜索节点或属性名称
    """
    search_result = []
    q = [node]
    while len(q):
        sub_node = q.pop(0)
        if sub_node.nodeName in search_list:
            search_result.append(sub_node)
        else:
            for child in get_children(sub_node):
                q.append(child)
    return search_result


def search_node_by_attribute(node: Element, search_list: list, attribute_name: str = None) -> List[Element]:
    """
    深度搜索获取特定节点类型的节点。
    @param node: minidom解析的树型根节点。
    @param search_list: 搜索节点或属性名称
    @param attribute_name: 搜索的属性名称
    """
    search_result = []
    q = [node]
    while len(q):
        sub_node = q.pop(0)
        if sub_node.getAttribute(attribute_name) in search_list:
            search_result.append(sub_node)
        else:
            for child in get_children(sub_node):
                q.append(child)
    return search_result


def replace_clone_node(parent_node: Element, new_node: Element, old_node: Element) -> Element:
    """
    将当前节点的孩子节点进行替换
    @param parent_node: 当前操作节点
    @param new_node: 用于替换的节点
    @param old_node: 将被替换的旧节点
    """
    new_node.nodeName = old_node.nodeName
    ori_node = parent_node.cloneNode(deep=True)
    old_node = get_single_node_by_path(ori_node, f'{ori_node.nodeName}/{old_node.nodeName}')
    new_node = new_node.cloneNode(deep=True)
    new_node.nodeName = old_node.nodeName
    ori_node.replaceChild(new_node, old_node)
    return ori_node


def single_level_assignment_conditional_convert(assignment_node: Element) -> List[Element]:
    """
        转换赋值类型的三目表达式, 将赋值内容向下一层级转移例如:

        原格式: r = a < 1 ? W < N.length ? 128 : 3 : D < T.length ? 9 : 12

        转换后: a < 1 ? r = W < N.length ? 128 : 3 : r = D < T.length ? 9 : 12

    """
    ae_parent_node = assignment_node.parentNode
    ae_node = assignment_node

    ce_node = get_single_node_by_path(ae_node, f'{ae_node.nodeName}/right')
    ce_consequent = get_single_node_by_path(ce_node, f'{ce_node.nodeName}/consequent')
    ce_alternate = get_single_node_by_path(ce_node, f'{ce_node.nodeName}/alternate')

    if ce_consequent and ce_alternate:
        new_ae_replace_left = replace_clone_node(ae_node, ce_consequent, ce_node)
        new_ae_replace_right = replace_clone_node(ae_node, ce_alternate, ce_node)

        new_ae_replace_left.nodeName = 'consequent'
        new_ae_replace_right.nodeName = 'alternate'
        ce_node.replaceChild(new_ae_replace_left, ce_consequent)
        ce_node.replaceChild(new_ae_replace_right, ce_alternate)
        ce_node.nodeName = ae_node.nodeName

        ae_parent_node.replaceChild(ce_node, ae_node)
        sub_ae_nodes = get_node_by_path(ae_parent_node, f'{ae_parent_node.nodeName}/{ce_node.nodeName}')
        return sub_ae_nodes


def assignment_conditional_convert(root: Element):
    """
        转换赋值类型的三目表达式, 将赋值内容向下转移, 直至底层。例如:

        原格式: r = a < 1 ? W < N.length ? 128 : 3 : D < T.length ? 9 : 12

        转换后: a < 1 ? W < N.length ? r = 128 : r = 3 : D < T.length ? r = 9 : r = 12

    """
    task_queue = search_node_by_attribute(root, search_list=['AssignmentExpression'], attribute_name='function_type')
    while task_queue:
        ce_node = task_queue.pop()
        sub_ae_nodes = single_level_assignment_conditional_convert(ce_node)
        if not sub_ae_nodes:
            continue
        for ae_node in sub_ae_nodes:
            sub_task = search_node_by_attribute(ae_node, search_list=['AssignmentExpression'], attribute_name='function_type')
            if sub_task:
                task_queue.extend(sub_task)


def expand_expression_list_format(node_list: List[Union[Element, str]],
                                  insert_model: str,
                                  insert_sequence: str = 'head',
                                  local_operation=False,
                                  template: List[str] = None,
                                  fill_info: Union[Element, str] = None,
                                  skip_head=1,
                                  skip_tail=1):
    """
    @param local_operation:
    @param node_list: 要进行格式化整理的节点列表
    @param insert_model: 格式化模式: mid | template
    @param insert_sequence: 插入方式, 从头向尾插入还是从尾向头插入: head | tail
    @param fill_info: 处于 mid_insert 格式化模式下的填充类型
    @param template: 按照模板格式进行填充
    @param skip_head: 跳过开头n个元素插入
    @param skip_tail: 跳过结尾n个元素插入
    @return: 格式化后的list信息

    """
    if not local_operation:
        node_list = deepcopy(node_list)
    if not fill_info:
        fill_info = ''
    if insert_model == 'mid':
        for i in range(len(node_list) - skip_tail, skip_head - 1, -1):
            node_list.insert(i, fill_info)
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


def extract_unary_operator_node(root: Element):
    task_queue = search_node_by_attribute(root, search_list=['FunctionExpression'], attribute_name='function_type')
    while task_queue:
        function_node = task_queue.pop()
        unary_node = function_node.parentNode
        unary_parent_node = unary_node.parentNode.parentNode
        if unary_node.getAttribute('function_type') == 'UnaryExpression':
            children = get_single_node_by_path(function_node, f'{function_node.nodeName}/body/body').childNodes
            for index, child in enumerate(children):
                unary_parent_node.appendChild(child.cloneNode(deep=True))
                text_node = Element('Literal')
                text_node.appendChild(Document().createTextNode(data=";"))
                if index < len(children) - 1:
                    unary_parent_node.appendChild(text_node)
        unary_parent_node.removeChild(unary_node.parentNode)

        sub_task = search_node_by_attribute(root, search_list=['FunctionExpression'], attribute_name='function_type')
        if sub_task:
            task_queue.extend(sub_task)

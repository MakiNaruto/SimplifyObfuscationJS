# -*- coding: UTF-8 -*-
"""
__Author__ = "MakiNaruto"
__Mail__: "become006@gamil.com"
__Created__ = "2024/04/18"
__Description__ = "转换为代码所需的配置文件模板"
"""


from config.format import Expression, Statement, Declaration, Other


class JsConfig:
    def __init__(self):
        self.declaration = Declaration()
        self.expression = Expression()
        self.statement = Statement()
        self.other = Other()


class Declaration(Declaration):
    pass


class Expression(Expression):
    pass


class Statement(Statement):
    pass


class Other(Other):
    pass

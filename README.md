# SimplifyObfuscationJS

通过AST解析JS代码，转换为树的结构，并将无效的节点去除，将复杂化的多层级逻辑结构进行简化。

## 目录结构
```markdown
.
├── code_convert.py   (js代码 在 ast、json、xml之间的相互转换)
├── unit_test.py      (单元测试, 保证更改后的代码不会改变以前示例的输出结果)
└── xml_parse.py      (节点树的各种逻辑处理, 简化js代码逻辑层的复杂度)
```

## 环境 (二选一)
#### 建议选择nodejs
    在解析js代码, 还原至ast结构时, @babel/parser 解析方式对于括号信息有 parenthesized 标识。
    pyjsparser 则没有标识。
    因此, ast结构化的数据还原至代码时, 括号信息会丢失。

### pyjsparser
    pip install pyjsparser

### nodejs
    npm install @babel/parser

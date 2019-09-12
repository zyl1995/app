import re
from exceptions import TempliteSyntaxError


class CodeBuilder:
    """构建python代码"""
    INDENT_STEP = 4  # 缩进

    def __init__(self, indent = 0):
        self.code = []
        self.indent_level = indent

    def add_line(self, line):
        """添加一行python代码(带上换行符)"""
        self.code.extend([' '*self.indent_level, line, '\n'])

    def indent(self):
        """加个缩进"""
        self.indent_level += self.INDENT_STEP

    def dedent(self):
        """取消个缩进"""
        self.indent_level -= self.INDENT_STEP

    def add_section(self):
        """另一个python片段的引用"""
        section = CodeBuilder(self.indent_level)
        self.code.append(section)
        return section

    def get_globals(self):
        """运行python代码,返回全局变量（字典）"""
        assert self.indent_level == 0
        python_source = str(self)
        global_namespace = {}
        exec(python_source, global_namespace)
        return global_namespace

    def __str__(self):
        """拼接成字符串"""
        return ''.join(str(code) for code in self.code)


class Templite:
    def __init__(self, text, *contexts):
        self.context = {}
        self.all_vals = set()
        self.loop_vars = set()
        # 保存上下文变量
        for context in contexts:
            self.context.update(context)
        # 开始写编译函数
        code = CodeBuilder()
        code.add_line("def render_function(context, do_dots):")
        code.indent()
        vars_code = code.add_section()
        code.add_line("result = []")
        code.add_line("append_result = result.append")
        code.add_line("extend_result = result.extend")
        code.add_line("to_str = str")

        buffered = []
        def flush_output():
            if len(buffered) == 1:
                code.add_line("append_result({})".format(buffered[0]))
            elif len(buffered) > 1:
                code.add_line("extend_result([{}])".format(','.join(buffered)))
            del buffered[:]

        ops_stack = []
        tokens = re.split(r"(?s)({{.*?}}|{%.*?%}|{#.*?#})", text)
        for token in tokens:
            if token.startswith('{#'):
                continue
            elif token.startswith('{{'):
                expr = self._expr_code(token[2:-2].strip())
                buffered.append("to_str({})".format(expr))
            elif token.startswith("{%"):
                flush_output()
                words = token[2:-2].strip().split()
                if words[0] == 'if':
                    if len(words) != 2:
                        self._syntax_error("Dont't understand if", token)
                    ops_stack.append('if')
                    code.add_line("if {}".format(self._expr_code(words[1])))
                    code.indent()
                elif words[0] == 'for':
                    if len(words) !=4 or words[2] != 'in':
                        self._syntax_error("Dont't understand for", token)
                    ops_stack.append('for')
                    self._variable(words[1], self.loop_vars)
                    code.add_line(
                        "for c_{} in {}:".format(words[1], self._expr_code(words[3]))
                    )
                    code.indent()
                elif words[0].startswith('end'):
                    if len(words) != 1:
                        self._syntax_error("Dont't understand end", token)
                    if not ops_stack:
                        self._syntax_error("Too many ends", token)
                    end_what = words[0][3:]
                    start_what = ops_stack.pop()
                    if end_what != start_what:
                        self._syntax_error("Mismatched end tag", end_what)
                    code.dedent()
                else:
                    self._syntax_error("Dont't understand tag", token)
            else:
                if token:
                    buffered.append(repr(token))
        if ops_stack:
            self._syntax_error("Unmatched action tag", ops_stack[-1])
        flush_output()
        # 变量定义
        for var_name in self.all_vals - self.loop_vars:
            vars_code.add_line("c_{} = context['{}']".format(var_name, var_name))

        code.add_line("return ''.join(result)")
        code.dedent()
        self._render_function = code.get_globals()['render_function']

    def _expr_code(self, expr):
        if '|' in expr:
            pipes = expr.split('|')
            code = self._expr_code(pipes[0])
            for func in pipes[1:]:
                self._variable(func, self.all_vals)
                code = "c_{}(({})".format(func, code)
        elif '.' in expr:
            dots = expr.split('.')
            code = self._expr_code(dots[0])
            args = ','.join(repr(d) for d in dots[1:])
            code = "do_dots({}, {})".format(code, args)
        else:
            self._variable(expr, self.all_vals)
            code = "c_{}".format(expr)
        return code

    def _variable(self, name, vars_set):
        vars_set.add(name)

    def _syntax_error(self, msg, thing):
        raise TempliteSyntaxError('{}:{}'.format(msg, thing))

    def _do_dots(self, value, *dots):
        for dot in dots:
            try:
                value = getattr(value, dot)
            except AttributeError:
                value = value[dot]
            if callable(value):
                value = value()
        return value

    def render(self, context):
        _context = dict(self.context)
        if context:
            _context.update(context)
        return self._render_function(_context, self._do_dots)

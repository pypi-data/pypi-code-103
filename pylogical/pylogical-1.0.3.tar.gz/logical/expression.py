#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Niyoufa
# @File: routes.py
# @Time: 2021/11/9 17:05

import re
import string

ID = 'ID'  # 变量名称
AND = 'AND'
OR = 'OR'
NOT = 'NOT'
LPAREN = 'LPAREN'  # 左括号
RPAREN = 'RPAREN'  # 右括号
EOF = 'EOF'  # 结束符号


class Token:
    def __init__(self, value_type, value):
        self.value_type = value_type
        self.value = value

    def __str__(self):
        return 'Token({value_type},{value})'.format(value_type=self.value_type, value=self.value)

    def __repr__(self):
        return self.__str__()

# 词法分析器
class Lexer:
    def __init__(self, text):
        self.text = text
        self.position = 0
        self.current_char = self.text[self.position]

    def error(self):
        raise Exception('词法分析发现错误: {}'.format(self.current_char))

    def _id(self):
        result = ''
        while self.current_char is not None and re.match(r"[0-9A-Z]", self.current_char):
            result += self.current_char
            self.advance()
        token = Token('ID', result)
        return token

    def peek(self):
        pos = self.position + 1
        if pos >= len(self.text):
            return None
        else:
            return self.text[pos]

    def skip_whitespace(self):
        while self.current_char is not None and self.current_char.isspace():
            self.advance()

    def advance(self):
        self.position += 1
        if self.position >= len(self.text):
            self.current_char = None
        else:
            self.current_char = self.text[self.position]

    def get_next_token(self):
        while self.current_char is not None:
            if self.current_char.isspace():
                self.skip_whitespace()
                continue
            if re.match(r"[1-9]", self.current_char):
                return self._id()
            if re.match(r"&", self.current_char):
                self.advance()
                return Token(AND, '&')
            if re.match(r"[|]", self.current_char):
                self.advance()
                return Token(OR, '|')
            if re.match(r"!", self.current_char):
                self.advance()
                return Token(NOT, '!')
            if self.current_char == '(':
                self.advance()
                return Token(LPAREN, '(')
            if self.current_char == ')':
                self.advance()
                return Token(RPAREN, ')')
            self.error()
        return Token(EOF, None)
    
    def yield_next_token(self):
        while self.current_char is not None:
            token = self.get_next_token()
            if token.value_type != EOF:
                yield token

# 语法分析器
class Parser:
    def __init__(self, lexer):
        self.lexer = lexer
        self.current_token = lexer.get_next_token()

    def error(self):
        raise Exception('语法分析发现错误: {}'.format(self.current_token))

    def eat(self, value_type):
        if self.current_token.value_type == value_type:
            self.current_token = self.lexer.get_next_token()
        else:
            self.lexer.error()

    def check_factor(self):
        current_token = self.current_token
        if current_token.value_type == ID:
            self.eat(ID)
        elif current_token.value_type == LPAREN:
            self.eat(LPAREN)
            self.check_expr()
            self.eat(RPAREN)

    def check_term(self):
        self.check_factor()
        while self.current_token.value_type == NOT:
            self.eat(NOT)
            self.check_factor()


    def check_expr(self):
        self.check_term()
        while self.current_token.value_type in (AND, OR):
            token = self.current_token
            if token.value_type == AND:
                self.eat(AND)
                self.check_term()
            elif token.value_type == OR:
                self.eat(OR)
                self.check_term()

    def check(self):
        self.check_expr()
        if self.current_token.value_type is not EOF:
            raise self.error()


# 逻辑表达式
class LogicExpression(object):
    """逻辑规则表达式"""

    def __init__(self, content):
        self.content = content
        self.content = re.sub(r"[\s]", "", self.content)

        #　用字母（Ａ－Ｚ）表示表达式
        self.expression_letters = self.yield_letter()
        # 逻辑运算符规则
        self.ops_rule = {
            '|': 1,
            '&': 1,
            "!": 2
        }

        self.expression_dict = {}
        self.expression = None
        if self.content:
            self.expression = self.generate(self.content)
            self.inverse_polish_expressoin = self.middle_to_after(self.expression)
        else:
            self.expression = ""
            self.inverse_polish_expressoin = []

    def yield_letter(self):
        for letter in string.ascii_uppercase:
            yield letter

    def preprocess(self, content):
        """
        规则表达式预处理，处理系统规则
        :param content:
        :return:
        """
        content = re.sub(r"[\s]", "", content)
        return content

    def check(self, content):
        lexer = Lexer(content)
        parser = Parser(lexer)
        parser.check()

    def generate(self, content):
        """生成复合规则表达式"""
        content = self.preprocess(content)
        self.check(content)
        lexer = Lexer(content)
        expression = ""
        for token in lexer.yield_next_token():
            if token.value_type == ID:
                letter = next(self.expression_letters)
                self.expression_dict[letter] = token.value
                expression += letter
            else:
                expression += token.value
        return expression

    def middle_to_after(self, s):
        """
        中缀表达式转化后缀表达式(逆波兰表达式).
        :param s: 中缀表达式的字符串表示，本程序中采用操作符跟数值之间用空格分开
        :return: 后缀表达式，数组的形式，每个数值或者操作符占一个数组下标.
        """
        expression = []
        ops = []
        ss = [c.strip() for c in s]
        for item in ss:
            if item in self.ops_rule.keys():  # 操作符
                while len(ops) >= 0:
                    if len(ops) == 0:
                        ops.append(item)
                        break
                    op = ops.pop()
                    if op == '(' or self.ops_rule[item] > self.ops_rule[op]:
                        ops.append(op)
                        ops.append(item)
                        break
                    else:
                        expression.append(op)
            elif item == '(':  # 左括号，直接入操作符栈
                ops.append(item)
            elif item == ')':  # 右括号，循环出栈道
                while len(ops) > 0:
                    op = ops.pop()
                    if op == '(':
                        break
                    else:
                        expression.append(op)
            else:
                expression.append(item)  # 数值，直接入表达式栈

        while len(ops) > 0:
            expression.append(ops.pop())

        return expression

    def calculate(self, n1, n2, op, context):
        if op == '|':
            if (isinstance(n1, bool) and n1 is True) or (not isinstance(n1, bool) and context.get(self.expression_dict[n1])):
                return True

            if (isinstance(n2, bool) and n2 is True) or (not isinstance(n2, bool) and context.get(self.expression_dict[n2])):
                return True
            else:
                return False

        if op == '&':
            if (isinstance(n1, bool) and n1 is False) or (not isinstance(n1, bool) and not context.get(self.expression_dict[n1])):
                return False

            if (isinstance(n2, bool) and n2 is False) or (not isinstance(n2, bool) and not context.get(self.expression_dict[n2])):
                return False
            else:
                return True

    def calculate_not(self, n, context):
        if (isinstance(n, bool) and n is True) or (not isinstance(n, bool) and context.get(self.expression_dict[n])):
            return False
        else:
            return True


    def execute(self, context):
        flag = False

        if len(self.inverse_polish_expressoin) == 0:
            return flag
        
        if len(self.inverse_polish_expressoin) == 1:
            return context.get(self.expression_dict[self.inverse_polish_expressoin[0]]) == True

        stack_value = []
        for item in self.inverse_polish_expressoin:
            if item in self.ops_rule.keys():
                if item != "!":
                    n2 = stack_value.pop()  # 注意，先出栈的在操作符右边.
                    n1 = stack_value.pop()
                    result = self.calculate(n1, n2, item, context)
                    stack_value.append(result)
                else:
                    n = stack_value.pop()
                    result = self.calculate_not(n, context)
                    stack_value.append(result)
            else:
                stack_value.append(item)  # 数值直接压栈.

        if stack_value and stack_value[0]:
            flag = True

        return flag

    def __str__(self) -> str:
        return self.content


if __name__ == "__main__":
    text = "(1A&2B)|1B"

    lexer = Lexer(text)
    token = None
    print("词法分析：")
    for token in lexer.yield_next_token():
        print(token)

    print("语法分析：")
    parser = Parser(Lexer(text))
    parser.check()

    exp = LogicExpression(text)
    print("content: {}".format(exp))
    print("expression_dict {}".format(exp.expression_dict))
    print("inverse_polish_expressoin {}".format(exp.inverse_polish_expressoin))
    context = {
        "1A": True,
        "2B": True,
    }
    print("result {}".format(exp.execute(context)))
    
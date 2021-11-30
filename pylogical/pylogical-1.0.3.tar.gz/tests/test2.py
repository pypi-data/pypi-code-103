from logical.expression import *

if __name__ == "__main__":
    text = "1B"

    lexer = Lexer(text)
    token = None
    print("词法分析：")
    while lexer.current_char is not None:
        token = lexer.get_next_token()
        print(token)

    print("语法分析：")
    parser = Parser(Lexer(text))
    parser.check()

    exp = LogicExpression(text)
    print("content: {}".format(exp))
    print("expression_dict {}".format(exp.expression_dict))
    print("inverse_polish_expressoin {}".format(exp.inverse_polish_expressoin))
    context = {
        "1A": False,
    }
    print("result {}".format(exp.execute(context)))
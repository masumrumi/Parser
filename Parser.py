# resources
# https://sly.readthedocs.io/en/latest/sly.html


# how to run:
# step one:
#   pip install sly
# step two:
#   python Parser.py
# step three:
# "language >" will show up.
# step 4:
# test the following programs.
# a = 7
# a = 3+4*8
# a = (4+7)*5


from sly import Lexer
from sly import Parser


class BasicLexer(Lexer):
    def __init__(self):
        self.nesting_level = 0

    tokens = {ID, NUMBER, STRING}
    ignore = '\t '
    literals = {'=', '+', '-', '/', '{', '}',
                '*', '(', ')', ',', ';'}

    # Define tokens as regular expressions
    # (stored as raw strings)
    ID = r'[a-zA-Z_][a-zA-Z0-9_]*'
    STRING = r'\".*?\"'
    # LPAREN = r'\('
    # RPAREN = r'\)'

    # Number token
    @_(r'\d+')
    def NUMBER(self, t):

        # convert it into a python integer
        t.value = int(t.value)
        return t

    # Comment token
    @_(r'//.*')
    def COMMENT(self, t):
        pass

    # Newline token(used only for showing
    # errors in new line)
    @_(r'\n+')
    def newline(self, t):
        self.lineno = t.value.count('\n')

    @_(r'\{')
    def lbrace(self, t):
        t.type = '{'      # Set token type to the expected literal
        self.nesting_level += 1
        return t

    @_(r'\}')
    def rbrace(self, t):
        t.type = '}'      # Set token type to the expected literal
        self.nesting_level -= 1
        return t

    # Error handling rule
    def error(self, t):
        print("Illegal character '%s'" % t.value[0])
        self.index += 1


class BasicParser(Parser):
    # tokens are passed from lexer to parser
    tokens = BasicLexer.tokens

    precedence = (
        ('left', '+', '-'),
        ('left', '*', '/'),
        ('right', 'UMINUS'),
    )

    def __init__(self):
        self.env = {}

    @_('')
    def statement(self, p):
        pass

    @_('var_assign')
    def statement(self, p):
        return p.var_assign

    @_('ID "=" expr')
    def var_assign(self, p):
        return ('var_assign', p.ID, p.expr)

    @_('ID "=" STRING')
    def var_assign(self, p):
        return ('var_assign', p.ID, p.STRING)

    @_('expr')
    def statement(self, p):
        return (p.expr)

    @_('"-" expr %prec UMINUS')
    def expr(self, p):
        return p.expr

    # Grammar rules and actions

    @_('expr "+" term')
    def expr(self, p):
        return p.expr + p.term

    @_('expr "-" term')
    def expr(self, p):
        return p.expr - p.term

    @_('term')
    def expr(self, p):
        return p.term

    @_('term "*" factor')
    def term(self, p):
        return p.term * p.factor

    @_('term "/" factor')
    def term(self, p):
        return p.term / p.factor

    @_('factor')
    def term(self, p):
        return p.factor

    @_('ID')
    def expr(self, p):
        return ('var', p.ID)

    @_('NUMBER')
    def factor(self, p):
        return p.NUMBER

    @_('"(" expr ")"')
    def factor(self, p):
        return p.expr


class BasicExecute:
    def __init__(self, tree, env):
        self.env = env
        result = self.walkTree(tree)
        if result is not None and isinstance(result, int):
            print(result)
        if isinstance(result, str) and result[0] == '"':
            print(result)

    def walkTree(self, node):

        if isinstance(node, int):
            return node
        if isinstance(node, str):
            return node

        if node is None:
            return None

        if node[0] == 'program':
            if node[1] == None:
                self.walkTree(node[2])
            else:
                self.walkTree(node[1])
                self.walkTree(node[2])

        if node[0] == 'num':
            return node[1]

        if node[0] == 'str':
            return node[1]

        if node[0] == 'add':
            return self.walkTree(node[1]) + self.walkTree(node[2])
        elif node[0] == 'sub':
            return self.walkTree(node[1]) - self.walkTree(node[2])
        elif node[0] == 'mul':
            return self.walkTree(node[1]) * self.walkTree(node[2])
        elif node[0] == 'div':
            return self.walkTree(node[1]) / self.walkTree(node[2])

        if node[0] == 'var_assign':
            self.env[node[1]] = self.walkTree(node[2])
            return node[1]

        if node[0] == 'var':
            try:
                return self.env[node[1]]
            except LookupError:
                print("Undefined variable '"+node[1]+"' found!")
                return 0


if __name__ == '__main__':
    lexer = BasicLexer()
    parser = BasicParser()
    print('Start')
    env = {}

    while True:

        try:
            text = input('my_parser > ')

        except EOFError:
            break

        if text:
            tree = parser.parse(lexer.tokenize(text))
            BasicExecute(tree, env)

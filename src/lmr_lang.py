# Définition de la grammaire et des classes de base pour le langage LMR

class Token:
    def __init__(self, type_, value):
        self.type = type_
        self.value = value
    def __repr__(self):
        return f"Token({self.type}, {self.value})"

class Lexer:
    def __init__(self, text):
        self.text = text
        self.pos = 0
        self.current_char = self.text[self.pos] if self.text else None

    def advance(self):
        self.pos += 1
        self.current_char = self.text[self.pos] if self.pos < len(self.text) else None

    def skip_whitespace(self):
        while self.current_char is not None and self.current_char.isspace():
            self.advance()

    def integer(self):
        result = ''
        while self.current_char is not None and self.current_char.isdigit():
            result += self.current_char
            self.advance()
        return int(result)

    def id(self):
        result = ''
        while self.current_char is not None and (self.current_char.isalnum() or self.current_char == '_'):
            result += self.current_char
            self.advance()
        return result

    def get_next_token(self):
        while self.current_char is not None:
            if self.current_char.isspace():
                self.skip_whitespace()
                continue
            if self.current_char.isdigit():
                return Token('INTEGER', self.integer())
            if self.current_char.isalpha() or self.current_char == '_':
                id_str = self.id()
                if id_str == 'fonction':
                    return Token('FONCTION', id_str)
                if id_str == 'return':
                    return Token('RETURN', id_str)
                return Token('ID', id_str)
            if self.current_char == '+':
                self.advance()
                return Token('PLUS', '+')
            if self.current_char == '-':
                self.advance()
                return Token('MINUS', '-')
            if self.current_char == '*':
                self.advance()
                return Token('MUL', '*')
            if self.current_char == '/':
                self.advance()
                return Token('DIV', '/')
            if self.current_char == '=':
                self.advance()
                return Token('ASSIGN', '=')
            if self.current_char == '(': 
                self.advance()
                return Token('LPAREN', '(')
            if self.current_char == ')':
                self.advance()
                return Token('RPAREN', ')')
            if self.current_char == ',':
                self.advance()
                return Token('COMMA', ',')
            if self.current_char == ':':
                self.advance()
                return Token('COLON', ':')
            if self.current_char == '\n':
                self.advance()
                return Token('NEWLINE', '\n')
            raise Exception(f"Caractère inconnu: {self.current_char}")
        return Token('EOF', None)

# Le parser et l'interpréteur seront ajoutés à la prochaine étape.
# Parser et interpréteur pour les expressions arithmétiques
class Parser:
    def parse_params(self):
        params = []
        self.eat('LPAREN')
        if self.current_token.type == 'ID':
            params.append(self.current_token.value)
            self.eat('ID')
            while self.current_token.type == 'COMMA':
                self.eat('COMMA')
                params.append(self.current_token.value)
                self.eat('ID')
        self.eat('RPAREN')
        return params

    def parse_args(self):
        args = []
        self.eat('LPAREN')
        if self.current_token.type not in ('RPAREN',):
            args.append(self.expr())
            while self.current_token.type == 'COMMA':
                self.eat('COMMA')
                args.append(self.expr())
        self.eat('RPAREN')
        return args
    def __init__(self, lexer):
        self.lexer = lexer
        self.current_token = self.lexer.get_next_token()

    def error(self):
        raise Exception('Erreur de syntaxe')

    def eat(self, token_type):
        if self.current_token.type == token_type:
            self.current_token = self.lexer.get_next_token()
        else:
            self.error()

    def factor(self):
        token = self.current_token
        if token.type == 'INTEGER':
            self.eat('INTEGER')
            return token.value
        elif token.type == 'ID':
            var_name = token.value
            self.eat('ID')
            if self.current_token.type == 'LPAREN':
                args = self.parse_args()
                return ('CALL', var_name, args)
            return ('VAR', var_name)
        elif token.type == 'LPAREN':
            self.eat('LPAREN')
            result = self.expr()
            self.eat('RPAREN')
            return result
        self.error()

    def term(self):
        result = self.factor()
        while self.current_token.type in ('MUL', 'DIV'):
            token = self.current_token
            if token.type == 'MUL':
                self.eat('MUL')
                result *= self.factor()
            elif token.type == 'DIV':
                self.eat('DIV')
                result /= self.factor()
        return result

    def expr(self):
        result = self.term()
        while self.current_token.type in ('PLUS', 'MINUS'):
            token = self.current_token
            if token.type == 'PLUS':
                self.eat('PLUS')
                result = ('ADD', result, self.term())
            elif token.type == 'MINUS':
                self.eat('MINUS')
                result = ('SUB', result, self.term())
        return result

    def function_def(self):
        self.eat('FONCTION')
        func_name = self.current_token.value
        self.eat('ID')
        params = self.parse_params()
        self.eat('COLON')
        if self.current_token.type == 'NEWLINE':
            self.eat('NEWLINE')
        if self.current_token.type == 'RETURN':
            self.eat('RETURN')
            body = self.expr()
            if self.current_token.type == 'NEWLINE':
                self.eat('NEWLINE')
            return ('FUNC_DEF', func_name, params, body)
        else:
            self.error()

    def assignment(self):
        if self.current_token.type == 'FONCTION':
            return self.function_def()
        elif self.current_token.type == 'ID':
            var_name = self.current_token.value
            self.eat('ID')
            if self.current_token.type == 'ASSIGN':
                self.eat('ASSIGN')
                expr_value = self.expr()
                return ('ASSIGN', var_name, expr_value)
            else:
                self.error()
        return self.expr()

class Interpreter:
    def __init__(self, parser):
        self.parser = parser
        self.GLOBAL_SCOPE = {}
        self.FUNCTIONS = {}

    def eval(self, node, local_scope=None):
        if local_scope is None:
            local_scope = {}
        if isinstance(node, int):
            return node
        if isinstance(node, tuple):
            if node[0] == 'ADD':
                return self.eval(node[1], local_scope) + self.eval(node[2], local_scope)
            elif node[0] == 'SUB':
                return self.eval(node[1], local_scope) - self.eval(node[2], local_scope)
            elif node[0] == 'MUL':
                return self.eval(node[1], local_scope) * self.eval(node[2], local_scope)
            elif node[0] == 'DIV':
                return self.eval(node[1], local_scope) / self.eval(node[2], local_scope)
            elif node[0] == 'VAR':
                var_name = node[1]
                if var_name in local_scope:
                    return local_scope[var_name]
                elif var_name in self.GLOBAL_SCOPE:
                    return self.GLOBAL_SCOPE[var_name]
                else:
                    raise Exception(f"Variable '{var_name}' non définie")
            elif node[0] == 'ASSIGN':
                var_name = node[1]
                value = self.eval(node[2], local_scope)
                self.GLOBAL_SCOPE[var_name] = value
                return value
            elif node[0] == 'FUNC_DEF':
                func_name = node[1]
                params = node[2]
                body = node[3]
                self.FUNCTIONS[func_name] = (params, body)
                return f"Fonction '{func_name}' définie"
            elif node[0] == 'CALL':
                func_name = node[1]
                args = node[2]
                if func_name not in self.FUNCTIONS:
                    raise Exception(f"Fonction '{func_name}' non définie")
                params, body = self.FUNCTIONS[func_name]
                if len(args) != len(params):
                    raise Exception(f"Nombre d'arguments incorrect pour '{func_name}'")
                local_vars = dict(zip(params, [self.eval(arg, local_scope) for arg in args]))
                return self.eval(body, local_vars)
        raise Exception('Noeud inconnu')

    def interpret(self):
        tree = self.parser.assignment()
        return self.eval(tree)

# Point d'entrée pour l'interpréteur/compilateur LMR
from lmr_lang import Lexer, Parser, Interpreter

if __name__ == "__main__":
    code = input("Entrez une expression LMR: ")
    lexer = Lexer(code)
    parser = Parser(lexer)
    interpreter = Interpreter(parser)
    result = interpreter.interpret()
    print(f"Résultat: {result}")

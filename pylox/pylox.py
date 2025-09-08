# from __future__ import annotations
import sys
from pylox.scanner import Scanner
from pylox.tokens import Token
from pylox.tokentype import TokenType
from pylox.error import ErrorReporter
from pylox.parser import Parser
from pylox.ast_printer import AstPrinter
from pylox.expr import Expr
from pylox.interpreter import Interpreter
from pylox.stmt import Stmt

class Pylox:
    interpreter: Interpreter = Interpreter()
    repl: bool = False

    @staticmethod
    def main():
        if len(sys.argv) > 2: # 2 cause python always takes .py file name as first argument
            print("Usage: pylox [script]") # TODO: make pylox work like this instead of running like a python script
            sys.exit(64)
        elif len(sys.argv) == 2: Pylox.run_file(sys.argv[1])
        else: 
            Pylox.repl = True
            Pylox.run_prompt()

    @staticmethod
    def run_file(path: str): 
        with open(path, encoding="utf-8", mode="r") as file:
            src_string: str = file.read()
        Pylox.run(src_string)
        if ErrorReporter.had_error: sys.exit(65)
        if ErrorReporter.had_runtime_error: sys.exit(70)

    @staticmethod
    def run_prompt() -> None:
        while True:
            try:
                line: str = input(">>> ")
                Pylox.run(line)
                ErrorReporter.had_error = False
            except EOFError: break

    @classmethod
    def run(cls, src: str):
        scanner = Scanner(src)
        tokens: list[Token] = scanner.scan_tokens()
        parser = Parser(tokens)

        if Pylox.repl and tokens[-2].token_type is not TokenType.SEMICOLON:
            expression: Expr = parser.expression()
            if ErrorReporter.had_error: return
            print("\nEval:")
            print(cls.interpreter.stringify(cls.interpreter.evaluate(expression)))
            return

        statements: list[Stmt] = parser.parse()

        # TODO: Print tree for each statement in pylox
        # if ErrorReporter.had_error: return
        # if ErrorReporter.had_error: print("\nPartial Tree:")
        # else: print("\nTree:")
        # print(AstPrinter().print(expression))
        
        if ErrorReporter.had_error: return
        print("\nEval:")
        cls.interpreter.interpret(statements)


if __name__ == "__main__":
    Pylox.main()
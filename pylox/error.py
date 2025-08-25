from pylox.tokens import Token
from pylox.tokentype import TokenType

class ErrorReporter:
    had_error: bool = False

    @classmethod
    def error(cls, token: Token, message: str):
        if token.token_type == TokenType.EOF:
            cls.report(token.line, " at end", message)
        else:
            cls.report(token.line, f" at '{token.lexeme}'", message)

    @classmethod
    def report(cls, line: int, where: str, message: str):
        print(f"[line {line}] Error{where}: {message}")
        cls.had_error = True
from pylox.tokens import Token
from pylox.tokentype import TokenType

class ErrorReporter:
    had_error: bool = False

    @classmethod
    def error(cls, message: str, **kwargs):
        if "line" in kwargs: 
            cls.report(kwargs["line"], "", message) # used in scanner
            return
        if kwargs["token"].token_type == TokenType.EOF: cls.report(kwargs["token"].line, " at end", message)
        else: cls.report(kwargs["token"].line, f" at '{kwargs['token'].lexeme}'", message)

    @classmethod
    def report(cls, line: int, where: str, message: str):
        print(f"[line {line}] Error{where}: {message}")
        cls.had_error = True
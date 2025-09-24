from pylox.tokens import Token
from pylox.tokentype import TokenType
from pylox.runtime_error import PyloxRuntimeError

class ErrorReporter:
    had_error: bool = False
    had_runtime_error: bool = False
    had_warning: bool = False

    @classmethod
    def error(cls, message: str, **kwargs): # TODO: is there a cleaner way to do this?
        # used in scanner
        if "line" in kwargs: 
            cls.report(kwargs["line"], "", message)
            return
        # used in parser ands resolver
        if kwargs["token"].token_type == TokenType.EOF: cls.report(kwargs["token"].line, " at end", message)
        elif "warning_flag" in kwargs: cls.report_warning(kwargs["token"].line, f" at '{kwargs['token'].lexeme}'", message)
        else: cls.report(kwargs["token"].line, f" at '{kwargs['token'].lexeme}'", message)

    @classmethod
    def report_warning(cls, line: int, where: str, message: str):
        print(f"[line {line}] Warning{where}: {message}")
        cls.had_warning = True

    @classmethod
    def report(cls, line: int, where: str, message: str):
        print(f"[line {line}] Error{where}: {message}")
        cls.had_error = True

    @classmethod
    def runtime_error(cls, error: PyloxRuntimeError):
        print(f"{error}\n[line {error.token.line}]")
        cls.had_runtime_error = True
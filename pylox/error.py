class ErrorReporter:
    had_error: bool = False

    @classmethod
    def error(cls, line: int, message: str):
        cls.report(line, "", message)

    @classmethod
    def report(cls, line: int, where: str, message: str):
        print(f"[line {line}] Error{where}: {message}")
        cls.had_error = True
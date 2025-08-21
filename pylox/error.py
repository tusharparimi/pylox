class ErrorReporter:
    had_error: bool = False

    @classmethod
    def error(self, line: int, message: str):
        self.report(line, "", message)

    @classmethod
    def report(self, line: int, where: str, message: str):
        print(f"[line {line}] Error{where}: {message}")
        self.had_error = True
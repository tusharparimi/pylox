from pylox.tokens import Token

class PyloxRuntimeError(RuntimeError):
    def __init__(self, token: Token, message: str):
        super().__init__(message)
        self.token = token
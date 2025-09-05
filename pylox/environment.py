from dataclasses import dataclass, field
from pylox.tokens import Token
from pylox.runtime_error import PyloxRuntimeError

@dataclass(frozen=True)
class Environment:
    __values: dict[str, object] = field(default_factory=dict) # state (field ensures each instance gets its own dict)

    def get(self, name: Token) -> str:
        if name.lexeme in self.__values.keys(): return self.__values[name.lexeme]
        raise PyloxRuntimeError(name, f"Undefined variable '{name.lexeme}'.")

    def define(self, name: str, value: object) -> None:
        self.__values[name] = value
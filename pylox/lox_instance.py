from __future__ import annotations
from dataclasses import dataclass, field
from pylox.tokens import Token
from pylox.runtime_error import PyloxRuntimeError
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pylox.lox_class import LoxClass
    from pylox.lox_function import LoxFunction

@dataclass(frozen=True)
class LoxInstance:
    klass: LoxClass
    fields: dict[str, object] = field(default_factory=dict)

    def get(self, name: Token) -> object:
        if name.lexeme in self.fields: return self.fields[name.lexeme]
        method: LoxFunction = self.klass.find_method(name.lexeme)
        if method is not None: return method.bind(self)
        raise PyloxRuntimeError(name, f"Undefined property '{name.lexeme}'.")
    
    def set(self, name: Token, value: object) -> None:
        self.fields[name.lexeme] = value

    def __str__(self):
        return self.klass.name + " instance"
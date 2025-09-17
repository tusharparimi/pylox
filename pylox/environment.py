from __future__ import annotations
from typing import Optional
from dataclasses import dataclass, field
from pylox.tokens import Token
from pylox.runtime_error import PyloxRuntimeError

@dataclass(frozen=True)
class Environment:
    enclosing: Optional[Environment] = None
    __values: dict[str, object | UnInitValue] = field(default_factory=dict) # state (field ensures each instance gets its own dict)

    def get(self, name: Token) -> object:
        if name.lexeme in self.__values.keys(): 
            if not isinstance(self.__values[name.lexeme], UnInitValue): return self.__values[name.lexeme]
            raise PyloxRuntimeError(name, f"Variable '{name.lexeme}' accessed before its initialized or assigned.")
        if self.enclosing is not None: return self.enclosing.get(name)
        raise PyloxRuntimeError(name, f"Undefined variable '{name.lexeme}'.")

    def define(self, name: str, value: object | UnInitValue) -> None:
        self.__values[name] = value

    def ancestor(self, distance: int) -> Environment:
        environment: Environment = self
        for i in range(distance): environment = environment.enclosing
        return environment

    def get_at(self, distance: int, name: str) -> object:
        return self.ancestor(distance).__values.get(name)
    
    def assign_at(self, distance: int, name: Token, value: object) -> None:
        self.ancestor(distance).__values[name.lexeme] = value

    def assign(self, name: Token, value: object) -> None:
        if name.lexeme in self.__values.keys():
            self.__values[name.lexeme] = value
            return
        if self.enclosing is not None: return self.enclosing.assign(name, value)
        raise PyloxRuntimeError(name, f"Undefined variable '{name.lexeme}'.")

@dataclass    
class UnInitValue:
    pass

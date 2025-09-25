from __future__ import annotations
from typing import Optional
from dataclasses import dataclass, field
from pylox.tokens import Token
from pylox.runtime_error import PyloxRuntimeError

@dataclass(frozen=True)
class Environment:
    enclosing: Optional[Environment] = None
    __values: list[object | UnInitValue] = field(default_factory=list) # state (field ensures each instance gets its own list)

    def get(self, name: Token, idx: int) -> object:
        if idx < len(self.__values):
            if not isinstance(self.__values[idx], UnInitValue): return self.__values[idx]
            raise PyloxRuntimeError(name, f"Variable '{name.lexeme}' accessed before its initialized or assigned.")
        if self.enclosing is not None: return self.enclosing.get(name, idx)
        raise PyloxRuntimeError(name, f"Undefined variable '{name.lexeme}'.")

    def define(self, value: object | UnInitValue) -> None:
        self.__values.append(value)

    def ancestor(self, distance: int) -> Environment:
        environment: Environment = self
        for i in range(distance): environment = environment.enclosing
        return environment
    
    def get_at(self, distance: int, name: str, idx: int) -> object:
        return self.ancestor(distance).__values[idx]

    def assign_at(self, distance: int, idx: int, value: object) -> None:
        self.ancestor(distance).__values[idx] = value
    
    def assign(self, name: Token, value: object, idx: int) -> None:
        if idx < len(self.__values):
            self.__values[idx] = value
            return
        if self.enclosing is not None: return self.enclosing.assign(name, value, idx)
        raise PyloxRuntimeError(name, f"Undefined variable '{name.lexeme}'.")

@dataclass    
class UnInitValue:
    pass

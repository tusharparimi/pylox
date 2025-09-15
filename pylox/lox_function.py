from __future__ import annotations
from dataclasses import dataclass
from pylox.lox_callable import LoxCallable
from pylox.stmt import Function
from pylox.return_signal import ReturnSignal
from pylox.environment import Environment
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pylox.interpreter import Interpreter

@dataclass(frozen=True)
class LoxFunction(LoxCallable):
    declaration: Function
    closure: Environment

    def call(self, interpreter: Interpreter, arguments: list[object]) -> object:
        environment: Environment = Environment(self.closure)
        for i in range(len(self.declaration.params)): environment.define(self.declaration.params[i].lexeme, arguments[i])
        try: interpreter.execute_block(self.declaration.body, environment)
        except ReturnSignal as r: return r.value
        return None
    
    def arity(self) -> int:
        return len(self.declaration.params)

    def __str__(self) -> str: return f"<fn {self.declaration.name.lexeme}>"
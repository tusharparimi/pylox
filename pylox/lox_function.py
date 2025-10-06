from __future__ import annotations
from dataclasses import dataclass
from pylox.lox_callable import LoxCallable
from pylox.stmt import Function
from pylox.expr import Lambda
from pylox.control_flow_signal import ReturnSignal
from pylox.environment import Environment
from pylox.lox_instance import LoxInstance
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pylox.interpreter import Interpreter

@dataclass(frozen=True)
class LoxFunction(LoxCallable):
    declaration: Function | Lambda
    closure: Environment
    is_initializer: bool

    def bind(self, instance: LoxInstance) -> LoxFunction:
        environment: Environment = Environment(self.closure)
        environment.define(instance)
        return LoxFunction(self.declaration, environment, self.is_initializer)

    def call(self, interpreter: Interpreter, arguments: list[object]) -> object:
        environment: Environment = Environment(self.closure)
        for i in range(len(self.declaration.params)): environment.define(arguments[i])
        try: interpreter.execute_block(self.declaration.body, environment)
        except ReturnSignal as r:
            if self.is_initializer: return self.closure.get_at(0, "this")
            return r.value
        if self.is_initializer: return self.closure.get_at(0, "this")
        return None
    
    def arity(self) -> int:
        return len(self.declaration.params)

    def __str__(self) -> str: 
        if isinstance(self.declaration, Lambda): return "<lambda fn>"
        return f"<fn {self.declaration.name.lexeme}>"
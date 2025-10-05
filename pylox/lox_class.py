from __future__ import annotations
from dataclasses import dataclass
from pylox.lox_callable import LoxCallable
from pylox.lox_instance import LoxInstance
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pylox.interpreter import Interpreter

@dataclass(frozen=True)
class LoxClass(LoxCallable):
    name: str

    def call(self, interpreter: Interpreter, arguments: list[object]) -> object:
        instance: LoxInstance = LoxInstance(self)
        return instance
    
    def arity(self) -> int:
        return 0

    def __str__(self):
        return self.name

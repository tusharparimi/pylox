from __future__ import annotations
from dataclasses import dataclass, field
from pylox.lox_callable import LoxCallable
from pylox.lox_instance import LoxInstance
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from pylox.interpreter import Interpreter
    from pylox.lox_function import LoxFunction

@dataclass(frozen=True)
class LoxClass(LoxCallable):
    name: str
    methods: dict[str, LoxFunction] = field(default_factory=dict)

    def find_method(self, name: str) -> Optional[LoxFunction]:
        if name in self.methods: return self.methods[name]

    def call(self, interpreter: Interpreter, arguments: list[object]) -> object:
        instance: LoxInstance = LoxInstance(self)
        initializer: LoxFunction = self.find_method("init")
        if initializer is not None: initializer.bind(instance).call(interpreter, arguments)
        return instance
    
    def arity(self) -> int:
        initializer: LoxFunction = self.find_method("init")
        if initializer is None: return 0
        return initializer.arity()

    def __str__(self):
        return self.name

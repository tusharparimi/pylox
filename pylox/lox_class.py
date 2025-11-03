from __future__ import annotations
from dataclasses import dataclass, field
from pylox.lox_callable import LoxCallable
from pylox.lox_instance import LoxInstance
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from pylox.interpreter import Interpreter
    from pylox.lox_function import LoxFunction

class LoxClass(LoxCallable, LoxInstance):
    # def __init__(self, name: str, superclass: Optional[LoxClass], methods: dict[str, LoxFunction]):
    def __init__(self, name: str, superclasses: list[LoxClass], methods: dict[str, LoxFunction]):
        self.name = name
        self.superclasses = superclasses
        self.methods = methods

    def find_method(self, name: str) -> Optional[LoxFunction]:
        # print("lox func: ", self)
        # print(self.methods)
        if name in self.methods:
            # print("found method //////////////////////")
            return self.methods[name]
        # if self.superclass is not None: return self.superclass.find_method(name)
        if self.superclasses:
            for sc in self.superclasses: # multiple inheritance follows
                if (loxfunc := sc.find_method(name)) is not None: return loxfunc

    def call(self, interpreter: Interpreter, arguments: list[object]) -> object:
        instance: LoxInstance = LoxInstance(klass=self, fields={})
        initializer: LoxFunction = self.find_method("init")
        if initializer is not None: initializer.bind(instance).call(interpreter, arguments)
        return instance
    
    def arity(self) -> int:
        initializer: LoxFunction = self.find_method("init")
        if initializer is None: return 0
        return initializer.arity()

    def __str__(self):
        return self.name
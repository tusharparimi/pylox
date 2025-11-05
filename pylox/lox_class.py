from __future__ import annotations
from dataclasses import dataclass, field
from pylox.lox_callable import LoxCallable
from pylox.lox_instance import LoxInstance
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from pylox.interpreter import Interpreter
    from pylox.lox_function import LoxFunction

class LoxClass(LoxCallable, LoxInstance):
    def __init__(self, name: str, superclasses: list[LoxClass], methods: dict[str, LoxFunction], mro: list[LoxClass] = []):
        self.name = name
        self.superclasses = superclasses
        self.methods = methods
        self.mro = mro

    def find_method(self, name: str, ignore_first: bool = False) -> Optional[LoxFunction]:
        mro = self.mro[-1::-1]
        if ignore_first: mro = mro[1:]
        for sc in mro:
            if name in sc.methods: return sc.methods[name]

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
        return self.name + str(len(self.mro))
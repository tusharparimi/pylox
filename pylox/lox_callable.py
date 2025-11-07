from __future__ import annotations
from abc import ABC, abstractmethod
import time
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pylox.interpreter import Interpreter

class LoxCallable(ABC):
    @abstractmethod
    def arity(self): ...

    @abstractmethod
    def call(self, interpreter: Interpreter, arguments: list[object]): ...

class Clock(LoxCallable):
    def arity(self) -> int: return 0
    def call(self, interpreter: Interpreter, arguments: list[object]) -> object: return time.time() # time.time() returns current unix timestamp in seconds
    def __str__(self) -> str: return "<native fn>"
from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pylox.lox_class import LoxClass

@dataclass(frozen=True)
class LoxInstance:
    klass: LoxClass

    def __str__(self):
        return self.klass.name + " instance"
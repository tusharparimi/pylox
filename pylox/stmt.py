from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Protocol
from pylox.expr import Expr

class Visitor(Protocol):
	def visit_Expression_Stmt(self, expression: Expression): ...
	def visit_Print_Stmt(self, print: Print): ...

class Stmt(ABC):
	@abstractmethod
	def accept(self, visitor: Visitor): ...

@dataclass(frozen=True)
class Expression(Stmt):
	expression: Expr

	def accept(self, visitor: Visitor):
		return visitor.visit_Expression_Stmt(self)

@dataclass(frozen=True)
class Print(Stmt):
	expression: Expr

	def accept(self, visitor: Visitor):
		return visitor.visit_Print_Stmt(self)
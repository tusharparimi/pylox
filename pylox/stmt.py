from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Protocol, Optional
from pylox.tokens import Token
from pylox.expr import Expr

class Visitor(Protocol):
	def visit_Block_Stmt(self, block: Block): ...
	def visit_Expression_Stmt(self, expression: Expression): ...
	def visit_Print_Stmt(self, print: Print): ...
	def visit_Var_Stmt(self, var: Var): ...

class Stmt(ABC):
	@abstractmethod
	def accept(self, visitor: Visitor): ...

@dataclass(frozen=True)
class Block(Stmt):
	statements: list[Stmt]

	def accept(self, visitor: Visitor):
		return visitor.visit_Block_Stmt(self)

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

@dataclass(frozen=True)
class Var(Stmt):
	name: Token
	initializer: Optional[Expr]

	def accept(self, visitor: Visitor):
		return visitor.visit_Var_Stmt(self)
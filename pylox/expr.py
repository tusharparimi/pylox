from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Protocol, Optional
from pylox.tokens import Token

class Visitor(Protocol):
	def visit_Assign_Expr(self, assign: Assign): ...
	def visit_Binary_Expr(self, binary: Binary): ...
	def visit_Call_Expr(self, call: Call): ...
	def visit_Grouping_Expr(self, grouping: Grouping): ...
	def visit_Literal_Expr(self, literal: Literal): ...
	def visit_Logical_Expr(self, logical: Logical): ...
	def visit_Unary_Expr(self, unary: Unary): ...
	def visit_Ternary_Expr(self, ternary: Ternary): ...
	def visit_Variable_Expr(self, variable: Variable): ...

class Expr(ABC):
	@abstractmethod
	def accept(self, visitor: Visitor): ...

@dataclass(frozen=True)
class Assign(Expr):
	name: Token
	value: Expr

	def accept(self, visitor: Visitor):
		return visitor.visit_Assign_Expr(self)

@dataclass(frozen=True)
class Binary(Expr):
	left: Optional[Expr]
	operator: Token
	right: Optional[Expr]

	def accept(self, visitor: Visitor):
		return visitor.visit_Binary_Expr(self)

@dataclass(frozen=True)
class Call(Expr):
	callee: Expr
	paren: Token
	arguments: list[Expr]

	def accept(self, visitor: Visitor):
		return visitor.visit_Call_Expr(self)

@dataclass(frozen=True)
class Grouping(Expr):
	expression: Expr

	def accept(self, visitor: Visitor):
		return visitor.visit_Grouping_Expr(self)

@dataclass(frozen=True)
class Literal(Expr):
	value: object

	def accept(self, visitor: Visitor):
		return visitor.visit_Literal_Expr(self)

@dataclass(frozen=True)
class Logical(Expr):
	left: Expr
	operator: Token
	right: Expr

	def accept(self, visitor: Visitor):
		return visitor.visit_Logical_Expr(self)

@dataclass(frozen=True)
class Unary(Expr):
	operator: Token
	right: Expr

	def accept(self, visitor: Visitor):
		return visitor.visit_Unary_Expr(self)

@dataclass(frozen=True)
class Ternary(Expr):
	condition: Expr
	operator1: Token
	expr_if_true: Expr
	operator2: Token
	expr_if_false: Expr

	def accept(self, visitor: Visitor):
		return visitor.visit_Ternary_Expr(self)

@dataclass(frozen=True)
class Variable(Expr):
	name: Token

	def accept(self, visitor: Visitor):
		return visitor.visit_Variable_Expr(self)
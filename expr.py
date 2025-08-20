from __future__ import annotations
from abc import ABC, abstractmmethod
from dataclasses import dataclass
from typing import Protocol
from tokens import Token

class Visitor(Protocol):
	def visit_Binary_Expr(binary: Binary): ...
	def visit_Grouping_Expr(grouping: Grouping): ...
	def visit_Literal_Expr(literal: Literal): ...
	def visit_Unary_Expr(unary: Unary): ...

class Expr(ABC):
	@abstractmmethod
	def accept(self, visitor: Visitor): ...

@dataclass(frozen=True)
class Binary(Expr):
	left: Expr
	operator: Token
	right: Expr

	def accept(self, visitor: Visitor):
		return visitor.visit_Binary_Expr(self)

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
class Unary(Expr):
	operator: Token
	right: Expr

	def accept(self, visitor: Visitor):
		return visitor.visit_Unary_Expr(self)
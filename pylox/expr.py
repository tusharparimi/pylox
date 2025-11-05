from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Protocol, Optional
from pylox.tokens import Token
from typing import TYPE_CHECKING

if TYPE_CHECKING:
	from pylox.stmt import Stmt

class Visitor(Protocol):
	def visit_Assign_Expr(self, assign: Assign): ...
	def visit_Binary_Expr(self, binary: Binary): ...
	def visit_Call_Expr(self, call: Call): ...
	def visit_Get_Expr(self, get: Get): ...
	def visit_Lambda_Expr(self, lambda_arg: Lambda): ...
	def visit_Grouping_Expr(self, grouping: Grouping): ...
	def visit_Literal_Expr(self, literal: Literal): ...
	def visit_Logical_Expr(self, logical: Logical): ...
	def visit_Set_Expr(self, set: Set): ...
	def visit_Super_Expr(self, super: Super): ...
	def visit_Inner_Expr(self, inner: Inner): ...
	def visit_This_Expr(self, this: This): ...
	def visit_Unary_Expr(self, unary: Unary): ...
	def visit_Ternary_Expr(self, ternary: Ternary): ...
	def visit_Variable_Expr(self, variable: Variable): ...

class Expr(ABC):
	@abstractmethod
	def accept(self, visitor: Visitor): ...

@dataclass(frozen=True, eq=False)
class Assign(Expr):
	name: Token
	value: Expr

	def accept(self, visitor: Visitor):
		return visitor.visit_Assign_Expr(self)

@dataclass(frozen=True, eq=False)
class Binary(Expr):
	left: Optional[Expr]
	operator: Token
	right: Optional[Expr]

	def accept(self, visitor: Visitor):
		return visitor.visit_Binary_Expr(self)

@dataclass(frozen=True, eq=False)
class Call(Expr):
	callee: Expr
	paren: Token
	arguments: list[Expr]

	def accept(self, visitor: Visitor):
		return visitor.visit_Call_Expr(self)

@dataclass(frozen=True, eq=False)
class Get(Expr):
	obj: Expr
	name: Token

	def accept(self, visitor: Visitor):
		return visitor.visit_Get_Expr(self)

@dataclass(frozen=True, eq=False)
class Lambda(Expr):
	params: list[Token]
	body: list[Stmt | None]

	def accept(self, visitor: Visitor):
		return visitor.visit_Lambda_Expr(self)

@dataclass(frozen=True, eq=False)
class Grouping(Expr):
	expression: Expr

	def accept(self, visitor: Visitor):
		return visitor.visit_Grouping_Expr(self)

@dataclass(frozen=True, eq=False)
class Literal(Expr):
	value: object

	def accept(self, visitor: Visitor):
		return visitor.visit_Literal_Expr(self)

@dataclass(frozen=True, eq=False)
class Logical(Expr):
	left: Expr
	operator: Token
	right: Expr

	def accept(self, visitor: Visitor):
		return visitor.visit_Logical_Expr(self)

@dataclass(frozen=True, eq=False)
class Set(Expr):
	obj: Expr
	name: Token
	value: Expr

	def accept(self, visitor: Visitor):
		return visitor.visit_Set_Expr(self)

@dataclass(frozen=True, eq=False)
class Super(Expr):
	keyword: Token
	method: Token

	def accept(self, visitor: Visitor):
		return visitor.visit_Super_Expr(self)

@dataclass(frozen=True, eq=False)
class Inner(Expr):
	keyword: Token
	method: Token

	def accept(self, visitor: Visitor):
		return visitor.visit_Inner_Expr(self)

@dataclass(frozen=True, eq=False)
class This(Expr):
	keyword: Token

	def accept(self, visitor: Visitor):
		return visitor.visit_This_Expr(self)

@dataclass(frozen=True, eq=False)
class Unary(Expr):
	operator: Token
	right: Expr

	def accept(self, visitor: Visitor):
		return visitor.visit_Unary_Expr(self)

@dataclass(frozen=True, eq=False)
class Ternary(Expr):
	condition: Expr
	operator1: Token
	expr_if_true: Expr
	operator2: Token
	expr_if_false: Expr

	def accept(self, visitor: Visitor):
		return visitor.visit_Ternary_Expr(self)

@dataclass(frozen=True, eq=False)
class Variable(Expr):
	name: Token

	def accept(self, visitor: Visitor):
		return visitor.visit_Variable_Expr(self)
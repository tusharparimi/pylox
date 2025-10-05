from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Protocol, Optional
from pylox.tokens import Token
from pylox.expr import Expr
from pylox.environment import UnInitValue

class Visitor(Protocol):
	def visit_Break_Stmt(self, break_arg: Break): ...
	def visit_Block_Stmt(self, block: Block): ...
	def visit_Class_Stmt(self, class_arg: Class): ...
	def visit_Expression_Stmt(self, expression: Expression): ...
	def visit_Function_Stmt(self, function: Function): ...
	def visit_If_Stmt(self, if_arg: If): ...
	def visit_Print_Stmt(self, print_arg: Print): ...
	def visit_Return_Stmt(self, return_arg: Return): ...
	def visit_Var_Stmt(self, var: Var): ...
	def visit_While_Stmt(self, while_arg: While): ...

class Stmt(ABC):
	@abstractmethod
	def accept(self, visitor: Visitor): ...

@dataclass(frozen=True, eq=False)
class Break(Stmt):
	

	def accept(self, visitor: Visitor):
		return visitor.visit_Break_Stmt(self)

@dataclass(frozen=True, eq=False)
class Block(Stmt):
	statements: list[Stmt | None]

	def accept(self, visitor: Visitor):
		return visitor.visit_Block_Stmt(self)

@dataclass(frozen=True, eq=False)
class Class(Stmt):
	name: Token
	methods: list[Function]

	def accept(self, visitor: Visitor):
		return visitor.visit_Class_Stmt(self)

@dataclass(frozen=True, eq=False)
class Expression(Stmt):
	expression: Expr

	def accept(self, visitor: Visitor):
		return visitor.visit_Expression_Stmt(self)

@dataclass(frozen=True, eq=False)
class Function(Stmt):
	name: Token
	params: list[Token]
	body: list[Stmt | None]

	def accept(self, visitor: Visitor):
		return visitor.visit_Function_Stmt(self)

@dataclass(frozen=True, eq=False)
class If(Stmt):
	condition: Expr
	then_branch: Stmt
	else_branch: Optional[Stmt]

	def accept(self, visitor: Visitor):
		return visitor.visit_If_Stmt(self)

@dataclass(frozen=True, eq=False)
class Print(Stmt):
	expression: Expr

	def accept(self, visitor: Visitor):
		return visitor.visit_Print_Stmt(self)

@dataclass(frozen=True, eq=False)
class Return(Stmt):
	keyword: Token
	value: Optional[Expr]

	def accept(self, visitor: Visitor):
		return visitor.visit_Return_Stmt(self)

@dataclass(frozen=True, eq=False)
class Var(Stmt):
	name: Token
	initializer: Expr | UnInitValue

	def accept(self, visitor: Visitor):
		return visitor.visit_Var_Stmt(self)

@dataclass(frozen=True, eq=False)
class While(Stmt):
	condition: Expr
	body: Stmt

	def accept(self, visitor: Visitor):
		return visitor.visit_While_Stmt(self)
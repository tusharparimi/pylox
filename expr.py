from abc import ABC
from dataclasses import dataclass
from tokens import Token

class Expr(ABC):
	pass

@dataclass(frozen=True)
class Binary(Expr):
	left: Expr
	operator: Token
	right: Expr

@dataclass(frozen=True)
class Grouping(Expr):
	expression: Expr

@dataclass(frozen=True)
class Literal(Expr):
	value: object

@dataclass(frozen=True)
class Unary(Expr):
	operator: Token
	right: Expr
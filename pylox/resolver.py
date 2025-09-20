from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum, auto
from pylox.interpreter import Interpreter
from pylox.stmt import Stmt, Block, Var, Function, Expression, If, Print, Return, While
from pylox.expr import Expr, Variable, Assign, Binary, Call, Grouping, Literal, Logical, Unary
from pylox.tokens import Token
from pylox.error import ErrorReporter

class FunctionType(Enum):
    NONE = auto()
    FUNCTION = auto()

@dataclass(frozen=True)
class Resolver:
    interpreter: Interpreter
    __scopes: list[dict[str, bool]] = field(default_factory=list)
    current_function: FunctionType = FunctionType.NONE

    def set_current_function(self, new_function: FunctionType) -> None: # bad code? why freeze then change value of an attribute
        object.__setattr__(self, "current_function", new_function)

    def resolve(self, statements: list[Stmt]) -> None:
        for statement in statements: self.resolve_stmt(statement)

    def resolve_stmt(self, stmt: Stmt) -> None:
        stmt.accept(self)

    def resolve_expr(self, expr: Expr) -> None:
        expr.accept(self)

    def visit_Block_Stmt(self, stmt: Block) -> None:
        self.begin_scope()
        self.resolve(stmt.statements)
        self.end_scope()

    def begin_scope(self) -> None:
        self.__scopes.append({})

    def end_scope(self) -> None:
        self.__scopes.pop()

    def visit_Var_Stmt(self, stmt: Var) -> None:
        self.declare(stmt.name)
        if stmt.initializer is not None: self.resolve_expr(stmt.initializer)
        self.define(stmt.name)

    def declare(self, name: Token) -> None:
        if len(self.__scopes) == 0: return
        scope: dict[str, bool] = self.__scopes[-1]
        if name.lexeme in scope: ErrorReporter.error("Already a variable with this name in this scope.", token=name)
        scope[name.lexeme] = False

    def define(self, name: Token) -> None:
        if len(self.__scopes) == 0: return
        self.__scopes[-1][name.lexeme] = True

    def visit_Variable_Expr(self, expr: Variable) -> None:
        if (not len(self.__scopes) == 0) and (self.__scopes[-1].get(expr.name.lexeme) == False):
            ErrorReporter.error("Can't read local vvariable in its own initializer.", token=expr.name)
        self.resolve_local(expr, expr.name)

    def resolve_local(self, expr: Expr, name: Token) -> None:
        for i in range(len(self.__scopes) - 1, -1, -1):
            if name.lexeme in self.__scopes[i]:
                self.interpreter.resolve(expr, len(self.__scopes) - 1 - i)
                return
            
    def visit_Assign_Expr(self, expr: Assign) -> None:
        self.resolve_expr(expr.value)
        self.resolve_local(expr, expr.name)

    def visit_Function_Stmt(self, stmt: Function) -> None:
        self.declare(stmt.name)
        self.define(stmt.name)
        self.resolve_function(stmt, FunctionType.FUNCTION)

    def resolve_function(self, stmt: Function, type: FunctionType) -> None:
        enclosing_function: FunctionType = self.current_function
        # self.current_function = type
        self.set_current_function(type)
        self.begin_scope()
        for param in stmt.params:
            self.declare(param)
            self.define(param)
        self.resolve(stmt.body)
        self.end_scope()
        # self.current_function = enclosing_function
        self.set_current_function(enclosing_function)

    def visit_Expression_Stmt(self, stmt: Expression) -> None:
        self.resolve_expr(stmt.expression)

    def visit_If_Stmt(self, stmt: If) -> None:
        self.resolve_expr(stmt.condition)
        self.resolve_stmt(stmt.then_branch)
        if stmt.else_branch is not None: self.resolve_stmt(stmt.else_branch)

    def visit_Print_Stmt(self, stmt: Print) -> None:
        self.resolve_expr(stmt.expression)

    def visit_Return_Stmt(self, stmt: Return) -> None:
        if self.current_function == FunctionType.NONE: ErrorReporter.error("Can't return from top-level code.", token=stmt.keyword)
        if stmt.value is not None: self.resolve_expr(stmt.value)

    def visit_While_Stmt(self, stmt: While) -> None:
        self.resolve_expr(stmt.condition)
        self.resolve_stmt(stmt.body)

    def visit_Binary_Expr(self, expr: Binary) -> None:
        self.resolve_expr(expr.left)
        self.resolve_expr(expr.right)

    def visit_Call_Expr(self, expr: Call) -> None:
        self.resolve_expr(expr.callee)
        for argument in expr.arguments: self.resolve_expr(argument)

    def visit_Grouping_Expr(self, expr: Grouping) -> None:
        self.resolve_expr(expr.expression)

    def visit_Literal_Expr(self, expr: Literal) -> None:
        return
    
    def visit_Logical_Expr(self, expr: Logical) -> None:
        self.resolve_expr(expr.left)
        self.resolve_expr(expr.right)

    def visit_Unary_Expr(self, expr: Unary) -> None:
        self.resolve_expr(expr.right)
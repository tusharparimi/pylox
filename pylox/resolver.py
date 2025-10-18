from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum, auto
from pylox.interpreter import Interpreter
from pylox.stmt import Stmt, Block, Var, Function, Expression, If, Print, Return, While, Break, Class
from pylox.expr import Expr, Variable, Assign, Binary, Call, Grouping, Literal, Logical, Unary, Ternary, Lambda, Get, Set, This, Super
from pylox.tokens import Token
from pylox.error import ErrorReporter
from pylox.environment import UnInitValue

class FunctionType(Enum):
    NONE = auto()
    FUNCTION = auto()
    INITIALIZER = auto()
    METHOD = auto()

class ClassType(Enum):
    NONE = auto()
    CLASS = auto()
    SUBCLASS = auto()

@dataclass(frozen=True)
class Resolver:
    interpreter: Interpreter
    # scope is a dict with var name keys and values as list of [is_resolved, is_used, token_for_error_reporting, uniq_index_for_var_in_each_scope]
    __scopes: list[dict[str, list[bool, bool, Token, int]]] = field(default_factory=list)
    current_function: FunctionType = FunctionType.NONE
    current_class: ClassType = ClassType.NONE
    var_counts: list[int] = field(default_factory=list)

    def set_current_function(self, new_function: FunctionType) -> None: # bad code? why freeze then change value of an attribute
        object.__setattr__(self, "current_function", new_function)

    def set_current_class(self, new_class: ClassType) -> None: # bad code? why freeze then change value of an attribute
        object.__setattr__(self, "current_class", new_class)

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

    def visit_Class_Stmt(self, stmt: Class) -> None:
        enclosing_class: ClassType = self.current_class
        self.set_current_class(ClassType.CLASS)
        self.declare(stmt.name)
        self.define(stmt.name)
        if stmt.superclass is not None and stmt.name.lexeme == stmt.superclass.name.lexeme: ErrorReporter.error("A class can't inherit from itself.", stmt.superclass.name)
        if stmt.superclass is not None:
            self.set_current_class(ClassType.SUBCLASS)
            self.resolve_expr(stmt.superclass)
        if stmt.superclass is not None:
            self.begin_scope()
            self.__scopes[-1]["super"] = [True, True, stmt.name, self.var_counts[-1]]
            self.var_counts[-1] += 1
        self.begin_scope()
        self.__scopes[-1]["this"] = [True, True, stmt.name, self.var_counts[-1]] # is_used is True for 'this' even if its not used in anywere in te class as its suppose to be hidden
        self.var_counts[-1] += 1
        for method in stmt.methods:
            declaration: FunctionType = FunctionType.METHOD
            if method.name.lexeme == "init": declaration = FunctionType.INITIALIZER
            self.resolve_function(method, declaration)
        for class_method in stmt.class_methods:
            declaration: FunctionType = FunctionType.METHOD
            if class_method.name.lexeme == "init": ErrorReporter.error("class methods cannot have name 'init'", token=class_method.name)
            self.resolve_function(class_method, declaration)
        self.end_scope()
        if stmt.superclass is not None: self.end_scope()
        self.set_current_class(enclosing_class)

    def begin_scope(self) -> None:
        self.__scopes.append({})
        self.var_counts.append(0)

    def end_scope(self) -> None:
        for k,v in self.__scopes[-1].items():
            if not v[1]: ErrorReporter.error(f"Local variable '{k}' not used", token=v[2], warning_flag=True)
        self.__scopes.pop()
        self.var_counts.pop()

    def visit_Var_Stmt(self, stmt: Var) -> None:
        self.declare(stmt.name)
        if stmt.initializer is not None and not isinstance(stmt.initializer, UnInitValue): self.resolve_expr(stmt.initializer)
        self.define(stmt.name)

    def declare(self, name: Token) -> None:
        if len(self.__scopes) == 0: return
        scope: dict[str, list[bool, bool, Token]] = self.__scopes[-1]
        if name.lexeme in scope: ErrorReporter.error("Already a variable with this name in this scope.", token=name)
        scope[name.lexeme] = [False, False, name, self.var_counts[-1]]
        self.var_counts[-1] += 1

    def define(self, name: Token) -> None:
        if len(self.__scopes) == 0: return
        self.__scopes[-1][name.lexeme][0] = True

    def visit_Variable_Expr(self, expr: Variable) -> None:
        if (len(self.__scopes) != 0) and self.__scopes[-1].get(expr.name.lexeme) and (self.__scopes[-1].get(expr.name.lexeme)[0] == False):
            ErrorReporter.error("Can't read local variable in its own initializer.", token=expr.name)
        for i in range(len(self.__scopes) - 1, -1, -1):
            if expr.name.lexeme in self.__scopes[i]: self.__scopes[i][expr.name.lexeme][1] = True
        self.resolve_local(expr, expr.name)

    def resolve_local(self, expr: Expr, name: Token) -> None:
        for i in range(len(self.__scopes) - 1, -1, -1):
            if name.lexeme in self.__scopes[i]:
                self.interpreter.resolve(expr, len(self.__scopes) - 1 - i, self.__scopes[i][name.lexeme][3])
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
        if stmt.value is not None:
            if self.current_function == FunctionType.INITIALIZER: ErrorReporter.error("Can't return a value from an initializer.", token=stmt.keyword)
            self.resolve_expr(stmt.value)

    def visit_While_Stmt(self, stmt: While) -> None:
        self.resolve_expr(stmt.condition)
        self.resolve_stmt(stmt.body)

    def visit_Break_Stmt(self, stmt: Break) -> None:
        return

    def visit_Binary_Expr(self, expr: Binary) -> None:
        self.resolve_expr(expr.left)
        self.resolve_expr(expr.right)

    def visit_Call_Expr(self, expr: Call) -> None:
        self.resolve_expr(expr.callee)
        for argument in expr.arguments: self.resolve_expr(argument)

    def visit_Get_Expr(self, expr: Get) -> None:
        self.resolve_expr(expr.obj)

    def visit_Grouping_Expr(self, expr: Grouping) -> None:
        self.resolve_expr(expr.expression)

    def visit_Literal_Expr(self, expr: Literal) -> None:
        return
    
    def visit_Logical_Expr(self, expr: Logical) -> None:
        self.resolve_expr(expr.left)
        self.resolve_expr(expr.right)

    def visit_Set_Expr(self, expr: Set) -> None:
        self.resolve_expr(expr.value)
        self.resolve_expr(expr.obj)

    def visit_Super_Expr(self, expr: Super) -> None:
        if self.current_class == ClassType.NONE: ErrorReporter.error("Can't use 'super' outside of a class.", token=expr.keyword)
        elif self.current_class != ClassType.SUBCLASS: ErrorReporter.error("Can't use 'super' in a class with no superclass.", token=expr.keyword)
        self.resolve_local(expr, expr.keyword)

    def visit_This_Expr(self, expr: This) -> None:
        if self.current_class == ClassType.NONE:
            ErrorReporter.error("Can't use 'this' outside of a class.", token=expr.keyword)
        self.resolve_local(expr, expr.keyword)

    def visit_Unary_Expr(self, expr: Unary) -> None:
        self.resolve_expr(expr.right)

    def visit_Ternary_Expr(self, expr: Ternary) -> None:
        self.resolve_expr(expr.condition)
        self.resolve_expr(expr.expr_if_true)
        self.resolve_expr(expr.expr_if_false)

    def visit_Lambda_Expr(self, expr: Lambda) -> None:
        self.resolve_function(expr, FunctionType.FUNCTION)
from typing import cast, Optional
from pylox.expr import Expr, Literal, Grouping, Unary, Binary, Ternary, Variable, Assign, Logical, Call
from pylox.tokentype import TokenType
from pylox.tokens import Token
from pylox.runtime_error import PyloxRuntimeError
from pylox.error import ErrorReporter
from pylox.stmt import Stmt, Expression, Print, Var, Block, If, While, Break, Function, Return
from pylox.environment import Environment, UnInitValue
from pylox.lox_callable import LoxCallable, Clock
from pylox.lox_function import LoxFunction
from pylox.control_flow_signal import ReturnSignal, BreakSignal

class Interpreter:
    globals: Environment = Environment()
    __environment: Environment = globals 

    globals.define("clock", Clock())

    def interpret(self, statements: list[Stmt]):
        try:
            for statement in statements: 
                assert statement is not None
                self.execute(statement)
        except PyloxRuntimeError as error: ErrorReporter.runtime_error(error)

    def execute(self, stmt: Stmt) -> None:
        # if stmt is None: return
        stmt.accept(self)

    def execute_block(self, statements: list[Stmt | None], environment: Environment) -> None:
        previous: Environment = self.__environment
        try:
            self.__environment = environment
            for statement in statements: 
                if statement is not None: self.execute(statement)
        finally: self.__environment = previous

    def visit_Block_Stmt(self, stmt: Block) -> None:
        self.execute_block(stmt.statements, Environment(self.__environment))

    def stringify(self, obj: object) -> str:
        if obj is None and not ErrorReporter.had_error: return "nil"
        if isinstance(obj, float):
            text: str = str(obj)
            if text[-2:] == ".0": text = text[:-2]
            return text
        if isinstance(obj, bool):
            if bool(obj): return "true" # python has True and False (capitalized T and F), Pylox has true and false
            return "false"
        return str(obj)

    def visit_Literal_Expr(self, expr: Literal) -> object:
        return expr.value
    
    def visit_Logical_Expr(self, expr: Logical) -> object:
        left: object = self.evaluate(expr.left)
        if expr.operator.token_type == TokenType.OR and self.is_truthy(left): return left
        if expr.operator.token_type == TokenType.AND and not self.is_truthy(left): return left
        return self.evaluate(expr.right) # a logic operator merely guarantees it will return a value with appropriate truthiness
    
    def visit_Grouping_Expr(self, expr: Grouping) -> object:
        return self.evaluate(expr.expression)
    
    def evaluate(self, expr: Optional[Expr]) -> object:
        if isinstance(expr, Expr): return expr.accept(self)
        return None

    def visit_Unary_Expr(self, expr: Unary) -> object:
        right: object = self.evaluate(expr.right)
        match expr.operator.token_type:
            case TokenType.MINUS:
                self.check_number_operand(expr.operator, right)
                return -float(cast(float, right)) # making mypy happy with cast
            case TokenType.BANG: return not self.is_truthy(right)
            case _: return None

    def is_truthy(self, obj: object) -> bool: # in pylox, except False and None everything else in truthy 
        if obj is None: return False
        if isinstance(obj, bool): return bool(obj)
        return True
    
    def visit_Binary_Expr(self, expr: Binary) -> object:
        left: object = self.evaluate(expr.left)
        right: object = self.evaluate(expr.right)
        match expr.operator.token_type:
            case TokenType.MINUS: 
                self.check_number_operands(expr.operator, left, right)
                return float(cast(float, left)) - float(cast(float, right))
            case TokenType.PLUS:
                if isinstance(left, float) and isinstance(right, float): return float(left) + float(right)
                if isinstance(left, str) or isinstance(right, str): 
                    return (str(left)[:-2] if isinstance(left, float) else str(left)) + (str(right)[:-2] if isinstance(right, float) else str(right))
                raise PyloxRuntimeError(expr.operator, "Operands must be numbers or strings.")
            case TokenType.SLASH: 
                self.check_number_operands(expr.operator, left, right)
                if float(cast(float, right)) == 0: raise PyloxRuntimeError(expr.operator, "Cannot divide by zero.")
                return float(cast(float, left)) / float(cast(float, right))
            case TokenType.STAR: 
                self.check_number_operands(expr.operator, left, right)
                return float(cast(float, left)) * float(cast(float, right))
            case TokenType.GREATER:
                self.check_number_operands(expr.operator, left, right)  
                return float(cast(float, left)) > float(cast(float, right))
            case TokenType.GREATER_EQUAL: 
                self.check_number_operands(expr.operator, left, right)
                return float(cast(float, left)) >= float(cast(float, right))
            case TokenType.LESS: 
                self.check_number_operands(expr.operator, left, right)
                return float(cast(float, left)) < float(cast(float, right))
            case TokenType.LESS_EQUAL: 
                self.check_number_operands(expr.operator, left, right)
                return float(cast(float, left)) <= float(cast(float, right))
            case TokenType.BANG_EQUAL: return not self.is_equal(left, right) # can just use left == right here
            case TokenType.EQUAL_EQUAL: return self.is_equal(left, right) # can just use left != right here
            case _: return None

    def visit_Call_Expr(self, expr: Call) -> object:
        callee: object = self.evaluate(expr.callee)
        arguments: list[object] = []
        for argument in expr.arguments: arguments.append(self.evaluate(argument))
        if not isinstance(callee, LoxCallable): raise PyloxRuntimeError(expr.paren, "Can only call functions and classes.")
        function: LoxCallable = callee
        if len(arguments) != function.arity(): raise PyloxRuntimeError(expr.paren, f"Expected {function.arity()} arguments but got {len(arguments)}.")
        return function.call(self, arguments)

    def is_equal(self, a: object, b: object) -> bool: # this func is not needed (in python) but reminds me ow a different lang like java would need it as lox hhandles equality differently from it
        if a is None and b is None: return True
        if a is None: return False
        return a == b
    
    def check_number_operand(self, operator: Token, operand: object):
        if isinstance(operand, float): return
        raise PyloxRuntimeError(operator, "Operand must be a number.")
    
    def check_number_operands(self, operator: Token, left: object, right: object):
        if isinstance(left, float) and isinstance(right, float): return
        raise PyloxRuntimeError(operator, "Operands must be numbers.")
    
    def visit_Ternary_Expr(self, expr: Ternary) -> object:
        condition_eval: object = self.evaluate(expr.condition)
        if self.is_truthy(condition_eval): return self.evaluate(expr.expr_if_true)
        return self.evaluate(expr.expr_if_false)
    
    def visit_Variable_Expr(self, expr: Variable) -> object: return self.__environment.get(expr.name)
    
    def visit_Expression_Stmt(self, stmt: Expression) -> None: self.evaluate(stmt.expression)

    def visit_Function_Stmt(self, stmt: Function) -> None:
        function: LoxFunction = LoxFunction(stmt, self.__environment)
        self.__environment.define(stmt.name.lexeme, function)

    def visit_If_Stmt(self, stmt: If) -> None:
        if self.is_truthy(self.evaluate(stmt.condition)): self.execute(stmt.then_branch)
        elif stmt.else_branch is not None: self.execute(stmt.else_branch)
    
    def visit_Print_Stmt(self, stmt: Print) -> None:
        value: object = self.evaluate(stmt.expression)
        print(self.stringify(value))

    def visit_Return_Stmt(self, stmt: Return) -> None:
        value: object = None
        if stmt.value is not None: value = self.evaluate(stmt.value)
        raise ReturnSignal(value)

    def visit_Var_Stmt(self, stmt: Var) -> None:
        value: object | UnInitValue = UnInitValue()
        if not isinstance(stmt.initializer, UnInitValue): value = self.evaluate(stmt.initializer)
        self.__environment.define(stmt.name.lexeme, value)

    def visit_While_Stmt(self, stmt: While) -> None:
        while self.is_truthy(self.evaluate(stmt.condition)):
            try: self.execute(stmt.body)
            except BreakSignal: break # TODO: implement pylox break withhout using python break

    def visit_Break_Stmt(self, stmt: Break) -> None:
        raise BreakSignal

    def visit_Assign_Expr(self, expr: Assign) -> object:
        value: object = self.evaluate(expr.value)
        self.__environment.assign(expr.name, value)
        return value # assignment is an expression that can be nested inside other expressions
    


from typing import cast, Optional
from pylox.expr import Expr, Literal, Grouping, Unary, Binary, Ternary
from pylox.tokentype import TokenType
from pylox.tokens import Token
from pylox.runtime_error import PyloxRuntimeError
from pylox.error import ErrorReporter

class Interpreter:
    def interpret(self, expression: Expr):
        try:
            value: object = self.evaluate(expression)
            print(self.stringify(value))
        except PyloxRuntimeError as error: ErrorReporter.runtime_error(error)

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
    
    def visit_Grouping_Expr(self, expr: Grouping) -> object:
        return self.evaluate(expr.expression)
    
    def evaluate(self, expr: Optional[Expr]) -> object:
        if isinstance(expr, Expr): return expr.accept(self)
        return None

    def visit_Unary_Expr(self, expr: Unary) -> object:
        right: object = self.evaluate(expr)
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

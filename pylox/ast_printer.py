from typing import Optional
from pylox.expr import Expr, Binary, Grouping, Literal, Unary, Ternary
from pylox.tokens import Token
from pylox.tokentype import TokenType

class AstPrinter:
    def print(self, expr: Optional[Expr]) -> str: 
        if isinstance(expr, Expr): return expr.accept(self)
        return "_"

    def visit_Binary_Expr(self, binary: Binary) -> str:
        return self.parenthesize(binary.operator.lexeme, binary.left, binary.right)
    
    def visit_Grouping_Expr(self, grouping: Grouping) -> str:
        return self.parenthesize("group", grouping.expression)
    
    @staticmethod  # TODO: why static check and remove
    def visit_Literal_Expr(literal: Literal) -> str:
        if literal.value == None: return "nil"
        return str(literal.value)
    
    def visit_Unary_Expr(self, unary: Unary) -> str:
        return self.parenthesize(unary.operator.lexeme, unary.right)
    
    def visit_Ternary_Expr(self, ternary: Ternary) -> str:
        return self.parenthesize(ternary.operator1.lexeme + ternary.operator2.lexeme, ternary.condition, ternary.expr_if_true, ternary.expr_if_false)
    
    def parenthesize(self, name: str, *args: Optional[Expr]) -> str: # TODO: just use expr_list no *args
        res: str = "(" + name
        for expr in args:
            if expr is None: return "_" # blank for error expressions (only to see partial syntax tree for error expressions)
            res += " "
            res += expr.accept(self)
        res += ")"
        return res
    
def main():
    expression = Binary(
        Unary(
            Token(TokenType.MINUS, "-", None, 1),
            Literal(123)
        ),
        Token(TokenType.STAR, "*", None, 1),
        Grouping(Literal(45.67))
    )
    print(AstPrinter().print(expression))

if __name__ == "__main__":
    main()

    
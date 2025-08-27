from typing import Optional
from pylox.expr import Expr, Binary, Grouping, Literal, Unary, Ternary
from pylox.tokens import Token
from pylox.tokentype import TokenType

class RpnPrinter:
    def print(self, expr: Expr): return expr.accept(self)

    def visit_Binary_Expr(self, binary: Binary) -> str:
        return self.rpn_style(binary.operator.lexeme, binary.left, binary.right)
    
    def visit_Grouping_Expr(self, grouping: Grouping) -> str:
        return self.rpn_style("group", grouping.expression)
    
    def visit_Literal_Expr(self, literal: Literal) -> str:
        if literal.value == None: return "nil"
        return str(literal.value)
    
    def visit_Unary_Expr(self, unary: Unary) -> str:
        return self.rpn_style(unary.operator.lexeme, unary.right)
    
    def visit_Ternary_Expr(self, ternary: Ternary) -> str:
        return self.rpn_style(ternary.operator1.lexeme + ternary.operator2.lexeme, ternary.condition, ternary.expr_if_true, ternary.expr_if_false)
    
    def rpn_style(self, name: str, *args: Optional[Expr]):
        res: str = ""
        for expr in args:
            if expr is None: return "_"
            res += expr.accept(self)
            res += " "
        res += name
        return res
    
def main():
    expression1 = Binary(
        Unary(
            Token(TokenType.MINUS, "-", None, 1),
            Literal(123)
        ),
        Token(TokenType.STAR, "*", None, 1),
        Grouping(Literal(45.67))
    )
    expression2 = Binary(
        Binary(
            Literal(1),
            Token(TokenType.PLUS, "+", None, 1),
            Literal(2)
        ),
        Token(TokenType.STAR, "*", None, 1),
        Binary(
            Literal(4),
            Token(TokenType.MINUS, "-", None, 1),
            Literal(3)
        )
    )
    print(RpnPrinter().print(expression1))
    print(RpnPrinter().print(expression2))

if __name__ == "__main__":
    main()
from typing import Optional
from pylox.expr import Expr, Binary, Grouping, Literal, Unary, Ternary, Assign, Logical, Variable
from pylox.stmt import Stmt, Break, Block, Expression, If, Print, Var, While
from pylox.tokens import Token
from pylox.tokentype import TokenType
from pylox.environment import UnInitValue

class AstPrinter:
    space_count = 0

    def print(self, statements: list[Stmt]) -> str:
        res = "Program: [\n\n"
        for statement in statements:
            # print(statement)
            res = res + statement.accept(self) + "\n\n"
            AstPrinter.space_count = 0
        res = res + "\n\n]"
        return res

    def visit_Break_Stmt(self, stmt: Break) -> str:
        res = f"{TokenType.BREAK.name}()"
        return res

    def visit_Block_Stmt(self, block: Block) -> str:
        AstPrinter.space_count += len("BLOCK(")
        space_mark: int = AstPrinter.space_count
        res = "BLOCK("
        for statement in block.statements:
            if statement is not None:
                res += statement.accept(self)
                AstPrinter.space_count = space_mark
                res += ",\n" + " "*space_mark
        res += ", )"
        return res
    
    def visit_Expression_Stmt(self, stmt: Expression) -> str:
        res = stmt.expression.accept(self)
        return res
    
    def visit_If_Stmt(self, stmt: If) -> str:
        AstPrinter.space_count += len(TokenType.IF.name) + 1
        space_mark: int = AstPrinter.space_count
        res = f"{TokenType.IF.name}("
        res += stmt.condition.accept(self)
        res += ",\n" + " "*space_mark
        res += stmt.then_branch.accept(self)
        if stmt.else_branch is not None:
            res += ",\n" + " "*space_mark
            res += stmt.then_branch.accept(self)
        res += ", )"
        return res 
    
    def visit_Print_Stmt(self, stmt: Print) -> str:
        AstPrinter.space_count += len(TokenType.PRINT.name) + 1
        res = f"{TokenType.PRINT.name}("
        res = res + stmt.expression.accept(self) + ")"
        return res
    
    def visit_Var_Stmt(self, var: Var) -> str:
        res = f"{TokenType.VAR.name}({TokenType.IDENTIFIER.name}({var.name.lexeme}), "
        AstPrinter.space_count += len(TokenType.VAR.name) + 1
        res = res + "\n"+ " "*AstPrinter.space_count + (var.initializer.accept(self) if not isinstance(var.initializer, UnInitValue) else "_") + ")"
        return res
    
    def visit_While_Stmt(self, stmt: While) -> str:
        AstPrinter.space_count += len(TokenType.WHILE.name) + 1
        space_mark: int = AstPrinter.space_count
        res = f"{TokenType.WHILE.name}("
        res += stmt.condition.accept(self)
        AstPrinter.space_count = space_mark
        res += ",\n" + " "*space_mark
        res += stmt.body.accept(self)
        AstPrinter.space_count = space_mark
        res += ", )"
        return res
    
    def visit_Assign_Expr(self, assign: Assign) -> str:
        AstPrinter.space_count += len(TokenType.EQUAL.name) + 1
        return self.parenthesize(TokenType.EQUAL.name, f"{TokenType.IDENTIFIER.name}({assign.name.lexeme})", assign.value)

    def visit_Logical_Expr(self, logical: Logical):
        AstPrinter.space_count += len(logical.operator.token_type.name) + 1
        return self.parenthesize(logical.operator.token_type.name, logical.left, logical.right)

    def visit_Variable_Expr(self, variable: Variable) -> str:
        return f"{TokenType.IDENTIFIER.name}({variable.name.lexeme})"

    def visit_Binary_Expr(self, binary: Binary) -> str:
        AstPrinter.space_count += len(binary.operator.token_type.name) + 1
        assert binary.left is not None
        assert binary.right is not None
        return self.parenthesize(binary.operator.token_type.name, binary.left, binary.right)
    
    def visit_Grouping_Expr(self, grouping: Grouping) -> str:
        AstPrinter.space_count += len("GROUP") + 1
        return self.parenthesize("GROUP", grouping.expression)
    
    @staticmethod  # TODO: why static check and remove
    def visit_Literal_Expr(literal: Literal) -> str:
        if literal.value is None: return f"{TokenType.NIL.name}"
        elif isinstance(literal.value, float): return f"{TokenType.NUMBER.name}({literal.value})" 
        elif isinstance(literal.value, str): return f"{TokenType.STRING.name}({literal.value})"
        elif isinstance(literal.value, bool): return f"{TokenType.TRUE.name}" if literal.value else f"{TokenType.FALSE.name}"
        return str(literal.value)
    
    def visit_Unary_Expr(self, unary: Unary) -> str:
        AstPrinter.space_count += len(unary.operator.token_type.name) + 1
        return self.parenthesize(unary.operator.token_type.name, unary.right)
    
    def visit_Ternary_Expr(self, ternary: Ternary) -> str:
        AstPrinter.space_count += len("TERNARY") + 1
        return self.parenthesize("TERNARY", ternary.condition, ternary.expr_if_true, ternary.expr_if_false)
    
    def parenthesize(self, name: str, *args: Expr | str) -> str: # TODO: just use expr_list no *args
        res: str = name
        if len(args) > 0:
            first: bool = True
            res += "("
            for expr in args:
                if (isinstance(expr, Literal) or isinstance(expr, Variable)) and not first: res += " "
                elif not first: res += "\n" + " "*AstPrinter.space_count
                if isinstance(expr, str): res += expr
                else: res += expr.accept(self)
                res += ", "
                first = False
            res += ")"
        return res

    
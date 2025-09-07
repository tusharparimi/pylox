from __future__ import annotations
from typing import Optional
from pylox.tokens import Token
from pylox.expr import Expr, Binary, Unary, Literal, Grouping, Ternary, Variable, Assign
from pylox.tokentype import TokenType
from pylox.error import ErrorReporter
from pylox.stmt import Stmt, Print, Expression, Var, Block
from pylox.environment import UnInitValue

class Parser:
    def __init__(self, tokens: list[Token]):
        self._tokens: list[Token] = tokens
        self.current: int = 0

    def parse(self) -> list[Stmt]:
        statements = []
        while not self.is_at_end():
            stmt = self.declaration()
            if stmt is not None: statements.append(stmt)
        return statements

    def declaration(self) -> Optional[Stmt]:
        try: 
            if self.match([TokenType.VAR]): return self.var_declaration()
            return self.statement()
        except Parser.ParseError:
            self.synchronize()
            return None
    
    def var_declaration(self) -> Stmt:
        name: Optional[Token] = self.consume(TokenType.IDENTIFIER, "Expect variable name.")
        assert name is not None
        initializer: Optional[Expr] = None
        if self.match([TokenType.EQUAL]): initializer = self.expression()
        self.consume(TokenType.SEMICOLON, "Expect ';' after variable declaration.")
        if initializer is None: return Var(name, UnInitValue())
        return Var(name, initializer)

    def statement(self) -> Stmt:
        if self.match([TokenType.PRINT]): return self.print_statement()
        if self.match([TokenType.LEFT_BRACE]): return Block(self.block())
        return self.expression_statement()
    
    def block(self) -> list[Stmt]:
        statements: list[Stmt] = []
        while not self.check(TokenType.RIGHT_BRACE) and not self.is_at_end(): statements.append(self.declaration())
        self.consume(TokenType.RIGHT_BRACE, "Expect '}' after block.")
        return statements
    
    def print_statement(self) -> Stmt:
        value: Expr = self.expression()
        self.consume(TokenType.SEMICOLON, "Expect ';' after value.")
        return Print(value)
    
    def expression_statement(self) -> Stmt:
        expr: Expr = self.expression()
        self.consume(TokenType.SEMICOLON, "Expect ';' after value.")
        return Expression(expr)
    
    def assignment(self) -> Expr:
        expr: Expr = self.ternary()
        if self.match([TokenType.EQUAL]):
            equals: Token = self.previous()
            value: Expr = self.assignment()
            if isinstance(expr, Variable): 
                name: Token = expr.name
                return Assign(name, value)
            self.error(equals, "Invalid assignment target.")
        return expr

    def expression(self) -> Expr:
        return self.comma()
    
    def comma(self) -> Expr:
        expr: Expr = self.assignment()
        while self.match([TokenType.COMMA]):
            operator: Token = self.previous()
            right: Expr = self.assignment()
            expr = Binary(expr, operator, right)
        return expr
    
    def ternary(self) -> Expr:
        expr: Expr = self.equality()
        if self.match([TokenType.QUESTION]):
            operator1: Token = self.previous()
            expr_if_true: Expr = self.equality()
            if self.match([TokenType.COLON]):
                operator2: Token = self.previous()
                expr_if_false: Expr = self.ternary()
                return Ternary(expr, operator1, expr_if_true, operator2, expr_if_false)
            raise self.error(self.peek(), "'?' only allowed as part of ternary operator, corresponding ':' not found")
        return expr
    
    def equality(self) -> Expr:
        expr: Expr = self.comparison()
        while (self.match([TokenType.BANG_EQUAL, TokenType.EQUAL_EQUAL])):
            operator: Token = self.previous()
            right: Expr = self.comparison()
            expr = Binary(expr, operator, right)
        return expr

    def match(self, token_types: list[TokenType]) -> bool:
        for type in token_types:
            if self.check(type):
                self.advance()
                return True
        return False
    
    def consume(self, type: TokenType, message: str) -> Optional[Token]:
        if self.check(type): return self.advance()
        raise self.error(self.peek(), message)

    def check(self, type: TokenType) -> bool:
        if self.is_at_end(): return False
        return self.peek().token_type == type

    def advance(self) -> Token:
        if not self.is_at_end(): self.current += 1
        return self.previous()
    
    def is_at_end(self) -> bool:
        return self.peek().token_type == TokenType.EOF
    
    def peek(self) -> Token:
        return self._tokens[self.current]
    
    def previous(self) -> Token:
        return self._tokens[self.current - 1]
    
    class ParseError(RuntimeError):
        """Custom exception for parsing errors."""
        pass
    
    def error(self, token: Token, message: str) -> Parser.ParseError:
        ErrorReporter.error(message, token=token)
        return self.ParseError()
    
    def synchronize(self):
        # self.advance()
        while not self.is_at_end():
            if self.previous().token_type == TokenType.SEMICOLON: return
            match self.peek().token_type:
                case TokenType.CLASS: return
                case TokenType.FUN: return
                case TokenType.VAR: return
                case TokenType.FOR: return
                case TokenType.IF: return
                case TokenType.WHILE: return
                case TokenType.PRINT: return
                case TokenType.RETURN: return
            self.advance()
    
    def comparison(self) -> Expr:
        expr: Expr = self.term()
        while (self.match([TokenType.GREATER, TokenType.GREATER_EQUAL, TokenType.LESS, TokenType.LESS_EQUAL])):
            operator: Token = self.previous()
            right: Expr = self.term()
            expr = Binary(expr, operator, right)
        return expr
    
    def term(self) -> Expr:
        expr: Expr = self.factor()
        while (self.match([TokenType.PLUS, TokenType.MINUS])):
            operator: Token = self.previous()
            right: Expr = self.factor()
            expr = Binary(expr, operator, right)
        return expr
    
    def factor(self) -> Expr:
        expr: Expr = self.unary()
        while (self.match([TokenType.SLASH, TokenType.STAR])):
            operator: Token = self.previous()
            right: Expr = self.unary()
            expr = Binary(expr, operator, right)
        return expr
    
    def unary(self) -> Expr:
        if (self.match([TokenType.BANG, TokenType.MINUS])):
            operator: Token = self.previous()
            right: Expr = self.unary()
            return Unary(operator, right)
        elif self.match([TokenType.EQUAL_EQUAL, TokenType.BANG_EQUAL]):
            operator = self.previous()
            self.error(operator, "Binary operator needs left and right operand")
            right = self.equality()
            return Binary(None, operator, right)
        elif self.match([TokenType.LESS, TokenType.LESS_EQUAL, TokenType.GREATER, TokenType.GREATER_EQUAL]):
            operator = self.previous()
            self.error(operator, "Binary operator needs left and right operand")
            right = self.comparison()
            return Binary(None, operator, right)
        elif self.match([TokenType.PLUS]):
            operator = self.previous()
            self.error(operator, "Binary operator needs left and right operand")
            right = self.term()
            return Binary(None, operator, right)
        elif self.match([TokenType.STAR, TokenType.SLASH]):
            operator = self.previous()
            self.error(operator, "Binary operator needs left and right operand")
            right = self.factor()
            return Binary(None, operator, right)
        return self.primary()

    def primary(self) -> Expr:
        if self.match([TokenType.FALSE]): return Literal(False)
        if self.match([TokenType.TRUE]): return Literal(True)
        if self.match([TokenType.NIL]): return Literal(None)
        if self.match([TokenType.NUMBER, TokenType.STRING]): return Literal(self.previous().literal)
        if self.match([TokenType.IDENTIFIER]): return Variable(self.previous())
        if self.match([TokenType.LEFT_PAREN]):
            expr: Expr = self.expression()
            self.consume(TokenType.RIGHT_PAREN, "Expect ')' after expression.")
            return Grouping(expr)
        raise self.error(self.peek(), "Expect exppression.")
    

    


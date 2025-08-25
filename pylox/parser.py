from __future__ import annotations
from pylox.tokens import Token
from pylox.expr import Expr, Binary, Unary, Literal, Grouping
from pylox.tokentype import TokenType
from pylox.error import ErrorReporter

class Parser:
    def __init__(self, tokens: list[Token]):
        self._tokens: list[Token] = tokens
        self.current: int = 0

    def parse(self):
        try: return self.expression()
        except Parser.ParseError: return None

    def expression(self) -> Expr:
        return self.equality()
    
    def equality(self) -> Expr:
        expr: Expr = self.comparison()
        while (self.match([TokenType.BANG_EQUAL, TokenType.EQUAL_EQUAL])):
            right: Expr = self.comparison()
            operator: Token = self.previous()
            expr = Binary(expr, operator, right)
        return expr

    def match(self, token_types: list[TokenType]) -> bool:
        for type in token_types:
            if self.check(type):
                self.advance()
                return True
        return False
    
    def consume(self, type: TokenType, message: str) -> None:
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
        ErrorReporter.error(token, message)
        return self.Parser.ParseError()
    
    def synchronize(self):
        self.advance()
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
        return self.primary()

    def primary(self) -> Expr:
        if self.match([TokenType.FALSE]): return Literal(False)
        if self.match([TokenType.TRUE]): return Literal(True)
        if self.match([TokenType.NIL]): return Literal(None)
        if self.match([TokenType.NUMBER, TokenType.STRING]): return Literal(self.previous().literal)
        if self.match([TokenType.LEFT_PAREN]):
            expr: Expr = self.expression()
            self.consume(TokenType.RIGHT_PAREN, "Expect ')' after expression.")
            return Grouping(expr)
        raise self.error(self.peek(), "Expect exppression.")
    

    


from __future__ import annotations
from typing import Optional
from pylox.tokens import Token
from pylox.expr import Expr, Binary, Unary, Literal, Grouping, Ternary, Variable, Assign, Logical, Call, Lambda, Get, Set, This, Super
from pylox.tokentype import TokenType
from pylox.error import ErrorReporter
from pylox.stmt import Stmt, Print, Expression, Var, Block, If, While, Break, Function, Return, Class
from pylox.environment import UnInitValue

class Parser:
    def __init__(self, tokens: list[Token]):
        self._tokens: list[Token] = tokens
        self.current: int = 0
        self.in_loop: bool = False

    def parse(self) -> list[Stmt]:
        statements = []
        while not self.is_at_end():
            stmt = self.declaration()
            if stmt is not None: statements.append(stmt)
        return statements

    def declaration(self) -> Optional[Stmt]:
        try:
            if self.match([TokenType.CLASS]): return self.class_declaration()
            if self.match([TokenType.FUN]): return self.function("function")
            if self.match([TokenType.VAR]): return self.var_declaration()
            return self.statement()
        except Parser.ParseError:
            self.synchronize()
            return None
        
    def class_declaration(self) -> Stmt:
        name: Token = self.consume(TokenType.IDENTIFIER, "Expect class name.")
        # superclass: Optional[Variable] = None
        superclasses: list[Variable] = []
        # if self.match([TokenType.LESS]):
        while not self.check(TokenType.LEFT_BRACE) and not self.is_at_end():
            self.consume(TokenType.LESS, "Expect '<' before superclass name.")
            self.consume(TokenType.IDENTIFIER, "Expect superclass name.")
            superclasses.append(Variable(self.previous()))
        self.consume(TokenType.LEFT_BRACE, "Expect '{' before class body.")
        methods: list[Function] = []
        class_methods: list[Function] = []
        while not self.check(TokenType.RIGHT_BRACE) and not self.is_at_end():
            if self.check(TokenType.CLASS):
                self.advance()
                class_methods.append(self.function("class_method"))
            else: methods.append(self.function("method"))
        self.consume(TokenType.RIGHT_BRACE, "Expect '}' after class body.")
        # for sc in superclasses: print(sc, "\n\n")
        return Class(name, superclasses, methods, class_methods)

    def function(self, kind: str) -> Function | Expression:
        is_getter: bool = False
        if not self.check(TokenType.IDENTIFIER):
            self.current -= 1
            return self.expression_statement()
        name: Optional[Token] = self.consume(TokenType.IDENTIFIER, f"Expect {kind} name.")
        parameters: list[Token] = []
        if not self.check(TokenType.LEFT_PAREN): is_getter = True
        else:
            self.consume(TokenType.LEFT_PAREN, f"Expect '(' after {kind} name.")
            if not self.check(TokenType.RIGHT_PAREN):
                while True:
                    if len(parameters) >= 255: self.error(self.peek(), "Can't have more than 255 parameters.")
                    param: Token | None = self.consume(TokenType.IDENTIFIER, "Expect parameter name.")
                    assert param is not None
                    parameters.append(param)
                    if not self.match([TokenType.COMMA]): break
            self.consume(TokenType.RIGHT_PAREN, "Expect ')' after parameters.")
        self.consume(TokenType.LEFT_BRACE, f"Expect '{{' before {kind} body.") # fstrings need double '{' to escape
        body: list[Stmt | None] = self.block()
        assert isinstance(name, Token)
        return Function(name, parameters, body, is_getter=is_getter)
    
    def var_declaration(self) -> Stmt:
        name: Optional[Token] = self.consume(TokenType.IDENTIFIER, "Expect variable name.")
        assert name is not None
        initializer: Optional[Expr] = None
        if self.match([TokenType.EQUAL]): initializer = self.expression()
        self.consume(TokenType.SEMICOLON, "Expect ';' after variable declaration.")
        if initializer is None: return Var(name, UnInitValue())
        return Var(name, initializer)

    def statement(self) -> Stmt:
        if self.match([TokenType.BREAK]): return self.break_statement()
        if self.match([TokenType.FOR]): return self.for_statement()
        if self.match([TokenType.IF]): return self.if_statement()
        if self.match([TokenType.PRINT]): return self.print_statement()
        if self.match([TokenType.RETURN]): return self.return_statement()
        if self.match([TokenType.WHILE]): return self.while_statement()
        if self.match([TokenType.LEFT_BRACE]): return Block(self.block())
        return self.expression_statement()
    
    def return_statement(self) -> Stmt:
        keyword: Token = self.previous()
        value: Expr | None = None
        if not self.check(TokenType.SEMICOLON): value = self.expression()
        self.consume(TokenType.SEMICOLON, "Expect ';' after return value.")
        return Return(keyword, value)
    
    def break_statement(self) -> Stmt:
        self.consume(TokenType.SEMICOLON, "Expect ';' after 'break'.")
        if not self.in_loop: raise self.error(self.peek(), "'break' only allowed inside loops.")
        return Break()
    
    def for_statement(self) -> Stmt: # desugaring into nodes the interpreter already 
        self.in_loop = True
        self.consume(TokenType.LEFT_PAREN, "Expect '(' after 'for'.")
        initializer: Optional[Stmt] = None
        if self.match([TokenType.SEMICOLON]): pass
        elif self.match([TokenType.VAR]): initializer = self.var_declaration()
        else: initializer = self.expression_statement()
        condition: Optional[Expr] = None
        if not self.check(TokenType.SEMICOLON): condition = self.expression()
        self.consume(TokenType.SEMICOLON, "Expect ';' after loop condition.")
        increment: Optional[Expr] = None
        if not self.check(TokenType.RIGHT_PAREN): increment = self.expression()
        self.consume(TokenType.RIGHT_PAREN, "Expect ')' after for clauses.")
        body: Stmt = self.statement()
        if increment is not None: body = Block([body, Expression(increment)])
        if condition is None: condition = Literal(True)
        body = While(condition, body)
        if initializer is not None: body = Block([initializer, body])
        self.in_loop = False
        return body
    
    def while_statement(self) -> Stmt:
        self.in_loop = True
        self.consume(TokenType.LEFT_PAREN, "Expect '(' after 'while'.")
        condition: Expr = self.expression()
        self.consume(TokenType.RIGHT_PAREN, "Expect ')' after 'while'.")
        body: Stmt = self.statement()
        self.in_loop = False
        return While(condition, body)
    
    def if_statement(self) -> Stmt:
        self.consume(TokenType.LEFT_PAREN, "Expect '(' after 'if'.")
        condition: Expr = self.expression()
        self.consume(TokenType.RIGHT_PAREN, "Expect ')' after 'if'.")
        then_branch: Stmt = self.statement()
        else_branch: Optional[Stmt] = None
        if self.match([TokenType.ELSE]): else_branch = self.statement()
        return If(condition, then_branch, else_branch)
    
    def block(self) -> list[Stmt | None]:
        statements: list[Stmt | None] = []
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
        expr: Expr = self.logical_or()
        if self.match([TokenType.EQUAL]):
            equals: Token = self.previous()
            value: Expr = self.assignment()
            if isinstance(expr, Variable): 
                name: Token = expr.name
                return Assign(name, value)
            elif isinstance(expr, Get):
                get: Get = expr
                return Set(get.obj, get.name, value)
            self.error(equals, "Invalid assignment target.")
        return expr
    
    def logical_or(self) -> Expr:
        expr: Expr = self.logical_and()
        while self.match([TokenType.OR]):
            operator: Token = self.previous()
            right: Expr = self.logical_and()
            expr = Logical(expr, operator, right)
        return expr
    
    def logical_and(self) -> Expr:
        expr: Expr = self.ternary()
        while self.match([TokenType.AND]):
            operator: Token = self.previous()
            right: Expr = self.ternary()
            expr = Logical(expr, operator, right)
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
        return self.call()
    
    def call(self) -> Expr:
        expr: Expr = self.primary()
        while True:
            if self.match([TokenType.LEFT_PAREN]): expr = self.finish_call(expr)
            elif self.match([TokenType.DOT]):
                name: Token = self.consume(TokenType.IDENTIFIER, "Expect propertyy name after '.'.")
                expr = Get(expr, name)
            else: break
        return expr
    
    def finish_call(self, callee: Expr) -> Expr:
        arguments: list[Expr] = []
        if not self.check(TokenType.RIGHT_PAREN):
            while True:
                if len(arguments) >= 255: self.error(self.peek(), "Can't have more than 255 arguments.")
                # arguments.append(self.expression())
                arguments.append(self.ternary()) # can't parse as expression() because comma will get parsed as comma() operator in function calls
                if not self.match([TokenType.COMMA]): break
        paren: Token | None = self.consume(TokenType.RIGHT_PAREN, "Expect ')' after arguments.")
        assert isinstance(paren, Token)
        return Call(callee, paren, arguments)

    def primary(self) -> Expr:
        if self.match([TokenType.FALSE]): return Literal(False)
        if self.match([TokenType.TRUE]): return Literal(True)
        if self.match([TokenType.NIL]): return Literal(None)
        if self.match([TokenType.NUMBER, TokenType.STRING]): return Literal(self.previous().literal)
        if self.match({TokenType.SUPER}):
            keyword: Token = self.previous()
            self.consume(TokenType.DOT, "Expect '.' after 'super'.")
            method: Token = self.consume(TokenType.IDENTIFIER, "Expect superclass method name.")
            return Super(keyword, method)
        if self.match([TokenType.THIS]): return This(self.previous())
        if self.match([TokenType.IDENTIFIER]): return Variable(self.previous())
        if self.match([TokenType.FUN]):
            kind: str = "lambda"
            self.consume(TokenType.LEFT_PAREN, f"Expect '(' after {kind} name.")
            parameters: list[Token] = []
            if not self.check(TokenType.RIGHT_PAREN):
                while True:
                    if len(parameters) >= 255: self.error(self.peek(), "Can't have more than 255 parameters.")
                    param: Token | None = self.consume(TokenType.IDENTIFIER, "Expect parameter name.")
                    assert param is not None
                    parameters.append(param)
                    if not self.match([TokenType.COMMA]): break
            self.consume(TokenType.RIGHT_PAREN, "Expect ')' after parameters.")
            self.consume(TokenType.LEFT_BRACE, f"Expect '{{' before {kind} body.") # fstrings need double '{' to escape
            body: list[Stmt | None] = self.block()
            return Lambda(parameters, body)
        if self.match([TokenType.LEFT_PAREN]):
            expr: Expr = self.expression()
            self.consume(TokenType.RIGHT_PAREN, "Expect ')' after expression.")
            return Grouping(expr)
        raise self.error(self.peek(), "Expect exppression.")
    

    


from dataclasses import dataclass
from pylox.tokens import Token
from pylox.tokentype import TokenType
# from pylox import Pylox
from pylox.error import ErrorReporter


@dataclass(frozen=True)
class ScannerData:
    _source: str
    _tokens: list[Token]

class Scanner:
    keywords: dict[str, TokenType] = {
        "and": TokenType.AND,
        "class": TokenType.CLASS,
        "else": TokenType.ELSE,
        "false": TokenType.FALSE,
        "for": TokenType.FOR,
        "fun": TokenType.FUN,
        "if": TokenType.IF,
        "nil": TokenType.NIL,
        "or": TokenType.OR,
        "print": TokenType.PRINT,
        "return": TokenType.RETURN,
        "super": TokenType.SUPER,
        "this": TokenType.THIS,
        "true": TokenType.TRUE,
        "var": TokenType.VAR,
        "while": TokenType.WHILE,
        "break": TokenType.BREAK,
    }

    def __init__(self, source: str):
        self._scanner_data = ScannerData(source, [])
        self.start: int = 0
        self.current: int = 0
        self.line: int = 0
        self.multi_line_comment_count: int = 0

    def scan_tokens(self) -> list[Token]:
        while not self.is_at_end():
            self.start = self.current # beginning of next lexeme
            self.scan_token()
        
        self._scanner_data._tokens.append(Token(TokenType.EOF, "", None, self.line))
        return self._scanner_data._tokens
    
    def is_at_end(self) -> bool:
        return self.current >= len(self._scanner_data._source)
    
    def scan_token(self) -> None:
        c: str = self.advance()
        match c:
            case '(': self.add_token(TokenType.LEFT_PAREN)
            case ')': self.add_token(TokenType.RIGHT_PAREN)
            case '{': self.add_token(TokenType.LEFT_BRACE)
            case '}': self.add_token(TokenType.RIGHT_BRACE)
            case ',': self.add_token(TokenType.COMMA)
            case '.': self.add_token(TokenType.DOT)
            case '-': self.add_token(TokenType.MINUS)
            case '+': self.add_token(TokenType.PLUS)
            case ';': self.add_token(TokenType.SEMICOLON)
            case "?": self.add_token(TokenType.QUESTION)
            case ":": self.add_token(TokenType.COLON)
            case '*':
                if self.multi_line_comment_count > 0 and self.match('/'): 
                    self.advance()
                    self.multi_line_comment_count -= 1
                elif self.multi_line_comment_count > 0: self.advance()
                else: self.add_token(TokenType.STAR)

            case '!': self.add_token(TokenType.BANG_EQUAL if self.match('=') else TokenType.BANG)
            case '=': self.add_token(TokenType.EQUAL_EQUAL if self.match('=') else TokenType.EQUAL)
            case '<': self.add_token(TokenType.LESS_EQUAL if self.match('=') else TokenType.LESS)
            case '>': self.add_token(TokenType.GREATER_EQUAL if self.match('=') else TokenType.GREATER)

            case '/':
                if self.match('/'): # single line comments start
                    while (self.peek() != '\n' and not self.is_at_end()): self.advance()
                elif self.match('*'): # multi line comments start
                    while ((self.peek() != '*' and self.peek() != '/') and not self.is_at_end()): self.advance()
                    self.multi_line_comment_count += 1
                else: self.add_token(TokenType.SLASH)

            case ' ': pass
            case '\r': pass
            case '\t': pass
            case '\n': self.line += 1

            case '"': self.string()

            case _: 
                if self.is_digit(c): self.number()
                elif self.is_alpha(c): self.identifier()
                else: ErrorReporter.error("Unexpected character.", line=self.line)

    def identifier(self):
        while self.is_alpha_numeric(self.peek()): self.advance()
        text = self._scanner_data._source[self.start:self.current]
        type = self.keywords.get(text)
        if type == None: type = TokenType.IDENTIFIER
        self.add_token(type)

    def is_alpha(self, c: str) -> bool:
        return (c >= 'a' and c <= 'z') or (c >= 'A' and c <= 'Z') or c == '_'
    
    def is_alpha_numeric(self, c: str) -> bool:
        return self.is_alpha(c) or self.is_digit(c)

    def is_digit(self, c: str) -> bool:
        return c >= '0' and c <= '9'
    
    def number(self):
        while self.is_digit(self.peek()): self.advance()
        if self.peek() == '.' and self.is_digit(self.peek_next()): # look for fractional part
            self.advance() # consumme the "."
            while self.is_digit(self.peek()): self.advance()
        self.add_token(TokenType.NUMBER, float(self._scanner_data._source[self.start:self.current]))

    def peek_next(self):
        if self.current + 1 >= len(self._scanner_data._source): return '\0'
        return self._scanner_data._source[self.current + 1]

    def string(self):
        while self.peek() != '"' and not self.is_at_end():
            if self.peek() == '\n': self.line += 1
            self.advance()
        if self.is_at_end(): 
            ErrorReporter.error(self.line, "Unterminated string.")
            return
        self.advance()
        value = self._scanner_data._source[self.start+1:self.current-1] # trim the surrounding quotes
        self.add_token(TokenType.STRING, value)

    def peek(self):
        if self.is_at_end(): return '\0'
        return self._scanner_data._source[self.current]

    def match(self, expected: str) -> bool:
        if self.is_at_end(): return False
        if self._scanner_data._source[self.current] != expected: return False
        self.current += 1
        return True

    def advance(self) -> str:
        c: str = self._scanner_data._source[self.current]
        self.current += 1 
        return c
    
    def add_token(self, type: TokenType, literal: object = None):
        text: str = self._scanner_data._source[self.start:self.current]
        self._scanner_data._tokens.append(Token(type, text, literal, self.line))




        
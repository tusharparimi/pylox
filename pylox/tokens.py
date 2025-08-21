from pylox.tokentype import TokenType
from dataclasses import dataclass

@dataclass(frozen=True)
class Token:
   token_type: TokenType
   lexeme: str
   literal: object
   line: int

   def to_string(self):
      return f"{self.token_type} {self.lexeme} {self.literal}"

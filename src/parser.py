from typing import Optional

from src.lexer import Lexer, Token


class Parser:
    def __init__(self, lexer: Lexer):
        self.lexer = lexer
        self.file_path = lexer.file_path
        self.current_token: Optional[Token] = None
        self.indent_level = 0

    @property
    def line_num(self) -> int:
        return self.current_token.line_num

    def next_token(self) -> Optional[Token]:
        token = self.current_token
        self.current_token = self.lexer.get_next_token()
        return token

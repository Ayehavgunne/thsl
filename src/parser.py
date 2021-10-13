from pathlib import Path
from pprint import pprint
from typing import Optional

from src.thsl_ast import Collection, Key, Value, AST
from src.grammar import TokenType, DataTypes
from src.lexer import Lexer, Token


class Parser:
    def __init__(self, file_path: Path) -> None:
        lexer = Lexer(file_path.open().read())
        self.tokens = lexer.parse()
        self.current_token = self.tokens[0]
        self.current_key = None
        self.current_data_type = None
        self.last_key = None
        self.pos = 0
        self._indent = 0
        self.stack = []

    @property
    def line(self) -> int:
        return self.current_token.line

    @property
    def indent(self) -> int:
        if self.current_token.type == TokenType.NEWLINE:
            return self._indent
        return self.current_token.indent

    @property
    def column(self) -> int:
        return self.current_token.column

    @property
    def value(self) -> str:
        return self.current_token.value

    @property
    def type(self) -> TokenType:
        return self.current_token.type

    @property
    def len(self) -> int:
        return len(self.tokens)

    def set_indent(self):
        if self.indent != self._indent:
            self._indent = self.indent

    def next_token(self) -> Token:
        # print(self.current_token)
        if self.type == TokenType.EOF:
            return self.current_token
        token = self.current_token
        self.pos += 1
        self.current_token = self.tokens[self.pos]
        return token

    def preview(self, num: int = 1) -> Token:
        preview_pos = self.pos + num
        if preview_pos >= self.len:
            preview_pos = self.len - 1
        return self.tokens[preview_pos]

    def parse(self) -> Collection:
        root = Collection(line=self.line, column=self.column)
        while self.type != TokenType.EOF:
            comp = self.compound_statement()
            root.items.extend(comp.items)
        return root

    def compound_statement(self) -> Collection:
        nodes = self.statement_list()
        root = Collection(line=self.line, column=self.column)
        for node in nodes:
            root.items.append(node)
        return root

    def statement_list(self) -> list[AST]:
        results = []
        self.set_indent()
        _indent = self._indent
        while self.indent == _indent:
            results.append(self.statement())
            if self.type == TokenType.NEWLINE:
                self.next_token()
            if self.type == TokenType.EOF:
                break
        self.set_indent()
        results = [result for result in results if result is not None]
        return results

    def statement(self) -> Optional[AST]:
        statement = None
        if self.type == TokenType.KEY:
            statement = self.eat_key()
        return statement

    def eat_key(self) -> Optional[Key]:
        name = self.value
        self.next_token()
        key_type = self.eat_type()
        self.next_token()
        if self.indent > self._indent:
            self.set_indent()
            value = self.compound_statement()
            self.set_indent()
        else:
            value = self.eat_value()
        return Key(
            name=name,
            type=key_type,
            items=value,
            line=self.line,
            column=self.column,
        )

    def eat_type(self) -> DataTypes:
        if self.type == TokenType.NEWLINE:
            return DataTypes.DICT
        return DataTypes(self.value)

    def eat_value(self) -> Value:
        value = Value(value=self.value, line=self.line, column=self.column)
        self.next_token()
        return value


if __name__ == "__main__":
    file = Path("../test.thsl")
    parser = Parser(file)
    pprint(parser.parse())

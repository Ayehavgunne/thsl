from pathlib import Path
from pprint import pprint
from typing import Optional

from src.thsl_ast import Collection, Key, Value, AST, Void
from src.grammar import TokenType, DataTypes, Operators
from src.lexer import Lexer, Token


class Parser:
    def __init__(self, file_path: Path | str) -> None:
        if isinstance(file_path, Path):
            file_path = file_path.open().read()
        self._lexer = Lexer(file_path)
        self.tokens = self._lexer.parse()
        self.current_token = self.tokens[0]
        self.current_key = None
        self.current_data_type = None
        self.last_key = None
        self.pos = 0
        self._indent = 0
        self.stack = []

    @property
    def user_types(self) -> list[str]:
        return self._lexer.user_types

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
        root = Collection(type=DataTypes.DICT, line=self.line, column=self.column)
        while self.type != TokenType.EOF:
            statements = self.statement_list()
            root.items.extend(statements)
        return root

    def make_collection(self, collection_type: DataTypes) -> Collection:
        return Collection(
            items=self.statement_list(),
            type=collection_type,
            line=self.line,
            column=self.column,
        )

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
        if self.type == TokenType.VALUE:
            statement = self.eat_value()
        return statement

    def eat_key(self) -> Optional[Key]:
        name = self.value
        self.next_token()
        key_type = self.eat_type()
        self.next_token()
        if self.type == TokenType.OPERATOR:
            value = self.eat_operator()
        elif self.indent > self._indent:
            self.set_indent()
            value = self.make_collection(key_type)
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
        if self.value == TokenType.NEWLINE.value:
            value = Void(line=self.line, column=self.column)
        else:
            value = self.value
        value = Value(value=value, line=self.line, column=self.column)
        self.next_token()
        return value

    def eat_operator(self) -> Collection:
        value = Collection(type=self.value, line=self.line, column=self.column)
        if self.value == Operators.LSQUAREBRACKET.value:
            closing_operator = Operators.RSQUAREBRACKET.value
        elif self.value == Operators.LANGLEBRACKET.value:
            closing_operator = Operators.RANGLEBRACKET.value
        elif self.value == Operators.LCURLYBRACKET.value:
            closing_operator = Operators.RCURLYBRACKET.value
        elif self.value == Operators.LPAREN.value:
            closing_operator = Operators.RPAREN.value
        else:
            raise NotImplementedError
        self.next_token()
        while self.value != closing_operator:
            while self.type == TokenType.NEWLINE:
                self.next_token()
            if (
                self.type == TokenType.OPERATOR
                and self.value == Operators.LIST_DELIMITER.value
            ):
                self.next_token()
            if self.value == closing_operator:
                self.next_token()
                break
            value.items.append(self.eat_value())
        if self.value == closing_operator:
            self.next_token()
        return value


if __name__ == "__main__":
    file = Path("../test.thsl")
    parser = Parser(file)
    pprint(parser.parse())

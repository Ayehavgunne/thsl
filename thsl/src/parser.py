from pathlib import Path

from thsl.src.abstract_syntax_tree import AST, Collection, Key, Value, Void
from thsl.src.grammar import (
    COMPOUND_ITEM_VALUES,
    CompoundDataType,
    DataType,
    Operator,
    ScalarDataType,
    TokenType,
)
from thsl.src.lexer import Lexer, Token


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

    def parse(self) -> Collection:
        root = Collection(
            type=CompoundDataType.DICT,
            line=self.line,
            column=self.column,
        )
        while self.type != TokenType.EOF:
            statements = self.statement_list()
            root.items.extend(statements)
        return root

    @property
    def user_types(self) -> list[str]:
        return self._lexer.user_types

    @property
    def line(self) -> int:
        return self.current_token.line

    @property
    def current_token_indent(self) -> int:
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

    def set_indent(self) -> None:
        if self.current_token_indent != self._indent:
            self._indent = self.current_token_indent

    def next_token(self) -> Token:
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

    def make_collection(self, collection_type: DataType) -> Collection:
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
        while self.current_token_indent == _indent:
            if statement := self.statement():
                results.append(statement)
            if self.type == TokenType.NEWLINE or (
                self.type == TokenType.OPERATOR
                and self.current_token.value in COMPOUND_ITEM_VALUES
            ):
                self.next_token()
            if self.type == TokenType.EOF:
                break
        self.set_indent()
        results = [result for result in results if result is not None]
        return results

    def statement(self) -> AST | None:
        if self.type == TokenType.KEY:
            return self.eat_key()
        if self.type == TokenType.VALUE:
            return self.eat_value()
        if self.type == TokenType.TYPE:
            value_type = self.eat_type()
            self.next_token()
            value = self.eat_value()
            value.type = value_type
            return value
        if self.type == TokenType.OPERATOR and self.value not in (
            Operator.LIST_DELIMITER.value,
            Operator.RCURLYBRACKET.value,
        ):
            return self.eat_operator()
        self.next_token()
        return None

    def eat_key(self) -> Key:
        name = self.value
        self.next_token()
        subtype = None
        key_type = self.eat_type()
        self.next_token()
        value: Value | Collection
        upcoming_token = self.preview(1)
        if (
            key_type == CompoundDataType.DICT or key_type == CompoundDataType.UNKNOWN
        ) and self.type == TokenType.NEWLINE:
            self.next_token()
        if (
            key_type == CompoundDataType.DICT or key_type == CompoundDataType.UNKNOWN
        ) and self.type == TokenType.KEY:
            value = self.make_collection(key_type)
        elif self.type == TokenType.OPERATOR:
            value = self.eat_operator()
        elif self.current_token_indent > self._indent:
            self.set_indent()
            value = self.make_collection(key_type)
            self.set_indent()
        elif (
            self.type == TokenType.NEWLINE and upcoming_token.type == TokenType.OPERATOR
        ):
            self.next_token()
            if self.current_token.value in COMPOUND_ITEM_VALUES:
                value = self.eat_operator()
            else:
                self.next_token()
                subtype = key_type
                key_type = CompoundDataType.LIST
                value = self.make_collection(key_type)
        else:
            value = self.eat_value()
        return Key(
            name=name,
            type=key_type,
            items=value,
            line=self.line,
            column=self.column,
            subtype=subtype,
        )

    def eat_type(self) -> DataType:
        if self.type == TokenType.NEWLINE or self.value == Operator.LCURLYBRACKET.value:
            return CompoundDataType.DICT
        if self.value in ScalarDataType.values():
            return ScalarDataType(self.value)
        return CompoundDataType(self.value)

    def eat_value(self) -> Value:
        value: str | Void
        if self.value == TokenType.NEWLINE.value:
            value = Void(line=self.line, column=self.column)
        else:
            value = self.value
        ret_value = Value(value=value, line=self.line, column=self.column)
        self.next_token()
        return ret_value

    def eat_operator(self) -> Collection:
        value = Collection(type=self.value, line=self.line, column=self.column)
        if self.value in COMPOUND_ITEM_VALUES:
            value.items.extend(self.eat_iterator_items())
            return value
        if self.value == Operator.LSQUAREBRACKET.value:
            closing_operator = Operator.RSQUAREBRACKET.value
        elif self.value == Operator.LANGLEBRACKET.value:
            closing_operator = Operator.RANGLEBRACKET.value
        elif self.value == Operator.LCURLYBRACKET.value:
            closing_operator = Operator.RCURLYBRACKET.value
        elif self.value == Operator.LPAREN.value:
            closing_operator = Operator.RPAREN.value
        else:
            raise NotImplementedError
        self.next_token()
        while self.value != closing_operator:
            while self.type == TokenType.NEWLINE:
                self.next_token()
            if (
                self.type == TokenType.OPERATOR
                and self.value == Operator.LIST_DELIMITER.value
            ):
                self.next_token()
            if self.value == closing_operator:
                self.next_token()
                break
            if self.current_token.type == TokenType.KEY:
                value.items.append(self.eat_key())
            else:
                value.items.append(self.eat_value())
        if self.value == closing_operator:
            self.next_token()
        return value

    def eat_iterator_items(self) -> list[AST]:
        current_indent = self.current_token_indent
        items: list[AST] = []
        self.set_indent()
        while self.current_token_indent == current_indent:
            self.next_token()
            if self.current_token.value in COMPOUND_ITEM_VALUES:
                self.next_token()
            if self.current_token.type == TokenType.VALUE:
                items.append(self.eat_value())
            elif self.current_token.type == TokenType.OPERATOR:
                items.append(self.eat_operator())
            else:
                statement = self.statement()
                if statement:
                    items.append(statement)
        return [item for item in items if item is not None]

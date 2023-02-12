from collections.abc import Iterator
from dataclasses import dataclass, field
from enum import auto, Enum
from typing import Literal

from thsl.src.grammar import (
    ALL_DATA_TYPE_VALUES,
    CLOSING_BRACKET_VALUES,
    CompoundDataType,
    DataType,
    MULTI_CHAR_OPERATORS,
    Operator,
    OPERATORS_TO_IGNORE,
    OTHER_NUMERIC_CHARACTERS,
    ScalarDataType,
    TokenType,
)


@dataclass
class TokenMetaData:
    single_quote: bool
    double_quote: bool


@dataclass
class Token:
    type: TokenType
    value: str
    line: int
    indent: int
    column: int = field(compare=False, default=0)
    meta_data: TokenMetaData | None = field(compare=False, default=None)

    def __str__(self) -> str:
        return f"Token(type={self.type.name}, value={self.value!r}, line={self.line})"


class TypeState(Enum):
    DICT = auto()
    LIST = auto()
    SET = auto()
    TUPLE = auto()


@dataclass
class Homogeneous:
    type: DataType | None


@dataclass
class Heterogeneous:
    def __eq__(self, other: object) -> bool:
        if self.__class__ == other:
            return True
        return super().__eq__(other)


TypeContentState = Homogeneous | Heterogeneous


@dataclass
class LexerState:
    type: TypeState = TypeState.DICT
    contents: TypeContentState = field(default_factory=lambda: Heterogeneous())


class Lexer:
    def __init__(self, text: str) -> None:
        self._pos: int
        self._column: int
        self._current_char: str | None
        self._char_type: TokenType | None
        self._current_token: Token | None
        self._current_data_type: DataType | None
        self._last_data_type: DataType | None
        self._current_key: Token | None
        self._word: str
        self._word_type: TokenType | None
        self._line_num: int
        self._indent_level: int
        self._type_stack = [LexerState()]
        self.user_types: list[str]
        self.text = text

    def parse(self) -> list[Token]:
        return list(self.analyze())

    def analyze(self) -> Iterator[Token]:
        token = self._get_next_token()
        while token.type != TokenType.EOF:
            yield token
            token = self._get_next_token()
        yield token

    @property
    def text(self) -> str:
        return self._text

    @text.setter
    def text(self, text: str) -> None:
        self._text = text
        self._pos = 0
        self._current_char = self.text[self._pos]
        self._line_num = 1
        self._indent_level = 0
        self._word = ""
        self._word_type = None
        self._column = 1
        self._char_type = None
        self._current_token = None
        self._last_data_type = None
        self._current_data_type = None
        self._current_key = None
        self.user_types = []

    @property
    def _current_state(self) -> LexerState:
        return self._type_stack[-1]

    @property
    def _len(self) -> int:
        return len(self._text)

    def _make_token(
        self,
        token_type: TokenType,
        value: str,
        line_num: int | None = None,
        meta_data: TokenMetaData | None = None,
    ) -> Token:
        if not line_num:
            line_num = self._line_num
        return Token(
            type=token_type,
            value=value,
            line=line_num,
            column=self._column,
            indent=self._indent_level,
            meta_data=meta_data,
        )

    def _next_char(self) -> None:
        self._pos += 1
        self._column += 1
        if self._pos > self._len - 1:
            self._current_char = None
            self._char_type = None
        else:
            self._current_char = self.text[self._pos]
            self._char_type = self._get_type(self._current_char)

    def _skip_char(self) -> None:
        self._pos += 1
        self._column += 1
        if self._pos > self._len - 1:
            self._current_char = None
            self._char_type = None
        else:
            self._current_char = self.text[self._pos]

    def _reset_word(self) -> str:
        old_word = self._word
        self._word = ""
        self._word_type = None
        return old_word

    def _peek(self, num: int, ignore_whitespace: bool = False) -> str | None:
        peek_pos = self._pos + num
        if ignore_whitespace:
            while (
                peek_pos < self._len - 1
                and self.text[peek_pos].isspace()
                and self.text[peek_pos] != TokenType.NEWLINE.value
            ):
                peek_pos += 1
            return self.text[peek_pos]
        if peek_pos > self._len - 1:
            return None
        return self.text[peek_pos]

    def preview_token(self, num: int = 1) -> Token | None:
        if num < 1:
            raise ValueError("num argument must be 1 or greater")
        next_token = None
        current_pos = self._pos
        current_char = self._current_char
        current_char_type = self._char_type
        current_word = self._word
        current_word_type = self._word_type
        current_line_num = self._line_num
        current_indent_level = self._indent_level
        current_last_data_type = self._last_data_type
        current_current_data_type = self._current_data_type
        current_column = self._column
        current_current_token = self._current_token
        current_current_key = self._current_key
        for _ in range(num):
            next_token = self._get_next_token()
        self._pos = current_pos
        self._current_char = current_char
        self._char_type = current_char_type
        self._word = current_word
        self._word_type = current_word_type
        self._line_num = current_line_num
        self._indent_level = current_indent_level
        self._last_data_type = current_last_data_type
        self._current_data_type = current_current_data_type
        self._column = current_column
        self._current_token = current_current_token
        self._current_key = current_current_key
        return next_token

    def _skip_whitespace(self) -> None:
        if self._peek(-1) == TokenType.NEWLINE.value:
            raise SyntaxError("Only tab characters can indent")
        while self._current_char is not None and self._current_char.isspace():
            self._next_char()
            self._reset_word()

    def _skip_comment(self) -> Token:
        while self._current_char != TokenType.NEWLINE.value:
            self._skip_char()
            if self._current_char is None:
                return self._eof()
        return self._eat_newline()

    def _increment_line_num(self) -> None:
        self._line_num += 1

    def _eat_newline(self) -> Token:
        self._reset_word()
        token = self._make_token(
            TokenType.NEWLINE,
            TokenType.NEWLINE.value,
        )
        self._column = 0
        self._indent_level = 0
        self._increment_line_num()
        self._last_data_type = self._current_data_type
        self._current_data_type = None
        self._current_key = None
        self._next_char()
        return token

    def _skip_indent(self) -> None:
        while (
            self._current_char is not None
            and self._current_char == TokenType.INDENT.value
        ):
            self._reset_word()
            self._indent_level += 1
            self._next_char()

    def _eof(self) -> Token:
        return self._make_token(
            TokenType.EOF,
            TokenType.EOF.value,
        )

    def _eat_rest_of_line(self) -> Token:
        if self._current_char == Operator.SINGLE_QUOTE.value:
            return self._eat_string(Operator.SINGLE_QUOTE)
        if self._current_char == Operator.DOUBLE_QUOTE.value:
            return self._eat_string(Operator.DOUBLE_QUOTE)
        while (
            self._current_char != TokenType.NEWLINE.value
            and self._current_char != TokenType.COMMENT.value
        ):
            if (
                self._current_char == TokenType.ESCAPE.value
                and self._peek(1) == TokenType.NEWLINE.value
            ):
                self._next_char()
            if self._current_char is not None:
                self._word += self._current_char
            self._next_char()
        self._word = self._word.strip()
        return self._eat_value(
            self._reset_word(),
        )

    def _eat_string(
        self,
        quote: Literal[Operator.DOUBLE_QUOTE, Operator.SINGLE_QUOTE],
    ) -> Token:
        self._next_char()
        while self._current_char != quote.value:
            if (
                self._current_char == TokenType.ESCAPE.value
                and self._peek(1) == quote.value
            ):
                self._next_char()
            if self._current_char == TokenType.NEWLINE.value:
                self._line_num += 1
            if self._current_char is not None:
                self._word += self._current_char
            self._next_char()
        self._next_char()
        if not self._current_key:
            token = self._eat_key(
                self._reset_word(),
            )
            self._current_key = token
            return token
        return self._eat_value(
            self._reset_word(),
            meta_data=TokenMetaData(quote.value == "'", quote.value == '"'),
        )

    def _eat_operator(self, value: str | None = None) -> Token:
        if value:
            token = self._make_token(TokenType.OPERATOR, value)
        else:
            if (
                self._current_char in MULTI_CHAR_OPERATORS
                and self.preview_token(1).value in MULTI_CHAR_OPERATORS  # type: ignore
            ):
                self._next_char()
                self._word += " "
                while (
                    self._char_type == TokenType.ALPHANUMERIC
                    or self._char_type == TokenType.NUMBER
                ):
                    if self._current_char is not None:
                        self._word += self._current_char
                    self._next_char()
                token = self._make_token(TokenType.OPERATOR, self._reset_word())
            else:
                if self._current_char in Operator.values():
                    self._word += self._current_char
                    self._next_char()
                token = self._make_token(
                    TokenType.OPERATOR,
                    self._reset_word(),
                )

        if token.value == Operator.LIST_DELIMITER.value:
            self._current_data_type = None

        type_content_state: TypeContentState

        if (
            self._current_data_type is not None
            and token.value not in CLOSING_BRACKET_VALUES
        ):
            type_content_state = Homogeneous(self._current_data_type)
        else:
            type_content_state = Heterogeneous()

        if token.value in CLOSING_BRACKET_VALUES:
            self._current_data_type = None

        type_content_state = self.set_type_stack(token.value, type_content_state)

        if token.value == Operator.RSQUAREBRACKET.value:
            if self._current_state.type != TypeState.LIST:
                raise SyntaxError
            self._type_stack.pop()
        if token.value == Operator.RANGLEBRACKET.value:
            if self._current_state.type != TypeState.SET:
                raise SyntaxError
            if not isinstance(type_content_state, Homogeneous):
                self._type_stack.pop()
        if token.value == Operator.RCURLYBRACKET.value:
            if self._current_state.type != TypeState.DICT:
                raise SyntaxError
            self._type_stack.pop()
        if token.value == Operator.RPAREN.value:
            if self._current_state.type != TypeState.TUPLE:
                raise SyntaxError
            if not isinstance(type_content_state, Homogeneous):
                self._type_stack.pop()
        return token

    def set_type_stack(
        self,
        value: str,
        type_content_state: TypeContentState,
    ) -> TypeContentState:
        if value == Operator.LCURLYBRACKET.value:
            self._type_stack.append(LexerState(TypeState.DICT, type_content_state))

        if value == Operator.LSQUAREBRACKET.value:
            self._type_stack.append(LexerState(TypeState.LIST, type_content_state))

        if value == Operator.LIST_ITEM.value:
            type_content_state = Homogeneous(self._last_data_type)
            self._type_stack.append(LexerState(TypeState.LIST, type_content_state))
            preview = self.preview_token()
            if preview.type == TokenType.NEWLINE:
                self.insert_str_to_text(" :", 1)

        if value == Operator.LANGLEBRACKET.value:
            self._type_stack.append(LexerState(TypeState.SET, type_content_state))

        if value == Operator.SET_ITEM.value:
            type_content_state = Homogeneous(self._last_data_type)
            self._type_stack.append(LexerState(TypeState.SET, type_content_state))
            preview = self.preview_token()
            if preview.type == TokenType.NEWLINE:
                self.insert_str_to_text(" :", 1)

        if value == Operator.LPAREN.value:
            self._type_stack.append(LexerState(TypeState.TUPLE, type_content_state))

        if value == Operator.TUPLE_ITEM.value:
            type_content_state = Homogeneous(self._last_data_type)
            self._type_stack.append(LexerState(TypeState.TUPLE, type_content_state))
            preview = self.preview_token()
            if preview.type == TokenType.NEWLINE:
                self.insert_str_to_text(" :", 1)
        return type_content_state

    def insert_str_to_text(self, chars: str, change_pos: int = 0) -> None:
        first = self.text[: self._pos]
        second = self.text[self._pos :]
        text = f"{first}{chars}{second}"
        self._text = text
        self._pos += change_pos
        self._current_char = self.text[self._pos]

    def _eat_type(self, value: str | None = None) -> Token:
        if value:
            return self._make_token(TokenType.TYPE, value)
        if self._current_char == Operator.TYPE_INITIATOR.value:
            self._next_char()
        while (
            self._char_type == TokenType.ALPHANUMERIC
            or self._char_type == TokenType.NUMBER
        ):
            if self._current_char == Operator.VALUE_DELIMITER.value:
                break
            if self._current_char is not None:
                self._word += self._current_char
            self._next_char()

        if self._word in ScalarDataType.values():
            self._current_data_type = ScalarDataType(self._word)
        else:
            self._current_data_type = CompoundDataType(self._word)

        if self._word in self.user_types:
            return self._make_token(
                TokenType.TYPE,
                self._reset_word(),
            )
        if self._word in ALL_DATA_TYPE_VALUES:
            return self._make_token(
                TokenType.TYPE,
                self._reset_word(),
            )
        raise SyntaxError("Expected a type")

    def _eat_alpha(self) -> Token:
        while (
            self._char_type == TokenType.ALPHANUMERIC
            or self._char_type == TokenType.NUMBER
        ):
            if self._current_char is not None:
                self._word += self._current_char
            self._next_char()

        if self._current_data_type in (ScalarDataType.FLOAT, ScalarDataType.DEC):
            return self._eat_number()
        if self._word in Operator.values():
            return self._eat_operator()
        if self._current_data_type:
            return self._eat_value(self._reset_word())
        return self._eat_key()

    def _eat_key(self, value: str | None = None) -> Token:
        if value:
            token = self._make_token(TokenType.KEY, value)
        else:
            while (
                self._char_type == TokenType.ALPHANUMERIC
                or self._char_type == TokenType.NUMBER
            ):
                if self._current_char is not None:
                    self._word += self._current_char
                self._next_char()
            token = self._make_token(TokenType.KEY, self._reset_word())
        self._current_key = token
        return token

    def _eat_value(self, value: str, meta_data: TokenMetaData | None = None) -> Token:
        return self._make_token(TokenType.VALUE, value, meta_data=meta_data)

    def _eat_number(self) -> Token:
        while (
            self._char_type == TokenType.NUMBER
            or self._current_char in OTHER_NUMERIC_CHARACTERS
        ):
            if self._current_char in OPERATORS_TO_IGNORE:
                self._skip_char()
            if self._current_char is not None:
                self._word += self._current_char
            self._next_char()
        return self._eat_value(
            self._reset_word(),
        )

    def _eat_escape(self) -> Token:
        self._reset_word()
        self._next_char()
        line_num = self._line_num
        if self._current_char == TokenType.NEWLINE.value:
            self._increment_line_num()
        self._next_char()
        return self._make_token(
            TokenType.ESCAPE,
            TokenType.ESCAPE.value,
            line_num,
        )

    @staticmethod
    def _get_type(char: str) -> TokenType:
        if char.isspace():
            return TokenType.WHITESPACE
        if char == TokenType.COMMENT.value:
            return TokenType.COMMENT
        if char == TokenType.ESCAPE.value:
            return TokenType.ESCAPE
        if char == Operator.MINUS.value:
            return TokenType.ALPHANUMERIC
        if char in Operator.values():
            return TokenType.OPERATOR
        if char.isdigit():
            return TokenType.NUMBER
        if char == "":
            return TokenType.EMPTY
        return TokenType.ALPHANUMERIC

    def _get_next_token(self) -> Token:
        if (
            self._current_char == Operator.LIST_DELIMITER.value
            and self._peek(1) == Operator.LIST_DELIMITER.value
        ):
            raise SyntaxError(
                f"Exected value line={self._line_num} column={self._column + 1}",
            )

        if self._current_char is None:
            return self._eof()

        if self._current_char == Operator.VALUE_DELIMITER.value:
            peek = self._peek(1, ignore_whitespace=True)
            if self._current_data_type is None and (
                peek == TokenType.NEWLINE.value or peek == TokenType.COMMENT.value
            ):
                self._next_char()
                return self._make_token(TokenType.TYPE, CompoundDataType.UNKNOWN.value)
            self._skip_char()

        if self._current_char == TokenType.NEWLINE.value:
            return self._eat_newline()
        if self._current_char == TokenType.INDENT.value:
            self._skip_indent()

        if self._current_char.isspace():
            self._skip_whitespace()

        if self._current_char == TokenType.COMMENT.value:
            return self._skip_comment()

        if (
            self._current_data_type is None
            and self._current_char == Operator.TYPE_INITIATOR.value
        ):
            return self._eat_type()

        if self._current_char == Operator.DOUBLE_QUOTE.value:
            return self._eat_string(Operator.DOUBLE_QUOTE)

        if self._current_char == Operator.SINGLE_QUOTE.value:
            return self._eat_string(Operator.SINGLE_QUOTE)

        if not self._char_type:
            self._char_type = self._get_type(self._current_char)
        if not self._word_type:
            self._word_type = self._char_type

        if isinstance(self._current_state.contents, Homogeneous):
            self._current_data_type = self._current_state.contents.type

        if self._word_type == TokenType.OPERATOR and self._current_data_type not in (
            ScalarDataType.PATH,
            ScalarDataType.REGEX,
        ):
            return self._eat_operator()

        if self._current_data_type in (
            ScalarDataType.STR,
            ScalarDataType.DATE,
            ScalarDataType.DATETIME,
            ScalarDataType.TIME,
            ScalarDataType.INTERVAL,
            ScalarDataType.URL,
            ScalarDataType.IP_ADDRESS,
            ScalarDataType.IP_NETWORK,
            ScalarDataType.BASE64,
            ScalarDataType.BASE64E,
            ScalarDataType.RANGE,
            ScalarDataType.PATH,
            ScalarDataType.REGEX,
        ):
            return self._eat_rest_of_line()

        if self._word_type == TokenType.ALPHANUMERIC:
            return self._eat_alpha()

        if (
            self._current_state.type in (TypeState.LIST, TypeState.SET, TypeState.TUPLE)
            and not isinstance(self._current_state.contents, Heterogeneous)
            and self._word_type == TokenType.NUMBER
        ):
            return self._eat_number()

        if self._current_key is None:
            return self._eat_key()

        if self._word_type == TokenType.NUMBER:
            return self._eat_number()

        if self._char_type == TokenType.ESCAPE:
            return self._eat_escape()

        raise SyntaxError("Unknown character")

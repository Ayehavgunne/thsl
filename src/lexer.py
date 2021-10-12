from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, Iterator, Literal

from src.grammar import (
    TokenType,
    DataTypes,
    Operators,
    OPERATORS_TO_IGNORE,
    MULTI_CHAR_OPERATORS,
    OTHER_NUMERIC_CHARACTERS,
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
    meta_data: Optional[TokenMetaData] = field(compare=False, default=None)

    def __str__(self):
        return (
            f"Token("
            f"type={self.type.name}, "
            f"value={self.value!r}, "
            f"line={self.line}"
            f")"
        )


class Lexer:
    def __init__(self, text: str) -> None:
        self._pos: int
        self._column: int
        self._current_char: Optional[str]
        self._char_type: Optional[TokenType]
        self._current_token: Optional[Token]
        self._current_data_type: Optional[DataTypes]
        self._current_key: Optional[Token]
        self._current_operator: Optional[Operators]
        self._word: str
        self._word_type: Optional[TokenType]
        self._line_num: int
        self._indent_level: int
        self.new_types: list[str]
        self.text = text

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
        self._current_data_type = None
        self._current_key = None
        self._current_operator = None
        self.new_types = []

    def _make_token(
        self,
        token_type: TokenType,
        value: str,
        line_num: int = None,
        meta_data: TokenMetaData = None,
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
        if self._pos > len(self.text) - 1:
            self._current_char = None
            self._char_type = None
        else:
            self._current_char = self.text[self._pos]
            self._char_type = self._get_type(self._current_char)

    def _skip_char(self) -> None:
        self._pos += 1
        self._column += 1
        if self._pos > len(self.text) - 1:
            self._current_char = None
            self._char_type = None
        else:
            self._current_char = self.text[self._pos]

    def _reset_word(self) -> str:
        old_word = self._word
        self._word = ""
        self._word_type = None
        return old_word

    def _peek(self, num: int, ignore_whitespace: bool = False) -> Optional[str]:
        peek_pos = self._pos + num
        if ignore_whitespace:
            while peek_pos > len(self.text) - 1 and self.text[peek_pos].isspace():
                peek_pos += 1
            return self.text[peek_pos]
        if peek_pos > len(self.text) - 1:
            return None
        else:
            return self.text[peek_pos]

    def preview_token(self, num: int = 1) -> Optional[Token]:
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
        for _ in range(num):
            next_token = self._get_next_token()
        self._pos = current_pos
        self._current_char = current_char
        self._char_type = current_char_type
        self._word = current_word
        self._word_type = current_word_type
        self._line_num = current_line_num
        self._indent_level = current_indent_level
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
        if self._current_char == Operators.SINGLE_QUOTE.value:
            return self._eat_string(Operators.SINGLE_QUOTE)
        if self._current_char == Operators.DOUBLE_QUOTE.value:
            return self._eat_string(Operators.DOUBLE_QUOTE)
        while (
            self._current_char != TokenType.NEWLINE.value
            and self._current_char != TokenType.COMMENT.value
        ):
            if (
                self._current_char == TokenType.ESCAPE.value
                and self._peek(1) == TokenType.NEWLINE.value
            ):
                self._next_char()
            self._word += self._current_char
            self._next_char()
        self._word = self._word.strip()
        return self._eat_value(
            self._reset_word(),
        )

    def _eat_string(
        self,
        quote: Literal[Operators.DOUBLE_QUOTE, Operators.SINGLE_QUOTE],
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

    def _eat_operator(self, value: str = None) -> Token:
        if value:
            return self._make_token(TokenType.OPERATOR, value)
        if self._current_char == Operators.MINUS.value:
            if self._get_type(self._peek(1)) == TokenType.ALPHANUMERIC:
                return self._eat_rest_of_line()
            else:
                return self._eat_number()
        while self._current_char in Operators.values():
            self._word += self._current_char
            self._next_char()
        self._current_operator = Operators(self._word)
        return self._make_token(
            TokenType.OPERATOR,
            self._reset_word(),
        )
        # if (
        #     self.word in MULTI_CHAR_OPERATORS
        #     and self.preview_token(1).value in MULTI_CHAR_OPERATORS
        # ):
        #     self.next_char()
        #     self.word += " "
        #     while (
        #             self.char_type == TokenType.ALPHANUMERIC
        #             or self.char_type == TokenType.NUMBER
        #     ):
        #         self.word += self.current_char
        #         self.next_char()
        #     token = self.make_token(TokenType.OPERATOR, self.reset_word())
        # else:
        #     token = self.make_token(TokenType.OPERATOR, self.reset_word())
        # self._current_operator = Operators(self.word)
        # return token

    def _eat_type(self, value: str = None) -> Token:
        if value:
            return self._make_token(TokenType.TYPE, value)
        if self._current_char == Operators.DOT.value:
            self._next_char()
        while (
            self._char_type == TokenType.ALPHANUMERIC
            or self._char_type == TokenType.NUMBER
        ):
            if self._current_char == Operators.VALUE_DELIMITER.value:
                break
            self._word += self._current_char
            self._next_char()

        self._current_data_type = DataTypes(self._word)

        if self._word in self.new_types:
            return self._make_token(
                TokenType.TYPE,
                self._reset_word(),
            )
        if self._word in DataTypes.values():
            if self._current_key and self._current_data_type == DataTypes.STRUCT:
                self.new_types.append(self._current_key.value)
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
            self._word += self._current_char
            self._next_char()

        if self._word in Operators.values():
            if (
                self._word in MULTI_CHAR_OPERATORS
                and self.preview_token(1).value in MULTI_CHAR_OPERATORS
            ):
                self._next_char()
                self._word += " "
                while (
                    self._char_type == TokenType.ALPHANUMERIC
                    or self._char_type == TokenType.NUMBER
                ):
                    self._word += self._current_char
                    self._next_char()
                token = self._eat_operator(self._reset_word())
            else:
                token = self._eat_operator(self._reset_word())
            self._current_operator = Operators(self._word)
            return token
        elif self._current_data_type:
            return self._eat_value(self._reset_word())
        else:
            return self._eat_key()

    def _eat_key(self, value: str = None) -> Token:
        if value:
            token = self._make_token(TokenType.KEY, value)
        else:
            while (
                self._char_type == TokenType.ALPHANUMERIC
                or self._char_type == TokenType.NUMBER
            ):
                self._word += self._current_char
                self._next_char()
            token = self._make_token(TokenType.KEY, self._reset_word())
        self._current_key = token
        return token

    def _eat_constant(self, value: str = None) -> Token:
        return self._make_token(TokenType.CONSTANT, value)

    def _eat_value(self, value: str = None, meta_data: TokenMetaData = None) -> Token:
        return self._make_token(TokenType.VALUE, value, meta_data=meta_data)

    def _eat_number(self) -> Token:
        while (
            self._char_type == TokenType.NUMBER
            or self._current_char in OTHER_NUMERIC_CHARACTERS
        ):
            if self._current_char in OPERATORS_TO_IGNORE:
                self._skip_char()
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
    def _get_type(char) -> TokenType:
        if char.isspace():
            return TokenType.WHITESPACE
        if char == TokenType.COMMENT.value:
            return TokenType.COMMENT
        if char == TokenType.ESCAPE.value:
            return TokenType.ESCAPE
        if char in Operators.values():
            return TokenType.OPERATOR
        if char.isdigit():
            return TokenType.NUMBER
        if char == "":
            return TokenType.EMPTY
        return TokenType.ALPHANUMERIC

    def _get_next_token(self) -> Token:
        if self._current_char is None:
            return self._eof()

        if self._current_char == Operators.VALUE_DELIMITER.value:
            self._skip_char()

        if self._current_char == TokenType.NEWLINE.value:
            return self._eat_newline()
        elif self._current_char == TokenType.INDENT.value:
            self._skip_indent()

        if self._current_char.isspace():
            self._skip_whitespace()

        if self._current_char == TokenType.COMMENT.value:
            return self._skip_comment()

        if (
            self._current_data_type is None
            and self._current_char == Operators.DOT.value
        ):
            return self._eat_type()

        if self._current_char == Operators.DOUBLE_QUOTE.value:
            return self._eat_string(Operators.DOUBLE_QUOTE)

        if self._current_char == Operators.SINGLE_QUOTE.value:
            return self._eat_string(Operators.SINGLE_QUOTE)

        if not self._char_type:
            self._char_type = self._get_type(self._current_char)
        if not self._word_type:
            self._word_type = self._char_type

        if self._word_type == TokenType.OPERATOR:
            return self._eat_operator()

        if self._current_data_type in (
            DataTypes.STR,
            DataTypes.DATE,
            DataTypes.DATETIME,
            DataTypes.TIME,
            DataTypes.INTERVAL,
            DataTypes.URL,
            DataTypes.IP_ADDRESS,
            DataTypes.IP_NETWORK,
            DataTypes.BASE64,
            DataTypes.BASE64E,
            DataTypes.RANGE,
        ):
            return self._eat_rest_of_line()

        if self._word_type == TokenType.ALPHANUMERIC:
            return self._eat_alpha()

        if self._current_key is None:
            return self._eat_key()

        if self._word_type == TokenType.NUMBER:
            return self._eat_number()

        if self._char_type == TokenType.ESCAPE:
            return self._eat_escape()

        raise SyntaxError("Unknown character")

    def analyze(self) -> Iterator[Token]:
        token = self._get_next_token()
        while token.type != TokenType.EOF:
            yield token
            token = self._get_next_token()
        yield token

    def parse(self) -> list[Token]:
        return list(self.analyze())


if __name__ == "__main__":
    file = Path("../test.thsl")
    lexer = Lexer(file.open().read())
    for t in lexer.analyze():
        print(t)

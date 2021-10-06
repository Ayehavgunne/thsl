from pathlib import Path
from typing import Optional, Any, Iterator, Literal

from src.grammar import DataTypes, TokenType, Constants, Operators


class Token:
    def __init__(
        self,
        token_type: TokenType,
        value: Any,
        line_num: int,
        column_num: int,
        indent_level: int,
    ) -> None:
        self.type = token_type
        self.value = value
        self.line_num = line_num
        self.column_num = column_num
        self.indent_level = indent_level

    def __str__(self):
        return (
            f"Token("
            f"type={self.type}, "
            f"value={repr(self.value)}, "
            f"line_num={self.line_num}, "
            # f"column_num={self.column_num}, "
            f"indent_level={self.indent_level}"
            f")"
        )

    __repr__ = __str__


class Lexer:
    def __init__(self, text: str, file_path: Path = None) -> None:
        self.text = text
        self.file_path = file_path
        self.pos = 0
        self.column = 1
        self.current_char: Optional[str] = self.text[self.pos]
        self.char_type: Optional[TokenType] = None
        self.word = ""
        self.word_type: Optional[TokenType] = None
        self._line_num = 1
        self._indent_level = 0
        self.last_token: Optional[Token] = None
        self.current_data_type: Optional[DataTypes] = None
        self.current_key: Optional[Token] = None
        self.new_types: list[str] = []
        self.open_bracket: Optional[
            Literal[Operators.LPAREN, Operators.LSQUAREBRACKET, Operators.LCURLYBRACKET]
        ] = None

    def next_char(self) -> None:
        self.pos += 1
        self.column += 1
        if self.pos > len(self.text) - 1:
            self.current_char = None
            self.char_type = None
        else:
            self.current_char = self.text[self.pos]
            self.char_type = self.get_type(self.current_char)

    def skip_char(self) -> None:
        self.pos += 1
        self.column += 1
        if self.pos > len(self.text) - 1:
            self.current_char = None
            self.char_type = None
        else:
            self.current_char = self.text[self.pos]

    def reset_word(self) -> str:
        old_word = self.word
        self.word = ""
        self.word_type = None
        return old_word

    def peek(self, num: int, ignore_whitespace: bool = False) -> Optional[str]:
        peek_pos = self.pos + num
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
        current_pos = self.pos
        current_char = self.current_char
        current_char_type = self.char_type
        current_word = self.word
        current_word_type = self.word_type
        current_line_num = self.line_num
        current_indent_level = self.indent_level
        for _ in range(num):
            next_token = self.get_next_token()
        self.pos = current_pos
        self.current_char = current_char
        self.char_type = current_char_type
        self.word = current_word
        self.word_type = current_word_type
        self._line_num = current_line_num
        self._indent_level = current_indent_level
        return next_token

    def skip_whitespace(self) -> None:
        if self.peek(-1) == TokenType.NEWLINE.value:
            raise SyntaxError("Only tab characters can indent")
        while self.current_char is not None and self.current_char.isspace():
            self.next_char()
            self.reset_word()

    def skip_comment(self) -> Token:
        while self.current_char != TokenType.NEWLINE.value:
            self.skip_char()
            if self.current_char is None:
                return self.eof()
        return self.eat_newline()

    def increment_line_num(self) -> None:
        self._line_num += 1

    @property
    def line_num(self) -> int:
        return self._line_num

    @property
    def indent_level(self) -> int:
        return self._indent_level

    def reset_indent_level(self) -> int:
        self._indent_level = 0
        return self._indent_level

    def reset_column(self) -> int:
        column = self.column
        self.column = 0
        return column

    def decriment_indent_level(self) -> int:
        self._indent_level -= 1
        return self._indent_level

    def increment_indent_level(self) -> int:
        self._indent_level += 1
        return self._indent_level

    def eat_newline(self) -> Token:
        self.reset_word()
        token = Token(
            TokenType.NEWLINE,
            TokenType.NEWLINE.value,
            self.line_num,
            self.column,
            self.indent_level,
        )
        self.current_data_type = None
        self.current_key = None
        self.reset_column()
        self.reset_indent_level()
        self.increment_line_num()
        self.next_char()
        return token

    def skip_indent(self) -> None:
        while (
            self.current_char is not None
            and self.current_char == TokenType.INDENT.value
        ):
            self.reset_word()
            self.increment_indent_level()
            self.next_char()

    def eof(self) -> Token:
        return Token(
            TokenType.EOF,
            TokenType.EOF.value,
            self.line_num,
            self.column,
            self.indent_level,
        )

    def eat_string(
        self,
        quote: Literal[
            Operators.DOUBLE_QUOTE, Operators.SINGLE_QUOTE, TokenType.NEWLINE
        ],
    ) -> Token:
        self.next_char()
        while self.current_char != quote.value:
            if (
                self.current_char == TokenType.ESCAPE.value
                and self.peek(1) == quote.value
            ):
                self.next_char()
            self.word += self.current_char
            self.next_char()
        if quote != TokenType.NEWLINE:
            self.next_char()
        return Token(
            TokenType.STRING,
            self.reset_word(),
            self.line_num,
            self.column,
            self.indent_level,
        )

    def eat_key(self) -> Token:
        if self.current_char in (
            Operators.DOUBLE_QUOTE.value,
            Operators.SINGLE_QUOTE.value,
        ):
            quote = Operators(self.current_char)
            self.next_char()
            while (
                self.current_char != quote.value
                and self.current_char != Operators.VALUE_DELIMITER.value
            ):
                if (
                    self.current_char == TokenType.ESCAPE.value
                    and self.peek(1) == quote.value
                ):
                    self.next_char()
                self.word += self.current_char
                self.next_char()
            self.next_char()
        else:
            while (
                not self.current_char.isspace()
                and self.current_char != Operators.VALUE_DELIMITER.value
            ):
                self.word += self.current_char
                self.next_char()
        token = Token(
            TokenType.KEY,
            self.reset_word(),
            self.line_num,
            self.column,
            self.indent_level,
        )
        self.current_key = token
        return token

    def eat_operator(self) -> Token:
        while self.current_char in Operators.values():
            self.word += self.current_char
            self.next_char()
        if self.word in (
            Operators.LPAREN.value,
            Operators.LSQUAREBRACKET.value,
            Operators.LCURLYBRACKET.value,
        ):
            self.open_bracket = Operators(self.word)
        return Token(
            TokenType.OPERATOR,
            self.reset_word(),
            self.line_num,
            self.column,
            self.indent_level,
        )

    def eat_type(self) -> Token:
        while (
            self.char_type == TokenType.ALPHANUMERIC
            or self.char_type == TokenType.NUMERIC
        ):
            if self.current_char == Operators.VALUE_DELIMITER.value:
                break
            self.word += self.current_char
            self.next_char()

        if self.word in self.new_types:
            return Token(
                TokenType.TYPE,
                self.reset_word(),
                self.line_num,
                self.column,
                self.indent_level,
            )
        if self.word in DataTypes.values():
            self.current_data_type = DataTypes(self.word)
            if self.current_key and self.current_data_type == DataTypes.STRUCT:
                self.new_types.append(self.current_key.value)
            return Token(
                TokenType.TYPE,
                self.reset_word(),
                self.line_num,
                self.column,
                self.indent_level,
            )
        elif self.current_char == Operators.VALUE_DELIMITER.value:
            self.next_char()
            return Token(
                TokenType.OPERATOR,
                Operators.VALUE_DELIMITER.value,
                self.line_num,
                self.column,
                self.indent_level,
            )

        self.skip_whitespace()

        if self.current_char == Operators.LPAREN.value:
            self.next_char()
            self.open_bracket = Operators.LPAREN
            return Token(
                TokenType.TYPE,
                DataTypes.TUPLE.value,
                self.line_num,
                self.column,
                self.indent_level,
            )
        if self.current_char == Operators.LSQUAREBRACKET.value:
            self.next_char()
            self.open_bracket = Operators.LSQUAREBRACKET
            return Token(
                TokenType.TYPE,
                DataTypes.LIST.value,
                self.line_num,
                self.column,
                self.indent_level,
            )
        if self.current_char == Operators.LCURLYBRACKET.value:
            self.next_char()
            self.open_bracket = Operators.LCURLYBRACKET
            return Token(
                TokenType.TYPE,
                DataTypes.SET.value,
                self.line_num,
                self.column,
                self.indent_level,
            )
        raise SyntaxError("Expected a type or colon character")

    def eat_alpha(self) -> Token:
        while (
            self.char_type == TokenType.ALPHANUMERIC
            or self.char_type == TokenType.NUMERIC
        ):
            if self.current_char == Operators.VALUE_DELIMITER.value:
                break
            self.word += self.current_char
            self.next_char()

        if self.word in Operators.values():
            return Token(
                TokenType.OPERATOR,
                self.reset_word(),
                self.line_num,
                self.column,
                self.indent_level,
            )

        if self.word in DataTypes.values():
            self.current_data_type = DataTypes(self.word)
            return Token(
                TokenType.TYPE,
                self.reset_word(),
                self.line_num,
                self.column,
                self.indent_level,
            )

        if self.word in Constants.values():
            return Token(
                TokenType.CONSTANT,
                self.reset_word(),
                self.line_num,
                self.column,
                self.indent_level,
            )

        return Token(
            TokenType.KEY,
            self.reset_word(),
            self.line_num,
            self.column,
            self.indent_level,
        )

    def eat_numeric(self) -> Token:
        if self.current_data_type == DataTypes.COMPLEX:
            while (
                self.char_type == TokenType.NUMERIC
                or self.current_char == "i"
                or self.current_char == Operators.DOT.value
                or self.current_char == Operators.MINUS.value
                and self.peek(1) != Operators.DOT.value
            ):
                self.word += self.current_char
                self.next_char()
            return Token(
                TokenType.NUMBER,
                self.reset_word(),
                self.line_num,
                self.column,
                self.indent_level,
            )
        if self.current_data_type == DataTypes.HEX:
            while (
                self.char_type == TokenType.NUMERIC
                or self.current_char == Operators.DOT.value
                or self.current_char in ("a", "b", "c", "d", "e", "f")
                or self.current_char == Operators.MINUS.value
                and self.peek(1) != Operators.DOT.value
            ):
                self.word += self.current_char
                self.next_char()
            return Token(
                TokenType.NUMBER,
                self.reset_word(),
                self.line_num,
                self.column,
                self.indent_level,
            )
        if (
            self.current_data_type == DataTypes.FLOAT
            or self.current_data_type == DataTypes.DEC
        ):
            next_word = self.current_char + self.peek(1) + self.peek(2)
            if next_word in Constants.values():
                self.skip_char()
                self.skip_char()
                self.skip_char()
                return Token(
                    TokenType.CONSTANT,
                    next_word,
                    self.line_num,
                    self.column,
                    self.indent_level,
                )
        while (
            self.char_type == TokenType.NUMERIC
            or self.current_char == Operators.DOT.value
            or self.current_char == Operators.NUMBER_SEPERATOR.value
            or self.current_char == Operators.MINUS.value
            and self.peek(1) != Operators.DOT.value
        ):
            self.word += self.current_char
            self.next_char()
        return Token(
            TokenType.NUMBER,
            self.reset_word().replace(Operators.NUMBER_SEPERATOR.value, ""),
            self.line_num,
            self.column,
            self.indent_level,
        )

    def eat_constant(self) -> Token:
        while (
            self.char_type == TokenType.ALPHANUMERIC
            or self.char_type == TokenType.NUMERIC
        ):
            if self.current_char == Operators.VALUE_DELIMITER.value:
                break
            self.word += self.current_char
            self.next_char()

        if self.word in Constants.values():
            return Token(
                TokenType.CONSTANT,
                self.reset_word(),
                self.line_num,
                self.column,
                self.indent_level,
            )
        raise SyntaxError("Unknown Error, expected contstant")

    def eat_escape(self) -> Token:
        self.reset_word()
        self.next_char()
        line_num = self.line_num
        if self.current_char == TokenType.NEWLINE.value:
            self.increment_line_num()
        self.next_char()
        return Token(
            TokenType.ESCAPE,
            TokenType.ESCAPE.value,
            line_num,
            self.column,
            self.indent_level,
        )

    @staticmethod
    def get_type(char) -> TokenType:
        if char.isspace():
            return TokenType.WHITESPACE
        if char == TokenType.COMMENT.value:
            return TokenType.COMMENT
        if char == TokenType.ESCAPE.value:
            return TokenType.ESCAPE
        if char in Operators.values():
            return TokenType.OPERATIC
        if char in Constants.values():
            return TokenType.CONSTANT
        if char.isdigit():
            return TokenType.NUMERIC
        if char == "":
            return TokenType.EMPTY
        return TokenType.ALPHANUMERIC

    def get_next_token(self) -> Token:
        if self.current_char is None:
            return self.eof()

        if (
            self.last_token
            and self.last_token.value == Operators.VALUE_DELIMITER.value
            and self.current_data_type == DataTypes.STR
            and self.peek(1, True) != Operators.DOUBLE_QUOTE.value
            and self.peek(1, True) != Operators.SINGLE_QUOTE.value
        ):
            return self.eat_string(TokenType.NEWLINE)

        if self.current_char == TokenType.NEWLINE.value:
            return self.eat_newline()
        elif self.current_char == TokenType.INDENT.value:
            self.skip_indent()

        if self.current_char.isspace():
            self.skip_whitespace()

        if self.current_char == TokenType.COMMENT.value:
            return self.skip_comment()

        if self.open_bracket and self.current_char in (
            Operators.RPAREN.value,
            Operators.RSQUAREBRACKET.value,
            Operators.RCURLYBRACKET.value,
        ):
            self.open_bracket = None
            return self.eat_operator()

        if self.current_data_type is None and self.current_key is None:
            return self.eat_key()

        if self.current_data_type is None:
            return self.eat_type()

        if self.current_data_type is None:
            print("didn't find a type")

        if (
            self.current_char == Operators.DOUBLE_QUOTE.value
            or self.current_char == Operators.SINGLE_QUOTE.value
        ):
            return self.eat_string(Operators(self.current_char))

        if not self.char_type:
            self.char_type = self.get_type(self.current_char)
        if not self.word_type:
            self.word_type = self.char_type

        if self.word_type == TokenType.OPERATIC:
            return self.eat_operator()

        if self.current_data_type in (
            DataTypes.HEX,
            DataTypes.OCT,
            DataTypes.COMPLEX,
            DataTypes.DEC,
            DataTypes.FLOAT,
            DataTypes.INT,
        ):
            return self.eat_numeric()

        if self.word_type == TokenType.CONSTANT:
            return self.eat_constant()

        if self.word_type == TokenType.ALPHANUMERIC:
            return self.eat_alpha()

        if self.word_type == TokenType.NUMERIC:
            return self.eat_numeric()

        if self.char_type == TokenType.ESCAPE:
            return self.eat_escape()

        raise SyntaxError("Unknown character")

    def analyze(self) -> Iterator[Token]:
        token = self.get_next_token()
        while token.type != TokenType.EOF:
            yield token
            self.last_token = token
            token = self.get_next_token()
        yield token


if __name__ == "__main__":
    file = Path("../test.thsl")
    lexer = Lexer(file.open().read(), file)
    for t in lexer.analyze():
        if t.type == TokenType.NEWLINE:
            print(t)
            print()
        else:
            print(t, end=" | ")

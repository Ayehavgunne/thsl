import base64
import ipaddress
import struct
from decimal import Decimal
from pathlib import Path
from typing import Optional, Any

import tempora
from dateutil import parser as dateutil

from src.grammar import TokenType, DataTypes, Constants, Operators
from src.lexer import Lexer, Token


class Parser:
    def __init__(self, lexer: Lexer) -> None:
        self.lexer = lexer
        self.file_path = lexer.file_path
        self.current_token: Token = self.lexer.get_next_token()
        self.current_key: Optional[Token] = None
        self.last_key: Optional[Token] = None
        self.dict_key_stack: list[str] = []
        self.current_data_type: Optional[DataTypes] = None
        self.current_operator: Optional[Operators] = None
        self.indent_level = 0
        self.root = {}

    def parse(self) -> dict:
        current_dict = self.root
        while self.current_token.type != TokenType.EOF:
            print(self.current_token)
            # if self.current_token.indent_level > self.indent_level:
            #     self.indent_level = self.current_token.indent_level
            #     current_dict = current_dict[self.current_key.value]
            match self.current_token:
                case Token(type=TokenType.KEY):
                    current_dict[self.eat_key()] = {}
                case Token(type=TokenType.TYPE):
                    self.eat_type()
                case Token(type=TokenType.NEWLINE):
                    self.last_key = self.current_key
                    self.current_key = None
                    self.current_data_type = None
                    self.indent_level = 0
                    current_dict = self.root
                case Token(type=TokenType.INDENT):
                    self.indent_level += 1
                    current_dict = self.root[self.last_dict_key]
                    # try:
                    #     current_dict = current_dict[self.last_dict_key]
                    # except KeyError:
                    #     pass
                case Token(type=TokenType.OPERATOR):
                    self.eat_operator()
                case Token(type=TokenType.VALUE):
                    if self.current_key is not None:
                        current_dict[self.current_key.value] = self.eat_value()
            self.next_token()
        return self.root

    def cast_complex(self) -> Any:
        #     LIST = "list"
        #     SET = "set"
        #     DICT = "dict"
        #     TUPLE = "tuple"
        #     ENUM = "enum"
        #     STRUCT = "struct"
        #     SERVICE = "service"
        pass

    def cast_scalar(self, value: str) -> Any:
        match self.current_data_type:
            case DataTypes.ANY:
                return value
            case DataTypes.INT:
                value = int(value)
            case DataTypes.STR:
                value = str(value)
            case DataTypes.CHAR:
                if len(value) > 1:
                    raise ValueError('Char type can only be a single character')
                value = str(value)
            case DataTypes.DEC:
                value = Decimal(value)
            case DataTypes.FLOAT:
                value = float(value)
            case DataTypes.HEX:
                value = int(value, 16)
                value = hex(value)
            case DataTypes.OCT:
                value = int(value, 8)
                value = oct(value)
            case DataTypes.COMPLEX:
                value = complex(value)
            case DataTypes.BASE64:
                value = base64.b64decode(value)
            case DataTypes.BOOL:
                if value == Constants.TRUE.value:
                    value = True
                elif value == Constants.FALSE.value:
                    value = False
                else:
                    raise ValueError(
                        f'Bool can only be {Constants.TRUE.value}'
                        f' or {Constants.FALSE.value}, not {value}'
                    )
            case DataTypes.BYTES:
                value = int(value, 2)
                value = struct.pack('!H', value)
            case DataTypes.DATETIME:
                value = dateutil.parse(value)
            case DataTypes.DATE:
                value = dateutil.parse(value).date()
            case DataTypes.TIME:
                value = dateutil.parse(value).time()
            case DataTypes.INTERVAL:
                value = tempora.parse_timedelta(value)
            case DataTypes.IP_ADDRESS:
                value = ipaddress.ip_address(value)
            case DataTypes.IP_NETWORK:
                value = ipaddress.ip_network(value)
            case DataTypes.RANGE:
                if '...' in value:
                    value = range(int(value[0]), int(value[-1]) + 1)
                else:
                    value = range(int(value[0]), int(value[-1]))
        if self.current_operator == Operators.MINUS:
            value = -value
            self.current_operator = None
        return value

    @property
    def line_num(self) -> int:
        return self.current_token.line_num

    def next_token(self) -> Token:
        token = self.current_token
        self.current_token = self.lexer.get_next_token()
        return token

    def preview(self, num: int = 1) -> Token:
        return self.lexer.preview_token(num)

    def eat_key(self) -> str:
        if self.current_token.type != TokenType.KEY:
            raise ValueError('Expected TokenType.KEY value')
        self.current_key = self.current_token
        return self.current_token.value

    def eat_type(self) -> None:
        if self.current_token.type != TokenType.TYPE:
            raise ValueError('Expected TokenType.TYPE value')
        self.current_data_type = DataTypes(self.current_token.value)

    def eat_operator(self) -> None:
        if self.current_token.type != TokenType.OPERATOR:
            raise ValueError('Expected TokenType.OPERATOR value')
        self.current_operator = Operators(self.current_token.value)

    def eat_value(self) -> Any:
        if self.current_token.type != TokenType.VALUE:
            raise ValueError('Expected TokenType.VALUE value')
        return self.cast_scalar(self.current_token.value)


if __name__ == "__main__":
    file = Path("../test.thsl")
    parser = Parser(Lexer(file.open().read(), file))
    print(parser.parse())

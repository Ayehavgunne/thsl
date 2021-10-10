import base64
import ipaddress
import os
import struct
import urllib.parse
from datetime import datetime, timedelta
from decimal import Decimal
from pathlib import Path
from pprint import pprint
from typing import Optional, Any

import tempora
from dateutil import parser as dateutil

from src.grammar import TokenType, DataTypes, Operators
from src.lexer import Lexer, Token


class Parser:
    def __init__(self, lexer: Lexer, file_path: Path) -> None:
        self.lexer = lexer
        self.file_path = file_path
        self.tokens = list(self.lexer.analyze())
        self.token_pos = 0
        self.current_token: Token = self.tokens[0]
        self.current_key: Optional[Token] = None
        self.last_key: Optional[str] = None
        self.current_data_type: Optional[DataTypes] = None
        self.current_operator: Optional[Operators] = None
        self.current_value: Optional[str] = None
        self.indent_level = 0
        self.root = {}
        self.current_dict = self.root
        self.stack: list[dict] = [self.root]

    def parse(self) -> dict:
        while self.current_token.type != TokenType.EOF:
            print(self.current_token)
            if self.current_token.indent > self.indent_level:
                self.indent_level = self.current_token.indent
                self.current_dict = self.stack[-1][self.last_key]
                self.stack.append(self.current_dict)
            if self.current_token.indent < self.indent_level:
                self.indent_level = self.current_token.indent
                self.stack.pop()
                self.current_dict = self.stack[-1]
            # if (
            #     self.current_operator == Operators.VALUE_DELIMITER
            #     and not self.current_data_type
            #     and self.current_token.type == TokenType.NEWLINE
            # ):
            #     print('infer!')
            match self.current_token:
                case Token(type=TokenType.KEY):
                    self.current_dict[self.eat_key()] = {}
                case Token(type=TokenType.TYPE):
                    self.eat_type()
                case Token(type=TokenType.NEWLINE):
                    if not self.current_value and self.current_data_type:
                        self.current_dict[
                            self.current_key.value
                        ] = self.get_default_value()
                    if self.current_key:
                        self.last_key = self.current_key.value
                    if self.current_operator == Operators.VALUE_DELIMITER:
                        self.current_operator = None
                    self.current_key = None
                    self.current_data_type = None
                case Token(type=TokenType.OPERATOR):
                    self.eat_operator()
                case Token(type=TokenType.VALUE):
                    if self.current_key:
                        self.current_dict[self.current_key.value] = self.eat_value()
                        self.current_value = self.current_dict[self.current_key.value]
            self.next_token()
        return self.root

    def cast_complex(self) -> Any:
        pass

    def cast_scalar(self, value: str) -> Any:
        result = None
        match self.current_data_type:
            case DataTypes.ANY:
                return value
            case DataTypes.INT:
                result = int(value)
            case DataTypes.STR:
                result = str(value)
            case DataTypes.CHAR:
                if len(value) > 1:
                    raise ValueError('Char type can only be a single character')
                result = str(value)
            case DataTypes.DEC:
                result = Decimal(value)
            case DataTypes.FLOAT:
                result = float(value)
            case DataTypes.HEX:
                intermediary = int(value, 16)
                result = hex(intermediary)
            case DataTypes.OCT:
                intermediary = int(value, 8)
                result = oct(intermediary)
            case DataTypes.COMPLEX:
                result = complex(value.replace('i', 'j'))
            case DataTypes.BASE64:
                result = base64.b64decode(value)
            case DataTypes.BASE64E:
                result = base64.b64encode(value.encode('utf-8'))
            case DataTypes.BOOL:
                result = bool(value)
            case DataTypes.BYTES:
                intermediary = int(value, 2)
                result = struct.pack('!H', intermediary)
            case DataTypes.DATETIME:
                result = dateutil.parse(value)
            case DataTypes.DATE:
                result = dateutil.parse(value).date()
            case DataTypes.TIME:
                result = dateutil.parse(value).time()
            case DataTypes.INTERVAL:
                result = tempora.parse_timedelta(value)
            case DataTypes.IP_ADDRESS:
                result = ipaddress.ip_address(value)
            case DataTypes.IP_NETWORK:
                result = ipaddress.ip_network(value)
            case DataTypes.URL:
                result = urllib.parse.urlparse(value)
            case DataTypes.RANGE:
                if '...' in value:
                    result = range(int(value[0]), int(value[-1]) + 1)
                else:
                    result = range(int(value[0]), int(value[-1]))
            case DataTypes.ENV:
                result = os.getenv(value)
        if self.current_operator == Operators.MINUS:
            result = -result
            self.current_operator = None
        return result

    @property
    def line_num(self) -> int:
        return self.current_token.line

    def next_token(self) -> Token:
        token = self.current_token
        self.token_pos += 1
        try:
            self.current_token = self.tokens[self.token_pos]
        except IndexError:
            return self.current_token
        return token

    # def preview(self, num: int = 1) -> Token:
    #     return self.lexer.preview_token(num)

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
        # if self.current_token.value != Operators.VALUE_DELIMITER.value:
        self.current_operator = Operators(self.current_token.value)
        if self.current_operator == Operators.LSQUAREBRACKET:
            self.eat_list()

    def eat_value(self) -> Any:
        if self.current_token.type != TokenType.VALUE:
            raise ValueError('Expected TokenType.VALUE value')
        return self.cast_scalar(self.current_token.value)

    def eat_list(self) -> None:
        pass
        # self.current_value = []
        # self.next_token()
        # while (
        #     self.current_token.value != Operators.RSQUAREBRACKET.value
        #     and self.current_token.type != TokenType.EOF
        # ):
        #     if self.current_token.type == TokenType.NEWLINE:
        #         self.next_token()
        #
        #     self.next_token()

    def get_default_value(self) -> Any:
        match self.current_data_type:
            case DataTypes.ANY:
                return None  # maybe raise exception
            case DataTypes.INT:
                return 0
            case DataTypes.STR:
                return ""
            case DataTypes.CHAR:
                return ""
            case DataTypes.DEC:
                return Decimal("0")
            case DataTypes.FLOAT:
                return float(0)
            case DataTypes.HEX:
                return hex(0)
            case DataTypes.OCT:
                return oct(0)
            case DataTypes.COMPLEX:
                return complex("0")
            case DataTypes.BASE64:
                return ""
            case DataTypes.BASE64E:
                return bytes("".encode('utf-8'))
            case DataTypes.BOOL:
                return False
            case DataTypes.BYTES:
                return bytes("".encode('utf-8'))
            case DataTypes.DATETIME:
                return datetime.now()
            case DataTypes.DATE:
                return datetime.now().date()
            case DataTypes.TIME:
                return datetime.now().time()
            case DataTypes.INTERVAL:
                return timedelta(seconds=0)
            case DataTypes.IP_ADDRESS:
                return ipaddress.ip_address("0.0.0.0")
            case DataTypes.IP_NETWORK:
                return ipaddress.ip_network("0.0.0.0/1")
            case DataTypes.URL:
                return urllib.parse.urlparse("")
            case DataTypes.RANGE:
                return range(1)
            case DataTypes.ENV:
                return ""
            case DataTypes.DICT | DataTypes.LIST | DataTypes.SET | DataTypes.TUPLE:
                return {}
        raise NotImplementedError(
            f"Still need to add default for type {self.current_data_type.value}"
        )


if __name__ == "__main__":
    file = Path("../test.thsl")
    parser = Parser(Lexer(file.open().read()), file)
    # print(parser.tokens)
    pprint(parser.parse())

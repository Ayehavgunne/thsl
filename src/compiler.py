import base64
import ipaddress
import os
import struct
import urllib.parse
from decimal import Decimal
from pathlib import Path
from pprint import pprint
from typing import Any

import tempora
from dateutil import parser as dateutil

from src.grammar import DataTypes
from src.parser import Parser
from src.thsl_ast import Key, Value, Collection


class Compiler:
    def __init__(self, file_path: Path):
        parser = Parser(file_path)
        self.tree = parser.parse()

    def visit(self, current_node: Collection = None) -> dict:
        root = {}
        if current_node is None:
            current_node = self.tree
        for item in current_node.items:
            match item:
                case Key(items=Value()) as key:
                    root[key.name] = self.cast_scalar(key.items.value, key.type)
                case Key(items=Collection()) as key:
                    root[key.name] = self.visit(key.items)
        return root

    @staticmethod
    def cast_scalar(value: str, cast_type: DataTypes) -> Any:
        result = None
        match cast_type:
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
                if value == 'true':
                    result = True
                elif value == 'false':
                    result = False
                else:
                    raise SyntaxError
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
        return result


if __name__ == "__main__":
    file = Path('../test.thsl')
    compiler = Compiler(file)
    data = compiler.visit()
    pprint(data)

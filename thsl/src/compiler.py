import base64
import ipaddress
import os
import struct
import urllib.parse
from datetime import datetime, timedelta
from decimal import Decimal
from pathlib import Path
from pprint import pprint
from typing import Any, Optional

import re
import semantic_version
import tempora
from dateutil import parser as dateutil

from thsl.src.grammar import DataTypes
from thsl.src.parser import Parser
from thsl.src.abstract_syntax_tree import Key, Value, Collection, Void


class Compiler:
    def __init__(self, file_path: Path | str):
        self._parser = Parser(file_path)
        self.tree = self._parser.parse()
        self._current_key: Optional[Key] = None

    @property
    def user_types(self) -> list[str]:
        return self._parser.user_types

    def _visit(self, current_node: Collection = None) -> Any:
        if current_node is None:
            current_node = self.tree
        root = self.cast_compound(current_node.type)
        for item in current_node.items:
            if isinstance(item, Key):
                self._current_key = item
            match item:
                case Key(items=Value()) as key:
                    root[key.name] = self.cast_scalar(key.items.value, key.type)
                case Key(items=Collection(
                    type=(
                        DataTypes.DICT
                        | DataTypes.LIST
                        | DataTypes.SET
                        | DataTypes.TUPLE
                    )
                )) as key:
                    root[key.name] = self._visit(key.items)
                case Value() as value:
                    match root:
                        case list():
                            root.append(
                                self.cast_scalar(value.value, self._current_key.type)
                            )
                        case set():
                            root.add(
                                self.cast_scalar(value.value, self._current_key.type)
                            )
                        case tuple():
                            root = (
                                *root,
                                self.cast_scalar(value.value, self._current_key.type)
                            )
        return root

    @staticmethod
    def cast_compound(collection_type: DataTypes) -> Any:
        match collection_type:
            case DataTypes.DICT:
                return {}
            case DataTypes.LIST:
                return []
            case DataTypes.SET:
                return set()
            case DataTypes.TUPLE:
                return tuple()

    def cast_scalar(self, value: str | Void, cast_type: DataTypes) -> Any:
        result = None
        if value == Void:
            return self.get_default_value(cast_type)
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
            case DataTypes.PATH:
                result = Path(value)
            case DataTypes.SEMVER:
                result = semantic_version.Version(value)
            case DataTypes.REGEX:
                result = re.compile(value)
        return result

    def get_default_value(self, cast_type: DataTypes) -> Any:
        match cast_type:
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
            case DataTypes.PATH:
                return Path()
            case DataTypes.SEMVER:
                return semantic_version.Version('0.0.0')
            case DataTypes.SEMVER:
                return re.compile('')
            case DataTypes.DICT:
                return {}
            case DataTypes.LIST:
                return []
            case DataTypes.SET:
                return set()
            case DataTypes.TUPLE:
                return tuple()
        raise NotImplementedError(
            f"Still need to add default for type {cast_type.value}"
        )

    def compile(self) -> dict:
        return self._visit()


if __name__ == "__main__":
    file = Path('../../test.thsl')
    compiler = Compiler(file)
    data = compiler.compile()
    pprint(data)

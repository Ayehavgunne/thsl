import base64
import ipaddress
import os
import re
import struct
import urllib.parse
from datetime import datetime, timedelta
from decimal import Decimal
from pathlib import Path
from typing import Any, Iterable

import semantic_version
import tempora
from dateutil import parser as dateutil

from thsl.src.abstract_syntax_tree import Collection, Key, Value, Void
from thsl.src.grammar import DataType
from thsl.src.parser import Parser


class Compiler:
    def __init__(self, file_path: Path | str):
        self._parser = Parser(file_path)
        self.tree = self._parser.parse()
        self._current_key: Key | None = None

    def compile(self) -> dict:
        return self._visit()  # type: ignore

    @property
    def user_types(self) -> list[str]:
        return self._parser.user_types

    def _visit(self, current_node: Collection | None = None) -> Iterable:
        if current_node is None:
            current_node = self.tree
        root = self.cast_compound(current_node.type)  # type: ignore
        for item in current_node.items:
            if isinstance(item, Key):
                self._current_key = item
            match item:
                case Key(items=Value()) as key:
                    # noinspection PyTupleItemAssignment
                    root[key.name] = self.cast_scalar(  # type: ignore
                        key.items.value,  # type: ignore
                        key.type,
                    )
                case Key(
                    items=Collection(
                        type=(
                            DataType.DICT
                            | DataType.LIST
                            | DataType.SET
                            | DataType.TUPLE
                        ),
                    ),
                ) as key:
                    # noinspection PyTupleItemAssignment
                    root[key.name] = self._visit(key.items)  # type: ignore
                case Value() as value:
                    # match self._current_key.type:
                    #     case DataType.DICT:
                    if self._current_key is not None:
                        if isinstance(root, list):
                            root.append(
                                self.cast_scalar(value.value, self._current_key.type),
                            )
                        if isinstance(root, set):
                            root.add(
                                self.cast_scalar(value.value, self._current_key.type),
                            )
                        if isinstance(root, tuple):
                            root = (
                                *root,
                                self.cast_scalar(value.value, self._current_key.type),
                            )
        return root

    @staticmethod
    def cast_compound(collection_type: DataType) -> Iterable:
        match collection_type:
            case DataType.DICT:
                return {}
            case DataType.LIST:
                return []
            case DataType.SET:
                return set()
            case DataType.TUPLE:
                return tuple()
            case _:
                return {}

    def cast_scalar(self, value: str | Void, cast_type: DataType) -> Any:
        result: Any = None
        if not isinstance(value, Void):
            match cast_type:
                case DataType.ANY:
                    return value
                case DataType.INT:
                    result = int(value)
                case DataType.STR:
                    result = str(value)
                case DataType.CHAR:
                    if len(value) > 1:
                        raise ValueError("Char type can only be a single character")
                    result = str(value)
                case DataType.DEC:
                    result = Decimal(value)
                case DataType.FLOAT:
                    result = float(value)
                case DataType.HEX:
                    intermediary = int(value, 16)
                    result = hex(intermediary)
                case DataType.OCT:
                    intermediary = int(value, 8)
                    result = oct(intermediary)
                case DataType.COMPLEX:
                    result = complex(value.replace("i", "j"))
                case DataType.BASE64:
                    result = base64.b64decode(value)
                case DataType.BASE64E:
                    result = base64.b64encode(value.encode("utf-8"))
                case DataType.BOOL:
                    if value == "true":
                        result = True
                    elif value == "false":
                        result = False
                    else:
                        raise SyntaxError
                case DataType.BYTES:
                    intermediary = int(value, 2)
                    result = struct.pack("!H", intermediary)
                case DataType.DATETIME:
                    result = dateutil.parse(value)
                case DataType.DATE:
                    result = dateutil.parse(value).date()
                case DataType.TIME:
                    result = dateutil.parse(value).time()
                case DataType.INTERVAL:
                    result = tempora.parse_timedelta(value)
                case DataType.IP_ADDRESS:
                    result = ipaddress.ip_address(value)
                case DataType.IP_NETWORK:
                    result = ipaddress.ip_network(value)
                case DataType.URL:
                    result = urllib.parse.urlparse(value)
                case DataType.RANGE:
                    if "..." in value:
                        result = range(int(value[0]), int(value[-1]) + 1)
                    else:
                        result = range(int(value[0]), int(value[-1]))
                case DataType.ENV:
                    result = os.getenv(value)
                case DataType.PATH:
                    result = Path(value)
                case DataType.SEMVER:
                    result = semantic_version.Version(value)
                case DataType.REGEX:
                    result = re.compile(value)
            return result
        return self.get_default_value(cast_type)

    def get_default_value(self, cast_type: DataType) -> Any:
        match cast_type:
            case DataType.ANY:
                return None  # maybe raise exception
            case DataType.INT:
                return 0
            case DataType.STR:
                return ""
            case DataType.CHAR:
                return ""
            case DataType.DEC:
                return Decimal("0")
            case DataType.FLOAT:
                return float(0)
            case DataType.HEX:
                return hex(0)
            case DataType.OCT:
                return oct(0)
            case DataType.COMPLEX:
                return complex("0")
            case DataType.BASE64:
                return ""
            case DataType.BASE64E:
                return bytes("".encode("utf-8"))
            case DataType.BOOL:
                return False
            case DataType.BYTES:
                return bytes("".encode("utf-8"))
            case DataType.DATETIME:
                return datetime.now()
            case DataType.DATE:
                return datetime.now().date()
            case DataType.TIME:
                return datetime.now().time()
            case DataType.INTERVAL:
                return timedelta(seconds=0)
            case DataType.IP_ADDRESS:
                return ipaddress.ip_address("0.0.0.0")
            case DataType.IP_NETWORK:
                return ipaddress.ip_network("0.0.0.0/1")
            case DataType.URL:
                return urllib.parse.urlparse("")
            case DataType.RANGE:
                return range(1)
            case DataType.ENV:
                return ""
            case DataType.PATH:
                return Path()
            case DataType.SEMVER:
                return semantic_version.Version("0.0.0")
            case DataType.SEMVER:
                return re.compile("")
            case DataType.DICT:
                return {}
            case DataType.LIST:
                return []
            case DataType.SET:
                return set()
            case DataType.TUPLE:
                return tuple()
        raise NotImplementedError(
            f"Still need to add default for type {cast_type.value}",
        )

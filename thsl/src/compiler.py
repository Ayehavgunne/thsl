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
from thsl.src.grammar import CompoundDataType, DataType, ScalarDataType
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
                    items=Collection(type=CompoundDataType()),
                ) as key:
                    # noinspection PyTupleItemAssignment
                    root[key.name] = self._visit(key.items)  # type: ignore
                case Collection() as collection:
                    if isinstance(root, list):
                        root.append(self._visit(collection))
                case Value() as value:
                    if self._current_key is not None:
                        subtype = self._current_key.subtype
                        if subtype is None:
                            subtype = self._current_key.type
                        if subtype == CompoundDataType.UNKNOWN:
                            subtype = value.type
                        if value.type is not None:
                            subtype = value.type
                        if isinstance(root, list):
                            root.append(
                                self.cast_scalar(value.value, subtype),
                            )
                        if isinstance(root, set):
                            root.add(
                                self.cast_scalar(value.value, subtype),
                            )
                        if isinstance(root, tuple):
                            root = (
                                *root,
                                self.cast_scalar(value.value, subtype),
                            )
        return root

    @staticmethod
    def cast_compound(collection_type: CompoundDataType) -> Iterable:
        match collection_type:
            case CompoundDataType.DICT:
                return {}
            case CompoundDataType.LIST:
                return []
            case CompoundDataType.SET:
                return set()
            case CompoundDataType.TUPLE:
                return tuple()
            case _:
                return {}

    def cast_scalar(self, value: str | Void, cast_type: ScalarDataType) -> Any:
        result: Any = None
        if not isinstance(value, Void):
            match cast_type:
                case ScalarDataType.INT:
                    result = int(value)
                case ScalarDataType.STR:
                    result = str(value)
                case ScalarDataType.CHAR:
                    if len(value) > 1:
                        raise ValueError("Char type can only be a single character")
                    result = str(value)
                case ScalarDataType.DEC:
                    result = Decimal(value)
                case ScalarDataType.FLOAT:
                    result = float(value)
                case ScalarDataType.HEX:
                    result = int(value, 16)
                case ScalarDataType.OCT:
                    result = int(value, 8)
                case ScalarDataType.COMPLEX:
                    result = complex(value.replace("i", "j"))
                case ScalarDataType.BASE64:
                    result = base64.b64decode(value)
                case ScalarDataType.BASE64E:
                    result = base64.b64encode(value.encode("utf-8"))
                case ScalarDataType.BOOL:
                    if value == "true":
                        result = True
                    elif value == "false":
                        result = False
                    else:
                        raise SyntaxError
                case ScalarDataType.BYTES:
                    intermediary = int(value, 2)
                    result = struct.pack("!H", intermediary)
                case ScalarDataType.DATETIME:
                    result = dateutil.parse(value)
                case ScalarDataType.DATE:
                    result = dateutil.parse(value).date()
                case ScalarDataType.TIME:
                    result = dateutil.parse(value).time()
                case ScalarDataType.INTERVAL:
                    result = tempora.parse_timedelta(value)
                case ScalarDataType.IP_ADDRESS:
                    result = ipaddress.ip_address(value)
                case ScalarDataType.IP_NETWORK:
                    result = ipaddress.ip_network(value)
                case ScalarDataType.URL:
                    result = urllib.parse.urlparse(value)
                case ScalarDataType.RANGE:
                    if "..." in value:
                        result = range(int(value[0]), int(value[-1]) + 1)
                    else:
                        result = range(int(value[0]), int(value[-1]))
                case ScalarDataType.ENV:
                    result = os.getenv(value)
                case ScalarDataType.PATH:
                    result = Path(value)
                case ScalarDataType.SEMVER:
                    result = semantic_version.Version(value)
                case ScalarDataType.REGEX:
                    result = re.compile(value)
            if result is None:
                print("THIS SHOULDN'T HAPPEN")
            return result
        return self.get_default_value(cast_type)

    def get_default_value(self, cast_type: DataType) -> Any:
        match cast_type:
            case ScalarDataType.INT:
                return 0
            case ScalarDataType.STR:
                return ""
            case ScalarDataType.CHAR:
                return ""
            case ScalarDataType.DEC:
                return Decimal("0")
            case ScalarDataType.FLOAT:
                return float(0)
            case ScalarDataType.HEX:
                return hex(0)
            case ScalarDataType.OCT:
                return oct(0)
            case ScalarDataType.COMPLEX:
                return complex("0")
            case ScalarDataType.BASE64:
                return ""
            case ScalarDataType.BASE64E:
                return bytes("".encode("utf-8"))
            case ScalarDataType.BOOL:
                return False
            case ScalarDataType.BYTES:
                return bytes("".encode("utf-8"))
            case ScalarDataType.DATETIME:
                return datetime.now()
            case ScalarDataType.DATE:
                return datetime.now().date()
            case ScalarDataType.TIME:
                return datetime.now().time()
            case ScalarDataType.INTERVAL:
                return timedelta(seconds=0)
            case ScalarDataType.IP_ADDRESS:
                return ipaddress.ip_address("0.0.0.0")
            case ScalarDataType.IP_NETWORK:
                return ipaddress.ip_network("0.0.0.0/1")
            case ScalarDataType.URL:
                return urllib.parse.urlparse("")
            case ScalarDataType.RANGE:
                return range(1)
            case ScalarDataType.ENV:
                return ""
            case ScalarDataType.PATH:
                return Path()
            case ScalarDataType.SEMVER:
                return semantic_version.Version("0.0.0")
            case ScalarDataType.SEMVER:
                return re.compile("")
            case CompoundDataType.DICT:
                return {}
            case CompoundDataType.LIST:
                return []
            case CompoundDataType.SET:
                return set()
            case CompoundDataType.TUPLE:
                return tuple()
        raise NotImplementedError(
            f"Still need to add default for type {cast_type.value}",
        )

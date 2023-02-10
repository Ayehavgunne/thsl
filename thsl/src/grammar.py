from enum import Enum


class EnumDict(Enum):
    @classmethod
    def values(cls) -> list[str]:
        return [enum.value for enum in cls]

    @classmethod
    def keys(cls) -> list[str]:
        return [enum.name for enum in cls]


class DataType(EnumDict):
    pass


class ScalarDataType(DataType):
    BOOL = "bool"
    BYTES = "bytes"
    INT = "int"
    DEC = "dec"
    FLOAT = "float"
    HEX = "hex"
    OCT = "oct"
    COMPLEX = "complex"
    BASE64 = "base64"
    BASE64E = "base64e"
    CHAR = "char"
    STR = "str"
    RANGE = "range"
    DATE = "date"
    DATETIME = "datetime"
    TIME = "time"
    INTERVAL = "interval"
    IP_ADDRESS = "ip"
    IP_NETWORK = "network"
    URL = "url"
    ENV = "env"
    PATH = "path"
    SEMVER = "semver"
    REGEX = "regex"


class CompoundDataType(DataType):
    LIST = "list"
    SET = "set"
    DICT = "dict"
    TUPLE = "tuple"
    UNKNOWN = "unknown"


ALL_DATA_TYPE_VALUES = (*ScalarDataType.values(), *CompoundDataType.values())


class Operator(EnumDict):
    DECORATOR = "@"
    VALUE_DELIMITER = ":"
    MINUS = "-"
    LPAREN = "("
    RPAREN = ")"
    LSQUAREBRACKET = "["
    RSQUAREBRACKET = "]"
    LCURLYBRACKET = "{"
    RCURLYBRACKET = "}"
    LANGLEBRACKET = "<"
    RANGLEBRACKET = ">"
    LIST_DELIMITER = ","
    LIST_ITEM = "-"
    SET_ITEM = ">"
    TUPLE_ITEM = ")"
    TYPE_INITIATOR = ":"
    DECIMAL_POINT = "."
    RANGE = ".."
    ELLIPSIS = "..."
    SINGLE_QUOTE = "'"
    DOUBLE_QUOTE = '"'
    EXTENDS = "->"


OPENING_BRACKETS = (Operator.LPAREN, Operator.LSQUAREBRACKET, Operator.LCURLYBRACKET)
OPENING_BRACKET_VALUES = tuple(item.value for item in OPENING_BRACKETS)
CLOSING_BRACKETS = (Operator.RPAREN, Operator.RSQUAREBRACKET, Operator.RCURLYBRACKET)
CLOSING_BRACKET_VALUES = tuple(item.value for item in CLOSING_BRACKETS)

LIST_OPERATORS = (Operator.LSQUAREBRACKET.value, Operator.LIST_ITEM.value)
SET_OPERATORS = (Operator.LANGLEBRACKET.value, Operator.SET_ITEM.value)
TUPLE_OPERATORS = (Operator.LPAREN.value, Operator.TUPLE_ITEM.value)
DICT_OPERATORS = (Operator.LCURLYBRACKET.value,)

QUOTES = (Operator.SINGLE_QUOTE, Operator.DOUBLE_QUOTE)

MULTI_CHAR_OPERATORS = (
    Operator.DECIMAL_POINT,
    Operator.RANGE,
    Operator.ELLIPSIS,
    Operator.EXTENDS,
)

COMPOUND_ITEMS = (Operator.LIST_ITEM, Operator.TUPLE_ITEM, Operator.SET_ITEM)
COMPOUND_ITEM_VALUES = tuple(item.value for item in COMPOUND_ITEMS)

OPERATORS_TO_IGNORE = ("_",)

OTHER_NUMERIC_CHARACTERS = (Operator.DECIMAL_POINT.value, "i", "e", "_", "-")


class TokenType(EnumDict):
    TYPE = "TYPE"
    NUMBER = "NUMBER"
    OPERATOR = "OPERATOR"
    COMMENT = "#"
    NEWLINE = "\n"
    INDENT = "\t"
    ESCAPE = "\\"
    EMPTY = ""
    KEY = "KEY"
    VALUE = "VALUE"
    EOF = "EOF"
    ALPHANUMERIC = "ALPHANUMERIC"
    WHITESPACE = "WHITESPACE"

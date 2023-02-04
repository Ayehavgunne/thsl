from enum import Enum


class EnumDict(Enum):
    @classmethod
    def values(cls) -> list[str]:
        return [enum.value for enum in cls]

    @classmethod
    def keys(cls) -> list[str]:
        return [enum.name for enum in cls]


class DataType(EnumDict):
    ANY = "any"
    INT = "int"
    DEC = "dec"
    FLOAT = "float"
    HEX = "hex"
    OCT = "oct"
    COMPLEX = "complex"
    BASE64 = "base64"
    BASE64E = "base64e"
    STR = "str"
    CHAR = "char"
    BOOL = "bool"
    BYTES = "bytes"
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

    LIST = "list"
    SET = "set"
    DICT = "dict"
    TUPLE = "tuple"
    ENUM = "enum"
    STRUCT = "struct"

    INTERFACE = "interface"
    ALIAS = "alias"


COMPOUND_TYPES = (
    DataType.LIST,
    DataType.SET,
    DataType.DICT,
    DataType.TUPLE,
    DataType.ENUM,
    DataType.STRUCT,
)


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
    TUPLE_ITEM = ")"
    SET_ITEM = ">"
    TYPE_INITIATOR = ":"
    DECIMAL_POINT = "."
    RANGE = ".."
    ELLIPSIS = "..."
    SINGLE_QUOTE = "'"
    DOUBLE_QUOTE = '"'
    EXTENDS = "->"


OPENING_BRACKETS = (Operator.LPAREN, Operator.LSQUAREBRACKET, Operator.LCURLYBRACKET)
CLOSING_BRACKETS = (Operator.RPAREN, Operator.RSQUAREBRACKET, Operator.RCURLYBRACKET)

QUOTES = (Operator.SINGLE_QUOTE, Operator.DOUBLE_QUOTE)

MULTI_CHAR_OPERATORS = (
    Operator.DECIMAL_POINT,
    Operator.RANGE,
    Operator.ELLIPSIS,
    Operator.EXTENDS,
)

ITERATOR_ITEMS = (Operator.LIST_ITEM, Operator.TUPLE_ITEM, Operator.SET_ITEM)

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

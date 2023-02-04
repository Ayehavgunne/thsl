from enum import Enum


class EnumDict(Enum):
    @classmethod
    def values(cls) -> list[str]:
        return [enum.value for enum in cls]

    @classmethod
    def keys(cls) -> list[str]:
        return [enum.name for enum in cls]


class DataTypes(EnumDict):
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
    DataTypes.LIST,
    DataTypes.SET,
    DataTypes.DICT,
    DataTypes.TUPLE,
    DataTypes.ENUM,
    DataTypes.STRUCT,
)


class Operators(EnumDict):
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
    TYPE_INITIATOR = ":"
    RANGE = ".."
    ELLIPSIS = "..."
    SINGLE_QUOTE = "'"
    DOUBLE_QUOTE = '"'
    EXTENDS = "->"
    DECIMAL_POINT = "."


OPENING_BRACKETS = (Operators.LPAREN, Operators.LSQUAREBRACKET, Operators.LCURLYBRACKET)
CLOSING_BRACKETS = (Operators.RPAREN, Operators.RSQUAREBRACKET, Operators.RCURLYBRACKET)

QUOTES = (Operators.SINGLE_QUOTE, Operators.DOUBLE_QUOTE)

MULTI_CHAR_OPERATORS = (
    Operators.DECIMAL_POINT,
    Operators.RANGE,
    Operators.ELLIPSIS,
    Operators.EXTENDS,
)

OPERATORS_TO_IGNORE = ("_",)

OTHER_NUMERIC_CHARACTERS = (Operators.DECIMAL_POINT.value, "i", "e", "_", "-")


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

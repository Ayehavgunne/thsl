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
    LIST = "list"
    SET = "set"
    DICT = "dict"
    TUPLE = "tuple"
    ENUM = "enum"
    STRUCT = "struct"
    SERVICE = "service"


class Constants(EnumDict):
    TRUE = "true"
    FALSE = "false"
    NAN = "nan"
    INF = "inf"
    NEGATIVE_INF = "-inf"


class Operators(EnumDict):
    DECORATOR = "@"
    VALUE_DELIMITER = ":"
    MINUS = "-"
    NUMBER_SEPERATOR = "_"
    LPAREN = "("
    RPAREN = ")"
    LSQUAREBRACKET = "["
    RSQUAREBRACKET = "]"
    LCURLYBRACKET = "{"
    RCURLYBRACKET = "}"
    LIST_DELIMITER = ","
    DOT = "."
    RANGE = ".."
    ELLIPSIS = "..."
    SINGLE_QUOTE = "'"
    DOUBLE_QUOTE = '"'
    EXTENDS = "extends"


class TokenType(EnumDict):
    TYPE = "TYPE"
    NUMBER = "NUMBER"
    STRING = "STRING"
    OPERATOR = "OPERATOR"
    CONSTANT = "CONSTANT"
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

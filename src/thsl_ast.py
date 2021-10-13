from dataclasses import dataclass, field
from typing import Union

from src.grammar import DataTypes


@dataclass
class AST:
    line: int
    column: int


@dataclass
class Value(AST):
    value: str


@dataclass
class Collection(AST):
    items: list[AST] = field(default_factory=list)


@dataclass
class Key(AST):
    name: str
    type: DataTypes
    items: Union[Value, Collection]


@dataclass
class AliasDeclaration(AST):
    name: str
    collection: Collection

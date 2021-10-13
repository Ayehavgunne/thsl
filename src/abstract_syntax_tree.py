from dataclasses import dataclass, field

from src.grammar import DataTypes, Operators


@dataclass
class AST:
    line: int
    column: int


@dataclass
class Void(AST):
    def __eq__(self, other) -> bool:
        if self.__class__ == other:
            return True
        return super().__eq__(other)


@dataclass
class Value(AST):
    value: str | Void


@dataclass
class Collection(AST):
    type: DataTypes | str
    items: list[AST] = field(default_factory=list)

    def __post_init__(self):
        if isinstance(self.type, str):
            if self.type == Operators.LSQUAREBRACKET.value:
                self.type = DataTypes.LIST
            elif self.type == Operators.LCURLYBRACKET.value:
                self.type = DataTypes.DICT
            elif self.type == Operators.LANGLEBRACKET.value:
                self.type = DataTypes.SET
            elif self.type == Operators.LPAREN.value:
                self.type = DataTypes.TUPLE
            else:
                raise NotImplementedError


@dataclass
class Key(AST):
    name: str
    type: DataTypes
    items: Value | Collection


@dataclass
class AliasDeclaration(AST):
    name: str
    collection: Collection

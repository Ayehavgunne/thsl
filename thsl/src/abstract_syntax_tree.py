from dataclasses import dataclass, field

from thsl.src.grammar import DataType, Operator


@dataclass
class AST:
    line: int
    column: int


@dataclass
class Void(AST):
    def __eq__(self, other: object) -> bool:
        if self.__class__ == other:
            return True
        return super().__eq__(other)


@dataclass
class Value(AST):
    value: str | Void


@dataclass
class Collection(AST):
    type: DataType | str
    items: list[AST] = field(default_factory=list)

    def __post_init__(self) -> None:
        # convert to match statement
        if isinstance(self.type, str):
            if self.type == Operator.LSQUAREBRACKET.value:
                self.type = DataType.LIST
            elif self.type == Operator.LCURLYBRACKET.value:
                self.type = DataType.DICT
            elif self.type == Operator.LANGLEBRACKET.value:
                self.type = DataType.SET
            elif self.type == Operator.LPAREN.value:
                self.type = DataType.TUPLE
            else:
                raise NotImplementedError


@dataclass
class Key(AST):
    name: str
    type: DataType
    items: Value | Collection
    subtype: DataType | None = None


@dataclass
class AliasDeclaration(AST):
    name: str
    collection: Collection

from dataclasses import dataclass, field

from thsl.src.grammar import CompoundDataType, DataType, Operator


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
    type: DataType | None = None


@dataclass
class Collection(AST):
    type: DataType | str
    items: list[AST] = field(default_factory=list)

    def __post_init__(self) -> None:
        # convert to match statement
        if isinstance(self.type, str):
            if self.type in (Operator.LSQUAREBRACKET.value, Operator.LIST_ITEM.value):
                self.type = CompoundDataType.LIST
            elif self.type == Operator.LCURLYBRACKET.value:
                self.type = CompoundDataType.DICT
            elif self.type in (Operator.LANGLEBRACKET.value, Operator.SET_ITEM.value):
                self.type = CompoundDataType.SET
            elif self.type in (Operator.LPAREN.value, Operator.TUPLE_ITEM.value):
                self.type = CompoundDataType.TUPLE
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

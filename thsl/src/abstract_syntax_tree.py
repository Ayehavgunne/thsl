from dataclasses import dataclass, field

from thsl.src.grammar import (
    CompoundDataType,
    DataType,
    DICT_OPERATORS,
    LIST_OPERATORS,
    SET_OPERATORS,
    TUPLE_OPERATORS,
)


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
        match self.type:
            case str() as collection_type if collection_type in LIST_OPERATORS:
                self.type = CompoundDataType.LIST
            case str() as collection_type if collection_type in SET_OPERATORS:
                self.type = CompoundDataType.SET
            case str() as collection_type if collection_type in TUPLE_OPERATORS:
                self.type = CompoundDataType.TUPLE
            case str() as collection_type if collection_type in DICT_OPERATORS:
                self.type = CompoundDataType.DICT
            case str():
                raise NotImplementedError
            case _:
                return None


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

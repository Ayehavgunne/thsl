from pathlib import Path

from thsl.exceptions import ThslLoadError
from thsl.src.compiler import Compiler
from typing import TextIO


def loads(text: str) -> dict:
    compiler = Compiler(text)
    try:
        return compiler.compile()
    except Exception as err:
        raise ThslLoadError from err


def load(file_path: TextIO | Path) -> dict:
    if isinstance(file_path, Path):
        return loads(file_path.open().read())
    return loads(file_path.read())

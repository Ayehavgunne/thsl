from pathlib import Path
from typing import TextIO

from thsl.exceptions import ThslLoadError
from thsl.src.compiler import Compiler


def loads(text: str) -> dict:
    compiler = Compiler(text)
    try:
        return compiler.compile()
    except Exception as err:
        raise ThslLoadError from err


def load(file_path: TextIO | Path) -> dict:
    if isinstance(file_path, Path):
        with file_path.open() as open_file:
            return loads(open_file.read())
    return loads(file_path.read())

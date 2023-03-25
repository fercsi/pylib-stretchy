from collections.abc import Iterable
from typing import Any

class Formatter:
    sep: str
    rowend: str
    begin: str
    end: str
    index: bool
    arrange: bool
    index_format: str
    def __init__(self, default: Any = ...) -> None: ...
    @property
    def literal(self) -> bool: ...
    @literal.setter
    def literal(self, value: bool) -> None: ...
    @property
    def output(self) -> str: ...
    def reset(self) -> None: ...
    def update_maxwidth(self, content: Iterable) -> None: ...
    def update_maxwidth_default(self) -> None: ...
    def output_iter(self, content: Iterable) -> None: ...
    def output_begin(self) -> None: ...
    def output_end(self) -> None: ...
    def output_firstrow(self, indent: str, index: list[int] = ...) -> None: ...
    def output_rowsep(self, separator: str, indent: str, index: list[int] = ...) -> None: ...
    def output_string(self, content: str) -> None: ...
    def apply_format_string(self, format_string: str) -> None: ...

class StrFormatter(Formatter):
    begin: str
    end: str
    arrange: bool

class ReprFormatter(Formatter):
    sep: str
    rowend: str
    begin: str
    end: str
    arrange: bool

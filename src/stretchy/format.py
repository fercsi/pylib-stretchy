#!/usr/bin/python3

from collections.abc import Iterable
from functools import partial
from io import StringIO
from typing import Any


def _valwidth_str(item: Any) -> int:
    return len(str(item)) if item is not None else 0

def _valwidth_repr(item: Any) -> int:
    return len(repr(item))


def _valrepr_str(item: Any, width: int) -> str:
    if item is None:
        return ' ' * width
    if isinstance(item, (int, float)) and not isinstance(item, bool):
        return f'{item!s: >{width}}'
    else:
        return f'{item!s: <{width}}'

def _valrepr_repr(item: Any, width: int) -> str:
    if isinstance(item, (int, float)) and not isinstance(item, bool):
        return f'{item!r: >{width}}'
    else:
        return f'{item!r: <{width}}'


class Formatter:
    sep: str = ' '
    rowend: str = ''
    begin: str = ''
    end: str = ''
    index: bool = False
    arrange: bool = False
    _literal: bool = False
    index_format: str = 'Index {}:'

    def __init__(self, default: Any = None) -> None:
        self._default: Any = default
        self.reset()
        self.literal = self._literal

    @property
    def literal(self) -> bool:
        return self._literal

    @literal.setter
    def literal(self, value: bool) -> None:
        self._literal = value
        if value:
            self._valwidth = _valwidth_repr
            self._valrepr = _valrepr_repr
        else:
            self._valwidth = _valwidth_str
            self._valrepr = _valrepr_str

    @property
    def output(self) -> str:
        return self._output.getvalue()

    def reset(self) -> None:
        self._maxwidth: int = 0
        self._output: StringIO = StringIO()

    def update_maxwidth(self, content: Iterable) -> None:
        maxwidth: int = max(map(self._valwidth, content))
        self._maxwidth = max(self._maxwidth, maxwidth)

    def update_maxwidth_default(self) -> None:
        self._maxwidth = max(self._maxwidth, self._valwidth(self._default))

    def output_iter(self, content: Iterable) -> None:
        self._output.write(self.begin)
        if self.arrange:
            maxwidth = self._maxwidth
        else:
            maxwidth = 0
        valrepr = partial(self._valrepr, width=maxwidth)
        itrepr: str = self.sep.join(map(valrepr, content))
        self._output.write(itrepr)
        self._output.write(self.end)

    def output_begin(self) -> None:
        self._output.write(self.begin)

    def output_end(self) -> None:
        self._output.write(self.end)

    def output_firstrow(self, indent: str, index: list[int] = []) -> None:
        if not self.index or not index:
            return
        if self.begin:
            self._output.write('\n')
        self._output.write(self.index_format.format(','.join(map(str,index))))
        self._output.write('\n')
        if self.begin:
            self._output.write(indent)

    def output_rowsep(self, separator: str, indent: str, index: list[int] = []) -> None:
        self._output.write(self.rowend + '\n')
        if self.index:
            if index:
                self._output.write(self.index_format.format(','.join(map(str,index))))
                self._output.write('\n')
        else:
            self._output.write(separator)
        if self.begin:
            self._output.write(indent)

    def output_string(self, content: str) -> None:
        self._output.write(content)

    def apply_format_string(self, format_string: str) -> None:
        current = None
        for c in format_string:
            if c == 's':
                self.sep = ''
                current = 'sep'
            elif c == 'r':
                self.rowend = ''
                current = 'rowend'
            elif c == 'b':
                self.begin = ''
                current = 'begin'
            elif c == 'e':
                self.end = ''
                current = 'end'
            elif c == 'i':
                self.index = True
                current = None
            elif c == 'a':
                self.arrange = True
                current = None
            elif c == 'l':
                self.literal = True
                current = None
            elif current == 'sep':
                self.sep += c
            elif current == 'rowend':
                self.rowend += c
            elif current == 'begin':
                self.begin += c
            elif current == 'end':
                self.end += c
            else:
                raise ValueError(f"Unknown format code '{c}' stretchy object")


class StrFormatter (Formatter):
    begin = '['
    end = ']'
    arrange = True


class ReprFormatter (Formatter):
    sep = ', '
    rowend = ','
    begin = '['
    end = ']'
    arrange = True
    _literal = True

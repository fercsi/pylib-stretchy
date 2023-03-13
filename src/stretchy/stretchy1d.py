#!/usr/bin/python3

import itertools
from typing import Any, Callable, TypeVar
from collections.abc import Iterator

T = TypeVar('T')

class Stretchy1D:
    def __init__(self, default: T|None = None) -> None:
        self.pos: list[T|None] = []
        self.neg: list[T|None] = []
        self.default: T|None = default

    def set(self, array: list|tuple, offset: int = 0) -> None:
        if offset >= 0:
            self.neg = []
            self.pos = [self.default] * offset + list(array)
        elif -offset > len(array):
            self.neg = [self.default] * (-offset - len(array)) + list(array[::-1])
            self.pos = []
        else:
            self.neg = list(array[-offset-1::-1])
            self.pos = list(array[-offset:])

    def __setitem__(self, index: int|slice, value: T|None) -> None:
        dim: list[int|None] = [None, None]
        if isinstance(index, slice):
            range_indices = self._range_indices(index)
            # Fill with value! (Python collections do not support this)
            for i in range(*range_indices):
                self.__setitem__(i, value)
            return
        if index >= 0:
            if len(self.pos) <= index:
                self.pos.extend([self.default] * (index - len(self.pos) + 1))
                dim[1] = len(self.pos)
            self.pos[index] = value
        else:
            index = -index - 1
            if len(self.neg) <= index:
                self.neg.extend([self.default] * (index - len(self.neg) + 1))
                dim[0] = -len(self.neg)
            self.neg[index] = value

    def __getitem__(self, index: int|slice) -> T|Iterator|None:
        if isinstance(index, slice):
            range_indices = self._range_indices(index)
            # Return iterator instead of some arbitrary collection
            return (self.__getitem__(i) for i in range(*range_indices))
        if index >= 0:
            if len(self.pos) <= index:
                return self.default
            return self.pos[index]
        else:
            index = -index - 1
            if len(self.neg) <= index:
                return self.default
            return self.neg[index]

    def _range_indices(self, indices: slice) -> tuple[int, int, int]:
        range_indices: list[int|None] = [indices.start, indices.stop, indices.step]
        if range_indices[2] is None:
            range_indices[2] = 1
        assert isinstance(range_indices[2], int)
        if range_indices[0] is None:
            if range_indices[2] > 0:
                range_indices[0] = -len(self.neg)
            else:
                range_indices[0] = len(self.pos) - 1
        if range_indices[1] is None:
            if range_indices[2] > 0:
                range_indices[1] = len(self.pos)
            else:
                range_indices[1] = -len(self.neg) - 1
        assert isinstance(range_indices[0], int)
        assert isinstance(range_indices[1], int)
        return (range_indices[0], range_indices[1], range_indices[2])

    def offset(self) -> int:
        return -len(self.neg)

    def __iter__(self) -> itertools.chain:
        return itertools.chain(reversed(self.neg), self.pos)

    def __len__(self) -> int:
        return len(self.pos) + len(self.neg)

    def __str__(self) -> str:
        return '|' + ','.join(map(str, self)) + '|'

    def __repr__(self) -> str:
        return '|' + ','.join(map(repr, self)) + '|'

    def _columns(self, mod: Callable) -> str:
        maxwidth = max(len(mod(item)) for item in self)
        repr = ''
        for i,item in enumerate(self):
            repr += ' ' if i else ''
            if item is None:
                item = ''
            if isinstance(item, (int, float)):
                repr += f'{mod(item): >{maxwidth}}'
            else:
                repr += f'{mod(item): <{maxwidth}}'
        return repr

    def __format__(self, format: str) -> str:
        if format == '':
            return str(self)
        mod: Callable = str
        if format[0] == 'r':
            mod = repr
            format = format[1:]
        if format == '':
            format = ',s'
        if format == 'a': # arranged in columns
            return self._columns(mod)
        if mod is str:
            values = map(str, ('' if value is None else value for value in self))
        else:
            values = map(repr, self)
        if format == 's': # separated
            return ''.join(values)
        if len(format) == 2 and format[1] == 's':
            return format[0].join(values)
        raise ValueError(f"Unknown format code '{format}' for object of type 'Stretchy1D'")


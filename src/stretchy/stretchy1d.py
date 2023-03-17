#!/usr/bin/python3

import itertools
from typing import Any, Callable, TypeVar
from collections.abc import Iterable, Iterator

from .format import Formatter

T = TypeVar('T')
Boundaries = tuple[tuple[int, int], ...]

class Stretchy1D:
    def __init__(self,
            default: T|None = None,
            *,
            content: Iterable|None = None,
            offset: int = 0
            ) -> None:
        self.pos: list[T|None] = []
        self.neg: list[T|None] = []
        self.default: T|None = default
        if content is not None:
            self.replace_content(content, offset)
        # Default Formatter() is for 'str'
        self.reprformatter = Formatter(self.default)
        self.reprformatter.literal = True
        self.reprformatter.sep = ', '
        self.reprformatter.rowend = ','

    def replace_content(self, content: Iterable, offset: int = 0) -> None:
        if offset >= 0:
            self.neg = []
            self.pos = [self.default] * offset + list(content)
            return
        self.neg = [self.default] * -offset
        self.pos = []
        it = iter(content)
        try:
            for index in range(-offset-1,-1,-1):
                self.neg[index] = next(it)
            while True:
                self.pos.append(next(it))
        except StopIteration:
            return

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

    def boundaries(self) -> tuple[int, int]:
        return -len(self.neg), len(self.pos)

    def __iter__(self) -> itertools.chain:
        return itertools.chain(reversed(self.neg), self.pos)

    def __len__(self) -> int:
        return len(self.pos) + len(self.neg)

    def __format__(self, format: str) -> str:
        formatter: Formatter = Formatter()
        if format:
            formatter.begin = ''
            formatter.end = ''
            formatter.arrange = False
            formatter.apply_format_string(format)
        return self._format(formatter)

    def __str__(self) -> str:
        return self._format(Formatter())

    def __repr__(self) -> str:
        self.reprformatter.reset()
        repr_string: str = self._format(self.reprformatter)
        return f'Stretchy1D(default={self.default!r}, ' \
            f'offset={self.offset()}, content={repr_string})'

    def _maxwidth(self, formatter: Formatter, boundaries: Boundaries) -> None:
        # This private method assumes, that repr shows all values
        formatter.update_maxwidth(self)
        if boundaries[0][0] < -len(self.neg) \
                or boundaries[0][1] > len(self.pos):
            formatter.update_maxwidth_default()

    def _output(self, formatter: Formatter, boundaries: Boundaries, indent: str = '', indices: list[int] = []) -> None:
        b: tuple[int, int] = self.boundaries()
        pre: int = b[0] - boundaries[0][0]
        post: int = boundaries[0][1] - b[1]
        items: itertools.chain = itertools.chain(
            itertools.repeat(self.default, pre),
            self,
            itertools.repeat(self.default, post),
        )
        formatter.output_iter(items)

    def _format(self, formatter: Formatter) -> str:
        formatter.update_maxwidth(self)
        formatter.output_iter(self)
        return formatter.output

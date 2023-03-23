#!/usr/bin/python3

import itertools
from typing import Any, Callable, TypeVar
from collections.abc import Iterable, Iterator

from .abc import Array
from .format import *

T = TypeVar('T')
Boundaries = tuple[tuple[int, int], ...]

class Array1D(Array):
    def __init__(self,
            default: T|None = None,
            *,
            content: Iterable|None = None,
            offset: int = 0
            ) -> None:
        self._pos: list[T|None] = []
        self._neg: list[T|None] = []
        self._default: T|None = default
        if content is not None:
            self.replace_content(content, offset)


    @property
    def dim(self) -> int:
        return 1

    @property
    def offset(self) -> int:
        return -len(self._neg)

    @property
    def boundaries(self) -> tuple[int, int]:
        return -len(self._neg), len(self._pos)


    def replace_content(self, content: Iterable, offset: int = 0) -> None:
        if offset >= 0:
            self._neg = []
            self._pos = [self._default] * offset + list(content)
            return
        self._neg = [self._default] * -offset
        self._pos = []
        it = iter(content)
        try:
            for index in range(-offset-1,-1,-1):
                self._neg[index] = next(it)
            while True:
                self._pos.append(next(it))
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
            if len(self._pos) <= index:
                self._pos.extend([self._default] * (index - len(self._pos) + 1))
                dim[1] = len(self._pos)
            self._pos[index] = value
        else:
            index = -index - 1
            if len(self._neg) <= index:
                self._neg.extend([self._default] * (index - len(self._neg) + 1))
                dim[0] = -len(self._neg)
            self._neg[index] = value

    def __getitem__(self, index: int|slice) -> T|Iterator|None:
        if isinstance(index, slice):
            range_indices = self._range_indices(index)
            # Return iterator instead of some arbitrary collection
            return (self.__getitem__(i) for i in range(*range_indices))
        if index >= 0:
            if len(self._pos) <= index:
                return self._default
            return self._pos[index]
        else:
            index = -index - 1
            if len(self._neg) <= index:
                return self._default
            return self._neg[index]

    def __iter__(self) -> itertools.chain:
        return itertools.chain(reversed(self._neg), self._pos)

    def __len__(self) -> int:
        return len(self._pos) + len(self._neg)

    def __format__(self, format: str) -> str:
        formatter: Formatter = Formatter(self._default)
        formatter.apply_format_string(format)
        return self._format(formatter)

    def __str__(self) -> str:
        return self._format(StrFormatter(self._default))

    def __repr__(self) -> str:
        repr_string: str = self._format(ReprFormatter(self._default))
        return f'Array1D(default={self._default!r}, ' \
            f'offset={self.offset}, content={repr_string})'


    def _range_indices(self, indices: slice) -> tuple[int, int, int]:
        range_indices: list[int|None] = [indices.start, indices.stop, indices.step]
        if range_indices[2] is None:
            range_indices[2] = 1
        assert isinstance(range_indices[2], int)
        if range_indices[0] is None:
            if range_indices[2] > 0:
                range_indices[0] = -len(self._neg)
            else:
                range_indices[0] = len(self._pos) - 1
        if range_indices[1] is None:
            if range_indices[2] > 0:
                range_indices[1] = len(self._pos)
            else:
                range_indices[1] = -len(self._neg) - 1
        assert isinstance(range_indices[0], int)
        assert isinstance(range_indices[1], int)
        return (range_indices[0], range_indices[1], range_indices[2])

    def _maxwidth(self, formatter: Formatter, boundaries: Boundaries) -> None:
        # This private method assumes, that repr shows all values
        if len(self):
            formatter.update_maxwidth(self)
        if boundaries[0][0] < -len(self._neg) \
                or boundaries[0][1] > len(self._pos):
            formatter.update_maxwidth_default()

    def _output(self, formatter: Formatter, boundaries: Boundaries, indent: str = '', indices: list[int] = []) -> None:
        b: tuple[int, int] = self.boundaries
        pre: int = b[0] - boundaries[0][0]
        post: int = boundaries[0][1] - b[1]
        items: itertools.chain = itertools.chain(
            itertools.repeat(self._default, pre),
            self,
            itertools.repeat(self._default, post),
        )
        formatter.output_iter(items)

    def _format(self, formatter: Formatter) -> str:
        if len(self):
            formatter.update_maxwidth(self)
        formatter.output_iter(self)
        return formatter.output

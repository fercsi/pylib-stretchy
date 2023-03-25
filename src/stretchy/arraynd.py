#!/usr/bin/python3

from collections.abc import Iterator, Sequence
import itertools
from typing import Any, TypeVar
#>from typing import Self # from v3.11!

from .abc import Array
from .array1d import Array1D
from .format import *

T = TypeVar('T')
Boundaries = tuple[tuple[int, int], ...]

def _minmax(arr: tuple[tuple[int, int], ...]) -> tuple[int, int]:
    minarr, maxarr = zip(*arr)
    return min(minarr), max(maxarr)


class ArrayND(Array):
    index_format: str|None

    def __init__(self,
            dim: int,
            default: T|None = None,
            *,
            content: Sequence|None = None,
            offset: tuple[int,...]|list[int]|int = 0
            ) -> None:
        self._pos: list = [] # list[Self|Array1D]
        self._neg: list = [] # list[Self|Array1D]
        self._dim: int = dim
        self._default: Any = default
        if content is not None:
            self.replace_content(content, offset)
        self.index_format = None


    @property
    def dim(self) -> int:
        return self._dim

    @property
    def offset(self) -> tuple[int, ...]:
        return tuple(map(lambda e: e[0], self.boundaries))

    @property
    def shape(self) -> tuple[int, ...]:
        return tuple(map(lambda e: e[1] - e[0], self.boundaries))

    @property
    def boundaries(self) -> Boundaries:
        if len(self) == 0:
            return (((0, 0),) * self._dim)
        all_bounds: Iterator[Boundaries]
        if self._dim == 2:
            all_bounds = ((plane.boundaries,) for plane in self)
        else:
            all_bounds = (plane.boundaries for plane in self)
        boundmax: Iterator[tuple[int, int]] = (_minmax(a) for a in zip(*all_bounds))
        return ((-len(self._neg), len(self._pos)), *boundmax)


    def replace_content(self, array: Sequence,
                        offset: tuple[int,...]|list[int]|int = 0) -> None:
        self._neg = []
        self._pos = []
        if isinstance(offset, int):
            offset = [offset] * self._dim
        offset = list(offset)
        current_offset: int = 0
        sub_offset: list[int] = [0]
        if len(offset) > 0:
            current_offset = offset[0]
            if len(offset) > 1:
                sub_offset = offset[1:]
        for index, subarray in enumerate(array, current_offset):
            plane = self._getplane(index) # Self|Array1D
            if self._dim == 2:
                plane.replace_content(subarray, sub_offset[0])
            else:
                plane.replace_content(subarray, sub_offset)

    def __setitem__(self, index: tuple[int, ...], value: T) -> None:
        if not isinstance(index, tuple) or len(index) != self._dim \
                or any(map(lambda x: not isinstance(x, int), index)):
            raise TypeError('Index must be a {self._dim} element tuple of integers')
        plane = self._getplane(index[0]) # Self|Array1D
        if self._dim == 2:
            plane[index[1]] = value
        else:
            plane[index[1:]] = value

    def __getitem__(self, index: int|tuple[int, ...]|slice) -> Any: # Self|Array1D|T
        if isinstance(index, slice):
            range_indices = self._range_indices(index)
            # Return iterator instead of some arbitrary collection
            return (self._getplane(i) for i in range(*range_indices))
        if isinstance(index, int):
            return self._getplane(index)
        if not isinstance(index, tuple) or len(index) != self._dim \
                or any(map(lambda x: not isinstance(x, int), index)):
            raise TypeError('Index must be a {self._dim} element tuple of integers')
        plane = self._getplane(index[0], create=False)
        if plane is None:
            return self._default
        elif self._dim == 2:
            return plane[index[1]]
        else:
            return plane[index[1:]]

    def __iter__(self) -> itertools.chain:
        return itertools.chain(reversed(self._neg), self._pos)

    def __len__(self) -> int:
        return len(self._pos) + len(self._neg)

    def __format__(self, format: str) -> str:
        formatter: Formatter = Formatter(self._default)
        if self.index_format:
            formatter.index_format = self.index_format
        formatter.apply_format_string(format)
        return self._format(formatter)

    def __str__(self) -> str:
        return self._format(StrFormatter(self._default))

    def __repr__(self) -> str:
        repr_string: str = self._format(ReprFormatter(self._default))
        if repr_string != '[]':
            repr_string = '\n' + repr_string
        return f'ArrayND(dim={self._dim}, default={self._default!r}, ' \
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

    def _getplane(self, index: int, create: bool = True) -> Any: # Self|Array1D
        if index >= 0:
            part = self._pos
        else:
            part = self._neg
            index = -index - 1
        if len(part) <= index:
            if not create:
                return None
            if self._dim == 2:
                part.extend([
                    Array1D(default=self._default)
                        for _ in range(index - len(part) + 1)
                ])
            else:
                part.extend([
                    ArrayND(dim=self._dim - 1, default=self._default)
                        for _ in range(index - len(part) + 1)
                ])
        return part[index]

    def _maxwidth(self, formatter: Formatter, boundaries: Boundaries) -> None:
        # This private method assumes, that repr shows all values
        for plane in self:
            plane._maxwidth(formatter, boundaries[1:])
        if boundaries[0][0] < -len(self._neg) \
                or boundaries[0][1] > len(self._pos):
            formatter.update_maxwidth_default()

    def _output(self, formatter: Formatter, boundaries: Boundaries,
                        indent: str = '', indices: list[int] = []) -> None:
        continued: bool = False
        separator: str = '\n' * (self._dim-2)
        subindent: str = indent + ' '
        dummy: Array1D|ArrayND|None = None
        formatter.output_begin()
        for index in range(boundaries[0][0], boundaries[0][1]):
            if continued:
                if self._dim == 3:
                    formatter.output_rowsep(separator, subindent, indices + [index])
                else:
                    formatter.output_rowsep(separator, subindent)
            else:
                if self._dim == 3:
                    formatter.output_firstrow(subindent, indices + [index])
            continued = True
            plane = self._getplane(index, create = False)
            if plane is None:
                if dummy is None: # lazy evaluation if needed
                    if self._dim == 2:
                        dummy = Array1D(self._default)
                    else:
                        dummy = ArrayND(self._dim - 1, self._default)
                plane = dummy
            plane._output(formatter, boundaries[1:], subindent, indices + [index])
        formatter.output_end()

    def _format(self, formatter: Formatter) -> str:
        boundaries = self.boundaries
        self._maxwidth(formatter, boundaries)
        self._output(formatter, boundaries)
        return formatter.output

#!/usr/bin/python3

from typing import Any
from collections.abc import Iterable, Sequence

from .stretchy1d import Stretchy1D
from .stretchynd import StretchyND


def _array_dim(content: Sequence, dim: int = 1) -> int:
    dims: list[int] = []
    for item in content:
        if isinstance(item, (list, tuple)):
            dims.append(_array_dim(item, dim + 1))
        else:
            return dim
    if dims:
        return max(dims)
    return dim


def array(
        content: Sequence|Iterable|None = None,
        *,
        default: Any = None,
        offset: tuple[int]|list[int]|int = 0,
        dim: int|None = None
        ) -> Stretchy1D|StretchyND:
    if dim is None:
        if not content or not isinstance(content, Sequence) \
                or isinstance(content, str):
            dim = 1
        else:
            dim = _array_dim(content)
    assert dim > 0
    if dim == 1:
        assert isinstance(offset, int)
        return Stretchy1D(default=default, content=content, offset=offset)
    else:
        assert isinstance(content, (Sequence, type(None)))
        return StretchyND(dim=dim, default=default, content=content, offset=offset)


def empty(dim: int = 1, *, default: Any = None) -> Stretchy1D|StretchyND:
    if dim == 1:
        return Stretchy1D(default)
    else:
        return StretchyND(dim, default)

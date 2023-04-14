from .format import *
import itertools
from .abc import Array as Array
from .array1d import Array1D as Array1D
from _typeshed import Incomplete
from collections.abc import Sequence
from typing import Any, TypeVar, overload

T = TypeVar('T')
Boundaries: Incomplete

class ArrayND(Array):
    index_format: Union[str, None]
    def __init__(self, dim: int, default: Union[T, None] = ..., *, content: Union[Sequence, None] = ..., offset: Union[tuple[int, ...], list[int], int] = ...) -> None: ...
    @property
    def dim(self) -> int: ...
    @property
    def offset(self) -> tuple[int, ...]: ...
    @property
    def shape(self) -> tuple[int, ...]: ...
    @property
    def boundaries(self) -> Boundaries: ...
    def replace_content(self, content: Union[Sequence, None] = ..., offset: Union[tuple[int, ...], list[int], int] = ..., *, array: Union[Sequence, None] = ...) -> None: ...
    def trim(self) -> None: ...
    @overload
    def shrink_by(self, by: int) -> None: ...
    @overload
    def shrink_by(self, by: tuple[int, ...]) -> None: ...
    @overload
    def shrink_by(self, by: tuple[tuple[int, int], ...]) -> None: ...
    def crop_to(self, boundaries: Boundaries) -> None: ...
    def __bool__(self) -> bool: ...
    def __setitem__(self, index: tuple[int, ...], value: T) -> None: ...
    def __getitem__(self, index: Union[int, tuple[int, ...], slice]) -> Any: ...
    def __iter__(self) -> itertools.chain: ...
    def __len__(self) -> int: ...
    def __format__(self, format: str) -> str: ...

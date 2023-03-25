from .array1d import Array1D
from .arraynd import ArrayND
from collections.abc import Iterable, Sequence
from typing import Any

def array(content: Union[Sequence, Iterable, None] = ..., *, default: Any = ..., offset: Union[tuple[int, ...], list[int], int] = ..., dim: Union[int, None] = ...) -> Union[Array1D, ArrayND]: ...
def empty(dim: int = ..., default: Any = ...) -> Union[Array1D, ArrayND]: ...

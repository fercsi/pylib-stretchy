# Stretchy Python Module

The stretchy module contains  one- and multi-dimensional containers that
can  grow in  any  direction (including  the negative  one).  To grow  a
container, simply add a value to an  element that is not yet used and it
will be created.  Containers are non-sparse containers,  meaning that if
you  give an  element a  value without  skipping several  positions, the
intermediate  values  will  also  take up  space.  The  `default`  value
specified  during  initialization will  be  placed  in these  cells  (by
default `None`). If data  is read from a cell that is  not yet used, the
default value will be returned there as well.

E.g.

```python
import stretchy
array = stretchy.empty(default='.')
for i in range(2,8,2):
  array[-i] = '#'
  array[i] = '#'
print(f'{array:s}')
```

Results in
```
#.#.#...#.#.#
```

It's also important  to note that array  storage starts at 0,  so if you
only put a value in cell 2, 0 and 1 will be created anyway. If you place
an element in  cell -2, then 0 is not created, just -1.  `array[2] = 42`
and `array[-2] = 42` result in the followings (respectively):

```
| -2 |  -1  |   0  |   1  |  2 |
|----|------|------|------|----|
|    |      | None | None | 42 |
| 42 | None |      |      |    |
```

This property affects related features  (such as `offset`, `len`, etc.),
too.

## `stretchy` functions

### `array`

```python
def array(
        content: Sequence|Iterable|None = None,
        *,
        default: Any = None,
        offset: tuple[int, ...]|list[int]|int = 0,
        dim: int|None = None
        ) -> Stretchy1D|StretchyND
```

- `content`: Array-like object (E.g. list, tuple...). In one-dimensional
  case this can be any iterable object (e.g. `itertools`-generated ones,
  or a generator), but in multidimensional cases it can be only Sequence
  of Sequences (e.g. list if lists).
- `offset`:  lower  boundaries  of  the  array  in  all  dimensions.  In
  one-dimensional case it muat be an `int`, and in multidimensional ones
  it is a tuple  of as much values as much the  number of dimensions the
  arrays has. This  value can be `int` also  in multi-dimensional cases,
  so that indexing in all dimensions are the same
- `default`: Default value for non-specified cells. If this parameter is
  not specifoed, the default value of `default` is `None`
- `dim`:  Number of  imensions in  the array.  If not  specified and  no
  `content` is provided the array will be one-dimensional.

This function  can be used to  create stretchy arrays. If  an array-like
array is  given as the input  (`content`) to the function,  the stretchy
array is filled with the contents of  the array. In this case the number
of  dimensions  is determined  automatically  by  the function,  but  in
ambiguous cases you can specify it manually.

In some cases, the determination of dimensions can be ambiguous. This is
the case  when the array contains  strings. By default, the  strings are
kept together  by the  function (except  if the  `content` itself  is an
`str`), but  if you  want the  string to be  interpreted as  a character
sequence, specify the appropriate dimension number. So,

```
stretchy.array(['abc','def','ghi'])
```

is handled as

```
['abc', 'def', 'ghi']
```

but

```
stretchy.array(['abc','def','ghi'], dim=2)
```

is

```
[['a', 'b', 'c'],
 ['d', 'e', 'f'],
 ['g', 'h', 'i']]
```

If the input `content`  is a string, it will be  split up, because dim=0
is pointless.

```
stretchy.array('abcdef')
```

results in a one-dimensional array of characters:

```
['a', 'b', 'c', 'd', 'e', 'f']
```

A more complex example:

```python
import stretchy

tic_tac_toe = stretchy.array(['___'] * 3, dim=2)
steps = ((1,0,'X'), (0,1,'O'), (0,0,'X'), (2,0,'O'), (1,1,'X'), \
                                                  (1,2,'O'), (2,2,'X'))
for i,(x,y,c) in enumerate(steps, 1):
  print('Round', i)
  tic_tac_toe[y,x] = c
  print(f'{tic_tac_toe:sb }')
```

The output of the program is:

```
Round 1
  _X_
  ___
  ___
Round 2
...
Round 7
  XXO
  OX_
  _OX
```

### `empty`

```
def empty(dim: int = 1, *, default: Any = None) -> Stretchy1D|StretchyND
```

This function can be used  to create one- and multi-dimensional stretchy
arrays.  The  functionality  (properties,  methods)  of  one-dimensional
arrays  is  slightly different  from  multi-dimensional  ones. For  more
information, see below.

- `dim`: Dimension  of the array.  If not  specified, the array  will be
  one-dimensional.
- `default`: Default value for non-specified cells. If this parameter is
  not specifoed, the default value of `default` is `None`

Example:

```python
import stretchy

array = stretchy.empty(3, default=0)
array[1,2,0] = 42
array[1,1,2] = 137
array[0,2,2] = 69
print(f'{array:s, ai}')
```

results in

```
Index 0:
  0,   0,   0
  0,   0,   0
  0,   0,  69
Index 1:
  0,   0,   0
  0,   0, 137
 42,   0,   0
```

## Array object properties

The properties can be used to get important information about the array.
There are  also properties  that are  writable. For  one-dimensional and
multi-dimensional arrays, propertys work somewhat differently. These are
discussed in the description of propertys.

### `dim` (read only)

Type: `int`

Use the `dim` property to get the dimension number of the array.

### `boundarires` (read only)

Type:

- One-dimensional arrays: `tuple[int, int]`
- Multi-dimensional arrays: `tuple[tuple[int, int], ...]`

The `boundaries` property can be used  to get the lower and upper bounds
of the array  in each dimension. While in the  multi-dimensional case it
is a tuple of tuples that gives the boundaries in all dimensions, in the
one-dimensional case it is just a tuple of the two boundaries. Following
the pythonic way,  the lower limit is the smallest  index on which there
is a cell, while the upper limit is the largest index plus 1.

E.g.

```python
import stretchy

array = stretchy.array([[1,0,1],[],[1,0,1]], offset=(-1,-1))
print(f'{array.boundaries=}')
print(f'{array!r}')
```

Results in

```
array.boundaries=((-1, 2), (-1, 2))
StretchyND(dim=2, default=None, offset=(-1, -1), content=
[[   1,    0,    1],
 [None, None, None],
  [   1,    0,    1]])
```

### `offset` (read only)

Type:

- One-dimensional arrays: `int`
- Multi-dimensional arrays: `tuple[int, ...]`

This property  is used  to get the  lower bounds of  the array  See also
[boundaries](#boundaries).

### `shape`

Type (only for multi-dimensional arrays): `tuple[int, ...]`

This property is used to get the size of the array in all directions. In
one-dimensional case, use `len(array)` instead.

### `index_format` (read & write)

In case of `dim >= 3`, two-dimensional planes are separated by different
number of empty lines, or by showing  the indices of the plane (See also
[Format](#format)). By default  this latter looks as  follows (5D array,
`f'{array:s,i}'`):

```
...
1,6,2
8,3,6
Index 2,-5,3:
5,7,2
9,5,3
...
```

The index text can be changed by setting the `index_format`. The default
value is `'Index {}:'` and the `{}` will be replaced by the index values
separated by commas.

## Examples

### Langton's ant

```python
import stretchy

array = stretchy.empty(2, default='.')
pos = (0, 0)
dir = 2
for _ in range(11000):
    if array[pos] == '#':
        dir = (dir + 1) % 4
    else:
        dir = (dir - 1) % 4
    array[pos] = '.' if array[pos] == '#' else '#'
    if dir == 0:
        pos = (pos[0], pos[1] + 1)
    elif dir == 1:
        pos = (pos[0] - 1, pos[1])
    elif dir == 2:
        pos = (pos[0], pos[1] - 1)
    elif dir == 3:
        pos = (pos[0] + 1, pos[1])
print(f'{array:s}')
```

## Future plans

There are some ideas for future development:

- **ellipsis**: in case of large arrays, represent values with ellipsis
- **sub-sub-planes**:  with  partial indexing  you  can  get plane  from
  any  levels. E.g.  in a  4-dimensional array,  `array[2,5]` returns  a
  2-dimensional one
- **normalization**:  To  delete  those  cells whose  contents  are  the
  default value, however they are not followed by others.
- **offset  shifting**: Offset  an existing  array without  changing the
  contents.
- **arbitrary  croping**:  Cut  to specified  size,  increase/shrink  by
  value(`int`), reshape to boundaries, cut defaults, etc.
- **non-zero centric operation**: Do not require storage starting from 0
  if all elements are in the positive or negative range.
- **comparison operators**
- **sparse solution**: There  should be no need to  store default items.
  It could be  possible to create huge arrays if  there are many default
  elements in there.

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

It's also important  to note that array  storage starts at 0.  So if you
only put a value in cell 2, cells 0 and 1 will be created anyway. If you
place an  element in cell -2,  then 0 is  not created, just -1.  In this
way,  `array[2] =  42` and  `array[-2] =  42` result  in the  followings
(respectively):

```
| -2 |  -1  |   0  |   1  |  2 |
|----|------|------|------|----|
|    |      | None | None | 42 |
| 42 | None |      |      |    |
```

This property affects related features  (such as `offset`, `len`, etc.),
too.

Also  important to  mention,  that one-  and multi-dimensional  stretchy
arrays' functionality (properties, methods)  are slightly different. For
more information, see below.

## `stretchy` functions

### `array`

```python
def array(
        content: Sequence|Iterable|None = None,
        *,
        default: Any = None,
        offset: tuple[int, ...]|list[int]|int = 0,
        dim: int|None = None
        ) -> Array1D|ArrayND
```

- `content`:   Array-like   object   (E.g.   `list`,   `tuple`...).   In
  one-dimensional   case  this   can  be   any  iterable   object  (e.g.
  `itertools`-generated ones, or a generator), but  in multi-dimensional
  cases it can be only Sequence of Sequences (e.g. list of lists).
- `offset`:  lower  boundaries  of  the  array  in  all  dimensions.  In
  one-dimensional case  it must  be an  `int`, and  in multi-dimensional
  ones  it  is a  `tuple`  of  as much  values  as  much the  number  of
  dimensions the arrays  has. The value of `offset` can  be `int` in the
  multi-dimensional case, in  which case it is equivalent  to having the
  same offset value in all dimensions.
- `default`: Default value for non-specified cells. If this parameter is
  not specified, the default value of `default` is `None`
- `dim`:  Number of  imensions in  the array.  If not  specified and  no
  `content`  is provided  the result  will be  an empty  one-dimensional
  stretchy array.

This function  can be used to  create stretchy arrays. If  an array-like
object is  given as the input (`content`) to the function,  the stretchy
array is filled with the contents of the object. In this case the number
of  dimensions  is determined  automatically  by  the function,  but  in
ambiguous cases you can specify it manually (using `dim`).

In some cases, the determination of dimensions can be ambiguous. This is
the case when the input array  contains strings. By default, the strings
are kept together  by the function (except if the  `content` itself is a
`str`), but  if you  want the  string to be  interpreted as  a character
sequence, specify the appropriate dimension number. So,

```python
stretchy.array(['abc','def','ghi'])
```

is handled as

```python
['abc', 'def', 'ghi']
```

but

```python
stretchy.array(['abc','def','ghi'], dim=2)
```

is

```python
[['a', 'b', 'c'],
 ['d', 'e', 'f'],
 ['g', 'h', 'i']]
```

If the input `content`  is a string, it will be  split up, because dim=0
is pointless.

```python
stretchy.array('abcdef')
```

results in a one-dimensional array of characters:

```python
['a', 'b', 'c', 'd', 'e', 'f']
```

`content`'s  embedded arrays  are  not reused,  so  repeating the  "same
arrays" does  not have any  side-effects. To define  a three-dimensional
array with an initial set of 10x10x10 `'.'` values, you can use:

```python
array = stretchy.array([[['.']*10]*10]*10)
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
  print(f'{tic_tac_toe:b }')
```

The output of the program is:

```
Round 1
  _ X _
  _ _ _
  _ _ _
Round 2
...
Round 7
  X X O
  O X _
  _ O X
```

### `empty`

```
def empty(dim: int = 1, default: Any = None) -> Array1D|ArrayND
```

Although  you can  also  use the  `array` function  to  create an  empty
stretchy array, this is a lightweight option.

- `dim`: Dimension  of the array.  If not  specified, the array  will be
  one-dimensional.
- `default`: Default value for non-specified cells. If this parameter is
  not specifoed, the default value of `default` is `None`.

Example:

```python
import stretchy

array = stretchy.empty(3, 0)
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

### `boundaries` (read only)

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
ArrayND(dim=2, default=None, offset=(-1, -1), content=
[[   1,    0,    1],
 [None, None, None],
 [   1,    0,    1]])
```

### `offset` (read only)

Type:

- One-dimensional arrays: `int`
- Multi-dimensional arrays: `tuple[int, ...]`

This property  is used  to get the  lower bounds of  the array. See also
[boundaries](#boundaries-read-only).

### `shape` (read only)

Type (only for multi-dimensional arrays): `tuple[int, ...]`

This property is used to get the size of the array in all directions. In
one-dimensional case, use `len(array)` instead.

### `index_format` (read & write)

In case of `dim >= 3`, two-dimensional planes are separated by different
number of empty lines, or by showing  the indices of the plane (See also
[Formatting](#formatting)). By default this  latter looks as follows (5D
array, `f'{array:s,i}'`):

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

## Array operations

### Length of array (`len`)

```python
length: int = len(array)
```

The function call gives the size  of the highest dimension of the array.
This is  the length of  the array in  the one-dimensional case,  and the
number of sub-planes (alse the first element of the `shape` property) in
the case of multi-dimensional arrays.

### Getting values or subplanes

By indexing a stretchy array, you can perform several tasks depending on
the type of index.

```python
value: Any = array[5,-7,-2]
subplane: stretchy.Array = array[3]
itr: Iterator = array[-10:10:2]
```

To get the  **value** of a cell,  use a `tuple` in which  the values are
the indices  of all dimensions. If  a non-existent cell is  indexed, the
default value of the array is returned.

You can also  get a **subplane** of  the array (indexed by  an `int`) on
which you can perform further read  or write operations. In this way, we
also affect the whole array. In  the case of a one-dimensional array, we
do not get a plane, but directly  the value of the addressed cell. It is
important to note that  if you request a plane that  does not yet exist,
the plane is  automatically created (for the sake  of write operations),
as  well as  all the  planes between  the current  boundary and  the new
plane.

If you use `slice` as an  index, unlike the traditional python approach,
you don't get  a stretchy array, but an **iterator**  to iterate through
the selected subplanes, or in the one-dimensional case, the cell values.
The note  mentioned in the previous  point, that new planes  are created
when indexing beyond the boundaries, is true also for this case.

In all of  the above cases, it  is true that negative  values and values
beyond the current boundaries are also valid index values.

### Changing cell values

To write  the contents of  the cells, the cells  must be indexed  in the
same way as for rrading:

```python
array[5,-7,-2] = 42
```

For one-dimensional arrays, slice indexing  can also be used, but unlike
it usually is in python, in this case all selected elements of the array
receive the passed value:

```python
import stretchy

array = stretchy.array('_'*31)
array[::3] = 'O'
print(f'{array:s}')
```

results in

```
O__O__O__O__O__O__O__O__O__O__O
```

To replace  the entire contents  of the array,  you can use  the array's
`replace_content` method:

One-dimensional arrays:

```python
replace_content(self, content: Iterable, offset: int = 0) -> None
```

Multi-dimensional arrays:

```python
replace_content(self, array: Sequence,
                      offset: tuple[int,...]|list[int]|int = 0) -> None
```

### Iterating over the array

Stretchy  arrays are  iterable.  This  means, that  you  can  use it  as
follows:

```python
import stretchy

array = stretchy.array([[0]*5]*5, offset=-2)
for index, subplane in enumerate(array, array.offset[0]):
    subplane[0] = index
print(f'{array:a}')
```

And the output is:

```
 0  0 -2  0  0
 0  0 -1  0  0
 0  0  0  0  0
 0  0  1  0  0
 0  0  2  0  0
```

## Formatting

Stretchy arrays come with a set of formatting options:

```python
s1 = f'{array:s;}'
s2 = '{:b|e|s|a}'.format(array)
...
```

Grammar of formatting options can be described as:

```
Format  ← Option*
Option  ← Command Param?
Command ← [a-zA-Z]
Param   ← (Char & !Command)+
Char    ← any single unicode character
```

This  means,  that  options  follow each  other  without  any  separator
characters.  The  ascii  letters  indicate  which  option  to  set,  the
characters after them  are their optional parameters.  Letters cannot be
parameters.

### Formatting options

- `s`: cell  separator. The  character string  after this  option will
  separate values in a row. Default: `' '`
- `r`: row  ending. This value  separates rows (i.e. separator  in the
  second or higher dimensions). Default: `''`
- `b`: beginning of  block. Each dimension is represented  by a single
  block. Default: `''`
- `e`: ending of block. Default: `''`
- `a`: arrange in  columns. `int` and `float` values are  aligned to the
  right, others to the left. `a` turns on arrangement, no parameters are
  allowed.
- `i`:  show indices.  If this  option  is turned  on, the  higher-order
  indices  (>2)  are  displayed   between  the  two-dimensional  blocks.
  Otherwise,  it uses  line breaks  to indicate  which block  follows (1
  empty line:  level 3, 2  empty lines:  level 4...). No  parameters are
  allowed.
- `l`: literal format.  If this option is turned on,  the repr format of
  the  cell content  is  used.  Note, that  otherwise,  `None` value  is
  represented by an empty string. No parameters are allowed.

With examples that build on each other:

```python
import stretchy

array = stretchy.empty(3)
array[-1,0,-1] = '#'
array[-1,0,1] = '@'
array[-1,1,0] = '%'
array[0,0,-1] = '$'
array[0,1,1] = '&'
print(f'{array}')
##  @
# %
#
# $
#   &
print(f'{array:s,}')
##,,@
#,%,
#
#$,,
#,,&
print(f'{array:s,b|e|}')
#|||#,,@|
#  |,%,||
#
# ||$,,|
#  |,,&|||
print(f'{array:s,r;b|e|}')
#|||#,,@|;
#  |,%,||;
#
# ||$,,|;
#  |,,&|||
print(f'{array:s,r;b|e|a}')
#|||#, ,@|;
#  | ,%, ||;
#
# ||$, , |;
#  | , ,&|||
print(f'{array:s,r;b|e|al}')
#|||'#' ,None,'@' |;
#  |None,'%' ,None||;
#
# ||'$' ,None,None|;
#  |None,None,'&' |||
print(f'{array:s,r;b|e|ali}')
#Index -1:
#|||'#' ,None,'@' |;
#  |None,'%' ,None||;
#Index 0:
# ||'$' ,None,None|;
#  |None,None,'&' |||
```

### `str()`

Converting  the   array  to  `str`   is  equivalent  to   the  following
formatting options: `b[e]a`. This also  means, that while `str(array) ==
f'{array:b[e]a}'`, `print(array)` differs from `print(f'{array}')`.

So, let us consider the following sniplet:

```python
import stretchy

array = stretchy.array([[['ab', 'cd'], ['ef', 'gh']], \
                                  [['ij', 'kl'], ['mn', 'op']]], dim=4)
print(array)
print(repr(array))
```

The output of it is:

```
[[[[a b]
   [c d]]

  [[e f]
   [g h]]]


 [[[i j]
   [k l]]

  [[m n]
   [o p]]]]
 ```

### `repr()`

You can  use this function  to print  more information about  the array.
When representing  arrays, other data  in the array are  also displayed,
e.g:

```
ArrayND(dim=2, default='.', offset=(0, 0), content=[])
```

The  `content` part  is  displayed  with the  format  equivalent to  the
following formatting options: `s, r,b[e]al`.

So the same code as above but with the following printout:

```python
print(repr(array)) # or print(f'{array!r}')
```

results in

```
ArrayND(dim=4, default=None, offset=(0, 0, 0, 0), content=
[[[['a', 'b'],
   ['c', 'd']],

  [['e', 'f'],
   ['g', 'h']]],


 [[['i', 'j'],
   ['k', 'l']],

  [['m', 'n'],
   ['o', 'p']]]])
```

## Complex examples

### Langton's ant

```python
import stretchy

array = stretchy.empty(2, '.')
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

- **arbitrary  croping**:  Cut  to specified  size,  increase/shrink  by
  amount (`int`) or reshape to boundaries
- **normalization**:  Cut off  the default values  at the  boundaries to
  prevent unnecessary storage
- **offset  shifting**: Offset  an existing  array without  changing the
  contents. Also, offset to center.
- **non-zero centric operation**: Do not require storage starting from 0
  if all elements are in the positive or negative range.
- **sub-sub-planes**:  with  partial indexing  you  can  get plane  from
  any  levels. E.g.  in a  4-dimensional array,  `array[2,5]` returns  a
  2-dimensional one
- **comparison operators**
- **ellipsis**: in case of large arrays, represent values with ellipsis (`str` or `repr`)

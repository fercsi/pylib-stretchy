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
from stretchy import Stretchy1D
array = Stretchy1D('.')
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

## Formatting

To indroduce different  formatting opportunities, let us  start from the
following stretchy array:

```python
array1d = Stretchy1D()
array1d.set(('#', 42, None, False, 3.1), -2)
```

### `str`

This  format can  be  used  with `str`  or  `format` without  formatting
options, so  the followings are equivalent:  `str(array)`, `f'{array}'`,
`f'{array!s}`.   The   result  is   comma   separated   values  of   str
representation of each element, surrounded by `|` characters:

```
|#,42,None,False,3.1|
```

### `repr`

The repr formatting (aka `repr(array)`  or `f'{array!r}'`) is similar to
the `str`  one except  that it  contains comma  separated values  of the
`repr` representation of the elements.

```
|'#',42,None,False,3.1|
```

### Arrangement into columns

To arrange  elements into  columns of same  with, use  formatting option
`a`: `f'{array:a}'`. In  this case elements will occupy  the same number
of  characters.  The non-used  characters  are  filled with  space.  The
columns are also separated by spaces.  The `None` values are replaced by
an empty field. Elements of types  `int` and `float` are arranged to the
right, all other types are arranged to the left.

```
     .     .     .     .     .
#        42       False   3.1
```

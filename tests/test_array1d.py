import pytest

from stretchy import Array1D

@pytest.mark.parametrize('default',
    (42, '#', 42.69, None, False)
)
def test_default(default):
    s = Array1D(default)
    assert s[2] == default
    assert s[-2] == default
    s[5] = ...
    assert s[3] == default
    s[-5] = ...
    assert s[-3] == default


def test_replace_content():
    # Simple prelimunary test; more tests later...
    s = Array1D('.')
    s.replace_content('abcde', 2)
    assert f'{s:s}' == '..abcde'
    s.replace_content('abcde', -7)
    assert f'{s:s}' == 'abcde..'


@pytest.mark.parametrize('pos, content',
    (
        ((0,), '#'),
        ((2,), '..#'),
        ((6,2), '..#...#'),
        ((2,6), '..#...#'),
        ((-2,), '#.'),
        ((-6,-2), '#...#.'),
        ((-2,-6), '#...#.'),
        ((-2,2), '#...#'),
        ((2,-2), '#...#'),
    )
)
def test_setitem(pos, content):
    s = Array1D('.')
    for p in pos:
        s[p] = '#'
    assert f'{s:s}' == content


@pytest.mark.parametrize('default, arr, check',
    (
        ([], ((None,None,7),), {0:None, 1:None, 2:7, 3:None, -1:None}),
        ((0,), ((0,0,7),), {0:0, 1:0, 2:7, 3:0, -1:0}),
        ((0,), ((7,),), {0:7, 1:0, -1:0}),
        ((0,), ((7,),2), {0:0, 1:0, 2:7, 3:0, -1:0}),
        ((0,), ((7,),-2), {0:0, -1:0, -2:7, -3:0, 1:0}),
    )
)
def test_getitem(default, arr, check):
    s = Array1D(*default)
    s.replace_content(*arr)
    for pos, value in check.items():
        assert s[pos] == value


SLICE_INPUT = (
    ((None,), '#########', 'abcdefghi'),

    ((-2,None), 'ab#######', 'cdefghi'),
    ((0,None), 'abcd#####', 'efghi'),
    ((2,None), 'abcdef###', 'ghi'),
    ((-6,None), '###########', '..abcdefghi'),
    ((6,None), 'abcdefghi', ''),

    ((None,-2), '##cdefghi', 'ab'),
    ((None,0), '####efghi', 'abcd'),
    ((None,2), '######ghi', 'abcdef'),
    ((None,-6), 'abcdefghi', ''),
    ((None,7), '###########', 'abcdefghi..'),

    ((-2,2), 'ab####ghi', 'cdef'),
    ((-6,2), '########ghi', '..abcdef'),
    ((-2,7), 'ab#########', 'cdefghi..'),
    ((-6,7), '#############', '..abcdefghi..'),

    ((None,None,3), '#bc#ef#hi', 'adg'),
    ((None,None,-3), 'ab#de#gh#', 'ifc'),
    ((-6,7,3), '#.a#cd#fg#i.#', '.beh.'),
    ((6,-7,-3), '#.a#cd#fg#i.#', '.heb.'),
)

@pytest.mark.parametrize('indices, content, got', SLICE_INPUT)
def test_setitem_slice(indices, content, got):
    s = Array1D(default='.', content='abcdefghi', offset=-4)
    s[slice(*indices)] = '#'
    assert f'{s:s}' == content


@pytest.mark.parametrize('indices, content, got', SLICE_INPUT)
def test_getitem_slice(indices, content, got):
    s = Array1D(default='.', content='abcdefghi', offset=-4)
    assert ''.join(s[slice(*indices)]) == got


# Followings test also the `replace_content` method
TEST_DATA = (
    (((7,),), [7]),
    (((7,),2), [None, None, 7]),
    (((7,),-2), [7, None]),
    (((7,8,9),2), [None, None, 7, 8, 9]),
    (((7,8,9),-2), [7, 8, 9]),
)

@pytest.mark.parametrize('arr, content', TEST_DATA)
def test_offset(arr, content):
    s = Array1D()
    s.replace_content(*arr)
    offset = arr[1] if len(arr) == 2 and arr[1] < 0 else 0
    assert s.offset == offset


@pytest.mark.parametrize('arr, content', TEST_DATA)
def test_boundaries(arr, content):
    s = Array1D()
    s.replace_content(*arr)
    offset = arr[1] if len(arr) == 2 and arr[1] < 0 else 0
    assert s.boundaries == (offset, offset + len(content))


@pytest.mark.parametrize('arr, content', TEST_DATA)
def test_len(arr, content):
    s = Array1D()
    s.replace_content(*arr)
    assert len(s) == len(content)


@pytest.mark.parametrize('arr, content', TEST_DATA)
def test_iter(arr, content):
    s = Array1D()
    s.replace_content(*arr)
    assert list(s) == content


@pytest.mark.parametrize('params, offset, content',
    (
        (('12345',), 0, '12345'),
        (('12345',3), 0, '...12345'),
        (('12345',-3), -3, '12345'),
        (('12345',-7), -7, '12345..'),
        (((1,2,3,4,5),-3), -3, '12345'),
        (([1,2,3,4,5],-3), -3, '12345'),
    )
)
def test_set(params, offset, content):
    s = Array1D('.')
    s.replace_content(*params)
    assert s.offset == offset
    assert f'{s:s}' == content


@pytest.fixture
def array():
    s = Array1D(default='.', offset=-3,
        content=('x', None,'.',234,'.',False,6.7))
    return s


def test_str_empty():
    s = Array1D()
    assert str(s) == "[]"


def test_str(array):
    assert str(array) == "[x           .       234 .     False   6.7]"


def test_repr_empty():
    s = Array1D()
    assert repr(s) == "Array1D(default=None, offset=0, content=[])"


def test_repr(array):
    assert repr(array) == "Array1D(default='.', offset=-3, " \
        "content=['x'  , None , '.'  ,   234, '.'  , False,   6.7])"


@pytest.mark.parametrize('fmt,result',
    (
        ('{}', "x  . 234 . False 6.7"),
        ('{:}', "x  . 234 . False 6.7"),
        ('{!s}', "[x           .       234 .     False   6.7]"),
        ('{!r}', "Array1D(default='.', offset=-3, " \
            "content=['x'  , None , '.'  ,   234, '.'  , False,   6.7])"),

        ('{:a}', "x           .       234 .     False   6.7"),

        ('{:s}', "x.234.False6.7"),
        ('{:s }', "x  . 234 . False 6.7"),
        ('{:s,}', "x,,.,234,.,False,6.7"),

        ('{:l}', "'x' None '.' 234 '.' False 6.7"),
        ('{:ls}', "'x'None'.'234'.'False6.7"),
        ('{:ls }', "'x' None '.' 234 '.' False 6.7"),
        ('{:ls,}', "'x',None,'.',234,'.',False,6.7"),

        ('{:s,b<e>}', "<x,,.,234,.,False,6.7>"),
    )
)
def test_format(fmt, result, array):
    assert fmt.format(array) == result


def test_wrong_format(array):
    with pytest.raises(ValueError):
        '{:@@@}'.format(array)


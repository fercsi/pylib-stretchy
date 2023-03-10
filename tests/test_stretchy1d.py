import pytest

from stretchy import Stretchy1D

@pytest.mark.parametrize('default',
    ( (42,), ('#',), (42.69,), (None,), (False,),)
)
def test_default(default):
    s = Stretchy1D(default)
    assert s[2] == default
    assert s[-2] == default
    s[5] = ...
    assert s[3] == default
    s[-5] = ...
    assert s[-3] == default


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
    s = Stretchy1D('.')
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
    s = Stretchy1D(*default)
    s.set(*arr)
    for pos, value in check.items():
        assert s[pos] == value


TEST_DATA = (
    (((7,),), [7]),
    (((7,),2), [None, None, 7]),
    (((7,),-2), [7, None]),
    (((7,8,9),2), [None, None, 7, 8, 9]),
    (((7,8,9),-2), [7, 8, 9]),
)

@pytest.mark.parametrize('arr, content', TEST_DATA)
def test_offset(arr, content):
    s = Stretchy1D()
    s.set(*arr)
    offset = arr[1] if len(arr) == 2 and arr[1] < 0 else 0
    assert s.offset() == offset


@pytest.mark.parametrize('arr, content', TEST_DATA)
def test_len(arr, content):
    s = Stretchy1D()
    s.set(*arr)
    assert len(s) == len(content)


@pytest.mark.parametrize('arr, content', TEST_DATA)
def test_iter(arr, content):
    s = Stretchy1D()
    s.set(*arr)
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
    s = Stretchy1D('.')
    s.set(*params)
    assert s.offset() == offset
    assert '{:s}'.format(s) == content


@pytest.fixture
def array():
    s = Stretchy1D('.')
    s.set(('x', None,'.',234,'.',False,6.7), -3)
    return s


def test_str(array):
    assert str(array) == '|x,None,.,234,.,False,6.7|'


def test_repr(array):
    assert repr(array) == "|'x',None,'.',234,'.',False,6.7|"


@pytest.mark.parametrize('fmt,result',
    (
        ('{}', '|x,None,.,234,.,False,6.7|'),
        ('{:}', "|x,None,.,234,.,False,6.7|"),
        ('{!s}', "|x,None,.,234,.,False,6.7|"),
        ('{!r}', "|'x',None,'.',234,'.',False,6.7|"),

        ('{:a}', "x           .       234 .     False   6.7"),

        ('{:s}', "x.234.False6.7"),
        ('{: s}', "x  . 234 . False 6.7"),
        ('{:,s}', "x,,.,234,.,False,6.7"),

        ('{:r}', "'x',None,'.',234,'.',False,6.7"),
        ('{:rs}', "'x'None'.'234'.'False6.7"),
        ('{:r s}', "'x' None '.' 234 '.' False 6.7"),
        ('{:r,s}', "'x',None,'.',234,'.',False,6.7"),
    )
)
def test_format(fmt, result, array):
    assert fmt.format(array) == result


def test_wrong_format(array):
    with pytest.raises(ValueError):
        '{:@@@}'.format(array)


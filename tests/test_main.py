#!/usr/bin/python3

import pytest
from itertools import product

import stretchy


@pytest.mark.parametrize('array, atype',
    (
        (stretchy.empty(1), stretchy.Array1D),
        (stretchy.empty(2), stretchy.ArrayND),
        (stretchy.empty(3), stretchy.ArrayND),
        (stretchy.array('abcde'), stretchy.Array1D),
        (stretchy.array(['ab','de']), stretchy.Array1D),
        (stretchy.array(['ab','de'], dim=2), stretchy.ArrayND),
        (stretchy.array([['ab','cd'],['ef','gh']]), stretchy.ArrayND),
    )
)
def test_isinstance(array, atype):
    assert isinstance(array, atype)
    assert isinstance(array, stretchy.Array)
    assert type(array) is atype


@pytest.mark.parametrize('params, dim, default, content, offset',
    (
        # dim
        ({}, 1, None, '', 0),
        ({'dim':1}, 1, None, '', 0),
        ({'dim':2}, 2, None, '', (0,)*2),
        ({'dim':4}, 4, None, '', (0,)*4),
        # default
        ({'default':'x'}, 1, 'x', '', 0),
        ({'dim':2, 'default':'x'}, 2, 'x', '', (0,)*2),
        ({'dim':4, 'default':'x'}, 4, 'x', '', (0,)*4),
        # content
        ({'content':'abcde'}, 1, None, 'a,b,c,d,e', 0),
        ({'content':['ab','cd']}, 1, None, 'ab,cd', 0),
        ({'content':['ab','cd'], 'dim':2}, 2, None, 'a,b\nc,d', (0,)*2),
        ({'content':[['ab','cd'],['ef','gh']]}, 2, None, 'ab,cd\nef,gh', (0,)*2),
        ({'content':[['ab','cd'],['ef','gh']], 'dim':3}, 3, None, 'a,b\nc,d\n\ne,f\ng,h', (0,)*3),
        ({'content':range(-4,5,2)}, 1, None, '-4,-2,0,2,4', 0),
        ({'content':map(''.join, product('xy',repeat=2))}, 1, None, 'xx,xy,yx,yy', 0),
        # offset
        ({'content':'abcde', 'offset':-2}, 1, None, 'a,b,c,d,e', -2),
        ({'content':'abcde', 'offset':-8}, 1, None, 'a,b,c,d,e,,,', -8),
        ({'content':'abcde', 'offset':0}, 1, None, 'a,b,c,d,e', 0),
        ({'content':'abcde', 'offset':3}, 1, None, ',,,a,b,c,d,e', 0),
        ({'content':['ab','cd'], 'dim':2, 'offset':-1}, 2, None, 'a,b\nc,d', (-1,)*2),
        ({'content':['ab','cd'], 'dim':2, 'offset':-3}, 2, None, 'a,b,\nc,d,\n,,', (-3,)*2),
        ({'content':['ab','cd'], 'dim':2, 'offset':0}, 2, None, 'a,b\nc,d', (0,)*2),
        ({'content':['ab','cd'], 'dim':2, 'offset':1}, 2, None, ',,\n,a,b\n,c,d', (0,)*2),
        ({'content':['ab','cd'], 'dim':2, 'offset':(-3,-4)}, 2, None, 'a,b,,\nc,d,,\n,,,', (-3,-4)),
        ({'content':['ab','cd'], 'dim':2, 'offset':(-3,2)}, 2, None, ',,a,b\n,,c,d\n,,,', (-3,0)),
        ({'content':['ab','cd'], 'dim':2, 'offset':(1,-4)}, 2, None, ',,,\na,b,,\nc,d,,', (0,-4)),
        ({'content':['ab','cd'], 'dim':2, 'offset':(1,2)}, 2, None, ',,,\n,,a,b\n,,c,d', (0,)*2),
    )
)
def test_array(params, dim, default, content, offset):
    array = stretchy.array(**params)
    assert array.dim == dim
    assert array._default == default
    if dim == 1:
        pos = 200
    else:
        pos = (200,) * dim
    assert array[pos] == default
    assert array.offset == offset
    assert f'{array:s,}' == content


@pytest.mark.parametrize('params, dim, default',
    (
        (tuple(), 1, None),
        ((1,), 1, None),
        ((2,), 2, None),
        ((4,), 4, None),
        ((1,'x'), 1, 'x'),
        ((2,'x'), 2, 'x'),
        ((4,'x'), 4, 'x'),
    )
)
def test_empty(params, dim, default):
    array = stretchy.empty(*params)
    assert array.dim == dim
    assert array._default == default
    if dim == 1:
        pos = 2
    else:
        pos = (2,) * dim
    assert array[pos] == default

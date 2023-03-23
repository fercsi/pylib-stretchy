import pytest

from stretchy import ArrayND

@pytest.mark.parametrize('default',
    (42, '#', 42.69, None, False)
)
def test_default(default):
    s = ArrayND(3, default)
    assert s[2,2,2] == default
    assert s[-2,-2,-2] == default


def view(offset, *planes):
    v = []
    for plane in planes:
        v.append(f'Index {offset}:')
        offset += 1
        for row in plane:
            v.append(row)
    return '\n'.join(v)


def test_replace_content():
    # Simple prelimunary test; more tests later...
    s = ArrayND(3, '.')
    s.replace_content([['ab','cd'],['ef','gh']], (1,2,3))
    exp = view( 0,
        [*['.'*5]*4],
        [*['.'*5]*2, '...ab', '...cd'],
        [*['.'*5]*2, '...ef', '...gh'],
    )
    assert f'{s:si}' == exp
    s.replace_content([['ab','cd'],['ef','gh']], (-3,-4,-5))
    exp = view( -3,
        ['ab...', 'cd...', *['.'*5]*2],
        ['ef...', 'gh...', *['.'*5]*2],
        [*['.'*5]*4],
    )
    assert f'{s:si}' == exp


def test_setitem():
    pass # TODO


def test_getitem():
    pass # TODO


INPUT_DATA = (
    (
        ((-1,-2),(-3,-1)),
        ((-3,0),(-2,0)),
        ('#','','#.')
    ), (
        ((1,2),(3,1)),
        ((0,4),(0,3)),
        ('','..#','','.#')
    ), (
        ((-2,3),(4,-5)),
        ((-2,5),(-5,4)),
        ('...#',*['']*5,'#....')
    ), (
        ((-1,-1,-2),(-1,-3,-1),(-4,-1,-1)),
        ((-4,0),(-3,0),(-2,0)),
        ('#','','','.#\n..\n#.')
    ), (
        ((1,1,2),(1,3,1),(4,1,1)),
        ((0,5),(0,4),(0,3)),
        ('','...\n..#\n...\n.#.','','','..\n.#')
    ), (
        ((-1,2,-3),(4,-5,-1),(-6,-1,7)),
        ((-6,5),(-5,3),(-3,8)),
        ('.......#',*['']*4,'...\n...\n#..',*['']*4,'#\n.\n.\n.\n.')
    ),
)

@pytest.mark.parametrize('cells, boundaries, planes', INPUT_DATA)
def test_offset(cells, boundaries, planes):
    s = ArrayND(len(boundaries))
    for cell in cells:
        s[cell] = 1
    assert s.offset == tuple(b[0] for b in boundaries)


@pytest.mark.parametrize('cells, boundaries, planes', INPUT_DATA)
def test_shape(cells, boundaries, planes):
    s = ArrayND(len(boundaries))
    for cell in cells:
        s[cell] = 1
    assert s.shape == tuple(b[1]-b[0] for b in boundaries)


@pytest.mark.parametrize('cells, boundaries, planes', INPUT_DATA)
def test_boundaries(cells, boundaries, planes):
    s = ArrayND(len(boundaries))
    for cell in cells:
        s[cell] = 1
    assert s.boundaries == boundaries


@pytest.mark.parametrize('cells, boundaries, planes', INPUT_DATA)
def test_len(cells, boundaries, planes):
    s = ArrayND(len(boundaries), '.')
    for cell in cells:
        s[cell] = '#'
    assert len(s) == len(planes)


@pytest.mark.parametrize('cells, boundaries, planes', INPUT_DATA)
def test_iter(cells, boundaries, planes):
    s = ArrayND(len(boundaries), '.')
    for cell in cells:
        s[cell] = '#'
    assert tuple(f'{sub:s}' for sub in s) == planes


@pytest.fixture
def array():
    s = ArrayND(dim=3, default='.', offset=-1, content=
        ((('x', None),
          ('.', 234)),
         (('.', False),
          (6.7, 1.1)))
    )
    return s


def test_str(array):
    pass # TODO


def test_repr(array):
    pass # TODO


def test_format(array):
#>    print(f'{array:a}')
    pass # TODO



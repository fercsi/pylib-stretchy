import pytest

from stretchy import ArrayND

def rows_to_str(rows):
    return '\n'.join(rows)


def view(offset, *planes):
    v = []
    for plane in planes:
        v.append(f'Index {offset}:')
        offset += 1
        for row in plane:
            v.append(row)
    return '\n'.join(v)


@pytest.fixture
def array():
    s = ArrayND(dim=4, default='.', offset=-1, content=
        (((('x', None),
           ('.', 234)),
          (('.', False),
           (6.7, 1.1))),
         (((None, None),
           (None, 'y')),
          ((-1, True),
           ('', None))))
    )
    return s


@pytest.mark.parametrize('default',
    (42, '#', 42.69, None, False)
)
def test_default(default):
    s = ArrayND(3, default)
    assert s[2,2,2] == default
    assert s[-2,-2,-2] == default


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


SE2 = [['...']*3] * 2
SE3 = [['...']*3] * 3
SP = ['...','...','..#']
SN = ['#..','...','...']
@pytest.mark.parametrize('pos, content',
    (
        (((0,0,0),), (['#'])),
        (((2,2,2),), (*SE2, SP)),
        (((6,2,2),(2,2,2)), (*SE2, SP, *SE3, SP)),
        (((2,2,2),(6,2,2)), (*SE2, SP, *SE3, SP)),
        (((-3,-3,-3),), (SN, *SE2)),
        (((-7,2,2),(-3,2,2)), (SP, *SE3, SP, *SE2)),
        (((-3,2,2),(-7,2,2)), (SP, *SE3, SP, *SE2)),
        (((-3,2,2),(2,2,2)), (SP, *SE2, *SE2, SP)),
        (((3,2,2),(-2,2,2)), (SP, *SE2, *SE2, SP)),
    )
)
def test_setitem(pos, content):
    dim = len(pos[0])
    offset = min(p[0] for p in pos)
    if offset > 0:
        offset = 0
    s = ArrayND(dim=dim, default='.')
    for p in pos:
        s[p] = '#'
    assert f'{s:si}' == view(offset, *content)


@pytest.mark.parametrize('index, content',
    (
        ((-1,-1,-1,-1), 'x'),
        ((-2,-1,-1,-1), '.'),
        ((-1,-1,-2,-1), '.'),
        ((-1,-1,-1,-2), '.'),
        ((0,0,0,0), None),
        ((1,0,0,0), '.'),
        ((0,0,1,0), '.'),
        ((0,0,0,1), '.'),
    )
)
def test_getitem(index, content, array):
    assert array[index] == content


def test_getitem_plane(array):
    plane = array[-1]
    expected = rows_to_str(["x ", ". 234", "", ". False", "6.7 1.1"])
    assert f'{plane}' == expected
    plane[-1,-1,-1] = 69
    expected = rows_to_str([
            "69 ", ". 234", "", ". False", "6.7 1.1", "", "",
            " ", " y", "", "-1 True", " "
        ])
    assert f'{array}' == expected


SLICE_INPUT = (
    ((None,), '|||||||||', 'abcdefghi'),

    ((-2,None), 'ab|||||||', 'cdefghi'),
    ((0,None), 'abcd|||||', 'efghi'),
    ((2,None), 'abcdef|||', 'ghi'),
    ((-6,None), '|||||||||||', '..abcdefghi'),
    ((6,None), 'abcdefghi', ''),

    ((None,-2), '||cdefghi', 'ab'),
    ((None,0), '||||efghi', 'abcd'),
    ((None,2), '||||||ghi', 'abcdef'),
    ((None,-6), 'abcdefghi', ''),
    ((None,7), '|||||||||||', 'abcdefghi..'),

    ((-2,2), 'ab||||ghi', 'cdef'),
    ((-6,2), '||||||||ghi', '..abcdef'),
    ((-2,7), 'ab|||||||||', 'cdefghi..'),
    ((-6,7), '|||||||||||||', '..abcdefghi..'),

    ((None,None,3), '|bc|ef|hi', 'adg'),
    ((None,None,-3), 'ab|de|gh|', 'ifc'),
    ((-6,7,3), '|.a|cd|fg|i.|', '.beh.'),
    ((6,-7,-3), '|.a|cd|fg|i.|', '.heb.'),
)

@pytest.mark.parametrize('indices, content, got', SLICE_INPUT)
def test_getitem_slice1d(indices, content, got):
    s = ArrayND(dim=2, default='.')
    for i, c in enumerate('abcdefghi', -4):
        j = round(i/4)
        s[i,j] = c
    # check read planes
    check = []
    for plane in s[slice(*indices)]:
        c = max(plane[i] for i in (-1, 0, 1))
        check.append(c)
        plane[0] = '|' # write
    assert ''.join(check) == got
    # check written planes
    check = []
    for plane in s:
        c = max(plane[i] for i in (-1, 0, 1))
        check.append(c)
    assert ''.join(check) == content


@pytest.mark.parametrize('indices, content, got', SLICE_INPUT)
def test_getitem_slicend(indices, content, got):
    s = ArrayND(dim=3, default='.')
    for i, c in enumerate('abcdefghi', -4):
        j = round(i/4)
        s[i,j,j] = c
    # check read planes
    check = []
    for plane in s[slice(*indices)]:
        c = max(plane[i,i] for i in (-1, 0, 1))
        check.append(c)
        plane[0,0] = '|' # write
    assert ''.join(check) == got
    # check written planes
    check = []
    for plane in s:
        c = max(plane[i,i] for i in (-1, 0, 1))
        check.append(c)
    assert ''.join(check) == content


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


def test_str(array):
    expected = [
        '[[[[x          ]',
        '   [.       234]]',
        '',
        '  [[.     False]',
        '   [  6.7   1.1]]]',
        '',
        '',
        ' [[[           ]',
        '   [      y    ]]',
        '',
        '  [[   -1 True ]',
        '   [           ]]]]',
    ]
    assert str(array) == rows_to_str(expected)


def test_repr(array):
    expected = [
        "ArrayND(dim=4, default='.', offset=(-1, -1, -1, -1), content=",
        "[[[['x'  , None ],",
        "   ['.'  ,   234]],",
        "",
        "  [['.'  , False],",
        "   [  6.7,   1.1]]],",
        "",
        "",
        " [[[None , None ],",
        "   [None , 'y'  ]],",
        "",
        "  [[   -1, True ],",
        "   [''   , None ]]]])",
    ]
    assert repr(array) == rows_to_str(expected)


@pytest.mark.parametrize('fmt, expected',
    (
        ( "{}", [
                "x ", ". 234", "", ". False", "6.7 1.1", "", "",
                " ", " y", "", "-1 True", " "
            ]),
        ( "{:s,}", [
                "x,", ".,234", "", ".,False", "6.7,1.1", "", "",
                ",", ",y", "", "-1,True", ","
            ]),
        ( "{:s,b<e>}", [
                "<<<<x,>", "   <.,234>>",
                "", "  <<.,False>", "   <6.7,1.1>>>",
                "", "", " <<<,>", "   <,y>>",
                "", "  <<-1,True>", "   <,>>>>"
            ]),
        ( "{:s,b<e>r;}", [
                "<<<<x,>;", "   <.,234>>;",
                "", "  <<.,False>;", "   <6.7,1.1>>>;",
                "", "", " <<<,>;", "   <,y>>;",
                "", "  <<-1,True>;", "   <,>>>>"
            ]),
        ( "{:s,b<e>r;a}", [
                "<<<<x    ,     >;", "   <.    ,  234>>;", "",
                "  <<.    ,False>;", "   <  6.7,  1.1>>>;", "", "",
                " <<<     ,     >;", "   <     ,y    >>;", "",
                "  <<   -1,True >;", "   <     ,     >>>>"
            ]),
        ( '{:s,b<e>r;al}', [
                "<<<<'x'  ,None >;", "   <'.'  ,  234>>;", "",
                "  <<'.'  ,False>;", "   <  6.7,  1.1>>>;", "", "",
                " <<<None ,None >;", "   <None ,'y'  >>;", "",
                "  <<   -1,True >;", "   <''   ,None >>>>"
            ]),
        ( '{:s,r;ali}', [
                "Index -1,-1:", "'x'  ,None ;", "'.'  ,  234;",
                "Index -1,0:", "'.'  ,False;", "  6.7,  1.1;",
                "Index 0,-1:", "None ,None ;", "None ,'y'  ;",
                "Index 0,0:", "   -1,True ;", "''   ,None "
            ]),
    )
)
def test_format(fmt, expected, array):
    assert fmt.format(array) == rows_to_str(expected)



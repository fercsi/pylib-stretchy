#!/usr/bin/python3

class Space1D:
    def __init__(self, default=None):
        self.pos = []
        self.neg = []
        self.default = default


    def __setitem__(self, index, value):
        self._setitem(index, value)


    def _setitem(self, index, value):
        dim = [None, None]
        if index >= 0:
            if len(self.pos) <= index:
                self.pos.extend([self.default] * (index - len(self.pos) + 1))
                dim[1] = len(self.pos)
            self.pos[index] = value
        else:
            index = -index - 1
            if len(self.neg) <= index:
                self.neg.extend([self.default] * (index - len(self.neg) + 1))
                dim[0] = -len(self.neg)
            self.neg[index] = value
        return tuple(dim)


    def __getitem__(self, index):
        if index >= 0:
            if len(self.pos) <= index:
                return self.default
            return self.pos[index]
        else:
            index = -index - 1
            if len(self.neg) <= index:
                return self.default
            return self.neg[index]


    def offset(self):
        return -len(self.neg)


    def list(self):
        l = self.neg.copy()
        l.reverse()
        l.extend(self.pos)
        return l


    def __iter__(self):
        l = self.neg.copy()
        l.reverse()
        l.extend(self.pos)
        return iter(l)


    def __len__(self):
        return len(self.pos) + len(self.neg)


    def __repr__(self):
        maxwidth = 0
        repr = '';
        for c in range(-len(self.neg), len(self.pos)):
            w = len(f'{self.__getitem__(c)!r}')
            if w > maxwidth:
                maxwidth = w
        for c in range(-len(self.neg), len(self.pos)):
            if c > -len(self.neg):
                repr += ' '
            item = self.__getitem__(c)
            if type(item) == int:
                repr += f'{item!r: >{maxwidth}}'
            else:
                repr += f'{item!r: <{maxwidth}}'
        return '|' + repr + '|'


    def __format__(self, format):
        if format == 'condensed':
            return ''.join([str(self.__getitem__(c)) for c in range(-len(self.neg), len(self.pos))])
        return self.__str__()


class Space2D:
    def __init__(self, default=None):
        self.br = []
        self.bl = []
        self.tr = []
        self.tl = []
        self.left = 0
        self.right = 0
        self.default = default


    def __setitem__(self, index, value):
        if type(index) != tuple or len(index) != 2 \
                or type(index[0]) != int or type(index[1]) != int:
            raise TypeError('Space2D indices must be a two element tuple of integers')
        row = self._getrow(index[0])
        (chgleft, chgright) = row._setitem(index[1], value)
        if chgleft != None and chgleft < self.left:
            self.left = chgleft
        if chgright != None and chgright > self.right:
            self.right = chgright


    def __getitem__(self, index):
        if type(index) == int:
            return self._getrow(index)
        if type(index) != tuple or len(index) != 2 \
                or type(index[0]) != int or type(index[1]) != int:
            raise TypeError('Space2D indices must be a two element tuple of integers')
        row = self._getrow(index[0], False)
        return row[index[1]] if row != None else self.default


    def _getrow(self, index, create=True):
        if index >= 0:
            if len(self.br) <= index:
                if not create:
                    return None
                self.br.extend([[] for _ in range(index - len(self.br) + 1)])
                self.bl.extend([[] for _ in range(index - len(self.bl) + 1)])
            pos = self.br[index]
            neg = self.bl[index]
        else:
            index = -index - 1
            if len(self.tr) <= index:
                if not create:
                    return None
                self.tr.extend([[] for _ in range(index - len(self.tr) + 1)])
                self.tl.extend([[] for _ in range(index - len(self.tl) + 1)])
            pos = self.tr[index]
            neg = self.tl[index]
        row = Space1D(self.default)
        row.pos = pos
        row.neg = neg
        return row


    def crop(self, top, left, bottom, right):
        if top > 0:
            raise ValueError('top cannot be larger than 0')
        if left > 0:
            raise ValueError('left cannot be larger than 0')
        if bottom < 0:
            raise ValueError('bottom cannot be smaller than 0')
        if right < 0:
            raise ValueError('right cannot be smaller than 0')
#>        if -top > len(self.tr):
        del self.tr[-top:]
        del self.tl[-top:]
        del self.br[bottom:]
        del self.bl[bottom:]
        for row in self.tl:
            del row[-left:]
        for row in self.bl:
            del row[-left:]
        for row in self.tr:
            del row[right:]
        for row in self.br:
            del row[right:]
        if left > self.left:
            self.left = left
        if right < self.right:
            self.right = right


    def shrink(self, by):
        top = -len(self.tr) + by
        if top > 0:
            top = 0
        left = self.left + by
        if left > 0:
            left = 0
        bottom = len(self.br) - by
        if bottom < 0:
            bottom = 0
        right = self.right - by
        if right < 0:
            right = 0
        self.crop(top, left, bottom, right)

    def offset(self):
        return (-len(self.tr), self.left)

    def shape(self):
        return (len(self.br)+len(self.tr), self.right-self.left)

    def boundaries(self):
        return (-len(self.tr), self.left, len(self.br), self.right)

    def __iter__(self):
        for idx in range(-len(self.tr), len(self.br)):
            yield self._getrow(idx)

    def __len__(self):
        return len(self.tr) + len(self.br)

    def __repr__(self):
        return self._repr_with_boundaries(-len(self.tr), self.left, len(self.br), self.right)

    def __format__(self, format):
        if format == 'condensed':
            return self._format_condensed_with_boundaries(-len(self.tr), self.left, len(self.br), self.right)
        return self.__str__()

    def _repr_with_boundaries(self, bt, bl, bb, br):
        maxwidth = 0
        repr = ''
        for r in range(-len(self.tr), len(self.br)):
            row = self._getrow(r)
            for c in range(self.left, self.right):
                w = len(f'{row[c]!r}')
                if w > maxwidth:
                    maxwidth = w
        for r in range(bt, bb):
            row = self._getrow(r, create=False)
            repr += '|'
            if row == None:
                row = Space1D(default=self.default)
            for c in range(bl, br):
                if c != bl:
                    repr += ' '
                if type(row[c]) == int:
                    repr += f'{row[c]!r: >{maxwidth}}'
                else:
                    repr += f'{row[c]!r: <{maxwidth}}'
            repr += '|\n'
        return repr[0:-1]

    def _format_condensed_with_boundaries(self, bt, bl, bb, br):
        repr = ''
        for r in range(bt, bb):
            row = self._getrow(r)
            if row == None:
                row = Space1D(default=self.default)
            repr += ''.join([str(row[c]) for c in range(bl, br)]) + '\n'
        return repr[0:-1]


class Space3D:

    def __init__(self, default=None):
        self.part_pos:list[Space2D] = []
        self.part_neg:list[Space2D] = []
        self.default = default


    def __setitem__(self, index, value):
        if type(index) != tuple or len(index) != 3 \
                or type(index[0]) != int or type(index[1]) != int  \
                or type(index[2]) != int:
            raise TypeError('Space3D indices must be a three element tuple of integers')
        plane = self._getplane(index[0])
        plane[index[1], index[2]] = value


    def __getitem__(self, index):
        if type(index) == int:
            return self._getplane(index)
        if type(index) != tuple or len(index) != 3 \
                or type(index[0]) != int or type(index[1]) != int  \
                or type(index[2]) != int:
            raise TypeError('Space3D indices must be a three element tuple of integers')
        plane = self._getplane(index[0], create=False)
        return plane[index[1], index[2]] if plane != None else self.default


    def _getplane(self, index, create=True):
        if index >= 0:
            if len(self.part_pos) <= index:
                if not create:
                    return None
                self.part_pos.extend([Space2D(default=self.default) for _ in range(index - len(self.part_pos) + 1)])
            return self.part_pos[index]
        else:
            index = -index - 1
            if len(self.part_neg) <= index:
                if not create:
                    return None
                self.part_neg.extend([
                    Space2D(default=self.default)
                        for _ in range(index - len(self.part_neg) + 1)
                ])
            return self.part_neg[index]


    def offset(self):
        return self.boundaries()[:3]


    def shape(self):
        bound = self.boundaries()
        return (bound[3]-bound[0], bound[4]-bound[1], bound[5]-bound[2])


    def boundaries(self):
        boundmax = [0] * 4
        for p in range(-len(self.part_neg), len(self.part_pos)):
            plane = self._getplane(p)
            pbound = plane.boundaries()
            boundmax[0] = min(boundmax[0], pbound[0])
            boundmax[1] = min(boundmax[1], pbound[1])
            boundmax[2] = max(boundmax[2], pbound[2])
            boundmax[3] = max(boundmax[3], pbound[3])
        return (-len(self.part_neg), *boundmax[:2], len(self.part_pos), *boundmax[2:])


    def __iter__(self):
        for idx in range(-len(self.part_neg), len(self.part_pos)):
            yield self._getplane(idx)


    def __len__(self):
        return len(self.part_neg) + len(self.part_pos)


    def __repr__(self):
        bounds = self.boundaries()
        bounds = bounds[1:3] + bounds[4:6]
        return '\n\n'.join([
            self._getplane(p)._repr_with_boundaries(*bounds)
                for p in range(-len(self.part_neg), len(self.part_pos))
        ])

    def __format__(self, format):
        if format == 'condensed':
            bounds = self.boundaries()
            bounds = bounds[1:3] + bounds[4:6]
            return '\n\n'.join([self._getplane(p)._format_condensed_with_boundaries(*bounds)
                    for p in range(-len(self.part_neg), len(self.part_pos))])
        return self.__str__()


def _minmac(it):
    pass

class SpaceND:

    def __init__(self, dimensions, default=None):
        self.part_pos:list[Space2D] = []
        self.part_neg:list[Space2D] = []
        self.dimensions = dimensions
        self.default = default


    def __setitem__(self, index, value):
        if type(index) != tuple or len(index) != self.dimension \
                or any(map(lambda x: type(x) is not int, index)):
            raise TypeError('Index must be a {self.dimension} element tuple of integers')
        plane = self._getplane(index[0])
        plane[index[1:]] = value


    def __getitem__(self, index):
        if type(index) == int:
            return self._getplane(index)
        if type(index) != tuple or len(index) != self.dimension \
                or any(map(lambda x: type(x) is not int, index)):
            raise TypeError('Index must be a {self.dimension} element tuple of integers')
        plane = self._getplane(index[0], create=False)
        return plane[index[1:]] if plane != None else self.default


    def _getplane(self, index: int, create: bool = True):
        if index >= 0:
            part = self.part_pos
        else:
            part = self.part_neg
            index = -index - 1
        if len(part) <= index:
            if not create:
                return None
            if self.dimensions == 3:
                part.extend([
                    Space2D(default=self.default)
                        for _ in range(index - len(part) + 1)
                ])
            else:
                part.extend([
                    SpaceND(dimensions=self.dimensions, default=self.default)
                        for _ in range(index - len(part) + 1)
                ])
        return part[index]

    #def resize/reshape: 
    # - no param: cut defaults
    # - 1 int: invrease/shrink by int
    # - 1 tuple[tuple[int, int]]: boundaries (crop/extend)

    def offset(self):
        return tuple(map(lambda e: e[0], self.boundaries()))


    def shape(self):
        return tuple(map(lambda e: e[1] - e[0], self.boundaries()))


    def boundaries(self):
        if self.dimensions == 3:
            all_bounds = []
            for p in range(-len(self.part_neg), len(self.part_pos)):
                b = self._getplane(p).boundaries()
                all_bounds.append(((b[0], b[2]), (b[1], b[3])))
        else:
            all_bounds = [
                self._getplane(p).boundaries()
                for p in range(-len(self.part_neg), len(self.part_pos))
            ]
        boundmax = [_minmax(a) for a in zip(*all_bounds)]
        return ((-len(self.part_neg), len(self.part_pos)), *boundmax)


    def __iter__(self):
        for idx in range(-len(self.part_neg), len(self.part_pos)):
            yield self._getplane(idx)


    def __len__(self):
        return len(self.part_neg) + len(self.part_pos)


    def __repr__(self):
        bounds = self.boundaries()
        bounds = bounds[1:3] + bounds[4:6]
        return '\n\n'.join([self._getplane(p)._repr_with_boundaries(*bounds)
                for p in range(-len(self.part_neg), len(self.part_pos))])

    def __format__(self, format):
        if format == 'condensed':
            bounds = self.boundaries()
            bounds = bounds[1:3] + bounds[4:6]
            return '\n\n'.join([self._getplane(p)._format_condensed_with_boundaries(*bounds)
                    for p in range(-len(self.part_neg), len(self.part_pos))])
        return self.__str__()

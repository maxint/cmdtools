# coding: utf-8
# author: maxint <NOT_SPAM_lnychina@gmail.com>
# version: 0.2

class Rect:
    def __init__(self, left=0, top=0, right=0, bottom=0):
        self.xmin = left
        self.ymin = top
        self.xmax = right
        self.ymax = bottom

    @staticmethod
    def from_center_size(x, y, width, height):
        return Rect(x - width / 2,
                    y - height / 2,
                    x + width / 2,
                    y + height / 2)

    @staticmethod
    def from_center_size1(center, size):
        return Rect.from_center_size(center[0], center[1], size[0], size[1])

    @property
    def cx(self):
        return (self.xmin + self.xmax) / 2

    @property
    def cy(self):
        return (self.ymin + self.ymax) / 2

    @property
    def center(self):
        return self.cx, self.cy

    @property
    def width(self):
        return self.xmax - self.xmin

    @property
    def height(self):
        return self.ymax - self.ymin

    @property
    def size(self):
        return self.width, self.height

    @property
    def area(self):
        return self.width * self.height

    @property
    def empty(self):
        return self.xmin == self.xmax or self.ymin == self.ymax

    @property
    def array(self):
        return self.xmin, self.ymin, self.xmax, self.ymax

    @property
    def is_zero(self):
        return all(map(lambda x: x == 0, self.array))

    @property
    def is_valid(self):
        return self.is_zero or not self.empty

    def __eq__(self, other):
        return all(map(lambda ab: ab[0] == ab[1], zip(self.array, other.array)))

    def __and__(self, other):
        return Rect(max(self.xmin, other.xmin),
                    max(self.ymin, other.ymin),
                    min(self.xmax, other.xmax),
                    min(self.ymax, other.ymax))

    def __or__(self, other):
        return Rect(min(self.xmin, other.xmin),
                    min(self.ymin, other.ymin),
                    max(self.xmax, other.xmax),
                    max(self.ymax, other.ymax))

    def __str__(self):
        return 'Rect ({})'.format(','.join(map(str, self.array)))


import re

DOT_PARSER_RE = re.compile(r'^(-?\d+),\s*(-?\d+),\s*(-?\d+),\s*(-?\d+)$')
"""
e.g.
332, 379, 738, 858
317, 381, 723, 860
300, 381, 706, 860
284, 393, 690, 872
...
"""

MARK_PARSER_RE = re.compile(r'^\d+[\s,\(\)0-9]*\s+\((-?\d+),(-?\d+),(-?\d+),(-?\d+)\)$')
"""
e.g.
0	(0,0,0)	(564,459,760,740)
1	(0,0,0)	(564,459,760,740)
2	(0,0,0)	(564,459,760,740)
3	(0,0,0)	(564,459,760,740)
4	(0,0,0)	(564,459,760,740)
...
or
0	(564,459,760,740)
1	(564,459,760,740)
2	(564,459,760,740)
3	(564,459,760,740)
4	(564,459,760,740)
...
"""


def parse_rect(line, pattern=DOT_PARSER_RE):
    m = pattern.match(line)
    assert m, 'Invalid format: ' + line
    g = m.groups()
    rc = Rect(*map(int, [g[0], g[1], g[2], g[3]]))
    assert rc.is_valid, 'Invalid rectangle: ' + line
    return rc


def parse_rect_with_index(line, pattern=MARK_PARSER_RE):
    assert isinstance(line, str)
    idx, res = line.split(None, 1)
    return int(idx), parse_rect(line, pattern)


def load_result(lines):
    return map(parse_rect, lines)


def load_marks(lines, verbose=True):
    data = []
    for line in lines:
        m = MARK_PARSER_RE.match(line)
        assert m, line
        g = m.groups()
        idx = int(g[0])
        rect = Rect(*map(int, [g[1], g[2], g[3], g[4]]))
        assert rect.is_valid, line
        if idx == len(data):
            data.append(rect)
        elif idx == len(data) - 1:
            if verbose:
                print '[W] Replace with duplicate mark: ', line
            data[idx] = rect
        else:
            raise Exception('Wrong data: ' + line)
    return data


def filter_marks(idx_rcs, allow_skip_frame=True):
    rcs = []
    for idx, rc in idx_rcs:
        if idx == len(rcs):
            rcs.append(rc)
        elif idx == len(rcs) - 1:
            # replace old one
            rcs[idx] = rc
        elif allow_skip_frame:
            rcs += [Rect()] * (idx - len(rcs) +1)
        else:
            raise Exception('Wrong index: ' + str(idx))
    return rcs


def load(path):
    with open(path) as f:
        line = f.readline()
        f.seek(0)
        # check whether it's in mark format
        is_marks = re.match(MARK_PARSER_RE, line) != None
        parser = parse_rect_with_index if is_marks else parse_rect
        data = map(parser, f)
        return filter_marks(data) if is_marks else data


if __name__ == '__main__':
    print len(load('data/1.avi_fingerMark_res.txt'))
    print len(load('data/1.avi_fingerMark.txt'))

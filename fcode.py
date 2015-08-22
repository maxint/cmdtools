# coding: utf-8
# author: maxint <NOT_SPAM_lnychina@gmail.com>

"""
Format code to my favorite style.

- Remove space surrounding brackets.
- Add space after 'if', 'for', 'swith', 'while', etc.

"""

import re

RLIST = [
    (re.compile(r'(if|for|switch|while)\('), r'\g<1> ('),
    (re.compile(r'\(\s(.*)\s\)'), r'(\g<1>)'),
    (re.compile(r'\t'), r'    '),
    (re.compile(r'\s+(\s)$'), r'\g<1>'),
]


def doline(line):
    for r, t in RLIST:
        line = r.sub(t, line)
    return line


def dofile(fpath):
    with open(fpath, 'r+') as f:
        lines = f.readlines()
        f.seek(0)
        f.truncate()
        for line in lines:
            f.write(doline(line))

if __name__ == '__main__':
    import sys
    dofile(sys.argv[1])

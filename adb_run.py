# coding: utf-8
# author: maxint <NOT_SPAM_lnychina@gmail.com>

import subprocess
import glob
import os

TMP_DIR = '/data/tmp'


def call(cmd):
    print cmd
    subprocess.check_call(cmd)


def parse_file_patterns(patterns):
    files = []
    for patt in patterns:
        if '*' in patt:
            files.extend(glob.glob(patt))
        elif os.path.isfile(patt):
            files.append(patt)
        else:
            print '[E] Unknown input file: "{}"'.format(patt)

    # unique list
    return list(set(files))


def run(path):
    src = path
    dst = TMP_DIR + '/' + os.path.basename(path)
    call('adb push {} {}'.format(src, dst))
    call('adb shell chmod 777 ' + dst)
    call('adb shell ' + dst)


def test():
    import sys

    files = parse_file_patterns(sys.argv[1:])
    if files:
        # prepare
        call('adb root on')
        call('adb shell mkdir -p ' + TMP_DIR)
        map(run, files)


if __name__ == '__main__':
    test()

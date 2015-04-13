#! /usr/bin/env python
# coding: utf-8

"""
Delete given files and update release note in SDK ZIP file.

examples:
    python sdkrm.py *.ZIP -d libarcsoft_face_tracking.so libarcsoft_face_detection.so
"""

import os
import shutil
import tempfile
import zipfile
import glob


def update_release_note(content, *deletes):
    deletes = ['|---' + d for d in deletes]
    def do_filter(line):
        return not any(d in line for d in deletes)

    return '\n'.join(filter(do_filter, content.splitlines()))


def sdk_rm(src_path, dst_file, *deletes):
    with zipfile.ZipFile(src_path, 'r') as z:
        with zipfile.ZipFile(dst_file, 'w') as zz:
            for name in z.namelist():
                basename = os.path.basename(name)
                if basename in deletes:
                    print '  Ignore', name
                    continue
                elif basename == 'releasenotes.txt':
                    zz.writestr(name, update_release_note(z.read(name), *deletes))
                else:
                    zz.writestr(name, z.read(name))


def sdk_rm_inplace(path, *deletes):
    tmp_file = tempfile.NamedTemporaryFile(suffix='.ZIP')
    try:
        sdk_rm(path, tmp_file, *deletes)
        shutil.move(tmp_file.name, path)
    except:
        os.unlink(tmp_file.name)
    assert not os.path.exists(tmp_file.name)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Remove files from SDK')
    parser.add_argument('targets', nargs='*', default=['*.ZIP'], help='Target ZIP SDKs')
    parser.add_argument('--deletes', '-d', nargs='+', help='Files to be deleted')

    args = parser.parse_args()

    print 'Files to be deleted:', args.deletes
    for name in args.targets:
        print 'Glob', name
        for path in glob.glob(name):
            print 'Processing', path
            sdk_rm_inplace(path, *args.deletes)

    print 'Done!'

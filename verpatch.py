#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright (C) 2014 maxint <NOT_SPAM_lnychina@gmail.com>
#
# Distributed under terms of the MIT license.

"""
Patch version resources to ArcSoft .exe or .dll files.
"""

import re
import subprocess
import os


def patch(path, verbose=False):
    text = open(path, 'rb').read()
    m = re.search(r'(ArcSoft_[a-zA-z_]+)_(\d{1,3}\.\d{1,3}\.\d{1,5}\.\d{1,4})[_a-zA-Z0-9:\(\)\ ]*[^\d]*(\d{1,2}/\d{1,2}/\d{4,4}).*(Copyright[\w\s\d,.]+)', text)
    product = m.group(1).replace('_', ' ')
    version = m.group(2)
    date = m.group(3)
    copyright = m.group(4)

    if verbose:
        print 'PRODUCT NAME:', product
        print 'PRODUCT VERSION:', version
        print 'BUILD DATE:', date
        print 'COPYRIGHT:', copyright

    cmd = 'verpatch /va "{0}" "{1}" /s company "ArcSoft Inc." /s title "{2}" /s copyright "{3}" /s product "{4}" /pv "{1} ({5})"'.format(
        path,
        version,
        os.path.basename(path),
        copyright,
        product,
        date
    )
    if verbose:
        print cmd
    subprocess.check_call(cmd)
    return path

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(
        description='Patch version resources to ArcSoft .dll library')
    parser.add_argument('file', help='target file')
    args = parser.parse_args()

    patch(args.file, True)

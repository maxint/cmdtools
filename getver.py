# coding: utf-8

import os
import zipfile
import re

def full_version_with_date(content):
    '''Get full version string with date (e.g. ArcSoft_XXX_0.1.12018.125_log(dev Nov 17 2013 14:08:30))'''
    m = re.search(r'ArcSoft_[a-zA-z_]+_\d{1,3}\.\d{1,3}\.\d{1,5}\.\d{1,4}[_a-zA-Z0-9:\(\)\ ]*', content)
    return m.group(0) if m else None

def is_library(name):
    for ext in ['.so', '.a', '.lib', '.dll']:
        if name.endswith(ext):
            return True

    return False


def get_versions(file):
    try:
        zz = zipfile.ZipFile(file)
    except:
        print '[E] Invalid ZIP data stream'

    names = filter(is_library, zz.namelist())
    versions = []
    for name in names:
        content = zz.open(name).read()
        v = full_version_with_date(content)
        if v:
            versions.append((name, v))
    return versions


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Get ArcSoft versions in ZIP input')
    parser.add_argument('file', type=argparse.FileType('rb'),
                        help='Target file to extract versions')

    args = parser.parse_args()

    for (name, version) in get_versions(args.file) or []:
        print '{}: {}'.format(name, version)
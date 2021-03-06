# coding: utf-8
# author: maxint <NOT_SPAM_lnychina@gmail.com>

import os
import zipfile
import re

def split3(version_str):
    """Split version numbers in version string, e.g.(0.1.2)"""
    m = re.search(r"^(\d+).(\d+).(\d+)$", version_str)
    if m:
        return m.groups()[0:3]


def split4(version_str):
    """Split version numbers in version string, e.g.(0.1.2.3)"""
    # e.g. ArcSoft_XXX_0.1.12018.125_log(dev Nov 17 2013 14:08:30)
    m = re.search(r'(?:_|\b)(\d{1,3})\.(\d{1,3})\.(\d{1,5})\.(\d{1,4})(?:_|\b)', version_str)
    if m:
        return m.groups()[0:4]

def full_version_with_date(content):
    """Get full version string with date (e.g. ArcSoft_XXX_0.1.12018.125_log(dev Nov 17 2013 14:08:30))"""
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
        return

    names = filter(is_library, zz.namelist())
    versions = []
    for name in names:
        content = zz.read(name)
        v = full_version_with_date(content)
        if v:
            versions.append((name, v))
    return versions


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Get ArcSoft versions in ZIP input')
    parser.add_argument('file', type=argparse.FileType('rb'),
                        help='Target file to extract versions')
    parser.add_argument('-nogui', '-n', action='store_true',
                        help='Do not show GUI message box')

    args = parser.parse_args()

    versions = get_versions(args.file) or []
    msg = map(lambda (name, version):'{}: {}'.format(name, version), versions)
    msg = '\n'.join(msg)

    print msg
    if not args.nogui:
        import tkMessageBox
        from Tkinter import Tk
        r = Tk()
        r.withdraw()
        name = os.path.basename(args.file.name)
        tkMessageBox.showinfo('Versions in ' + name, msg)
        r.destroy()
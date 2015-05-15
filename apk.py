#! /usr/bin/env python
# coding: utf-8

import subprocess
import os
import glob

def run(cmd, **kwargs):
    subprocess.check_call(cmd, **kwargs)


def build(project_dir, verbose=False, ndk_build=True):
    def do(cmd):
        run(cmd, stdout=subprocess.STDOUT if verbose else subprocess.PIPE)

    if verbose:
        print('[C] android update project')
    do('E:/NDK/adt-bundle-windows-x86-20130219/sdk/tools/android.bat --silent update project --path ' + project_dir)

    if ndk_build:
        if verbose:
            print('[C] ndk-build')
        do('E:/NDK/android-ndk-r8e/ndk-build.cmd --silent -C ' + project_dir)

    if verbose:
        print('[C] ant debug')
    do('E:/NDK/apache-ant-1.9.0/bin/ant.bat debug -silent -f ' + os.path.join(project_dir, 'build.xml'))

    return get_apk(project_dir)


def get_apk(project_dir):
    paths = glob.glob(os.path.join(project_dir, 'bin', '*-debug.apk'))
    assert len(paths) == 1
    return paths[0]


if __name__ == '__main__':
    import argparse

    class readable(argparse.Action):
        def __call__(self, parser, namespace, values, option_string=None):
            path = values
            if not os.path.isdir(path):
                msg = '{0} is not a valid path'.format(path)
                parser.error(msg)
            setattr(namespace, self.dest, path)

    parser = argparse.ArgumentParser(description='Build APK')
    parser.add_argument('project_dir', action=readable, nargs='?', default='.',
                        help='APK project directory')
    parser.add_argument('--verbose', '-V', action='store_true')
    parser.add_argument('--noNDK', '-n', action='store_true',
                        help='do not run ndk-build')

    args = parser.parse_args()

    path = build(args.project_dir, args.verbose, not args.noNDK)
    print '[I] Final APK:', path
    print 'Done!'
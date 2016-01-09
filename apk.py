# coding: utf-8
# author: maxint <NOT_SPAM_lnychina@gmail.com>

import subprocess
import os
import glob
import re
import shutil

def run(cmd, **kwargs):
    subprocess.check_call(cmd, **kwargs)


def is_library(project_dir):
    path = os.path.join(project_dir, 'project.properties')
    return re.search(r'\nandroid\.library=true\s*\n', open(path).read()) is not None


def build(project_dir, verbose=False, ndk_build=True):
    def do(cmd):
        if verbose:
            print '    ' + cmd
            run(cmd)
        else:
            run(cmd, stdout=subprocess.PIPE)

    def echo(msg):
        if verbose:
            print(msg)

    is_lib = is_library(project_dir)

    # remove output directory
    bin_dir = os.path.join(project_dir, 'bin')
    if os.path.exists(bin_dir):
        echo('[I] Clean ' + bin_dir)
        shutil.rmtree(bin_dir)

    echo('[C] android update project')
    if is_lib:
        do('E:/NDK/android-sdk/tools/android.bat --silent update lib-project --path ' + project_dir)
    else:
        do('E:/NDK/android-sdk/tools/android.bat --silent update project --path ' + project_dir)

    if ndk_build:
        echo('[C] ndk-build')
        do('E:/NDK/android-ndk-r10d/ndk-build.cmd --silent -C ' + project_dir)

    echo('[C] ant debug')
    do('E:/NDK/apache-ant/bin/ant.bat debug -silent -f ' + os.path.join(project_dir, 'build.xml'))

    return get_output(project_dir, is_lib)


def get_output(project_dir, is_library):
    pattern = os.path.join(project_dir, 'bin/*.jar' if is_library else 'bin/*-debug.apk')
    paths = glob.glob(pattern)
    assert len(paths) == 1, pattern
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
    print '[I] Final output:', path
    print 'Done!'

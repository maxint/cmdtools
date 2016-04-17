# coding: utf-8
# author: maxint <NOT_SPAM_lnychina@gmail.com>

import subprocess
import os
import glob
import re
import shutil


android_exec = 'E:/NDK/android-sdk/tools/android.bat'
ndk_build_exec = 'E:/NDK/android-ndk-r10d/ndk-build.cmd'
ant_exec = 'E:/NDK/apache-ant/bin/ant.bat'


def run(cmd, **kwargs):
    subprocess.check_call(cmd, **kwargs)


def is_library(project_dir):
    path = os.path.join(project_dir, 'project.properties')
    return re.search(r'\nandroid\.library=true\s*\n', open(path).read()) is not None


def get_reference_libraries(project_dir):
    project_properties_path = os.path.join(project_dir, 'project.properties')
    if not os.path.exists(project_properties_path):
        return

    paths = []
    for line in open(project_properties_path).readlines():
        m = re.search(r'android\.library.reference\.\d+=([^\n]*)', line)
        if m:
            paths.append(m.group(1))
    return paths


def build(project_dir, verbose=False, ndk_build=True):
    for path in get_reference_libraries(project_dir):
        build(os.path.join(project_dir, path), verbose, ndk_build)

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
    cmd = android_exec + ' --silent update {} --path {}'
    cmd = cmd.format('lib-project' if is_lib else 'project', project_dir)
    do(cmd)

    if ndk_build:
        echo('[C] ndk-build')
        do(ndk_build_exec + ' --silent -C ' + project_dir)

    echo('[C] ant debug')
    do(ant_exec + ' debug -silent -f ' + os.path.join(project_dir, 'build.xml'))

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
    parser.add_argument('--no_ndk_build', '-n', action='store_true',
                        help='do not run ndk-build')

    args = parser.parse_args()

    path = build(args.project_dir, args.verbose, not args.no_ndk_build)
    print '[I] Final output:', path
    print 'Done!'

# !/usr/bin/env python
# coding: utf-8

import subprocess
import os
import glob

def run(cmd):
    subprocess.check_call(cmd)


def build_apk(project_dir):
    print('[C] android update project')
    run('E:/NDK/adt-bundle-windows-x86-20130219/sdk/tools/android.bat --silent update project --path ' + project_dir)
    print('[C] ndk-build')
    run('E:/NDK/android-ndk-r8e/ndk-build.cmd --silent -C ' + project_dir)
    print('[C] ant debug')
    run('E:/NDK/apache-ant-1.9.0/bin/ant.bat debug -silent -f ' + os.path.join(project_dir, 'build.xml'))
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

    args = parser.parse_args()

    path = build_apk(args.project_dir)
    print '[I] Final APK:', path
    print 'Done!'
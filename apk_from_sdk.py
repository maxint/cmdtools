# coding: utf-8
# author: maxint <NOT_SPAM_lnychina@gmail.com>

import os
import re
import zipfile

import apk
import getver

def get_ABI_name(project_dir):
    # check libs/
    names = os.listdir(os.path.join(project_dir, 'libs'))
    if len(names) == 1 and names[0].startswith('armeabi'):
        return names[0]

    # check Application.mk
    with open(os.path.join(project_dir, 'jni/Application.mk')) as f:
        for line in f.readlines():
            m = re.search(r'^APP_ABI\s*:?=\s*(\S+)\s*$', line)
            if m:
                return m.group(1)

    return 'armeabi'


def get_native_lib_path(project_dir):
    return os.path.join(project_dir, 'libs', get_ABI_name(project_dir))


def build(project_dir, sdk_path, verbose=False, ndk_build=False):
    # get libs path
    lib_dir = get_native_lib_path(project_dir)
    if not os.path.exists(lib_dir):
        os.makedirs(lib_dir)

    def echo(msg):
        if verbose:
            print(msg)

    # copy libraries to libs directory
    sdk_versions = getver.get_versions(sdk_path)
    z = zipfile.ZipFile(sdk_path)
    for n, v in sdk_versions or []:
        bn = os.path.basename(n)
        if verbose:
            echo('  Copy {}: {}'.format(os.path.basename(n), v))
        with open(os.path.join(lib_dir, bn), 'wb') as f:
            f.write(z.read(n))

    # build apk
    apk_path = apk.build(project_dir, verbose, ndk_build)

    # check apk version
    apk_versions = getver.get_versions(apk_path)
    for n, v in apk_versions or []:
        bn = os.path.basename(n)
        for n1, v1 in sdk_versions:
            if n1.endswith(bn):
                if verbose:
                    echo('Checking ' + bn)
                if v1 != v:
                    raise Exception('Version in apk (%s) is not same with SDK (%s) for %s', v, v1, bn)

    return apk_path


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
    parser.add_argument('sdk', type=argparse.FileType('rb'),
                        help='SDK path')
    parser.add_argument('--verbose', '-V', action='store_true')
    parser.add_argument('--noNDK', '-n', action='store_true',
                        help='do not run ndk-build')

    args = parser.parse_args()

    path = build(args.project_dir, args.sdk, args.verbose, not args.noNDK)
    print '[I] Final APK:', path
    print 'Done!'

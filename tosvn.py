#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright (C) 2014 maxint <NOT_SPAM_lnychina@gmail.com>
#
# Distributed under terms of the MIT license.

'''
Commit git repository to svn by "git svn".
'''

import subprocess
import os
import re

COMMIT_LOG = 'commit.log'


def runout(cmd):
    return subprocess.check_output(cmd)


def svn_url(branch):
    '''Get SVN url'''
    log = runout('git log {} -1 --format="%b"'.format(branch)).strip()
    m = re.search(r'git-svn-id:\s(?P<url>.*)@', log)
    return m.group('url')


def get_version(s):
    m = re.search(r'\b(\d+)\.(\d+)\.\d+\.(\d+)\b', s)
    if m:
        m = m.groups()
        return 'v{}.{}.{}'.format(m[0], m[1], m[2])


def get_last_commit(s):
    m = re.search(r'\bcommit (\S+)\b', s).groups()
    return m[0]


def get_squash_log(src, dst):
    cmd = 'git log {} -1 --format="%B"'.format(dst)
    last_sha1 = get_last_commit(runout(cmd))
    cmd = 'git log "{}".."{}" --format=short --graph'.format(last_sha1, src)
    return runout(cmd)


def get_git_log(branch, num):
    cmd = 'git log {} -n {}'.format(branch, num)
    return runout(cmd)


def checkrun(cmd):
    try:
        runout(cmd)
        return True
    except:
        return False


def check_branch(name):
    cmd = 'git show-ref --verify --quiet "refs/heads/{}"'.format(name)
    return checkrun(cmd)


def check_tag(name):
    cmd = 'git rev-parse --verify --quiet "{}"'.format(name)
    return checkrun(cmd)


def do(src, dst, message, version=None, dryrun=False, verbose=0):
    print 'Commit version {} to SVN ({})'.format(str(version), svn_url(dst))

    def run(cmd):
        print cmd
        if not dryrun:
            return subprocess.check_call(cmd)

    if version and not check_tag(version):
        run('git tag ' + version)

    run('git checkout ' + dst)

    if message:
        if dryrun and verbose > 0:
            print message
        else:
            open(COMMIT_LOG, 'wt').write(message)

        run('git merge {} --no-ff --no-commit'.format(src))
        run('git commit -F {}'.format(COMMIT_LOG))
        run('git svn dcommit')

        if not dryrun:
            os.remove(COMMIT_LOG)

    if version:
        run('git svn tag ' + version)

    if check_branch(src):
        run('git checkout ' + src)


def main(**args):
    dst = args.get('dst')
    src = args.get('src')
    message = args.get('message')
    version = args.get('version')
    tag = args.get('tag')

    assert(src and dst)

    if not check_branch(src) and not check_tag(src):
        print '[E] source commit {} does not exist'.format(src)
        return

    if not check_branch(dst):
        print '[E] destination branch {} does not exist'.format(src)
        return

    # log since last svn commit
    slog = get_squash_log(src, dst).strip()
    if not slog and not tag:
        print '[W] Commit has been done.'
        return

    if not version and tag:
        version = get_version(slog or get_git_log(src, 10))

    if slog and not message:
        if version:
            message = 'Squashed commit: ' + version + '\n\n' + slog
        else:
            message = slog

    return do(src, dst, message, version,
              args.get('dryrun'), args.get('verbose'))


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Merge and commit git to svn')
    parser.add_argument('--src', '-s', nargs='?', default='dev',
                        help='source branch or version [dev]')
    parser.add_argument('--dst', nargs='?', default='master',
                        help='destination branch attached with svn [master]')
    parser.add_argument('--message', '-m', nargs='?', default=None,
                        help='commit message')
    parser.add_argument('--dryrun', '-d', action='store_true',
                        help='do not run command')
    parser.add_argument('--verbose', '-V', type=int, nargs='?', default=0,
                        help='mesage verbose mode, default is 0')
    parser.add_argument('--version', nargs='?', default=None,
                        help='version info, parsed from git log if None')
    parser.add_argument('--tag', '-t', action='store_true', default=False,
                        help='create git and svn tag, disabled by default')
    args = parser.parse_args()

    main(**vars(args))

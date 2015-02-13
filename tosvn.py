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

dryrun = False


def runout(cmd):
    return subprocess.check_output(cmd)


def run(cmd):
    print '[C]', cmd
    if not dryrun:
        return subprocess.check_call(cmd)


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


def git_last_commit(branch):
    cmd = 'git log {} -1 --format="%H"'.format(branch)
    return runout(cmd).strip()


def git_commits(start, end):
    cmd = 'git log {}..{} --reverse --format=%H'.format(start, end)
    return runout(cmd).split()


def git_squash_log(src, dst):
    last_sha1 = git_last_commit(dst)
    cmd = 'git log {}..{} --format=short --graph'.format(last_sha1, src)
    return runout(cmd)


def git_log(sha1, num=1):
    cmd = 'git log {} -n {}'.format(sha1, num)
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


def git_commit(message):
    import tempfile
    f = tempfile.NamedTemporaryFile(suffix='_commit.log', delete=False)
    f.write(message)
    f.close()

    run('git commit -F {}'.format(f.name))
    os.unlink(f.name)


def squash_commit(src, dst, message, version):
    # log since last svn commit
    print '[I] Commits: '
    print runout('git log {}..{} --oneline --graph'.format(dst, src)).strip()
    if not message:
        message = 'Squashed commit: ' + str(version) + '\n\n' + git_squash_log(src, dst).strip()

    run('git merge {} --no-ff --no-commit'.format(src))
    git_commit(message)
    run('git svn dcommit')


def step_commit(src, dst):
    for c in git_commits(dst, src):
        run('git merge {} --no-ff --no-commit'.format(c))
        message = runout('git log --format="[svn] %s%n%n    %b%n%n commit: %H" -n 1 ' + c)
        git_commit(message)
    run('git svn dcommit')


def main(src, dst, message, version, tag, verbose, step):
    assert(src and dst)

    if not check_branch(src) and not check_tag(src):
        print '[E] source commit {} does not exist'.format(src)
        return

    if not check_branch(dst):
        print '[E] destination branch {} does not exist'.format(src)
        return

    if not version and tag:
        version = get_version(runout('git log {}..{} --format=%s'.format(dst, src)))

    print '[I] Commit version {} to SVN ({})'.format(str(version), svn_url(dst))

    if not git_commits(dst, src) and not tag:
        print '[W] No new commits, stop.'
        return

    if version and not check_tag(version):
        run('git tag ' + version)

    run('git checkout ' + dst)

    if step:
        step_commit(src, dst)
    else:
        squash_commit(src, dst, message, version)

    if version:
        run('git svn tag ' + version)

    if check_branch(src):
        run('git checkout ' + src)


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
    parser.add_argument('--step', action='store_true',
                        help='Merge to SVN branch step by step')
    args = parser.parse_args()

    dryrun = args.dryrun
    kwargs = vars(args)
    kwargs.pop('dryrun', None)
    main(**kwargs)

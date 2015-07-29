#! /usr/bin/env python
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
verbose = 0


def runout(cmd):
    return subprocess.check_output(cmd)


def run(cmd, echo=True):
    if echo:
        print '[C]', cmd
    if not dryrun:
        return subprocess.check_call(cmd)


def svn_url(branch):
    '''Get SVN url'''
    log = runout('git log {} -1 --format="%b"'.format(branch)).strip()
    m = re.search(r'git-svn-id:\s(?P<url>.*)@', log)
    return m.group('url') if m else None


def get_version(s):
    m = re.search(r'\b(\d+)\.(\d+)\.\d+\.(\d+)\b', s)
    if m:
        m = m.groups()
        return 'v{}.{}.{}'.format(m[0], m[1], m[2])


def git_last_commit(branch):
    cmd = 'git log {} -1 --format="%H"'.format(branch)
    return runout(cmd).strip()


def git_commits(start, end):
    cmd = 'git log {}..{} --reverse --format=%H --first-parent'.format(start, end)
    return runout(cmd).split()


def git_squash_log(start, end):
    cmd = 'git log {}..{} --format=oneline --graph --first-parent'.format(start, end)
    return runout(cmd)


def git_log(revision, num=1):
    cmd = 'git log {} -n {}'.format(revision, num)
    return runout(cmd)


def git_diff(sha1, sha2):
    cmd = 'git diff --name-status {} {}'.format(sha1, sha2)
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


def current_branch():
    return runout('git rev-parse --abbrev-ref HEAD').strip()


def git_commit(message):
    import tempfile
    f = tempfile.NamedTemporaryFile(suffix='_commit.log', delete=False)
    f.write(message)
    f.close()

    run('git commit -F {}'.format(f.name), echo=False)
    os.unlink(f.name)


def git_merge(dst, c, message, skip_empty=True):
    diff = git_diff(dst, c)
    print '[C] git merge {} ({})'.format(c[:7], message.split('\n', 1)[0])
    if diff:
        run('git merge {} --no-ff --no-commit'.format(c), echo=False)
        git_commit(message)
    else:
        print '[W] Skip empty merge'


def squash_commit(src, dst, message, version):
    # log since last svn commit
    print '[I] Commits:'
    print runout('git log {}..{} --oneline --graph'.format(dst, src)).strip()

    if not message:
        message = 'Squashed commit: {}\n\n{}'.format(version or '',
                                                     git_squash_log(dst, src).strip())

    git_merge(dst, src, message)
    run('git svn dcommit')


def step_by_step_commit(dst, commits):
    for c in commits:
        message = runout('git log --format="[svn] %B%ncommit: %H" -n 1 ' + c)
        git_merge(dst, c, message)
    run('git svn dcommit')


def main(src, dst, message, version, tag, squashed):
    assert(src and dst)

    original_branch = current_branch()
    if original_branch:
        print '[I] Current branch: {}'.format(original_branch)
    if not check_branch(src) and not check_tag(src):
        print '[E] source object {} does not exist'.format(src)
        return

    if not check_branch(dst):
        print '[E] destination branch {} does not exist'.format(src)
        return

    if not version and tag:
        logs = runout('git log {}..{} --format=%s'.format(dst, src))\
               or runout('git log {} -n 10 --format=%s'.format(src))
        version = get_version(logs)

    print '[I] Commit version {} to SVN branch "{}" ({})'.format(str(version), dst, svn_url(dst))

    commits = git_commits(dst, src)
    if not commits and not tag:
        print '[W] No new commits, stop.'
        return

    # git tag
    if version and not check_tag(version):
        run('git tag {} {}'.format(version, src))

    if version or commits:
        # checkout to svn branch
        if original_branch != dst:
            run('git checkout ' + dst)

        # commit
        if commits:
            if squashed:
                squash_commit(src, dst, message, version)
            else:
                step_by_step_commit(dst, commits)

        # svn tag
        if version:
            run('git svn tag ' + version)

        # back to original branch
        if original_branch and original_branch != dst:
            run('git checkout ' + original_branch)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Merge and commit git to svn')
    parser.add_argument('--src', '-s', nargs='?', default='dev',
                        help='source revision, default is dev')
    parser.add_argument('--dst', '-d', nargs='?', default='master',
                        help='destination SVN branch, default is master')
    parser.add_argument('--message', '-m', nargs='?', default=None,
                        help='commit message')
    parser.add_argument('--dryrun', '-D', action='store_true',
                        help='do not run command')
    parser.add_argument('--verbose', '-V', type=int, nargs='?', default=0,
                        help='mesage verbose mode, default is 0')
    parser.add_argument('--version', nargs='?', default=None,
                        help='version info, parsed from git log if None')
    parser.add_argument('--tag', '-t', action='store_true', default=False,
                        help='create git and svn tag, disabled by default')
    parser.add_argument('--squashed', '-Q', action='store_true',
                        help='Merge to SVN branch with squashed log')
    args = parser.parse_args()

    dryrun = args.dryrun
    verbose = args.verbose

    kwargs = vars(args)
    kwargs.pop('dryrun', None)
    kwargs.pop('verbose', None)

    main(**kwargs)

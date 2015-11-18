# coding: utf-8
# author: maxint <NOT_SPAM_lnychina@gmail.com>

"""
Create svn repository and create git repository based on it.
"""

import subprocess

dryrun = False


def run(cmd, msg=None):
    print msg or cmd
    if not dryrun:
        subprocess.check_call(cmd)


def runout(cmd):
    return subprocess.check_output(cmd)


def create_svn_layout(url, msg):
    try:
        cmd = 'svn mkdir {0} {0}/trunk {0}/branches {0}/tags'.format(url)
        cmd += ' -m "' + msg + '" --parents'
        run(cmd, 'svn mkdir %s/{trunk,branches,tags}' % url)
    except subprocess.CalledProcessError:
        pass
    finally:
        pass


def create_svn_layout_no_parent(url, msg):
    try:
        cmd = 'svn mkdir {0}/trunk {0}/branches {0}/tags'.format(url)
        cmd += ' -m "' + msg + '" --parents'
        run(cmd, 'svn mkdir %s/{trunk,branches,tags}' % url)
    except subprocess.CalledProcessError:
        pass
    finally:
        pass


def create_svn(url):
    try:
        create_svn_layout(url, 'Add new project (%s)' % url)
    except subprocess.CalledProcessError:
        pass
    finally:
        create_svn_layout_no_parent(url, 'Add new project (%s)' % url)


def create_git(url):
    try:
        run('git init')
    except subprocess.CalledProcessError:
        pass
    finally:
        run('git svn init -s ' + url)
        run('git svn fetch')
        # run('git svn rebase')


def main(url, git):
    create_svn(url)
    if git:
        create_git(url)

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Create svn/git repository')
    parser.add_argument('--dryrun', '-d', action='store_true',
                        help='do not run command')
    parser.add_argument('--git', '-g', action='store_true',
                        help='create git resposity')
    parser.add_argument('svnurl',
                        help='SVN location')

    args = parser.parse_args()
    dryrun = args.dryrun
    main(args.svnurl, args.git)

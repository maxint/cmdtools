#!/usr/bin/env python
# coding: utf-8

"""
Git subtree manage commands.
"""

import subprocess


def run(cmd):
    print cmd
    return subprocess.check_call(cmd)


def do_add(args):
    run('git remote add -f {}.git {}'.format(args.prefix, args.url))
    run('git subtree add --prefix {0} {0}.git master --squash'.format(args.prefix))


def do_push(args):
    run('git subtree push --prefix {0} {0}.git master'.format(args.prefix))
    do_pull(args)


def do_pull(args):
    run('git subtree pull --prefix {0} {0}.git master'.format(args.prefix))


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Convienient operations for git subtree command')
    subparsers = parser.add_subparsers()
    parser.add_argument('prefix', help='direcotry prefix')

    addp = subparsers.add_parser('add')
    addp.add_argument('url', help='repository location')
    addp.set_defaults(func=do_add)

    pushp = subparsers.add_parser('push')
    pushp.set_defaults(func=do_push)

    pullp = subparsers.add_parser('pull')
    pullp.set_defaults(func=do_pull)

    args = parser.parse_args()
    args.func(args)

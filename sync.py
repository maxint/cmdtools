# coding: utf-8
# author: maxint <lny1856@arcsoft.com>

import os
import fnmatch
import shutil
import logging
import copy

logger = logging.getLogger('sync')
dry_run = False

def setup_logging(logger, log_filename=None):
    if log_filename is None:
        log_filename = logger.name + '.log'

    formatter = logging.Formatter('%(name)-8s %(asctime)s [%(levelname)-5s] %(message)s', '%a, %d %b %Y %H:%M:%S')
    file_handler = logging.FileHandler(log_filename)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    import sys
    formatter = logging.Formatter('[%(levelname)-1.1s] %(message)s')
    stream_handler = logging.StreamHandler(sys.stderr)
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    logger.setLevel(logging.DEBUG)

def name_match(name, ignores):
    for ignore in ignores:
        if fnmatch.fnmatch(name, ignore):
            return True
    return False


def find_paths(directory, ignores_fn, ignores_dn):
    for root, dirs, files in os.walk(directory):
        dirs0 = copy.deepcopy(dirs)
        for basename in dirs0:
            if ignores_dn is None or not name_match(basename, ignores_dn):
                yield os.path.relpath(os.path.join(root, basename), directory)
            else:
                dirs.remove(basename)
        for basename in files:
            if ignores_fn is None or not name_match(basename, ignores_fn):
                yield os.path.relpath(os.path.join(root, basename), directory)


def sync(source, destination, ignores_fn, ignores_dn):
    if os.path.realpath(source) == os.path.realpath(destination):
        logger.warn('Ignore when source and destination are the same: %s', source)
        return

    src_paths = set(find_paths(source, ignores_fn, ignores_dn))
    dst_paths = set(find_paths(destination, ignores_fn, ignores_dn))
    uni_paths = src_paths.intersection(dst_paths)
    del_paths = dst_paths - uni_paths
    add_paths = src_paths - uni_paths
    #for p in sorted(src_paths): print p

    def path_do(paths, do_func):
        for path in paths:
            src = os.path.join(source, path)
            dst = os.path.join(destination, path)
            do_func(src, dst)

    def do_add_path(src, dst):
        if os.path.isdir(src):
            if not os.path.exists(dst):
                logger.info('Create directory: %s', dst)
                if not dry_run: os.makedirs(dst)
        else:
            logger.info('Copy file: %s -> %s', src, dst)
            if not dry_run:
                if (not os.path.exists(os.path.dirname(dst))):
                    os.makedirs(os.path.dirname(dst))
                shutil.copy(src, dst)

    def do_del_path(src, dst):
        if os.path.isdir(dst):
            logger.info('Delete directory: %s', dst)
            if not dry_run: shutil.rmtree(dst)
        elif os.path.exists(dst):
            logger.info('Delete file: %s', dst)
            if not dry_run: os.remove(dst)

    def do_union_path(src, dst):
        if os.path.isfile(src) and os.path.getmtime(dst) < os.path.getmtime(src):
            logger.info('Update file: %s', dst)
            if not dry_run: shutil.copy(src, dst)

    path_do(sorted(add_paths), do_add_path)
    path_do(sorted(del_paths), do_del_path)
    path_do(sorted(uni_paths), do_union_path)


def sync_all(source, destinations, ignores_fn, ignores_dn):
    logger.info('-'*60)
    logger.info('Source directory: %s', source)
    logger.info('Destination directories: %s', str(destinations))
    if destinations is None:
        sync(source, '.', ignores_fn, ignores_dn)
    else:
        map(lambda d: sync(source, d, ignores_fn, ignores_dn), destinations)


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Sync directories')
    parser.add_argument('-s', '--source', default='.',
                        help='Source directory')
    parser.add_argument('-d', '--destination', nargs='*',
                        help='Destination directories')
    parser.add_argument('-i', '--ignore_fn', nargs='*',
                        help='Ignore patterns for file name')
    parser.add_argument('-I', '--ignore_dn', nargs='*', default=['.*'],
                        help='Ignore patterns for directory')
    parser.add_argument('-D', '--dry_run', action='store_true',
                        help='Print operations without do them')
    args = parser.parse_args()

    global dry_run
    dry_run = args.dry_run
    setup_logging(logger)

    sync_all(args.source, args.destination, args.ignore_fn, args.ignore_dn)

    print 'Done!'

if __name__ == '__main__':
    main()

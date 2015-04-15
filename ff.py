#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2014 maxint <NOT_SPAM_lnychina@gmail.com>
#
# Distributed under terms of the MIT license.

"""
Convert video files to specific format.
"""

import glob
import subprocess
import os
import re


def quote(path):
    if ' ' in path:
        return '"{}"'.format(path)
    else:
        return path


def info(filename):
    cmd = 'ffmpeg -i {} -hide_banner'.format(quote(filename))
    try:
        out = subprocess.check_output(cmd, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError, e:
        out = e.output
    m = re.search(r'Video: [^,]+, [^,]+, (\d+)x(\d+)(?=\s[^,]+,|,)', out)
    return int(m.group(1)), int(m.group(2))


def get_target_filename(src, target_dir=None):
    if target_dir is not None:
        src = os.path.join(target_dir, os.path.basename(src))
    return os.path.splitext(src)[0]


def parse_file_patterns(patts):
    files = []
    for patt in patts:
        if '*' in patt:
            files.extend(glob.glob(patt))
        elif os.path.isfile(patt):
            files.append(patt)
        else:
            print '[E] Unknown input file: "{}"'.format(patt)

    # unique list
    return list(set(files))


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Convert videos with ffmpeg')
    parser.add_argument('-e', '--ext', nargs='?', default='mp4',
                        help='extension of destination file')
    parser.add_argument('files', nargs='*', default=['*.avi'],
                        help='input video files')
    parser.add_argument('-d', '--target_dir', default=None,
                        help='target directory (default is source directory)')
    parser.add_argument('-v', '--verbose', action='store_true', default=False,
                        help='show convert commands')
    parser.add_argument('-D', '--dryrun', action='store_true', default=False,
                        help='do not run command')
    parser.add_argument('-f', '--force', action='store_true', default=False,
                        help='override exist file')
    parser.add_argument('-m', '--max_height', type=int, default=None,
                        help='max height for output video')
    parser.add_argument('-ss', '--time_off', type=float, default=None,
                        help='the start time offset in seconds')
    parser.add_argument('-t', '--duration', type=float, default=None,
                        help='duration in seconds')
    parser.add_argument('-r', '--fps', type=float, default=30,
                        help='frame rate')
    args = parser.parse_args()

    # input files
    files = parse_file_patterns(args.files)

    for src in files:
        print '[I] >> Converting "{}"...'.format(src)
        # ffmpeg cmd
        cmd = 'ffmpeg -v warning -hide_banner -i {} -an'.format(quote(src))
        cmd += ' -r ' + str(args.fps)
        # basename
        dst = get_target_filename(src, args.target_dir)
        # frame size
        w, h = info(src)
        if args.max_height is not None and args.max_height < h:
            nw = args.max_height * w / h
            nh = args.max_height
            cmd += ' -s {}x{}'.format(nw, nh)
            print '[I] Resize from {}x{} to {}x{}'.format(w, h, nw, nh)
            w = nw
            h = nh
        # clip interval
        if args.time_off is not None:
            cmd += ' -ss ' + str(args.time_off)
        if args.duration is not None:
            cmd += ' -t ' + str(args.duration)
        # destination file
        dst += '_{}x{}.{}'.format(w, h, args.ext)
        print '[I] Destination file: ' + dst
        if os.path.exists(dst):
            print '[W] Destination file has existd'
        if not os.path.exists(dst) or args.force:
            cmd += ' "{}"'.format(dst)
            if args.verbose:
                print '[D] Runinging "{}"'.format(cmd)
            if not args.dryrun:
                subprocess.check_call(cmd)
        else:
            print '[W] Skip existed destination file'

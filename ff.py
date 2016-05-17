# coding: utf-8
# author: maxint <NOT_SPAM_lnychina@gmail.com>

"""
Convert video files to specific format.
"""

import glob
import subprocess
import os
import ffmpeg
import logging


def quote(path):
    if ' ' in path:
        return '"{}"'.format(path)
    else:
        return path


def get_target_filename(src, target_dir=None):
    if target_dir is not None:
        src = os.path.join(target_dir, os.path.basename(src))
    return os.path.splitext(src)[0]


def filename_not_endswith_resolution(path):
    import re
    return re.match(r'.*_\d{1,4}[xX]\d{1,4}\.\w+', path) is None


def parse_file_patterns(patterns, no_ignore):
    files = []
    for patt in patterns:
        if '*' in patt:
            new_files = glob.glob(patt)
            if not no_ignore:
                new_files = filter(filename_not_endswith_resolution, new_files)
            files.extend(new_files)
        elif os.path.isfile(patt):
            files.append(patt)
        else:
            logging.error('Unknown input file: "{}"'.format(patt))

    # unique list
    return list(set(files))


def convert_video(src_path, target_dir, ext, fps=None, max_height=None, time_off=None, duration=None,
                  verbose=False, dryrun=False, force=False):
    info = ffmpeg.Info(src_path)
    # ffmpeg cmd
    cmd = 'ffmpeg -v warning -hide_banner -i {} -an -pix_fmt yuv420p'.format(quote(src_path))
    if fps:
        cmd += ' -r ' + str(fps)

    # basename
    dst_path = get_target_filename(src_path, target_dir)

    # frame size
    w, h = info.size
    if max_height is not None and max_height < h:
        nw = max_height * w / h
        nh = max_height
        cmd += ' -s {}x{}'.format(nw, nh)
        logging.info('Resize from {}x{} to {}x{}'.format(w, h, nw, nh))
        w = nw
        h = nh

    # destination file
    dst_path += '_{}x{}.{}'.format(w, h, ext)
    logging.info('Destination file: %s', dst_path)

    # clip interval
    if time_off is not None:
        cmd += ' -ss ' + str(time_off)
    if duration is not None:
        cmd += ' -t ' + str(duration)

    # check existence of destination
    if not os.path.exists(dst_path) or force:
        cmd += ' "{}"'.format(dst_path)
        if verbose:
            logging.debug('Ruining "{}"'.format(cmd))
        if not dryrun:
            subprocess.check_call(cmd)
    else:
        logging.warning('Skip existed destination file: %s', dst_path)

    return dst_path, w, h


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Convert videos with ffmpeg')
    parser.add_argument('-e', '--ext', nargs='?', default='mp4',
                        help='extension of destination file, default is "mp4"')
    parser.add_argument('files', nargs='*', default=['*.avi'],
                        help='input video files, default is "*.avi"')
    parser.add_argument('-d', '--target_dir', default=None,
                        help='target directory, default is source directory')
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
    parser.add_argument('-r', '--fps', type=float, default=None,
                        help='frame rate')
    parser.add_argument('-I', '--no_ignore', action='store_true', default=False,
                        help='Do not ignore converted files (**_*x*.*)')
    args = parser.parse_args()

    logging.basicConfig(format='[%(levelname)-1.1s] %(message)s',
                        level=logging.DEBUG if args.verbose else logging.INFO)

    # input files
    files = parse_file_patterns(args.files, args.no_ignore)

    kwargs = vars(args)
    kwargs.pop('files')
    kwargs.pop('no_ignore')

    total = len(files)
    for i, src in enumerate(files):
        logging.info('[{}/{}] Converting "{}"...'.format(i+1, total, src))
        convert_video(src, **kwargs)

if __name__ == '__main__':
    main()

# coding: utf-8
# author: maxint <NOT_SPAM_lnychina@gmail.com>
# version: 0.1

"""
Generate compare result between ground true and tracking result for Object Tracking project.
"""

import subprocess
import glob
import os
import rect
import rect_compare


def get_mark_paths(dst_path):
    return glob.glob(os.path.join(dst_path, '*_fingerMark.txt'))


def copy_from_mobile(src, dst):
    cmd = 'adb pull {} {}'.format(src, dst)
    subprocess.check_call(cmd)


def get_unused_path(path):
    i = 1
    res_path = path
    while os.path.exists(res_path):
        res_path = path + '.' + str(i)
        i += 1
    return res_path


def main(dst_path, overlap_fn, overlap_threshold=0.5):
    mark_paths = get_mark_paths(dst_path)
    summary_path = os.path.join(dst_path, 'summary.csv')
    all_results = []
    for mark_path in mark_paths:
        mark_path_no_ext = os.path.splitext(mark_path)[0]
        result_path = mark_path_no_ext + '_res.txt'
        cmp_path = mark_path_no_ext + '_res.csv'
        marks = rect.load(mark_path)
        result = rect.load(result_path)
        cmp_result = rect_compare.compare(marks, result, overlap_fn)
        res = rect_compare.save_compare(cmp_path, cmp_result, overlap_threshold)
        all_results.append(res)

    rect_compare.save_summary(summary_path, all_results)


if __name__ == '__main__':
    import argparse

    def restricted_float(start, end):
        def impl(x):
            x = float(x)
            if x < start or x > end:
                msg = "%r not in range [%r, %r]".format(x, start, end)
                raise argparse.ArgumentTypeError(msg)
            return x
        return impl

    MOBILE_DIR = '/sdcard/Arcsoft/com.arcsoft.objecttrackingload/ConfigFile'

    parser = argparse.ArgumentParser(description='OT result report')
    parser.add_argument('--nocopy', '-n', action='store_true', default=False,
                        help='do not copy data from mobile')
    parser.add_argument('--source', '-s', default=MOBILE_DIR,
                        help='source data path in android device')
    parser.add_argument('--overlap',
                        choices=['rect', 'pos'], default='pos',
                        help='overlap function')
    parser.add_argument('--threshold', '-t',
                        type=restricted_float(0.1, 0.9), default=0.5,
                        help='overlap threshold')
    parser.add_argument('--quiet', action='store_true', default=False,
                        help='no warning')
    args = parser.parse_args()

    data_dir = 'data'
    if not args.nocopy:
        data_dir = get_unused_path(data_dir)
        copy_from_mobile(args.source, data_dir)

    # determine overlap function
    overlap_fn = dict(rect=rect_compare.overlap, pos=rect_compare.overlap_only_pos)[args.overlap]
    main(data_dir, overlap_fn, args.threshold)

    os.system('pause')
    print 'Done!'

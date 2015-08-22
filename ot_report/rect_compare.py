# coding: utf-8
# author: maxint <NOT_SPAM_lnychina@gmail.com>
# version: 0.2

"""
Generate compare result between ground true and tracking result.
"""

from rect import Rect


def overlap(rc1, rc2):
    if rc1.is_zero and rc2.is_zero:
        return 1.0
    else:
        return float((rc1 & rc2).area) / max(1, (rc1 | rc2).area)


def overlap_only_pos(rc1, rc2):
    if rc1.is_zero and rc2.is_zero:
        return 1.0
    else:
        rc1 = Rect.from_center_size1(rc1.center, rc2.size)
        return float((rc1 & rc2).area) / max(1, (rc1 | rc2).area)


def compare(marks, result, overlap_fn=overlap):
    if len(marks) != len(result):
        raise Exception('The rectangle number in mark (%d) and result (%d) files are not equal!' % (len(marks), len(result)))
    return [(rc1, rc2, overlap_fn(rc1, rc2)) for rc1, rc2 in zip(marks, result)]


def save_compare(path, results, overlap_threshold):
    passed = [o > overlap_threshold for _, _, o in results]
    passed_num = passed.count(True)
    with open(path, 'wt') as f:
        count = len(results)
        passed_ratio = float(passed_num) / max(1, count)
        f.write('TOTAL frames: {}\n'.format(count))
        f.write('Passed frames: {}\n'.format(passed_num))
        f.write('Passed ratio: {}\n'.format(passed_ratio))
        f.write('#NO.({}), #Ground True,,,, #Tracking Result,,,, #Overlap, #Passed(>{})\n'.format(count, overlap_threshold))

        def rect2str(rc):
            return ','.join(map(str, rc.array))

        for idx, (passed, (rc1, rc2, o)) in enumerate(zip(passed, results)):
            f.write('{}, {}, {}, '.format(idx, rect2str(rc1), rect2str(rc2)) +
                    '{}, {}\n'.format(o, 1 if passed else 0))

        return path, count, passed_num, passed_ratio


def save_summary(path, results):
    if len(results) == 0:
        return

    with open(path, 'wt') as f:
        f.write('#NO.(' + str(len(results)) + ', #Path, #Total, #Passed, #Ratio\n')
        total_count = 0
        passed_count = 0
        for idx, (path, count, passed, ratio) in enumerate(results):
            f.write('{}, {}, {}, {}, {}\n'.format(idx,
                                                  path,
                                                  count,
                                                  passed,
                                                  ratio))
            total_count += count
            passed_count += passed

        passed_ratio = float(passed_count) / max(1, total_count)
        f.write('TOTAL frames: {}\n'.format(total_count))
        f.write('Passed frames: {}\n'.format(passed_count))
        f.write('Passed ratio: {}\n'.format(passed_ratio))


def main():
    import argparse
    import os

    def restricted_float(start, end):
        def impl(x):
            x = float(x)
            if x < start or x > end:
                msg = "%r not in range [%r, %r]" % (x, start, end)
                raise argparse.ArgumentTypeError(msg)
            return x
        return impl

    def readable_dir(path):
        if not os.path.isdir(path):
            raise argparse.ArgumentTypeError("{0} is not a valid directory".format(path))
        if not os.access(path, os.R_OK):
            raise argparse.ArgumentTypeError("{0} is not a readable dir".format(path))
        return path


    parser = argparse.ArgumentParser(description='Compare rectangles in files')
    parser.add_argument('source', nargs='?', default='.', type=readable_dir,
                        help='tracking result and / or mark files directory (default is current directory)')
    parser.add_argument('--overlap', '-o',
                        choices=['rect', 'position'], default='rect',
                        help='overlap function (default is position)')
    parser.add_argument('--threshold', '-t',
                        type=restricted_float(0.1, 0.9), default=0.5,
                        help='overlap threshold (default is 0.5)')
    parser.add_argument('--marks', '-m', nargs='?', default=None, type=readable_dir,
                        help='mark files directory (default is the same as --source)')
    args = parser.parse_args()

    import glob
    result_paths = glob.glob(os.path.join(args.source, '*.txt'))
    if args.marks:
        mark_paths = glob.glob(os.path.join(args.marks, '*_fingerMark.txt'))
    else:
        mark_paths = filter(lambda p : p.endswith('_fingerMark.txt'), result_paths)
        result_paths = list(set(result_paths) - set(mark_paths))

    if len(mark_paths) != len(result_paths):
        raise Exception("The number of mark files (%d) and result files (%d) are not equal!" % (len(mark_paths), len(result_paths)))

    if len(mark_paths) == 0:
        print '[W] No mark file is found in %s!' % args.source
        return

    mark_paths.sort()
    result_paths.sort()

    import rect
    # determine overlap function
    overlap_fn = dict(rect=overlap, position=overlap_only_pos)[args.overlap]
    summary_path = os.path.join(args.marks or args.source, 'summary.csv')
    all_results = []

    for mark_path, result_path in zip(mark_paths, result_paths):
        print '[I] Comparing ' + mark_path
        print '    with ' + result_path
        result_path_no_ext = os.path.splitext(result_path)[0]
        cmp_path = result_path_no_ext + '.csv'
        marks = rect.load(mark_path)
        result = rect.load(result_path)
        if len(result) < len(marks):
            result += [rect.Rect()] * (len(marks) - len(result))
        cmp_result = compare(marks, result, overlap_fn)
        res = save_compare(cmp_path, cmp_result, args.threshold)
        all_results.append(res)

    save_summary(summary_path, all_results)
    print 'Done!'

if __name__ == '__main__':
    main()
# coding: utf-8
# author: maxint <NOT_SPAM_lnychina@gmail.com>

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
    assert len(marks) == len(result)
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
        f.write('#NO.({}), #Ground True,,,, #Tracking Result,,,, #Overlap, ' +
                '#Passed(>{})\n'.format(count, overlap_threshold))

        def rect2str(rc):
            return ','.join(map(str, rc.array))

        for idx, (passed, (rc1, rc2, o)) in enumerate(zip(passed, results)):
            f.write('{}, {}, {}, '.format(idx, rect2str(rc1), rect2str(rc2)) +
                    '{}, {}\n'.format(o, 1 if passed else 0))

        return path, count, passed_num, passed_ratio


def save_summary(path, results):
    with open(path, 'wt') as f:
        f.write('#NO.({}), #Path, '.format(len(results)) +
                '#Total, #Passed, #Ratio\n')
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
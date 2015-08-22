# coding: utf-8
# author: maxint <NOT_SPAM_lnychina@gmail.com>

""" Get custom camera calibration file from OpenCV camera calibration file.

Custom format (https://github.com/tum-vision/lsd_slam):
    fx fy cx cy k1 k2 p1 p2
    inputWidth inputHeight
    "crop" / "full" / "none" / "e1 e2 e3 e4 0"
    outputWidth outputHeight

   http://docs.opencv.org/trunk/doc/tutorials/calib3d/camera_calibration/camera_calibration.html
"""

import yaml
import os


# http://stackoverflow.com/questions/15964056/what-is-the-difference-between-and-in-yaml
def opencv_matrix(loader, node):
    mapping = loader.construct_mapping(node, True)
    data = mapping["data"]
    rows = mapping['rows']
    cols = mapping['cols']
    if rows == 1 or cols == 1:
        return data
    else:
        return [[data[y*cols + x] for x in range(cols)] for y in range(rows)]

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Get custom camera calibration file')
    parser.add_argument('input', type=argparse.FileType('rt'),
                        help='OpenCV camera calibration file')

    args = parser.parse_args()

    lines = args.input.readlines()
    if len(lines) > 0 and lines[0].startswith('%YAML'):
        lines = lines[1:]

    yaml.add_constructor(u"tag:yaml.org,2002:opencv-matrix", opencv_matrix)
    d = yaml.load(''.join(lines))
    camera_matrix = d['camera_matrix']
    dist_coeffs = d['distortion_coefficients']

    dst_path = os.path.splitext(args.input.name)[0] + '.cfg'
    with open(dst_path, 'wt') as f:
        coefs = [camera_matrix[0][0],
                 camera_matrix[1][1],
                 camera_matrix[0][2],
                 camera_matrix[1][2]] + dist_coeffs
        s = ' '.join(map(str, coefs))
        s += '\n'
        s += '{} {}'.format(d['image_width'], d['image_height'])
        s += '\n'
        s += 'crop'
        s += '\n'
        s += '{} {}'.format(d['image_width'], d['image_height'])

        print s
        f.write(s)
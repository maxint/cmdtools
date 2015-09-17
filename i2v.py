# coding: utf-8
# author: maxint <NOT_SPAM_lnychina@gmail.com>

import sys
import ffmpeg
import os
import re


def create_zip_reader(path, pattern=None):
    import zipfile
    z = zipfile.ZipFile(path, 'r')

    if pattern:
        names = [info.filename for info in z.infolist() if pattern.match(info.filename)]
    else:
        names = z.namelist()

    names.sort()

    for name in names:
        """:type info: zipfile.ZipInfo"""
        info = z.getinfo(name)
        if info.file_size == 0: # ignore directory
            continue

        if pattern and not pattern.match(name):
            continue

        data = z.read(name)
        yield name, data

    z.close()


def create_tar_reader(path, pattern):
    import tarfile
    z = tarfile.open(path, 'r')

    if pattern:
        names = [info.name for info in z.getmembers() if pattern.match(info.name)]
    else:
        names = z.getnames()

    names.sort()

    for name in names:
        """:type tarinfo: tarfile.TarInfo"""
        info = z.getmember(name)
        if info.isreg():
            data = z.extractfile(info).read()
            yield name, data

    z.close()


def create_dir_reader(path):
    import glob
    for name in glob.glob(path):
        with open(name) as f:
            yield name, f.read()


def get_real_path(path):
    real_path = path
    while not os.path.exists(real_path):
        real_path = os.path.dirname(real_path)

    return real_path


def create_file_reader(path, pattern=None):
    ext = os.path.splitext(path)[1].lower()
    if ext in ['.zip']:
        return create_zip_reader(path, pattern)
    elif ext in ['.gz', '.tgz', '.tar', '.bz2']:
        return create_tar_reader(path, pattern)
    else:
        raise Exception('Unknown extension ' + ext)


def create_reader(path):
    real_path = get_real_path(path)
    if len(real_path) != len(path):
        if os.path.isdir(real_path):
            reader_iter = create_dir_reader(path)
        else:
            pattern = path[len(real_path)+1:].replace('\\', '/').replace('.', '\\.').replace('*', '.*')
            reader_iter = create_file_reader(real_path, re.compile(pattern))
    else:
        if os.path.isdir(real_path):
            reader_iter = create_dir_reader(os.path.join(path, '*'))
        else:
            reader_iter = create_file_reader(path)

    return os.path.basename(real_path) + '.mp4', reader_iter


def convert(read_iter, dst, fps=20.0):
    path, data = read_iter.next()
    i = ffmpeg.Info('-', data=data)

    print '[I] Writing to video to ' + dst
    writer = ffmpeg.Writer(dst, i.size, in_fps=fps,
                           in_vcodec=i.vcodec, in_pix_fmt=i.pix_fmt,
                           out_pix_fmt='gray' if i.pix_fmt == 'gray' else 'yuv420p')

    while data:
        sys.stdout.write('\r--- Writing frame (%s)' % path)
        sys.stdout.flush()
        writer.write(data)
        try:
            path, data = read_iter.next()
        except StopIteration:
            break

    print '\t[DONE]'
    writer.close()


def main():
    import argparse

    example_msg = '''Path examples of input images (@param images):
    - images.zip
    - images.zip/*.jpg
    - image_dir/
    - image_dir/*.jpg
    '''

    parser = argparse.ArgumentParser(description='Convert images to video', epilog=example_msg, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('images',
                        help='Path to image directory / zip / tar')
    parser.add_argument('--dst', '-d', default=None,
                        help='Path of output video file')
    parser.add_argument('--fps', type=float, default=20,
                        help='FPS of output video')

    args = parser.parse_args()

    if args.dst is None:
        args.dst, read_fn = create_reader(args.images)
    else:
        _, read_fn = create_reader(args.images)

    convert(read_fn, args.dst, args.fps)

if __name__ == '__main__':
    main()
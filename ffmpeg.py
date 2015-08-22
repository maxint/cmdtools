# coding: utf-8
# author: maxint <NOT_SPAM_lnychina@gmail.com>

"""
http://zulko.github.io/blog/2013/09/27/read-and-write-video-frames-in-python-using-ffmpeg/
"""

import re
import subprocess as sp
from nbstreamreader import NonBlockingStreamReader as NBSR

FFMPEG_BIN = 'ffmpeg'


def convert_seconds(time):
    """ Will convert any time into seconds.
    Here are the accepted formats:
    >>> convert_seconds(15.4) -> 15.4 # seconds
    >>> convert_seconds( (1,21.5) ) -> 81.5 # (min,sec)
    >>> convert_seconds( (1,1,2) ) -> 3662 # (hr, min, sec)
    >>> convert_seconds('01:01:33.5') -> 3693.5  #(hr,min,sec)
    >>> convert_seconds('01:01:33.045') -> 3693.045
    >>> convert_seconds('01:01:33,5') #coma works too
    """

    if isinstance(time, str):
        if (',' not in time) and ('.' not in time):
            time += '.0'
        expr = r"(\d+):(\d+):(\d+)[,|.](\d+)"
        finds = re.findall(expr, time)[0]
        nums = map(float, finds)
        return (3600*int(finds[0])
                + 60*int(finds[1])
                + int(finds[2])
                + nums[3]/(10**len(finds[3])))

    elif isinstance(time, tuple):
        if len(time) == 3:
            hr, mn, sec = time
        elif len(time) == 2:
            hr, mn, sec = 0, time[0], time[1]
        else:
            hr, mn, sec = 0, 0, time[0]
        return 3600*hr + 60*mn + sec

    else:
        return time


class Info(object):
    def __init__(self, path, data=None, check_duration=True):
        command = [FFMPEG_BIN, '-hide_banner', '-i', path, '-']
        pipe = sp.Popen(command, stdin=sp.PIPE, stdout=sp.PIPE, stderr=sp.PIPE)
        if data:
            pipe.stdin.write(data)
            pipe.stdin.close()
        pipe.stdout.readline()
        pipe.terminate()

        for line in pipe.stderr.readlines():
            line = line.strip()
            if line.startswith('Stream #'):
                if ' Video:' in line:
                    self._parse_video_stream(line)
            elif line.startswith('Duration:') and check_duration:
                self._parse_duration(line)

        if check_duration:
            self.nframes = (int(self.duration * self.fps) + 1) if self.fps else 0

        del pipe

    def _parse_video_stream(self, line):
        line = re.sub(r'\s*\([^)]*\)', '', line)
        line = re.sub(r'\s*\[[^]]*\]', '', line)
        m = re.search(r'Stream #\d:\d: Video: (\S+), (\S+), (\d+)x(\d+),', line)
        self.vcodec = m.group(1)
        self.pix_fmt = m.group(2)
        self.size = int(m.group(3)), int(m.group(4))
        m = re.search(r'\b([.\d]+)\s*fps\b', line)  # fps
        self.fps = float(m.group(1)) if m else None

    def _parse_duration(self, line):
        m = re.search(r'Duration: ([.:\d]+), start: ([.\d]+), bitrate: (\d+) kb/s', line)
        if m:
            self.duration = convert_seconds(m.group(1))
            self.start = float(m.group(2))
            self.bitrate = int(m.group(3))


class Reader(object):
    def __init__(self, path, data=None, vcodec='rawvideo', pix_fmt='bgr24'):
        self.info = Info(path, data)
        command = [
            FFMPEG_BIN,
            '-hide_banner',
            '-i', path,
            '-f', 'image2pipe',
            '-vcodec', vcodec,
            '-pix_fmt', pix_fmt,
            '-',
        ]
        self.pipe = sp.Popen(command, stdin=sp.PIPE, stdout=sp.PIPE, stderr=sp.PIPE, bufsize=10**8)
        self.bytes_for_frame = self.info.size[0] * self.info.size[1] * 3
        self.path = path
        if data:
            self.pipe.stdin.write(data)
            self.pipe.stdin.close()

    def read(self):
        try:
            return self.pipe.stdout.read(self.bytes_for_frame)
        except IOError as err:
            ffmpeg_error = self.pipe.stderr.read()
            error = (str(err) + ("\n\nFFMPEG error: FFMPEG encountered "
                                 "the following error while writing file %s:"
                                 "\n\n %s" % (self.path, ffmpeg_error)))
            raise IOError(error)

    def close(self):
        if hasattr(self, 'pipe'):
            self.pipe.terminate()
            self.pipe.stdout.close()
            if self.pipe.stderr:
                self.pipe.stderr.close()
            del self.pipe

    def __del__(self):
        self.close()


class Writer(object):
    def __init__(self, path, size, in_fps=25.0,
                 in_vcodec='rawvideo', in_pix_fmt='bgr24',
                 out_fps=None, out_vcodec='h264', out_pix_fmt='yuvj420p'):
        command = [
            FFMPEG_BIN,
            '-hide_banner',
            '-y',   # (optional) overwrite output file if it exists
            '-s', '%dx%d' % (size[0], size[1]),
            '-r', '%.02f' % in_fps,  # frames per second
            '-f', 'rawvideo' if in_vcodec == 'rawvideo' else 'image2pipe',  # image2pipe for image stream
            '-vcodec', in_vcodec,
            '-pix_fmt', in_pix_fmt,
            '-i', '-',  # input comes from a pipe
            '-an',  # no audio
            '-r', '%.02f' % (out_fps or in_fps),  # frames per second
            '-vcodec', out_vcodec,
            '-pix_fmt', out_pix_fmt,
            path,
        ]
        self.path = path
        self.pipe = sp.Popen(command, stdin=sp.PIPE, stderr=sp.PIPE)
        self.nb_stderr = NBSR(self.pipe.stderr)

    def write(self, data):
        try:
            self.nb_stderr.read(0.1)
            self.pipe.stdin.write(data)
        except IOError as err:
            ffmpeg_error = self.nb_stderr.read()
            error = (str(err) + ("\n\nFFMPEG error: FFMPEG encountered "
                                 "the following error while writing file %s:"
                                 "\n\n %s" % (self.path, ffmpeg_error)))
            raise IOError(error)

    def close(self):
        if hasattr(self, 'pipe'):
            self.pipe.stdin.close()
            self.nb_stderr.close()
            self.pipe.wait()
            del self.pipe

    def __del__(self):
        self.close()


def test():
    path = r'f:\projects\object_tracking\data\bug\v1.3_sony_jasmine_miss.mp4'
    video_reader = Reader(path)
    video_writer = Writer(r'c:\tmp.mp4', video_reader.info.size, video_reader.info.fps)
    count = 0
    while True:
        frame = video_reader.read()
        if frame:
            video_writer.write(frame)
            count += 1
        else:
            break
    print 'Frame number: (%d / %d)' % (video_reader.info.nframes, count)


if __name__ == '__main__':
    test()

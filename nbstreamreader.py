# coding: utf-8
# author: maxint <NOT_SPAM_lnychina@gmail.com>

from threading import Thread
try:
    from Queue import Queue, Empty
except ImportError:
    from queue import Queue, Empty


class UnexpectedEndOfStream(Exception):
    pass


def populate_queue(stream, queue):
    """
    Collect lines from 'stream' and put them in 'queue'.
    :type stream: file
    :type queue: Queue
    """
    for line in iter(stream.readline, b''):
        queue.put(line)


class NonBlockingStreamReader:
    def __init__(self, stream):
        """
        :param stream: the stream to read from. Usually a process' stdout or stderr.
        :type stream: io.RawIO
        """

        self._s = stream
        self._q = Queue()

        self._t = Thread(target=populate_queue, args=(self._s, self._q))
        self._t.daemon = True  # thread dies with the program
        self._t.start()  # start collecting lines from the stream

    def close(self):
        self._t.join()
        self._s.close()

    def readline(self, timeout=None):
        try:
            return self._q.get(block=timeout is not None, timeout=timeout)
        except Empty:
            return None

    def read(self, timeout=None):
        def readline():
            return self.readline(timeout)
        data = ''
        for line in iter(readline, None):
            data += line
        return data

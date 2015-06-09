# coding: utf-8

from threading import Thread
from Queue import Queue, Empty


class UnexpectedEndOfStream(Exception):
    pass


def populate_queue(stream, queue):
    """
    Collect lines from 'stream' and put them in 'queue'.
    """
    while True:
        line = stream.readline()
        if line:
            queue.put(line)
        else:
            raise UnexpectedEndOfStream


class NonBlockingStreamReader:
    def __init__(self, stream):
        """
        stream: the stream to read from.
                Usually a process' stdout or stderr.
        """

        self._s = stream
        self._q = Queue()

        self._t = Thread(target=populate_queue, args=(self._s, self._q))
        self._t.daemon = True
        self._t.start()  # start collecting lines from the stream

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

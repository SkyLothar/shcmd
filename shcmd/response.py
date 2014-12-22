# -*- coding: utf8 -*-


ITER_CHUNK_SIZE = 1024


class CmdResponse(object):
    def __init__(self, proc):
        self._proc = proc

    @property
    def request(self):
        return self._proc.request

    @property
    def return_code(self):
        return self._proc.return_code

    @property
    def stdout(self):
        return self._proc.stdout

    @property
    def stderr(self):
        return self._proc.stderr

    def iter_content(self, chunk_size=1):
        for data in self._porc.stream(chunk_size):
            yield data

    def iter_lines(self, chunk_size=ITER_CHUNK_SIZE, delimiter=None):
        pending = None
        for chunk in self.iter_content(chunk_size=chunk_size):
            if pending is not None:
                chunk = pending + chunk
            if delimiter:
                lines = chunk.split(delimiter)
            else:
                lines = chunk.splitlines()

            if lines and lines[-1] and lines[-1][-1] == chunk[-1]:
                pending = lines.pop()
            else:
                pending = None
            for line in lines:
                yield line
        if pending is not None:
            yield pending

    def raise_for_return_code(self):
        if self.ok is False:
            pass

    def ok(self):
        return self.return_code == 0

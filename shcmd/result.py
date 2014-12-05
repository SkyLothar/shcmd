from . import compat


ITER_CHUNK_SIZE = 512


class Result(compat.str):
    """
    Simple string subclass to allow arbitrary attribute access.
    """
    @property
    def stdout(self):
        return str(self)

    @property
    def stderr(self):
        return self._stderr

    def ok(self):
        return self.retcode == 0

    def raise_for_retcode(self):
        if not self.ok:
            raise ValueError()

    def retcode(self):
        return self._retcode

    def iter_lines(
        self,
        chunk_size=ITER_CHUNK_SIZE,
        decode_unicode=None,
        delimiter=None
    ):
        pass

    def iter_content(self, chunk_size=1, decode_unicode=False):
        pass

    @property
    def reason(self):
        pass

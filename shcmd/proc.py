import contextlib
import logging
import subprocess
import threading


logger = logging.getLogger(__name__)


class CmdProc(object):
    def __init__(self, request, timeout, decode_unicode):
        self._request = request
        self._proc = None
        self._timer = threading.Timer(timeout, self.kill)

        self._codec = decode_unicode

        if decode_unicode is None:
            # raw bytes
            self._stdout = self._stderr = b""
        else:
            # decode to string
            self._stdout = self._stderr = ""

    @property
    def stdout(self):
        return self._stdout

    @property
    def stderr(self):
        return self._stderr

    @property
    def proc(self):
        return self._proc

    @property
    def request(self):
        return self._request

    def kill(self):
        if self.proc is None:
            logger.warn("{0} not started".format(self))
        elif self.proc.returncode is not None:
            logger.warn("{0} ended".format(self))
        else:
            self.proc.kill()
            logger.info("{0} killed".format(self))

    def decode_unicode(self, raw_bytes):
        if self._codec is None:
            return raw_bytes
        else:
            return raw_bytes.decode(self._codec)

    def block(self):
        """
        :param decode_unicode: (default is False, not decode),
            set decode_unicode to "utf8" so stdout/stderr willl be decoded
        """
        with self.run_with_timeout() as proc:
            stdout, stderr = proc.communicate()

        self._stdout = self.decode_unicode(stdout)
        self._stderr = self.decode_unicode(stderr)
        return self.stdout, self.stderr

    def stream(self, chunk_size=1):
        """
        :param decode_unicode: (default is False, not decode),
            set decode_unicode to "utf8" so stdout/stderr willl be decoded
        """
        with self.run_with_timeout() as proc:
            while proc.poll() is None:
                data = self.decode_unicode(proc.stdout.read(chunk_size))
                self._stdout += data
                yield self.decode_unicode(data)
            self._stderr = self.decode_unicode(proc.stderr)

    @contextlib.contextmanager
    def run_with_timeout(self):
        timer = threading.Timer(self.kill, self.timeout)
        try:
            proc = subprocess.Popen(
                self.request.cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=self.request.cwd,
                env=self.request.env
            )
            timer.start()
            yield proc
        finally:
            timer.cancel()

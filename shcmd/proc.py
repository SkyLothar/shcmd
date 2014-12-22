# -*- coding: utf8 -*-

import contextlib
import logging
import subprocess
import threading


logger = logging.getLogger(__name__)


class CmdProc(object):
    """
    Simple Wrapper around the built-in subprocess module

    use threading.Timer to add timeout option
    easy interface for get streamed output of stdout
    """
    def __init__(self, request, timeout, decode_unicode):
        self._request = request
        self._timer = threading.Timer(timeout, self.kill)

        self._codec = decode_unicode
        self._return_code = None

        if decode_unicode is None:
            # raw bytes
            self._stdout = self._stderr = b""
        else:
            # decode to string
            self._stdout = self._stderr = ""

    @property
    def stdout(self):
        """Proc's stdout"""
        return self._stdout

    @property
    def stderr(self):
        """Proc's stderr"""
        return self._stderr

    @property
    def request(self):
        """The original request"""
        return self._request

    def kill(self):
        """Kill proc if started
        Returns True if proc is killed actually
        """
        if self.proc is None:
            logger.warn("{0} not started".format(self))
        elif self.proc.returncode is not None:
            logger.warn("{0} ended".format(self))
        else:
            self.proc.kill()
            logger.info("{0} killed".format(self))

    def decode_unicode(self, raw_bytes):
        """Decode bytes into unicode
        Returns unicode
        """
        if self._codec is None:
            return raw_bytes
        else:
            return raw_bytes.decode(self._codec)

    def block(self):
        """Blocked executation
        Return (stdout, stderr) tuple

        :param decode_unicode: (default is False, not decode),
            set decode_unicode to "utf8" so stdout/stderr willl be decoded

        Usage::

            >>> stdout, stderr = proc.block(1024)
            >>> stdout == proc.stdout, "stdout output error"

        """
        with self.run_with_timeout() as proc:
            stdout, stderr = proc.communicate()

        self._stdout = self.decode_unicode(stdout)
        self._stderr = self.decode_unicode(stderr)
        return self.stdout, self.stderr

    def stream(self, chunk_size=1):
        """Streamed yield stdout
        Return a generator

        :param decode_unicode: (default is False, not decode),
            set decode_unicode to "utf8" so stdout/stderr willl be decoded

        Usage::

            >>> all_data = ""
            >>> for data in proc.stream(1024):
            ...     all_data += data
            ...
            >>> assert all_data == proc.stdout, "stdout output error"

        """
        with self.run_with_timeout() as proc:
            while proc.poll() is None:
                data = self.decode_unicode(proc.stdout.read(chunk_size))
                self._stdout += data
                yield self.decode_unicode(data)

        self._stderr = self.decode_unicode(proc.stderr)

    @contextlib.contextmanager
    def run_with_timeout(self):
        """Execute this proc with timeout

        Usage::

            >>> with cmd_proc.run_with_timeout() as cmd_proc:
            ...     stdout, stderr = cmd_proc.communicate()
            ...
            >>> assert cmd_proc.proc.return_code == 0, "proc exec failed"

        """
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
            self._return_code = proc.returncode
        finally:
            timer.cancel()

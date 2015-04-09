# -*- coding: utf8 -*-

import contextlib
import io
import logging
import subprocess
import threading
import time

from .errors import ShCmdError


logger = logging.getLogger(__name__)

LINE_CHUNK_SIZE = 1024


def kill_proc(proc, cmd, started_at):
    """kill proc if started
    returns True if proc is killed actually
    """
    if proc.returncode is None:
        proc.kill()


class Proc(object):
    """
    Simple Wrapper around the built-in subprocess module

    use threading.Timer to add timeout option
    easy interface for get streamed output of stdout
    """
    codec = "utf8"

    def __init__(self, cmd, cwd, env, timeout):
        self._cmd = cmd
        self._cwd = cwd
        self._env = env
        self._timeout = timeout
        self._return_code = self._stdout = self._stderr = None

    @property
    def cmd(self):
        return self._cmd[:]

    @property
    def cwd(self):
        return self._cwd

    @property
    def env(self):
        return self._env.copy()

    @property
    def timeout(self):
        return self._timeout

    @property
    def stdout(self):
        """proc's stdout."""
        return self._stdout.decode(self.codec)

    @property
    def stderr(self):
        """proc's stderr."""
        return self._stderr.decode(self.codec)

    @property
    def return_code(self):
        return self._return_code

    @property
    def content(self):
        return self._stdout

    @property
    def ok(self):
        return self.return_code == 0

    def raise_for_error(self):
        if not self.ok:
            tip = "running {0} @<{1}> error, return code {2}".format(
                " ".join(self.cmd), self.cwd, self.return_code
            )
            logger.error("{0}\nstdout:{1}\nstderr:{2}\n".format(
                tip, self.stdout, self.stderr
            ))
            raise ShCmdError(tip)

    @contextlib.contextmanager
    def _stream(self):
        """Execute subprocess with timeout

        Usage::

            >>> with cmd_proc.run_with_timeout() as cmd_proc:
            ...     stdout, stderr = cmd_proc.communicate()
            ...
            >>> assert cmd_proc.proc.return_code == 0, "proc exec failed"

        """
        timer = None
        try:
            proc = subprocess.Popen(
                self.cmd, cwd=self.cwd, env=self.env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            timer = threading.Timer(
                self.timeout,
                kill_proc, [proc, self.cmd, time.time()]
            )
            timer.start()
            yield proc
        finally:
            if timer:
                timer.cancel()

    def iter_lines(self):
        remain = ""
        for data in self.iter_content(LINE_CHUNK_SIZE):
            line_break_found = data[:1] in ("\n", "\r")
            lines = data.decode(self.codec).splitlines()
            lines[0] = remain + lines[0]
            if not line_break_found:
                remain = lines.pop()
            for line in lines:
                yield line

    def iter_content(self, chunk_size=1):
        if self.return_code is not None:
            stdout = io.BytesIO(self._stdout)
            data = stdout.read(chunk_size)
            while data:
                yield data
                data = stdout.read(chunk_size)
        else:
            data = b''
            started_at = time.time()
            with self._stream() as proc:
                while proc.poll() is None:
                    chunk = proc.stdout.read(chunk_size)
                    yield chunk
                    data += chunk

                if proc.returncode == -9:
                    raise subprocess.TimeoutExpired(
                        proc.args, time.time() - started_at
                    )

                chunk = proc.stdout.read(chunk_size)
                while chunk:
                    yield chunk
                    chunk = proc.stdout.read(chunk_size)

            self._return_code = proc.returncode
            self._stderr = proc.stderr.read()
            self._stdout = data

    def block(self):
        """blocked executation."""
        if self._return_code is None:
            proc = subprocess.Popen(
                self.cmd, cwd=self.cwd, env=self.env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            self._stdout, self._stderr = proc.communicate(timeout=self.timeout)
            self._return_code = proc.returncode

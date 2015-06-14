# -*- coding: utf8 -*-

import contextlib
import functools
import io
import logging
import subprocess
import threading
import time

from .errors import ShCmdError


logger = logging.getLogger(__name__)

LINE_CHUNK_SIZE = 1024
FINISHED = "finished"


def kill_proc(proc, cmd, started_at):
    """kill proc if started
    returns True if proc is killed actually
    """
    if proc.returncode is None:
        proc.kill()


def output(func):
    @functools.wraps(func)
    def checked_output(proc):
        if not proc.finished:
            raise ShCmdError(proc)
        return func(proc)
    return property(checked_output)


class Proc(object):
    """
    Simple Wrapper around the built-in subprocess module

    use threading.Timer to add timeout option
    easy interface for get streamed output of stdout
    """
    codec = "utf8"

    def __init__(self, cmd, cwd, env, timeout):
        """
        :param cmd: the command
        :param cwd: the command should be running under `cwd` dir
        :param env: the environment variable
        :param timeout: the command should return in `timeout` seconds

        Usage::

            >>> p = Proc("ls", "/", timeout=1)
            >>> p.block()
            >>> p.ok
            True
            >>> type(p.stdout)
            <class 'str'>

        """
        self._cmd = cmd
        self._cwd = cwd
        self._env = env
        self._timeout = timeout
        self._state = "not executed"
        self._return_code = self._stdout = self._stderr = None

    @property
    def finished(self):
        return self._state == FINISHED

    @property
    def state(self):
        return self._state

    @property
    def cmd(self):
        """the proc's command."""
        return self._cmd[:]

    @property
    def cwd(self):
        """the proc's execuation dir."""
        return self._cwd

    @property
    def env(self):
        """the proc's environment setting."""
        return self._env.copy()

    @property
    def timeout(self):
        """the proc's timeout setting."""
        return self._timeout

    @output
    def stdout(self):
        """proc's stdout."""
        return self._stdout.decode(self.codec)

    @output
    def stderr(self):
        """proc's stderr."""
        self.raise_for_error()
        return self._stderr.decode(self.codec)

    @property
    def return_code(self):
        """proc's return_code"""
        return self._return_code

    @output
    def content(self):
        """the output gathered in stdout in bytes format"""
        return self._stdout

    @property
    def ok(self):
        """`True` if proc's return_code is 0"""
        return self.return_code == 0

    def raise_for_error(self):
        """
        raise `ShCmdError` if the proc's return_code is not 0
        otherwise return self

        ..Usage::

            >>> proc = shcmd.run("ls").raise_for_error()
            >>> proc.return_code == 0
            True

        """
        if self.ok:
            return self
        tip = "running {0} @<{1}> error, return code {2}".format(
            " ".join(self.cmd), self.cwd, self.return_code
        )
        logger.error("{0}\nstdout:{1}\nstderr:{2}\n".format(
            tip, self._stdout.decode("utf8"), self._stderr.decode("utf8")
        ))
        raise ShCmdError(self)

    @contextlib.contextmanager
    def _stream(self):
        """execute subprocess with timeout

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
            if timer is not None:
                timer.cancel()

    def iter_lines(self, warn_only=False):
        """yields stdout text, line by line."""
        remain = ""
        for data in self.iter_content(LINE_CHUNK_SIZE, warn_only=True):
            line_break_found = data[-1] in (b"\n", b"\r")
            lines = data.decode(self.codec).splitlines()
            lines[0] = remain + lines[0]
            if not line_break_found:
                remain = lines.pop()
            for line in lines:
                yield line
        if remain:
            yield remain

        self._state = FINISHED
        if not warn_only:
            self.raise_for_error()

    def iter_content(self, chunk_size=1, warn_only=False):
        """
        yields stdout data, chunk by chunk

        :param chunk_size: size of each chunk (in bytes)
        """
        self._state = "not finished"
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
                    if not chunk:
                        continue
                    yield chunk
                    data += chunk

                if proc.returncode == -9:
                    elapsed = time.time() - started_at
                    self._state = "timeouted"
                    raise subprocess.TimeoutExpired(proc.args, elapsed)

                chunk = proc.stdout.read(chunk_size)
                while chunk:
                    yield chunk
                    data += chunk
                    chunk = proc.stdout.read(chunk_size)

            self._return_code = proc.returncode
            self._stderr = proc.stderr.read()
            self._stdout = data

            self._state = FINISHED
            if not warn_only:
                self.raise_for_error()

    def block(self, warn_only=False):
        """blocked executation."""
        self._state = "not finished"
        if self._return_code is None:
            proc = subprocess.Popen(
                self.cmd, cwd=self.cwd, env=self.env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            self._stdout, self._stderr = proc.communicate(timeout=self.timeout)
            self._return_code = proc.returncode

        self._state = FINISHED
        if not warn_only:
            self.raise_for_error()

    def __str__(self):
        return "<{0}@{1}  ret: {2} state: {3}>".format(
            " ".join(self.cmd), self.cwd, self.return_code, self.state
        )

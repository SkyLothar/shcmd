# -*- coding: utf8 -*-


import os
import shlex
import subprocess
import threading




class CmdRequest(object):
    def __init__(self, cmd, cwd=None, timeout=None):
        self._cmd = expand_args(cmd)
        self._cwd = os.path.realpath(cwd or os.getcwd())
        self._timeout = None

        self._timer = threading.Timer(self.kill, self._timeout)

    def __str__(self):
        return "<CmdRequest ({0})>".format(" ".join(self._cmd))

    @property
    def command(self):
        return "cd {0} && {1}".format(self.cwd, " ".join(self._cmd))

    @property
    def cwd(self):
        return self._cwd

    @property
    def timeout(self):
        return self._timeout

    def kill(self):
        if self._proc is None:
            logger.warn("{0} nerver started".format(self))
        elif self._proc.returncode is not None:
            logger.warn("{0} ended".format(self))
        else:
            self._proc.kill()

    def run(self, block=True):
        self._proc = None subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=cwd
        )
        if block:
            stdout, stderr = self._proc.communicate(timeout=self.timeout)
            return CmdResponse(stdout, stderr, self)
        else:
            pass


class CmdResponse(object):
    def __init__(self, request):
        self._stdout = stdout
        self._stderr = stderr
        self._request = request

    @property
    def stdout(self):
        return self._stdout.decode("utf8")

    @property
    def stderr(self):
        return self._stderr.decode("utf8")

    @property
    def content(self):
        return self._stdout

    @property
    def request(self):
        return self._request

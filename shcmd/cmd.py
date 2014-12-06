# -*- coding: utf8 -*-

import contextlib
import os
import subprocess
import shlex
import threading

from . import compat


ITER_CHUNK_SIZE = 1024


def expand_args(cmd_args):
    """Split command args to args list
    Returns a list of args

    :param cmd_args: command args, can be tuple, list or str
    """
    if isinstance(cmd_args, (tuple, list)):
        args_list = list(cmd_args)
    elif compat.is_py2 and isinstance(cmd_args, compat.str):
        args_list = shlex.split(cmd_args.encode("utf8"))
    elif compat.is_py3 and isinstance(cmd_args, compat.bytes):
        args_list = shlex.split(cmd_args.decode("utf8"))
    else:
        args_list = shlex.split(cmd_args)
    return args_list


@contextlib.contextmanager
def cd(cd_path):
    oricwd = os.getcwd()
    try:
        os.chdir(cd_path)
        yield
    finally:
        os.chdir(oricwd)


class CmdRequest(object):
    def __init__(self, cmd, cwd):
        self._raw = cmd
        self._cmd = expand_args(cmd)
        self._cwd = os.path.realpath(cwd or os.getcwd())

    def __str__(self):
        return "<CmdRequest ({0})@{1}>".format(self._raw, self.cwd)

    @property
    def raw(self):
        return self._raw

    @property
    def cmd(self):
        return self._cmd[:]

    @property
    def cwd(self):
        return self._cwd


def run(cmd, cwd=None, timeout=None, stream=False):
    request = CmdRequest(cmd, cwd)

    response = CmdExecutor(request, timeout)

    if stream is False:
        response.block()
    return response


class CmdExecutor(object):
    def __init__(self, request, timeout):
        self._request = request

        self._stdout = None
        self._stderr = None
        self._return_code = None
        self._data_consumed = False

        self._proc = subprocess.Popen(
            request.cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=request.cwd
        )
        self._timer = threading.Timer(self.kill)

    def block(self):
        self._stdout, self._stderr = self._proc.communicate()
        self._timer.cancel()
        self._return_code = self._proc.returncode

    def iter_content(self, chunk_size=1):
        def generator():
            data = self._proc.stdout.read(chunk_size)
            while data != compat.empty_bytes:
                yield data
                data = self._proc.stdout.read(chunk_size)

            self._timer.cancel()
            self._data_consumed = True

        if self._data_consumed:
            raise ValueError()

        stream_chunk = generator()
        return stream_chunk

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

    def kill(self):
        self._proc.kill()

    def raise_for_return_code(self):
        if self.ok is False:
            pass

    def ok(self):
        return self._return_code == 0

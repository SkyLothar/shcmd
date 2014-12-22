# -*- coding: utf8 -*-


import os
import shlex

from . import compat


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

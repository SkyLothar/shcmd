# -*- coding: utf8 -*-

import shlex


def expand_args(cmd_args):
    """split command args to args list
    returns a list of args

    :param cmd_args: command args, can be tuple, list or str
    """
    if isinstance(cmd_args, (tuple, list)):
        args_list = list(cmd_args)
    else:
        args_list = shlex.split(cmd_args)
    return args_list

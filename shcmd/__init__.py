__version__ = "0.4.0"
__author__ = "SkyLothar"
__email__ = "allothar@gmail.com"
__url__ = "https://github.com/skylothar/shcmd"

import os

__all__ = ["cd", "cd_to", "mkdir", "rm", "run", "TarGenerator"]

from .cmd import cd, cd_to, mkdir, rm
from .proc import Proc
from .tar import TarGenerator
from .utils import expand_args


DEFAULT_TIMEOUT = 60


def run(cmd, cwd=None, env=None, timeout=None, stream=False, warn_only=False):
    """
    :param cmd:
    :param cwd:
    :param env:
    :param timeout:
    :param stream:
    :param warn_only:
    """
    proc = Proc(
        expand_args(cmd),
        os.path.realpath(cwd or os.getcwd()),
        env=env or {},
        timeout=timeout or DEFAULT_TIMEOUT
    )

    if not stream:
        proc.block()
        if not warn_only:
            proc.raise_for_error()
    return proc

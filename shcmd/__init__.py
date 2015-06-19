__version__ = "0.5.0"
__author__ = "SkyLothar"
__email__ = "allothar@gmail.com"
__url__ = "https://github.com/skylothar/shcmd"

import os

__all__ = [
    "cd", "cd_to",
    "mkdir", "rm", "run", "tailf",
    "TarGenerator",
    "ShCmdError"
]

from .cmd import cd, cd_to, mkdir, rm
from .errors import ShCmdError
from .proc import Proc
from .tar import TarGenerator
from .utils import expand_args
from .tailf import tailf


DEFAULT_TIMEOUT = 60


def run(cmd, cwd=None, env=None, timeout=None, stream=False, warn_only=False):
    """
    :param cmd: command to run
    :param cwd: change dir into before execute, default is current dir
    :param env: environments to pass to subprocess
    :param timeout: timeout
    :param stream: stream output, default is False, block until finished
    :param warn_only: default False, set to True to allow unsuccessful result
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

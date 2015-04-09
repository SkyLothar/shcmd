__version__ = "0.1.2"
__author__ = "SkyLothar"
__email__ = "allothar@gmail.com"
__url__ = "https://github.com/skylothar/shcmd"

import os

from .proc import Proc
from .utils import expand_args


DEFAULT_TIMEOUT = 60


def run(cmd, cwd=None, env=None, timeout=None, stream=False):
    proc = Proc(
        expand_args(cmd),
        os.path.realpath(cwd or os.getcwd()),
        env=env or {},
        timeout=timeout or DEFAULT_TIMEOUT
    )

    if not stream:
        proc.block()
    return proc

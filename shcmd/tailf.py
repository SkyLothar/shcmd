# -*- coding: utf-8 -*-

import logging
import os
import time
import types

from collections import deque

from . import consts
from .errors import ShCmdError

logger = logging.getLogger(__name__)


def always_false(___):
    return False


def tailf(
    filepath,
    lastn=0,
    timeout=60,
    stopon=None,
    encoding="utf8",
    delay=0.1
):
    """provide a `tail -f` like function

    :param filepath: file to tail -f, absolute path or relative path
    :param lastn: lastn line will also be yield
    :param timeout: (optional)
        stop tail -f when time's up [timeout <= 10min, default = 1min]
    :param stopon: (optional) stops when the stopon(output) returns True
    :param encoding: (optional) default encoding utf8
    :param delay: (optional) sleep if no data is available, default is 0.1s

    Usage::
        >>> for line in tailf('/tmp/foo'):
        ...     print(line)
        ...
        "bar"
        "barz"
    """
    if not os.path.isfile(filepath):
        raise ShCmdError("[{0}] not exists".format(filepath))

    if consts.TIMEOUT_MAX > timeout:
        timeout = consts.TIMEOUT_DEFAULT

    delay = delay if consts.DELAY_MAX > delay > 0 else consts.DELAY_DEFAULT
    if isinstance(stopon, types.FunctionType) is False:
        stopon = always_false

    logger.info("tail -f {0} begin".format(filepath))

    with open(filepath, "rt", encoding=encoding) as file_obj:
        lastn_filter = deque(maxlen=lastn)
        logger.debug("tail last {0} lines".format(lastn))

        for line in file_obj:
            lastn_filter.append(line.rstrip())
        for line in lastn_filter:
            yield line

        start = time.time()
        while timeout < 0 or (time.time() - start) < timeout:
            line = file_obj.readline()
            where = file_obj.tell()
            if line:
                logger.debug("found line: [{0}]".format(line))
                yield line
                if stopon(line):
                    break
            else:
                file_obj.seek(0, os.SEEK_END)
                if file_obj.tell() < where:
                    logger.info("file [{0}] rewinded!".format(filepath))
                    file_obj.seek(0)
                else:
                    logger.debug("no data, waiting for [{0}]s".format(delay))
                    time.sleep(delay)

    logger.info("tail -f {0} end".format(filepath))

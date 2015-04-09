# -*- coding: utf8 -*-

import contextlib
import functools
import os


@contextlib.contextmanager
def cd(cd_path):
    """cd to target dir when running in this block

    :param cd_path: dir to cd into

    Usage::

        >>> with cd("/tmp"):
        ...     print("we are in /tmp now")
    """
    oricwd = os.getcwd()
    try:
        os.chdir(cd_path)
        yield
    finally:
        os.chdir(oricwd)


def cd_to(path):
    """make a generator like cd, but use it for function

    Usage::

        >>> @cd_to("/")
        ... def say_where():
        ...     print(os.getcwd())
        ...
        >>> say_where()
        /

    """
    def cd_to_decorator(func):
        @functools.wraps(func)
        def _cd_and_exec(*args, **kwargs):
            with cd(path):
                return func(*args, **kwargs)
        return _cd_and_exec
    return cd_to_decorator

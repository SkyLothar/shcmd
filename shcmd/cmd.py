# -*- coding: utf8 -*-

import contextlib
import functools
import os


@contextlib.contextmanager
def cd(cd_path):
    oricwd = os.getcwd()
    try:
        os.chdir(cd_path)
        yield
    finally:
        os.chdir(oricwd)


def cd_to(path):
    def cd_to_decorator(func):
        @functools.wraps(func)
        def _cd_and_exec(*args, **kwargs):
            with cd(path):
                return func(*args, **kwargs)
        return _cd_and_exec
    return cd_to_decorator

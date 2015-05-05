# -*- coding: utf8 -*-

import contextlib
import functools
import os
import shutil


@contextlib.contextmanager
def cd(cd_path, create=False):
    """cd to target dir when running in this block

    :param cd_path: dir to cd into
    :param create: create new dir if destination not there

    Usage::

        >>> with cd("/tmp"):
        ...     print("we are in /tmp now")
    """
    oricwd = os.getcwd()
    if create:
        mkdir(cd_path)
    try:
        os.chdir(cd_path)
        yield
    finally:
        os.chdir(oricwd)


def cd_to(path, mkdir=False):
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
            with cd(path, mkdir):
                return func(*args, **kwargs)
        return _cd_and_exec
    return cd_to_decorator


def mkdir(path):
    """just like mkdir -p

    :param path: dir you want to make
    """
    os.makedirs(path, exist_ok=True)


def rm(path, isdir=False):
    """delete file or dir
    returns True if deleted, if file/dir not exists, return False

    :param path: path to delete
    :param isdir: set True if you want to delete dir
    """
    if isdir:
        deleted = os.path.isdir(path)
        shutil.rmtree(path, ignore_errors=True)
    elif os.path.isfile(path):
        deleted = True
        os.remove(path)
    else:
        deleted = False
    return deleted

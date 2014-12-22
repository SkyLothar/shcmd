# -*- coding: utf8 -*-

import contextlib
import os


@contextlib.contextmanager
def cd(cd_path):
    oricwd = os.getcwd()
    try:
        os.chdir(cd_path)
        yield
    finally:
        os.chdir(oricwd)

# -*- coding: utf8 -*-

import nose


import shcmd.cmd


def test_asc_split_args():
    correct = ["/bin/bash", "echo", "上海崇明岛"]

    # str
    result = shcmd.cmd.split_args("/bin/bash echo 上海崇明岛")
    nose.tools.eq_(result, correct)

    # unicode
    result = shcmd.cmd.split_args(u"/bin/bash echo 上海崇明岛")
    nose.tools.eq_(result, correct)

    # bytes
    result = shcmd.cmd.split_args(u"/bin/bash echo 上海崇明岛".encode("utf8"))
    nose.tools.eq_(result, correct)

    # list
    result = shcmd.cmd.split_args(["/bin/bash", "echo", "上海崇明岛"])
    nose.tools.eq_(result, correct)

    # tuple
    result = shcmd.cmd.split_args(("/bin/bash", "echo", "上海崇明岛"))
    nose.tools.eq_(result, correct)

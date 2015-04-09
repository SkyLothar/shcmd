# -*- coding: utf8 -*-

import nose

import shcmd.utils


def test_asc_expand_args():
    correct = ["/bin/bash", "echo", "上海崇明岛"]

    # str
    result = shcmd.utils.expand_args("/bin/bash echo 上海崇明岛")
    nose.tools.eq_(result, correct)

    # list
    result = shcmd.utils.expand_args(["/bin/bash", "echo", "上海崇明岛"])
    nose.tools.eq_(result, correct)

    # tuple
    result = shcmd.utils.expand_args(("/bin/bash", "echo", "上海崇明岛"))
    nose.tools.eq_(result, correct)

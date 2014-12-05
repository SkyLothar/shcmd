# -*- coding: utf8 -*-

import os
import tempfile

import nose

import shcmd.cmd


def test_asc_split_args():
    correct = ["/bin/bash", "echo", "上海崇明岛"]

    # str
    result = shcmd.cmd.split_args("/bin/bash echo 上海崇明岛")
    nose.tools.eq_(result, correct, "str test failed")

    # unicode
    result = shcmd.cmd.split_args(u"/bin/bash echo 上海崇明岛")
    nose.tools.eq_(result, correct, "unicode test failed")

    # bytes
    result = shcmd.cmd.split_args(u"/bin/bash echo 上海崇明岛".encode("utf8"))
    nose.tools.eq_(result, correct, "bytes test failed")

    # list
    result = shcmd.cmd.split_args(["/bin/bash", "echo", "上海崇明岛"])
    nose.tools.eq_(result, correct, "list test failed")

    # tuple
    result = shcmd.cmd.split_args(("/bin/bash", "echo", "上海崇明岛"))
    nose.tools.eq_(result, correct, "tuple test failed")


def test_cd():
    tmpdir = os.path.realpath(tempfile.gettempdir())
    oridir = os.getcwd()
    nose.tools.ok_(oridir != tmpdir, "tmp dir == curr dir")
    with shcmd.cmd.cd(tmpdir):
        nose.tools.eq_(
            os.path.realpath(os.getcwd()),
            tmpdir,
            "not cd to dir"
        )
    nose.tools.eq_(os.getcwd(), oridir, "not cd back")


def test_request():
    cwd = os.path.realpath("tmp")
    cmd_req = shcmd.cmd.CmdRequest("/bin/bash eval 'ls'", "tmp")
    nose.tools.eq_(cmd_req.cmd, ["/bin/bash", "eval", "ls"])
    nose.tools.eq_(cmd_req.raw, "/bin/bash eval 'ls'")
    nose.tools.eq_(cmd_req.cwd, cwd)
    nose.tools.eq_(
        str(cmd_req),
        "<CmdRequest (/bin/bash eval 'ls')@{0}>".format(cwd)
    )

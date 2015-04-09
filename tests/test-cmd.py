# -*- coding: utf8 -*-

import os
import tempfile

import nose

import shcmd.cmd


TMPDIR = os.path.realpath(tempfile.gettempdir())


def test_cd():
    oridir = os.getcwd()
    nose.tools.ok_(oridir != TMPDIR)
    with shcmd.cmd.cd(TMPDIR):
        nose.tools.eq_(os.path.realpath(os.getcwd()), TMPDIR)
    nose.tools.eq_(os.getcwd(), oridir)


@shcmd.cmd.cd_to(TMPDIR)
def test_cd_to():
    nose.tools.eq_(TMPDIR, os.getcwd())

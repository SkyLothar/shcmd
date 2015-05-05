# -*- coding: utf8 -*-

import os
import tempfile
import uuid

import nose
import shutil

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


def test_mkdir():
    random_dir = os.path.join(TMPDIR, uuid.uuid4().hex)
    try:
        with shcmd.cd(random_dir, create=True):
            nose.tools.eq_(random_dir, os.getcwd())
    finally:
        shutil.rmtree(random_dir, ignore_errors=True)


@nose.tools.raises(FileNotFoundError)
def test_not_mkdir():
    with shcmd.cd('/f/a/ke_dir'):
        pass


def test_rm_file():
    random_file = os.path.join(TMPDIR, uuid.uuid4().hex)
    with open(random_file, "wt") as f:
        f.write(random_file)
    try:
        nose.tools.eq_(os.path.isfile(random_file), True)
        nose.tools.eq_(random_file, open(random_file).read())
        nose.tools.eq_(shcmd.cmd.rm(random_file), True)
        nose.tools.eq_(os.path.isfile(random_file), False)
    finally:
        if os.path.isfile(random_file):
            os.remove(random_file)
    nose.tools.eq_(shcmd.cmd.rm(random_file), False)


def test_rm_dir():
    random_dir = os.path.join(TMPDIR, uuid.uuid4().hex)
    # dir created
    os.makedirs(random_dir)
    nose.tools.ok_(os.path.isdir(random_dir), )
    nose.tools.ok_(shcmd.cmd.rm(random_dir, isdir=True), "dir not deleted")
    # no such dir, should ignore errors
    nose.tools.eq_(os.path.isdir(random_dir), False)
    nose.tools.eq_(shcmd.cmd.rm(random_dir, isdir=True), False)

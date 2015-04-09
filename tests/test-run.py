# -*- coding: utf8 -*-

import os
import tempfile
import subprocess
import uuid

import mock

import shcmd
from shcmd.errors import ShCmdError


from nose import tools


class TestRun(object):
    def setup(self):
        self.tmp = os.path.realpath(tempfile.gettempdir())
        self.ls_cmd = "ls {0}".format(self.tmp)
        self.ramdom_files = []
        for __ in range(4):
            fname = os.path.join(self.tmp, uuid.uuid4().hex)
            with open(fname, "wt") as f:
                f.write("test-run")
            self.ramdom_files.append(fname)

    def teardown(self):
        for fname in self.ramdom_files:
            os.remove(fname)

    def test_block(self):
        # run once
        proc = shcmd.run(self.ls_cmd)
        ls_result = set(name for name in proc.stdout.splitlines())
        random_files = set(
            os.path.basename(name) for name in self.ramdom_files
        )
        tools.ok_(random_files.issubset(ls_result))
        tools.eq_(proc.return_code, 0)
        proc.raise_for_error()

        # run again
        with mock.patch("subprocess.Popen") as mock_p:
            proc.block()
            tools.eq_(mock_p.mock_calls, [])

    def test_iter_content(self):
        # run once
        proc = shcmd.run(self.ls_cmd, stream=True)
        data = b"".join(d for d in proc.iter_content(100))
        ls_result = set(name for name in data.decode("utf8").splitlines())
        random_files = set(
            os.path.basename(name) for name in self.ramdom_files
        )
        tools.ok_(random_files.issubset(ls_result))
        tools.eq_(proc.return_code, 0)
        proc.raise_for_error()

        # run again
        with mock.patch("subprocess.Popen") as mock_p:
            for d in proc.iter_content(100):
                tools.ok_(len(d) <= 100)
            tools.eq_(mock_p.mock_calls, [])

    def test_iter_lines(self):
        # run once
        proc = shcmd.run(self.ls_cmd, stream=True)
        ls_result = set(name for name in proc.iter_lines())
        random_files = set(
            os.path.basename(name) for name in self.ramdom_files
        )
        tools.ok_(random_files.issubset(ls_result))
        tools.eq_(proc.return_code, 0)
        proc.raise_for_error()

        # run again
        with mock.patch("subprocess.Popen") as mock_p:
            ls_result = set(name for name in proc.iter_lines())
            random_files = set(
                os.path.basename(name) for name in self.ramdom_files
            )
            tools.ok_(random_files.issubset(ls_result))
            tools.eq_(mock_p.mock_calls, [])

    @tools.raises(ShCmdError)
    @mock.patch("subprocess.Popen.communicate")
    def test_error(self, mock_c):
        mock_c.return_value = b"stdout", b"stderr"
        proc = shcmd.run(
            "ls -alh /random-dir/random",
            cwd="/",
            timeout=1,
            env=dict(TEST="1")
        )
        tools.eq_(proc.cmd, ["ls", "-alh", "/random-dir/random"])
        tools.eq_(proc.cwd, "/")
        tools.eq_(proc.timeout, 1)
        tools.eq_(proc.env, {"TEST": "1"})

        tools.eq_(proc.stdout, "stdout")
        tools.eq_(proc.stderr, "stderr")
        tools.eq_(proc.content, b"stdout")

        proc.raise_for_error()

    @tools.raises(subprocess.TimeoutExpired)
    def test_block_timeout(self):
        shcmd.run("grep X", timeout=0.1)

    @tools.raises(subprocess.TimeoutExpired)
    def test_stream_timeout(self):
        proc = shcmd.run("grep X", timeout=0.1, stream=True)
        for data in proc.iter_content(1):
            tools.eq_(data, b"")

# -*- coding: utf8 -*-

import io
import os
import tarfile
import tempfile
import uuid

import mock
from nose import tools

import shcmd.tar


class TestRun(object):
    def setup(self):
        tmp = os.path.realpath(tempfile.gettempdir())
        self.ramdom_files = {}
        for __ in range(4):
            fname = os.path.join(tmp, uuid.uuid4().hex)
            with open(fname, "wb") as f:
                content = uuid.uuid4().hex.encode("utf8")
                f.write(content)
            self.ramdom_files[fname] = content

        old_tar_buffer = io.BytesIO()
        old_tar_content = uuid.uuid4().hex.encode("utf8")
        old_tar = tarfile.TarFile(mode="w", fileobj=old_tar_buffer)
        tar_info = tarfile.TarInfo("old")
        tar_info.size = len(old_tar_content)
        old_tar.addfile(tar_info, io.BytesIO(old_tar_content))
        old_tar.close()

        self.old_tar_content = old_tar_content
        self.old_tar = old_tar_buffer.getvalue()

    def teardown(self):
        for fname in self.ramdom_files.keys():
            os.remove(fname)

    def test_tar(self):
        tg = shcmd.tar.TarGenerator(self.old_tar)
        tg.add_fileobj("bytes", b"foo")
        tg.add_fileobj("str", "bar")
        tg.add_fileobj("io", io.BytesIO(b"baz"))
        tg.files_to_add = self.ramdom_files.keys()

        tar_data = b"".join(b for b in tg.generate())

        test_cases = list(self.ramdom_files.items())
        test_cases += [
            ("bytes", b"foo"),
            ("str", b"bar"),
            ("io", b"baz"),
            ("old", self.old_tar_content)
        ]
        self._check_content(tar_data, test_cases)

    def test_property(self):
        tg = shcmd.tar.TarGenerator()
        tg.files_to_add = list(self.ramdom_files.keys())

        self._check_content(tg.tar, self.ramdom_files.items())

        with mock.patch.object(tg, "generate") as mock_g:
            tools.eq_(tg.tar, tg.tar_io.read())

        tools.eq_(mock_g.mock_calls, [])

    def _check_content(self, tar_data, test_cases):
        tar_obj = tarfile.open(fileobj=io.BytesIO(tar_data))
        for (name, content) in test_cases:
            if name.startswith("/"):
                name = name[1:]
            info = tar_obj.getmember(name)
            e_content = tar_obj.extractfile(info)
            tools.eq_(info.name, name)
            tools.eq_(e_content.read(), content)

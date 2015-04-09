# -*- coding: utf8 -*-

import io
import os
import tarfile
import tempfile
import uuid

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

    def teardown(self):
        for fname in self.ramdom_files.keys():
            os.remove(fname)

    def test_tar(self):
        extras = [
            ("bytes", b"foo"),
            ("str", "bar"),
            ("io", io.BytesIO(b"baz"))
        ]
        file_list = list(self.ramdom_files.keys()) + extras

        tar_data = b"".join(b for b in shcmd.tar.tar_generator(file_list))
        tar_obj = tarfile.open(fileobj=io.BytesIO(tar_data))

        test_cases = list(self.ramdom_files.items())
        test_cases += [
            ("xbytes", b"foo"),  # fake prefix
            ("xstr", b"bar"),
            ("xio", b"baz")
        ]

        for (name, content) in test_cases:
            name = name[1:]  # tar has not / prefix
            info = tar_obj.getmember(name)
            e_content = tar_obj.extractfile(info)
            tools.eq_(info.name, name)
            tools.eq_(e_content.read(), content)

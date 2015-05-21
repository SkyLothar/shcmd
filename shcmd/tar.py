import io
import os
import tarfile


class TarGenerator(object):
    """
    generate or appending some file to tar file

    Usage::

        >>> tg = TarGenerator(old_tar_file)
        >>> tg.files_to_add = ["/path/to/file0", "/path/to/file1"]
        >>> tg.add_fileobj("obj0", "")
        >>> tarfile = b"".join(data for data in tg.generate())
        >>> assert tarfile == tg.tar

    """

    def __init__(self, origin=None):
        """
        :param origin: tar file to appending (default None, generate new tar)
        """
        self._tar_buffer = io.BytesIO()

        self._tar_obj = tarfile.TarFile(
            mode="w",
            fileobj=self._tar_buffer,
            dereference=True
        )

        self._generated = False
        self._files_to_add = set()
        self._ios_to_add = dict()

        if origin:
            if isinstance(origin, bytes):
                origin = io.BytesIO(origin)
            origin_tar = tarfile.TarFile(fileobj=origin)
            for info in origin_tar.getmembers():
                self._tar_obj.addfile(info, origin_tar.extractfile(info))

    @property
    def files(self):
        """files that will be add to tar file later
        should be tuple, list or generator that returns strings
        """
        ios_names = [info.name for info in self._ios_to_add.keys()]
        return set(self.files_to_add + ios_names)

    @property
    def files_to_add(self):
        return list(self._files_to_add)

    @files_to_add.setter
    def files_to_add(self, new_fs_list):
        self._files_to_add = new_fs_list

    def add_fileobj(self, fname, fcontent):
        """add file like object, it will be add to tar file later

        :param fname: name in tar file
        :param fcontent: content. bytes, string, BytesIO or StringIO
        """
        tar_info = tarfile.TarInfo(fname)
        if isinstance(fcontent, io.BytesIO):
            tar_info.size = len(fcontent.getvalue())
        elif isinstance(fcontent, io.StringIO):
            tar_info.size = len(fcontent.getvalue())
            fcontent = io.BytesIO(fcontent.getvalue().encode("utf8"))
        else:
            if hasattr(fcontent, "readable"):
                fcontent = fcontent
            tar_info.size = len(fcontent)
            if isinstance(fcontent, str):
                fcontent = fcontent.encode("utf8")
            fcontent = io.BytesIO(fcontent)
        self._ios_to_add[tar_info] = fcontent

    def generate(self):
        """generate tar file

        ..Usage::

            >>> tarfile = b"".join(data for data in tg.generate())
        """
        if self._tar_buffer.tell():
            self._tar_buffer.seek(0, 0)
            yield self._tar_buffer.read()

        for fname in self._files_to_add:
            last = self._tar_buffer.tell()
            self._tar_obj.add(fname)
            self._tar_buffer.seek(last, os.SEEK_SET)
            data = self._tar_buffer.read()
            yield data

        for info, content in self._ios_to_add.items():
            last = self._tar_buffer.tell()
            self._tar_obj.addfile(info, content)
            self._tar_buffer.seek(last, os.SEEK_SET)
            data = self._tar_buffer.read()
            yield data

        self._tar_obj.close()
        yield self._tar_buffer.read()
        self._generated = True

    @property
    def generated(self):
        return self._generated

    @property
    def tar(self):
        """tar in bytes format"""
        if not self.generated:
            for data in self.generate():
                pass
        return self._tar_buffer.getvalue()

    @property
    def tar_io(self):
        """tar in file like object"""
        return io.BytesIO(self.tar)

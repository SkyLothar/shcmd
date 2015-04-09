import io
import os
import tarfile


def tar_generator(file_list):
    """
    :Usage:
        >>> tg = tar_generator([
        ...     "/path/to/a",
        ...     "/path/to/b",
        ...     ("filename", "content")
        ... ])
        >>> len(b"".join(tg))
        1024

    :param file_list: a list of file_path or (file_name, file_content) tuple
    """
    tar_buffer = io.BytesIO()
    tar_obj = tarfile.TarFile(mode="w", fileobj=tar_buffer, dereference=True)

    for file_detail in file_list:
        last = tar_buffer.tell()
        if isinstance(file_detail, str):
            tar_obj.add(file_detail)
        else:
            content_name, content = file_detail
            content_info = tarfile.TarInfo(content_name)
            if isinstance(content, io.BytesIO):
                content_info.size = len(content.getvalue())
            else:
                content_info.size = len(content)
                content = io.BytesIO(content)

        tar_buffer.seek(last, os.SEEK_SET)
        data = tar_buffer.read()
        yield data

    tar_obj.close()
    yield tar_buffer.read()

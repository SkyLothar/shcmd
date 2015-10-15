import logging
import os
import time
import threading

from shcmd import tailf


__curdir__ = os.path.dirname(os.path.realpath(__file__))

TEST_FILE = os.path.join(__curdir__, "foobar")


def remove_file():
    if os.path.isfile(TEST_FILE):
        os.remove(TEST_FILE)


def test_tailf():
    def fake_writer():
        try:
            with open(TEST_FILE, "at") as f:
                time.sleep(0.05)
                f.write("foo\nbar\n")
            time.sleep(0.05)
            with open(TEST_FILE, "wt") as f:
                time.sleep(0.05)
                f.write("third\n")
                f.write("stop\n")
                f.write("somthing more\n")
                f.write("somthing more again\n")
        finally:
            if os.path.isfile(TEST_FILE):
                os.remove(TEST_FILE)

    try:
        with open(TEST_FILE, "wb"):
            pass
        writer = threading.Thread(target=fake_writer)
        writer.start()
        result = [
            line
            for line in tailf(
                TEST_FILE,
                delay=0.01,
                stopon=lambda x: x == "stop\n",
                timeout=0.5
            )
        ]
        logging.debug("result is {0}".format(result))
        assert result == ["foo\n", "bar\n", "third\n", "stop\n"]
    finally:
        remove_file()

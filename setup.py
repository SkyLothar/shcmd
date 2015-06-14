# -*- coding: utf-8 -*-

import os
import sys

from codecs import open

__version__ = "0.4.1"
__author__ = "SkyLothar"
__email__ = "allothar@gmail.com"
__url__ = "https://github.com/skylothar/shcmd"


try:
    import setuptools
except ImportError:
    from distutils.core import setuptools


if sys.argv[-1] == "publish":
    os.system("python setup.py sdist upload")
    sys.exit()


packages = ["shcmd"]


with open("README.rst", "r", "utf-8") as f:
    readme = f.read()

with open("tests/requirements.txt", "r", "utf-8") as f:
    tests_require = f.read()


setuptools.setup(
    name="shcmd",
    version=__version__,
    description="simple command-line wrapper",
    long_description=readme,
    author=__author__,
    author_email=__email__,
    url=__url__,
    packages=packages,
    package_data={
        "": ["LICENSE"]
    },
    package_dir={
        "shcmd": "shcmd"
    },
    include_package_data=True,
    license="Apache 2.0",
    zip_safe=False,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4"
    ],
    setup_requires=["nose >= 1.0"],
    tests_require=tests_require,
    test_suite="nose.collector"
)

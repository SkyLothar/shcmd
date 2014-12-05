# -*- coding: utf-8 -*-

__version__ = ""
__author__ = ""
__email__ = ""
__url__ = ""


import os
import sys

from codecs import open

try:
    import setuptools
except ImportError:
    from distutils.core import setuptools


if sys.argv[-1] == "publish":
    os.system("python setup.py sdist upload")
    sys.exit()


packages = ["shcmd"]


with open("README.md", "r", "utf-8") as f:
    readme = f.read()

with open("tests/requirements.txt", "r", "utf-8") as f:
    tests_require = f.read()


setuptools.setup(
    name="shcmd",
    version=__version__,
    description="",
    long_description=readme,
    author=__author__,
    author_email=__email__,
    url=__url__,
    packages=packages,
    package_data={
        "": ["LICENSE", "NOTICE"]
    },
    package_dir={
        "shcmd": "shcmd"
    },
    include_package_data=True,
    install_requires=[],
    license="Apache 2.0",
    zip_safe=False,
    classifiers=(
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4"

    ),
    setup_requires=["nose >= 1.0"],
    tests_require=tests_require,
    test_suite="nose.collector"
)

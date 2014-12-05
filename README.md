SHCMD ~~上海崇明岛~~
====================

Note: Work in Progress.

This lib aims to provide a Human friendly interface for subprocess.

If you need piped subprocesses, give [envoy](https://github.com/kennethreitz/envoy) a try.


[![Build Status][travis-image]][travis-url]
[![Coverage Status][coverage-image]][coverage-url]
[![Requirements Status][req-status-image]][req-status-url]


### Usage
```python
import shcmd

with shcmd.cd("/tmp"):
    # get result directly
    assert shcmd.run("pwd") == "/tmp"
    # get streamed result packed in a generator
    streamed = shcmd.run("ls", stream=True)
    for filename in streamed.iter_lines():
        print(filename)
    # get full stdout/stderr
    print(streamed.stdout)
    print(streamed.stderr)
```


[travis-url]: https://travis-ci.org/SkyLothar/shcmd
[travis-image]: https://travis-ci.org/SkyLothar/shcmd.svg?branch=master
[coverage-image]: https://coveralls.io/repos/SkyLothar/shcmd/badge.png
[coverage-url]: https://coveralls.io/r/SkyLothar/shcmd
[req-status-url]: https://requires.io/github/SkyLothar/shcmd/requirements/?branch=master
[req-status-image]: https://requires.io/github/SkyLothar/shcmd/requirements.svg?branch=master

SHCMD
-----

Note: Work in Progress.

This lib aims to provide a Human friendly interface for subprocess.

If you need piped subprocesses, give envoy_ a try.

.. image:: https://travis-ci.org/SkyLothar/shcmd.svg?branch=master
    :target: https://travis-ci.org/SkyLothar/shcmd
.. image:: https://travis-ci.org/SkyLothar/shcmd.svg?branch=master
    :target: https://travis-ci.org/SkyLothar/shcmd
.. image:: https://img.shields.io/coveralls/SkyLothar/shcmd/master.svg
    :target: https://coveralls.io/r/SkyLothar/shcmd

Usage
^^^^^^

.. code-block:: python

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

.. _`envoy`: https://github.com/kennethreitz/envoy
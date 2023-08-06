
`rtmigo / commie.python <https://github.com/rtmigo/commie.python/>`_
========================================================================


.. image:: https://github.com/rtmigo/commie.python/workflows/CI/badge.svg?branch=master
   :target: https://github.com/rtmigo/commie.python/actions
   :alt: Actions Status


.. image:: https://img.shields.io/pypi/status/commie.svg
   :target: https://pypi.python.org/pypi/commie/
   :alt: PyPI status


.. image:: https://img.shields.io/pypi/v/commie.svg
   :target: https://pypi.python.org/pypi/commie/
   :alt: PyPI version shields.io


.. image:: https://img.shields.io/pypi/l/commie.svg
   :target: https://pypi.python.org/pypi/commie/
   :alt: PyPI license


.. image:: https://img.shields.io/pypi/pyversions/commie.svg
   :target: https://pypi.python.org/pypi/commie/
   :alt: PyPI pyversions


Usage
=====

.. code-block:: python

   from pathlib import Path
   import commie

   # in this example we'll parse a Go source file
   sourceCode=Path("/path/to/mycode.go").read_text()

   for comment in commie.iter_comments_go(sourceCode):

     # comment code: "/* sample */"
     print("Comment inner text:", comment.text_span.extract(sourceCode))
     print("Comment text location:", comment.text_span.start, comment.text_span.end)

     # comment text: " sample "
     print("Comment code:", comment.markup_span.extract(sourceCode))
     print("Comment code location:", comment.markup_span.start, comment.markup_span.end)

Parsers
=======

.. list-table::
   :header-rows: 1

   * - **Method**
     - **Works for**
   * - ``commie.iter_comments_c``
     - C99+, C++, Objective-C, C#, Java
   * - ``commie.iter_comments_js``
     - JavaScript, Dart
   * - ``commie.iter_comments_go``
     - Go
   * - ``commie.iter_comments_ruby``
     - Ruby
   * - ``commie.iter_comments_python``
     - Python
   * - ``commie.iter_comments_shell``
     - Bash, Sh
   * - ``commie.iter_comments_html``
     - HTML, XML, SGML
   * - ``commie.iter_comments_css``
     - CSS


Forked from `comment_parser <https://github.com/jeanralphaviles/comment_parser>`_
=====================================================================================

Motivation:

.. list-table::
   :header-rows: 1

   * - **comment_parser**
     - **commie**
   * - Returned only a line number
     - Returns positions where the comment starts and ends. Just like regular string search
   * - Returned only the text of a comment
     - Respects markup as well, making it possible to remove or replace the entire comment
   * - Depends on `python-magic <https://pypi.org/project/python-magic>`_ requiring an optional installation of binaries
     - Does not have this dependency


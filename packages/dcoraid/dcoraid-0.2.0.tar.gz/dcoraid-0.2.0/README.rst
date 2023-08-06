|DCOR-Aid|
==========

|PyPI Version| |Build Status Unix| |Tests Status Win| |Coverage Status|


DCOR-Aid is a GUI for managing data on DCOR (https://dcor.mpl.mpg.de).


Installation
------------
Installers for Windows and macOS are available at the `release page <https://github.com/DCOR-dev/DCOR-Aid/releases>`__.

If you have Python 3 installed, you can install DCOR-Aid with

::

    pip install dcoraid


Testing
-------
By default, testing is done with https://dcor-dev.mpl.mpg.de and the user
"dcoraid". The API key must either be present in the environment variable
``DCOR_API_KEY`` or in the file ``tests/api_key``.

::

    pip install -e .
    python setup.py test
    

.. |DCOR-Aid| image:: https://raw.github.com/DCOR-dev/DCOR-Aid/master/dcoraid/img/dcoraid_text.png
.. |PyPI Version| image:: https://img.shields.io/pypi/v/dcoraid.svg
   :target: https://pypi.python.org/pypi/DCOR-Aid
.. |Build Status Unix| image:: https://img.shields.io/github/workflow/status/DCOR-dev/DCOR-Aid/Checks
   :target: https://github.com/DCOR-dev/DCOR-Aid/actions?query=workflow%3AChecks
.. |Tests Status Win| image:: https://img.shields.io/appveyor/ci/paulmueller/DCOR-Aid/master.svg?label=tests_win
   :target: https://ci.appveyor.com/project/paulmueller/DCOR-Aid
.. |Coverage Status| image:: https://img.shields.io/codecov/c/github/DCOR-dev/DCOR-Aid/master.svg
   :target: https://codecov.io/gh/DCOR-dev/DCOR-Aid

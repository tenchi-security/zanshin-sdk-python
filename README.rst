|PyPI version shields.io| |PyPI pyversions|

Zanshin Python SDK
==================

This Python package contains an SDK to interact with the `API of the
Zanshin SaaS service <https://api.zanshin.tenchisecurity.com>`__ from
`Tenchi Security <https://www.tenchisecurity.com>`__.

This SDK is used to implement a command-line utility, which is available
on `Github <https://github.com/tenchi-security/zanshin-cli>`__ and on
`PyPI <https://pypi.python.org/pypi/zanshincli/>`__.

Configuration File
------------------

The way the SDK handles credentials is by using a configuration file in
the format created by the Python
`RawConfigParser <https://docs.python.org/3/library/configparser.html#configparser.RawConfigParser>`__
class.

The file is located at ``~/.tenchi/config``, where ``~`` is the `current
user's home
directory <https://docs.python.org/3/library/pathlib.html#pathlib.Path.home>`__.

Each section is treated as a configuration profile, and the SDK will
look for a section called ``default`` if another is not explicitly
selected.

These are the supported options:

-  ``api_key`` (required) which contains the Zanshin API key obtained at
   the `Zanshin web
   portal <https://zanshin.tenchisecurity.com/my-profile>`__.
-  ``user_agent`` (optional) allows you to override the default
   user-agent header used by the SDK when making API requests.
-  ``api_url`` (optional) directs the SDK to use a different API
   endpoint than the default (https://api.zanshin.tenchisecurity.com).

This is what a minimal configuration file looks like:

.. code:: ini

   [default]
   api_key = abcdefghijklmnopqrstuvxyz

The SDK
-------

The SDK uses Python 3 type hints extensively. It attempts to abstract
API artifacts such as pagination by using Python generators, thus making
the service easier to interact with.

The network connections are done using the wonderful
`httpx <https://www.python-httpx.org/>`__ library.

Currently it focuses on returning the parsed JSON values instead of
converting them into native classes for higher level abstractions.

The ``zanshinsdk.Client`` class is the main entry point of the SDK. Here
is a quick example that shows information about the owner of the API key
in use:

.. code:: python

   from zanshinsdk import Client
   from json import dumps

   client = Client()   # loads API key from the "default" profile in ~/.tenchi/config
   me = client.me()    # calls /me API endpoint
   print(dumps(me, indent=4))

Support
=======

If you are a Zanshin customer and have any questions regarding the use
of the service, its API or this SDK package, please get in touch via
e-mail at support {at} tenchisecurity {dot} com or via the support
widget on the `Zanshin Portal <https://zanshin.tenchisecurity.com>`__.

.. |PyPI version shields.io| image:: https://img.shields.io/pypi/v/zanshinsdk.svg
   :target: https://pypi.python.org/pypi/zanshinsdk/
.. |PyPI pyversions| image:: https://img.shields.io/pypi/pyversions/zanshinsdk.svg
   :target: https://pypi.python.org/pypi/zanshinsdk/

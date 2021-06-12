Zanshin Python SDK
==================

This Python package contains an SDK and CLI utility to interact with the
`API of the Zanshin SaaS
service <https://api.zanshin.tenchisecurity.com>`__ from `Tenchi
Security <https://www.tenchisecurity.com>`__.

Configuration File
------------------

The way the SDK and CLI handles credentials is by using a configuration
file in the format created by the Python
`RawConfigParser <https://docs.python.org/3/library/configparser.html#configparser.RawConfigParser>`__
class.

The file is located at ``~/.tenchi/config``, where ``~`` is the `current
user's home
directory <https://docs.python.org/3/library/pathlib.html#pathlib.Path.home>`__.

Each section is treated as a configuration profile, and the SDK and CLI
will look for a section called ``default`` if another is not explicitly
selected.

These are the supported options:

-  ``api_key`` (required) which contains the Zanshin API key obtained at
   the `Zanshin web
   portal <https://zanshin.tenchisecurity.com/my-profile>`__.
-  ``user_agent`` (optional) allows you to override the default
   user-agent header used by the SDK when making API requests.
-  ``api_url`` (optional) directs the SDK and CLI to use a different API
   endpoint than the default (https://api.zanshin.tenchisecurity.com).

You can populate the file with the ``zanshin init`` command of the CLI
tool. This is what a minimal configuration file would look like:

.. code:: ini

   [default]
   api_key = abcdefghijklmnopqrstuvxyz

CLI Utility
-----------

This package installs a command-line utility called ``zanshin`` built
with the great `Typer <https://typer.tiangolo.com/>`__ package.

You can obtain help by using the ``--help`` option.

Keep in mind that when options are present that expect multiple values,
these need to be provided as multiple options. For example if you wanted
to list an organization's alerts filtering by the OPEN and RISK_ACCEPTED
states, this is the command you would use:

.. code:: shell

   $ zanshin organization alerts d48edaa6-871a-4082-a196-4daab372d4a1 --state OPEN --state RISK_ACCEPTED

The SDK
-------

The SDK uses Python 3 type hints extensively. It attempts to abstract
API artifacts such as pagination by using Python generators, thus making
the service easier to interact with.

Currently it focuses on returning the parsed JSON values instead of
converting them into native classes for higher level abstractions.

The brunt of the work is done by the zanshinsdk.Client class. Here is a
quick example that shows information about the owner of the API key in
use:

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

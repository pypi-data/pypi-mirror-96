exec-helpers
============

.. image:: https://github.com/python-useful-helpers/exec-helpers/workflows/Python%20package/badge.svg
    :target: https://github.com/python-useful-helpers/exec-helpers/actions
.. image:: https://readthedocs.org/projects/exec-helpers/badge/?version=latest
    :target: https://exec-helpers.readthedocs.io/
    :alt: Documentation Status
.. image:: https://img.shields.io/pypi/v/exec-helpers.svg
    :target: https://pypi.python.org/pypi/exec-helpers
.. image:: https://img.shields.io/pypi/pyversions/exec-helpers.svg
    :target: https://pypi.python.org/pypi/exec-helpers
.. image:: https://img.shields.io/pypi/status/exec-helpers.svg
    :target: https://pypi.python.org/pypi/exec-helpers
.. image:: https://img.shields.io/github/license/python-useful-helpers/exec-helpers.svg
    :target: https://raw.githubusercontent.com/python-useful-helpers/exec-helpers/master/LICENSE
.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :target: https://github.com/ambv/black

Execution helpers for simplified usage of subprocess and ssh.
Why another subprocess wrapper and why no clear `paramiko`?

Historically `paramiko` offers good ssh client, but with specific limitations:
you can call command with timeout, but without receiving return code,
or call command and wait for return code, but without timeout processing.

In the most cases, we are need just simple SSH client with comfortable API for calls, calls via SSH proxy and checking return code/stderr.
This library offers this functionality with deadlock free polling and friendly result objects
(with inline decoding of XML Element tree, YAML, JSON, binary or just strings).
In addition this library offers the same API for subprocess calls, but with specific limitation: no parallel calls
(for protection from race conditions).

Pros:

* STDOUT and STDERR polling during command execution - no deadlocks.
* The same API for subprocess and ssh.
* Free software: Apache license
* Open Source: https://github.com/python-useful-helpers/exec-helpers
* PyPI packaged: https://pypi.python.org/pypi/exec-helpers
* Self-documented code: docstrings with types in comments
* Tested: see badges on top
* Support multiple Python versions:

::

    Python 3.7
    Python 3.8
    Python 3.9

.. note:: Old pythons: For Python 2.7 and PyPy use versions 1.x.x, python 3.4 use versions 2.x.x, python 3.5 and PyPy 3.5 use versions 3.x.x

This package includes:

* `SSHClient` - historically the first one helper, which used for SSH connections.
  Several API calls for sFTP also presents.

* `SSHAuth` - class for credentials storage. `SSHClient` does not store credentials as-is, but uses `SSHAuth` for it.
  Objects of this class can be copied between ssh connection objects, also it used for `execute_through_host`.

* `Subprocess` - `subprocess.Popen` wrapper with timeouts, polling and almost the same API, as `SSHClient`
  (except specific flags, like `cwd` for subprocess and `get_tty` for ssh).

* `async_api.Subprocess` - the same, as `Subprocess` helper, but works with asyncio.
  .. note:: for Windows `ProactorEventLoop` or another non-standard event loop should be used!

* `ExecResult` - class for execution results storage.
  Contains exit code, stdout, stderr and getters for decoding as JSON, YAML, XML (and LXML) element tree, string, bytearray
  and brief strings (up to 7 lines).

* `ExitCodes` - enumerator for standard Linux exit codes. BASH return codes (produced from signal codes) also available.

Installation
============

Standard: `pip install exec-helpers`
Extras:

* ``yaml`` - install `PyYaml` for yaml decoding (`PyYAML` is main decoder, `ruamel.YAML` also supported as fallback.)

* ``xml`` - install `defusedxml` for safe XML parsing to `xml.etree.ElementTree.Element`.

* ``lxml`` - install `lxml` for advanced XML parsing. Can be unsafe.

* ``ALL_FORMATS`` (``all-formats``) - install all parsers. When new parsers will be added, it will ne also supported.

Usage
=====

SSHClient
---------

Basic initialization of `SSHClient` can be done without construction of specific objects:

.. code-block:: python

    client = exec_helpers.SSHClient(host, username="username", password="password")

If ssh agent is running - keys will be collected by paramiko automatically,
but if keys are in specific location  - it should be loaded manually and provided as iterable object of `paramiko.RSAKey`.

For advanced cases or re-use of credentials, `SSHAuth` object should be used.
It can be collected from connection object via property `auth`.

Creation from scratch:

.. code-block:: python

    auth = exec_helpers.SSHAuth(
        username='username',  # type: Optional[str]
        password='password',  # type: Optional[str]
        key=None,  # type: Optional[paramiko.RSAKey]
        keys=None,  # type: Optional[Iterable[paramiko.RSAKey]],
        key_filename=None,  # type: Union[List[str], None]
        passphrase=None,  # type: Optional[str]
    )

Key is a main connection key (always tried first) and keys are alternate keys.
Key filename is a filename or list of filenames with keys, which should be loaded.
Passphrase is an alternate password for keys, if it differs from main password.
If main key now correct for username - alternate keys tried, if correct key found - it became main.
If no working key - password is used and None is set as main key.

Context manager is available, connection is closed and lock is released on exit from context.

.. note:: context manager is strictly not recommended in scenarios with fast reconnect to the same host with te same credentials.

Subprocess
----------

Context manager is available, subprocess is killed and lock is released on exit from context.

Base methods
------------
Main methods are `execute`, `check_call` and `check_stderr` for simple executing, executing and checking return code
and executing, checking return code and checking for empty stderr output.
This methods are almost the same for `SSHClient` and `Subprocess`, except specific flags.

.. note:: By default ALL methods have timeout 1 hour, infinite waiting can be enabled, but it's special case.

.. code-block:: python

    result: ExecResult = helper.execute(
        command,  # type: Union[str, Iterable[str]]
        verbose=False,  # type: bool
        timeout=1 * 60 * 60,  # type: Union[int, float, None]
        # Keyword only:
        log_mask_re=None,  # type: Optional[str]
        stdin=None,  # type: Union[bytes, str, bytearray, None]
        open_stdout=True,  # type: bool
        open_stderr=True,  # type: bool
        **kwargs
    )


.. code-block:: python

    result: ExecResult = helper.check_call(
        command,  # type: Union[str, Iterable[str]]
        verbose=False,  # type: bool
        timeout=1 * 60 * 60,  # type: type: Union[int, float, None]
        error_info=None,  # type: Optional[str]
        expected=(0,),  # type: Iterable[Union[int, ExitCodes]]
        raise_on_err=True,  # type: bool
        # Keyword only:
        log_mask_re=None,  # type: Optional[str]
        stdin=None,  # type: Union[bytes, str, bytearray, None]
        open_stdout=True,  # type: bool
        open_stderr=True,  # type: bool
        exception_class=CalledProcessError,  # Type[CalledProcessError]
        **kwargs
    )

.. code-block:: python

    result: ExecResult = helper.check_stderr(
        command,  # type: Union[str, Iterable[str]]
        verbose=False,  # type: bool
        timeout=1 * 60 * 60,  # type: type: Union[int, float, None]
        error_info=None,  # type: Optional[str]
        raise_on_err=True,  # type: bool
        # Keyword only:
        expected=(0,),  # Iterable[Union[int, ExitCodes]]
        log_mask_re=None,  # type: Optional[str]
        stdin=None,  # type: Union[bytes, str, bytearray, None]
        open_stdout=True,  # type: bool
        open_stderr=True,  # type: bool
        exception_class=CalledProcessError,  # Type[CalledProcessError]
    )

.. code-block:: python

    result: ExecResult = helper(  # Lazy way: instances are callable and uses `execute`.
        command,  # type: Union[str, Iterable[str]]
        verbose=False,  # type: bool
        timeout=1 * 60 * 60,  # type: Union[int, float, None]
        # Keyword only:
        log_mask_re=None,  # type: Optional[str]
        stdin=None,  # type: Union[bytes, str, bytearray, None]
        open_stdout=True,  # type: bool
        open_stderr=True,  # type: bool
        **kwargs
    )

.. note::

  If command is provided as `Iterable[str]`, `shell=True` will be still used,
  but all command components will be joined with escaping to protect from shell processing.

If no STDOUT or STDERR required, it is possible to disable this FIFO pipes via `**kwargs` with flags `open_stdout=False` and `open_stderr=False`.

The next command level uses lower level and kwargs are forwarded, so expected exit codes are forwarded from `check_stderr`.
Implementation specific flags are always set via kwargs.

If required to mask part of command from logging, `log_mask_re` attribute can be set global over instance or provided with command.
All regex matched groups will be replaced by `'<*masked*>'`.

.. code-block:: python

    result: ExecResult = helper.execute(
        command="AUTH='top_secret_key'; run command",  # type: Union[str, Iterable[str]]
        verbose=False,  # type: bool
        timeout=1 * 60 * 60,  # type: Optional[int]
        log_mask_re=r"AUTH\s*=\s*'(\w+)'"  # type: Optional[str]
    )

`result.cmd` will be equal to `AUTH='<*masked*>'; run command`

ExecResult
----------

Execution result object has a set of useful properties:

* `cmd` - Command
* `exit_code` - Command return code. If possible to decode using enumerators for Linux -> it used.
* `stdin` -> `str`. Text representation of stdin.
* `stdout` -> `Tuple[bytes]`. Raw stdout output.
* `stderr` -> `Tuple[bytes]`. Raw stderr output.
* `stdout_bin` -> `bytearray`. Binary stdout output.
* `stderr_bin` -> `bytearray`. Binary stderr output.
* `stdout_str` -> `str`. Text representation of output.
* `stderr_str` -> `str`. Text representation of output.
* `stdout_brief` -> `str`. Up to 7 lines from stdout (3 first and 3 last if >7 lines).
* `stderr_brief` -> `str`. Up to 7 lines from stderr (3 first and 3 last if >7 lines).

* `stdout_json` - STDOUT decoded as JSON.

* `stdout_yaml` - STDOUT decoded as YAML. Accessible only if `PyYAML` or `ruamel.YAML` library installed.
  (Extras: ``yaml``)

* `stdout_xml` - STDOUT decoded as XML to `ElementTree` using `defusedxml` library. Accessible only if `defusedxml` library installed.
  (Extras: ``xml``)

* `stdout_lxml` - STDOUT decoded as XML to `ElementTree` using `lxml` library. Accessible only if `lxml` library installed.
  (Extras: ``lxml``) Can be insecure.

* `timestamp` -> `Optional(datetime.datetime)`. Timestamp for received exit code.

SSHClient specific
------------------

SSHClient commands support get_pty flag, which enables PTY open on remote side.
PTY width and height can be set via keyword arguments, dimensions in pixels are always 0x0.

Possible to call commands in parallel on multiple hosts if it's not produce huge output:

.. code-block:: python

    results: Dict[Tuple[str, int], ExecResult] = SSHClient.execute_together(
        remotes,  # type: Iterable[SSHClient]
        command,  # type: Union[str, Iterable[str]]
        timeout=1 * 60 * 60,  # type: type: Union[int, float, None]
        expected=(0,),  # type: Iterable[Union[int, ExitCodes]]
        raise_on_err=True,  # type: bool
        # Keyword only:
        stdin=None,  # type: Union[bytes, str, bytearray, None]
        open_stdout=True,  # type: bool
        open_stderr=True,  # type: bool
        log_mask_re=None,  # type: Optional[str]
        exception_class=ParallelCallProcessError  # Type[ParallelCallProcessError]
    )
    results  # type: Dict[Tuple[str, int], exec_result.ExecResult]

Results is a dict with keys = (hostname, port) and and results in values.
By default execute_together raises exception if unexpected return code on any remote.

To open new connection using current as proxy is accessible method `proxy_to`. Basic usage example:

.. code-block:: python

    conn: SSHClient = client.proxy_to(host, username="username", password="password")

.. note:: for full command API please rely API documentation.

For execute through SSH host can be used `execute_through_host` method:

.. code-block:: python

    result: ExecResult = client.execute_through_host(
        hostname,  # type: str
        command,  # type: Union[str, Iterable[str]]
        # Keyword only:
        auth=None,  # type: Optional[SSHAuth]
        port=22,  # type: int
        timeout=1 * 60 * 60,  # type: type: Union[int, float, None]
        verbose=False,  # type: bool
        stdin=None,  # type: Union[bytes, str, bytearray, None]
        open_stdout=True,  # type: bool
        open_stderr=True,  # type: bool
        log_mask_re=None,  # type: Optional[str]
        get_pty=False,  # type: bool
        width=80,  # type: int
        height=24  # type: int
    )

Where hostname is a target hostname, auth is an alternate credentials for target host.

SSH client implements fast sudo support via context manager:

.. note:: In case of combination sudo + chroot, chroot will be applied first. For alternative order write command with chroot manually.

Commands will be run with sudo enforced independently from client settings for normal usage:

.. code-block:: python

    with client.sudo(enforce=True):
        ...


Commands will be run *without sudo* independently from client settings for normal usage:

.. code-block:: python

    with client.sudo(enforce=False):
        ...

"Permanent client setting":

.. code-block:: python

    client.sudo_mode = mode  # where mode is True or False

SSH Client supports sFTP for working with remote files:

.. code-block:: python

    with client.open(path, mode='r') as f:
        ...

For fast remote paths checks available methods:

- `exists(path)` -> `bool`

.. code-block:: python

    >>> conn.exists('/etc/passwd')
    True

- `stat(path)` -> `paramiko.sftp_attr.SFTPAttributes`

.. code-block:: python

    >>> conn.stat('/etc/passwd')
    <SFTPAttributes: [ size=1882 uid=0 gid=0 mode=0o100644 atime=1521618061 mtime=1449733241 ]>
    >>> str(conn.stat('/etc/passwd'))
    '-rw-r--r--   1 0        0            1882 10 Dec 2015  ?'

- `isfile(path)` -> `bool`

.. code-block:: python

    >>> conn.isfile('/etc/passwd')
    True

- `isdir(path)` -> `bool`

.. code-block:: python

    >>> conn.isdir('/etc/passwd')
    False

Additional (non-standard) helpers:

- `mkdir(path: str)` - execute mkdir -p path
- `rm_rf(path: str)` - execute rm -rf path
- `upload(source: str, target: str)` - upload file or from source to target using sFTP.
- `download(destination: str, target: str)` - download file from target to destination using sFTP.

Subprocess specific
-------------------
Keyword arguments:

- cwd - working directory.
- env - environment variables dict.

.. note:: `shell=true` is always set.

async_api.Subprocess specific
-----------------------------

All standard methods are coroutines. Async context manager also available.

Example:

.. code-block:: python

    async with helper:
      result: ExecResult = await helper.execute(
          command,  # type: Union[str, Iterable[str]]
          verbose=False,  # type: bool
          timeout=1 * 60 * 60,  # type: Union[int, float, None]
          **kwargs
      )

Testing
=======
The main test mechanism for the package `exec-helpers` is using `tox`.
Available environments can be collected via `tox -l`

CI systems
==========
For code checking several CI systems is used in parallel:

1. `GitHub actions: <https://github.com/python-useful-helpers/exec-helpers/actions>`_ is used for checking: PEP8, pylint, bandit, installation possibility and unit tests.

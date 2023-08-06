#    Copyright 2018 - 2020 Alexey Stepanov aka penguinolog.

#    Copyright 2016 Mirantis, Inc.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

"""Execution result."""

from __future__ import annotations

# Standard Library
import contextlib
import datetime
import json
import logging
import threading
import typing

# Package Implementation
from exec_helpers import exceptions
from exec_helpers import proc_enums
from exec_helpers.proc_enums import ExitCodeT

try:
    # noinspection PyPackageRequirements
    # External Dependencies
    import yaml
except ImportError:
    yaml = None  # type:ignore
try:
    # External Dependencies
    from ruamel import yaml as ruamel_yaml
except ImportError:
    ruamel_yaml = None  # type:ignore
try:
    # External Dependencies
    # noinspection PyPackageRequirements
    import defusedxml.ElementTree  # type: ignore
except ImportError:
    defusedxml = None  # pylint: disable=invalid-name
try:
    # External Dependencies
    # noinspection PyPackageRequirements
    import lxml.etree  # type: ignore  # nosec
except ImportError:
    lxml = None  # pylint: disable=invalid-name

if typing.TYPE_CHECKING:
    # Standard Library
    import xml.etree.ElementTree  # nosec  # for typing only

    # External Dependencies
    # noinspection PyPackageRequirements
    import logwrap

__all__ = ("ExecResult", "OptionalStdinT")

LOGGER: logging.Logger = logging.getLogger(__name__)

OptionalStdinT = typing.Union[bytes, str, bytearray, None]
_OptBytesIterableT = typing.Optional[typing.Iterable[bytes]]
_OptLoggerT = typing.Optional[logging.Logger]


def _get_str_from_bin(src: bytearray) -> str:
    """Join data in list to the string.

    :param src: source to process
    :type src: bytearray
    :return: decoded string
    :rtype: str
    """
    return src.strip().decode(encoding="utf-8", errors="backslashreplace")


def _get_bytearray_from_array(src: typing.Iterable[bytes]) -> bytearray:
    """Get bytearray from array of bytes blocks.

    :param src: source to process
    :type src: typing.List[bytes]
    :return: bytearray
    :rtype: bytearray
    """
    return bytearray(b"".join(src))


class LinesAccessProxy:
    """Lines access proxy."""

    __slots__ = ("_data",)

    def __init__(self, data: typing.Sequence[bytes]) -> None:
        """Lines access proxy.

        :param data: data to work with.
        :type data: typing.Sequence[bytes]
        """
        self._data: typing.Tuple[bytes, ...] = tuple(data)

    # pylint: disable=undefined-variable
    def __getitem__(
        self,
        item: typing.Union[int, slice, typing.Iterable[typing.Union[int, slice, ellipsis]]],  # noqa: F821
    ) -> str:
        """Access magic.

        :param item: index
        :type item: typing.Union[int, slice, typing.Iterable[typing.Union[int, slice, ellipsis]]]
        :return: Joined selected lines
        :rtype: str
        :raises TypeError: Unexpected key
        """
        if isinstance(item, int):
            return _get_str_from_bin(_get_bytearray_from_array([self._data[item]]))
        if isinstance(item, slice):
            return _get_str_from_bin(_get_bytearray_from_array(self._data[item]))
        if isinstance(item, tuple):
            buf: typing.List[bytes] = []
            for rule in item:
                if isinstance(rule, int):
                    buf.append(self._data[rule])
                elif isinstance(rule, slice):
                    buf.extend(self._data[rule])
                elif rule is Ellipsis:
                    buf.append(b"...\n")
                else:
                    raise TypeError(f"Unexpected key type: {rule!r} (from {item!r})")
            return _get_str_from_bin(_get_bytearray_from_array(buf))
        raise TypeError(f"Unexpected key type: {item!r}")

    def __len__(self) -> int:  # pragma: no cover
        """Data len.

        :return: strings count
        :rtype: int
        """
        return len(self._data)

    def __str__(self) -> str:  # pragma: no cover
        """Get string for debug purposes.

        :return: string representation for full content
        :rtype: str
        """
        return self[:]

    def __repr__(self) -> str:
        """Repr for debug purposes.

        :return: full representation for debug purposes
        :rtype: str
        """
        return f"{self.__class__.__name__}(data={self._data!r})"


class ExecResult:
    """Execution result."""

    __slots__ = [
        "__cmd",
        "__stdin",
        "_stdout",
        "_stderr",
        "__exit_code",
        "__timestamp",
        "_stdout_str",
        "_stderr_str",
        "_stdout_brief",
        "_stderr_brief",
        "__stdout_lock",
        "__stderr_lock",
        "__started",
    ]

    def __init__(
        self,
        cmd: str,
        stdin: OptionalStdinT = None,
        stdout: _OptBytesIterableT = None,
        stderr: _OptBytesIterableT = None,
        exit_code: ExitCodeT = proc_enums.INVALID,
        *,
        started: typing.Optional[datetime.datetime] = None,
    ) -> None:
        """Command execution result.

        :param cmd: command
        :type cmd: str
        :param stdin: string STDIN
        :type stdin: typing.Union[bytes, str, bytearray, None]
        :param stdout: binary STDOUT
        :type stdout: typing.Optional[typing.Iterable[bytes]]
        :param stderr: binary STDERR
        :type stderr: typing.Optional[typing.Iterable[bytes]]
        :param exit_code: Exit code. If integer - try to convert to BASH enum.
        :type exit_code: typing.Union[int, proc_enums.ExitCodes]
        :param started: Timestamp of command start
        :type started: typing.Optional[datetime.datetime]
        """
        self.__stdout_lock = threading.RLock()
        self.__stderr_lock = threading.RLock()

        self.__cmd: str = cmd
        if isinstance(stdin, bytes):
            self.__stdin: typing.Optional[str] = _get_str_from_bin(bytearray(stdin))
        elif isinstance(stdin, bytearray):
            self.__stdin = _get_str_from_bin(stdin)
        else:
            self.__stdin = stdin

        if stdout is not None:
            self._stdout: typing.Tuple[bytes, ...] = tuple(stdout)
        else:
            self._stdout = ()

        if stderr is not None:
            self._stderr: typing.Tuple[bytes, ...] = tuple(stderr)
        else:
            self._stderr = ()

        self.__exit_code: ExitCodeT = proc_enums.INVALID
        self.__timestamp: typing.Optional[datetime.datetime] = None
        self.exit_code = exit_code

        self.__started: typing.Optional[datetime.datetime] = started

        # By default is none:
        self._stdout_str: typing.Optional[str] = None
        self._stderr_str: typing.Optional[str] = None
        self._stdout_brief: typing.Optional[str] = None
        self._stderr_brief: typing.Optional[str] = None

    @property
    def stdout_lock(self) -> threading.RLock:
        """Lock object for thread-safe operation.

        :return: internal lock for stdout
        :rtype: threading.RLock

        .. versionadded:: 2.2.0
        """
        return self.__stdout_lock

    @property
    def stderr_lock(self) -> threading.RLock:
        """Lock object for thread-safe operation.

        :return: internal lock for stderr
        :rtype: threading.RLock

        .. versionadded:: 2.2.0
        """
        return self.__stderr_lock

    @property
    def timestamp(self) -> typing.Optional[datetime.datetime]:
        """Timestamp.

        :return: exit code timestamp
        :rtype: typing.Optional[datetime.datetime]
        """
        return self.__timestamp

    def set_timestamp(self) -> None:
        """Set timestamp if empty.

        This will block future object changes.

        .. versionadded:: 4.0.0
        """
        if self.timestamp is None:
            self.__timestamp = datetime.datetime.utcnow()

    @classmethod
    def _get_brief(cls, data: typing.Tuple[bytes, ...]) -> str:
        """Get brief output: 7 lines maximum (3 first + ... + 3 last).

        :param data: source to process
        :type data: typing.Tuple[bytes, ...]
        :return: brief from source
        :rtype: str
        """
        if len(data) <= 7:
            return _get_str_from_bin(_get_bytearray_from_array(data))
        return LinesAccessProxy(data)[:3, ..., -3:]

    @property
    def cmd(self) -> str:
        """Executed command.

        :return: command string
        :rtype: str
        """
        return self.__cmd

    @property
    def stdin(self) -> typing.Optional[str]:
        """Stdin input as string.

        :return: STDIN content if applicable.
        :rtype: typing.Optional[str]
        """
        return self.__stdin

    @property
    def stdout(self) -> typing.Tuple[bytes, ...]:
        """Stdout output as list of binaries.

        :return: STDOUT as tuple of binary strings
        :rtype: typing.Tuple[bytes, ...]
        """
        return self._stdout

    @property
    def stderr(self) -> typing.Tuple[bytes, ...]:
        """Stderr output as list of binaries.

        :return: STDERR as tuple of binary strings
        :rtype: typing.Tuple[bytes, ...]
        """
        return self._stderr

    @staticmethod
    def _poll_stream(
        src: typing.Iterable[bytes],
        log: _OptLoggerT = None,
        verbose: bool = False,
    ) -> typing.List[bytes]:
        """Stream poll helper.

        :param src: source to read from
        :param log: logger instance, if line per line logging expected
        :param verbose: use INFO level for logging
        :return: read result as list of bytes strings
        :rtype: typing.List[bytes]
        """
        dst: typing.List[bytes] = []
        with contextlib.suppress(IOError):
            for line in src:
                dst.append(line)
                if log:
                    log.log(
                        level=logging.INFO if verbose else logging.DEBUG,
                        msg=line.decode("utf-8", errors="backslashreplace").rstrip(),
                    )
        return dst

    def read_stdout(
        self,
        src: _OptBytesIterableT = None,
        log: _OptLoggerT = None,
        verbose: bool = False,
    ) -> None:
        """Read stdout file-like object to stdout.

        :param src: source
        :type src: typing.Optional[typing.Iterable]
        :param log: logger
        :type log: typing.Optional[logging.Logger]
        :param verbose: use log.info instead of log.debug
        :type verbose: bool
        :raises RuntimeError: Exit code is already received

        .. versionchanged:: 1.2.0 - src can be None
        """
        if not src:
            return
        if self.timestamp:
            raise RuntimeError("Final exit code received.")

        with self.stdout_lock:
            self._stdout_str = self._stdout_brief = None
            self._stdout += tuple(self._poll_stream(src, log, verbose))

    def read_stderr(
        self,
        src: _OptBytesIterableT = None,
        log: _OptLoggerT = None,
        verbose: bool = False,
    ) -> None:
        """Read stderr file-like object to stdout.

        :param src: source
        :type src: typing.Optional[typing.Iterable]
        :param log: logger
        :type log: typing.Optional[logging.Logger]
        :param verbose: use log.info instead of log.debug
        :type verbose: bool
        :raises RuntimeError: Exit code is already received

        .. versionchanged:: 1.2.0 - src can be None
        """
        if not src:
            return
        if self.timestamp:
            raise RuntimeError("Final exit code received.")

        with self.stderr_lock:
            self._stderr_str = self._stderr_brief = None
            self._stderr += tuple(self._poll_stream(src, log, verbose))

    @property
    def stdout_bin(self) -> bytearray:
        """Stdout in binary format.

        Sometimes logging is used to log binary objects too (example: Session),
        and for debug purposes we can use this as data source.
        :return: full STDOUT output as bytearray.
        :rtype: bytearray
        """
        with self.stdout_lock:
            return _get_bytearray_from_array(self.stdout)

    @property
    def stderr_bin(self) -> bytearray:
        """Stderr in binary format.

        :return: full STDERR output as bytearray.
        :rtype: bytearray
        """
        with self.stderr_lock:
            return _get_bytearray_from_array(self.stderr)

    @property
    def stdout_str(self) -> str:
        """Stdout output as string.

        :return: full STDOUT output.
        :rtype: str
        """
        with self.stdout_lock:
            if self._stdout_str is None:
                self._stdout_str = _get_str_from_bin(self.stdout_bin)
            return self._stdout_str

    @property
    def stderr_str(self) -> str:
        """Stderr output as string.

        :return: full STDERR output.
        :rtype: str
        """
        with self.stderr_lock:
            if self._stderr_str is None:
                self._stderr_str = _get_str_from_bin(self.stderr_bin)
            return self._stderr_str

    @property
    def stdout_brief(self) -> str:
        """Brief stdout output (mostly for exceptions).

        :return: up to 3 first and 3 last lines of output.
        :rtype: str
        """
        with self.stdout_lock:
            if self._stdout_brief is None:
                self._stdout_brief = self._get_brief(self.stdout)
            return self._stdout_brief

    @property
    def stderr_brief(self) -> str:
        """Brief stderr output (mostly for exceptions).

        :return: up to 3 first and 3 last lines of output.
        :rtype: str
        """
        with self.stderr_lock:
            if self._stderr_brief is None:
                self._stderr_brief = self._get_brief(self.stderr)
            return self._stderr_brief

    @property
    def stdout_lines(self) -> LinesAccessProxy:
        """Get lines by indexes.

        :return: proxy object for lines join by line indexes
        :rtype: LinesAccessProxy

        Usage example:

        .. code-block::python

            res.stdout_lines[<line_number>, <index_start>:<index_end>, ...]
        """
        return LinesAccessProxy(self.stdout)

    @property
    def stderr_lines(self) -> LinesAccessProxy:
        """Magic to get lines human-friendly way.

        :return: proxy object for lines join by line indexes
        :rtype: LinesAccessProxy
        """
        return LinesAccessProxy(self.stderr)

    @property
    def exit_code(self) -> ExitCodeT:
        """Return(exit) code of command.

        :return: exit code
        :rtype: typing.Union[int, proc_enums.ExitCodes]
        """
        return self.__exit_code

    @exit_code.setter
    def exit_code(self, new_val: ExitCodeT) -> None:
        """Return(exit) code of command.

        :param new_val: new exit code
        :type new_val: typing.Union[int, proc_enums.ExitCodes]
        :raises RuntimeError: Exit code is already received
        :raises TypeError: exit code is not int instance

        If valid exit code is set - object became read-only.
        """
        if self.timestamp:
            raise RuntimeError("Exit code is already received.")
        if not isinstance(new_val, int):
            raise TypeError(f"Exit code is strictly int, received: {new_val!r}")
        with self.stdout_lock, self.stderr_lock:
            self.__exit_code = proc_enums.exit_code_to_enum(new_val)
            if self.__exit_code != proc_enums.INVALID:
                self.__timestamp = datetime.datetime.utcnow()

    @property
    def started(self) -> typing.Optional[datetime.datetime]:
        """Timestamp of command start.

        :return: timestamp from command start, if applicable
        :rtype: typing.Optional[datetime.datetime]
        .. versionadded:: 4.0.0
        """
        return self.__started

    def __deserialize(self, fmt: str) -> typing.Any:
        """Deserialize stdout as data format.

        :param fmt: format to decode from
        :type fmt: str
        :return: decoded object
        :rtype: typing.Any
        :raises NotImplementedError: fmt deserialization not implemented
        :raises DeserializeValueError: Not valid source format
        """
        try:
            if fmt == "json":
                return json.loads(self.stdout_str)
            if fmt == "yaml":
                if yaml is not None:
                    if yaml.__with_libyaml__:  # pragma: no cover
                        return yaml.load(self.stdout_str, Loader=yaml.CSafeLoader)  # nosec  # Safe
                    return yaml.safe_load(self.stdout_str)  # pragma: no cover
                return ruamel_yaml.YAML(typ="safe").load(self.stdout_str)  # nosec  # Safe
            if fmt == "xml":
                return defusedxml.ElementTree.fromstring(b"".join(self.stdout))
            if fmt == "lxml":
                return lxml.etree.fromstring(b"".join(self.stdout))  # nosec
        except Exception as e:
            tmpl: str = f"{{self.cmd}} stdout is not valid {fmt}:\n{{stdout!r}}\n"
            LOGGER.exception(tmpl.format(self=self, stdout=self.stdout_str))

            raise exceptions.DeserializeValueError(tmpl.format(self=self, stdout=self.stdout_brief)).with_traceback(
                e.__traceback__
            ) from e

        msg = f"{fmt} deserialize target is not implemented"
        LOGGER.error(msg)
        raise NotImplementedError(msg)

    @property
    def stdout_json(
        self,
    ) -> typing.Union[typing.Dict[str, typing.Any], typing.List[typing.Any], str, int, float, bool, None]:
        """JSON from stdout.

        :return: decoded JSON document
        :rtype: typing.Any
        :raises DeserializeValueError: STDOUT can not be deserialized as JSON
        """
        with self.stdout_lock:
            return self.__deserialize(fmt="json")  # type:ignore

    @property
    def stdout_yaml(self) -> typing.Any:
        """YAML from stdout.

        :return: decoded YAML document
        :rtype: typing.Any
        :raises DeserializeValueError: STDOUT can not be deserialized as YAML
        :raises AttributeError: no any yaml parser installed
        """
        if yaml is None and ruamel_yaml is None:
            raise AttributeError("no any yaml parser installed -> attribute is not functional.")
        with self.stdout_lock:
            return self.__deserialize(fmt="yaml")

    # noinspection PyUnresolvedReferences
    @property
    def stdout_xml(self) -> xml.etree.ElementTree.Element:
        """XML from stdout.

        :return: decoded XML document
        :rtype: xml.etree.ElementTree.Element
        :raises DeserializeValueError: STDOUT can not be deserialized as XML
        :raises AttributeError: defusedxml is not installed
        """
        if defusedxml is None:
            raise AttributeError("defusedxml is not installed -> attribute is not functional by security reasons.")
        with self.stdout_lock:
            return self.__deserialize(fmt="xml")  # type: ignore

    @property
    def stdout_lxml(self) -> lxml.etree.Element:
        """XML from stdout using lxml.

        :return: decoded XML document
        :rtype: lxml.etree.Element
        :raises DeserializeValueError: STDOUT can not be deserialized as XML
        :raises AttributeError: lxml is not installed

        .. note:: Can be insecure.
        """
        if lxml is None:
            raise AttributeError("lxml is not installed -> attribute is not functional.")
        with self.stdout_lock:
            return self.__deserialize(fmt="lxml")

    def __dir__(self) -> typing.List[str]:
        """Override dir for IDE and as source for getitem checks.

        :return: list with public attributes and methods
        :rtype: typing.List[str]
        """
        content = [
            "cmd",
            "stdout",
            "stderr",
            "exit_code",
            "stdout_bin",
            "stderr_bin",
            "stdout_str",
            "stderr_str",
            "stdout_brief",
            "stderr_brief",
            "stdout_lines",
            "stderr_lines",
            "stdout_json",
            "lock",
        ]
        if yaml is not None or ruamel_yaml is not None:
            content.append("stdout_yaml")
        if defusedxml is not None:
            content.append("stdout_xml")
        if lxml is not None:
            content.append("stdout_lxml")
        return content

    def __getitem__(self, item: str) -> typing.Any:
        """Dict like get data.

        :param item: key
        :type item: str
        :return: item if attribute exists
        :rtype: typing.Any
        :raises IndexError: no attribute exists or not allowed to get (not in dir())
        """
        if item in dir(self):
            return getattr(self, item)
        raise IndexError(f'"{item}" not found in {dir(self)}')

    def __repr__(self) -> str:
        """Representation for debugging.

        :return: full representation for debug purposes
        :rtype: str
        """
        if self.started:
            started = f" started={self.started!r},"
        else:
            started = ""
        return (
            f"{self.__class__.__name__}("
            f"cmd={self.cmd!r}, stdout={self.stdout!r}, stderr={self.stderr!r}, exit_code={self.exit_code!s},{started})"
        )

    def __pretty_repr__(
        self,
        log_wrap: logwrap.PrettyRepr,
        indent: int = 0,
        no_indent_start: bool = False,
    ) -> str:
        """Make human readable representation of object.

        :param log_wrap: logwrap instance
        :type log_wrap: logwrap.PrettyRepr
        :param indent: start indentation
        :type indent: int
        :param no_indent_start: do not indent open bracket and simple parameters
        :type no_indent_start: bool
        :return: formatted string
        :rtype: str
        """
        next_indent = log_wrap.next_indent(indent)
        started = f"{'':<{next_indent}}started={self.started!r},\n" if self.started else ""
        stdout = log_wrap.process_element(self.stdout, indent=next_indent, no_indent_start=True)
        stderr = log_wrap.process_element(self.stderr, indent=next_indent, no_indent_start=True)
        msg = (
            f"{'':<{0 if no_indent_start else indent}}{self.__class__.__name__}(\n"
            f"{'':<{next_indent}}cmd={self.cmd!r},\n"
            f"{'':<{next_indent}}stdout={stdout},\n"
            f"{'':<{next_indent}}stderr={stderr},\n"
            f"{'':<{next_indent}}exit_code={self.exit_code!s},\n"
            f"{started}"
            f"{'':<{0 if no_indent_start else indent}})"
        )
        return msg

    def __str__(self) -> str:
        """Representation for logging.

        :return: string representation with brief information
        :rtype: str
        """
        if self.started:
            started = f"\tstarted={self.started.strftime('%Y-%m-%d %H:%M:%S')},\n"
            if self.timestamp:
                _spent = (self.timestamp - self.started).seconds
                spent = f"\tspent={_spent // (60 * 60):02d}:{_spent // 60:02d}:{_spent % 60:02d},\n"
            else:
                spent = ""
        else:
            started = ""
            spent = ""
        return (
            f"{self.__class__.__name__}(\n"
            f"\tcmd={self.cmd!r},\n"
            f"\tstdout=\n"
            f"{self.stdout_brief!r},\n"
            f"\tstderr=\n"
            f"{self.stderr_brief!r}, \n"
            f"\texit_code={self.exit_code!s},\n"
            f"{started}{spent})"
        )

    def __eq__(self, other: typing.Any) -> bool:
        """Comparison.

        :param other: other ExecResult instance.
        :type other: typing.Any
        :return: current object equals other
        :rtype: bool
        """
        return (
            self.__class__ is other.__class__
            or issubclass(self.__class__, other.__class__)
            or issubclass(other.__class__, self.__class__)
        ) and (
            self.cmd == other.cmd
            and self.stdin == other.stdin
            and self.stdout == other.stdout
            and self.stderr == other.stderr
            and self.exit_code == other.exit_code
        )

    def __ne__(self, other: typing.Any) -> bool:
        """Comparison.

        :param other: other ExecResult instance.
        :type other: typing.Any
        :return: current object not equals other
        :rtype: bool
        """
        return not self.__eq__(other)

    def __hash__(self) -> int:
        """Hash for usage as dict key and in sets.

        :return: calculated hash value
        :rtype: int
        """
        return hash((self.__class__, self.cmd, self.stdin, self.stdout, self.stderr, self.exit_code))

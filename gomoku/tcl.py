"""Locate the Tcl/Tk runtime that ships with the running interpreter.

uv-managed CPython builds (python-build-standalone) bundle Tcl/Tk inside the
interpreter prefix, e.g. ``<prefix>/lib/tcl8.6/init.tcl``.  Inside a virtual
environment Tcl derives its search path from ``sys.executable``, which points at
``.venv/bin/python``, so it looks for ``.venv/lib/tcl8.6`` and fails with
"Can't find a usable init.tcl".  Pointing ``TCL_LIBRARY``/``TK_LIBRARY`` at the
base prefix restores the lookup.  On interpreters that already resolve Tcl
correctly (system/Homebrew builds, non-venv uv Pythons) the base prefix simply
has no bundled Tcl directory and the function is a no-op.
"""

from __future__ import annotations

import os
import pathlib
import sys


def _find_bundled(directory: pathlib.Path, name: str) -> pathlib.Path | None:
    """Return ``<directory>/<name><version>`` containing ``init.tcl``, if any."""
    for candidate in sorted(directory.glob(f"{name}[0-9]*")):
        if (candidate / "init.tcl").is_file():
            return candidate
    return None


def configure_tcl_environment() -> None:
    """Make a venv-local interpreter find the Tcl/Tk libraries of its base."""
    if sys.platform != "darwin" or sys.prefix == sys.base_prefix:
        return

    lib = pathlib.Path(sys.base_prefix) / "lib"
    for name, variable in (("tcl", "TCL_LIBRARY"), ("tk", "TK_LIBRARY")):
        if variable in os.environ:
            continue
        if (found := _find_bundled(lib, name)) is not None:
            os.environ[variable] = str(found)

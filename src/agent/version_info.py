"""Build a PyInstaller PE version resource from the root VERSION file.

Imported by protocol0-agent.spec and protocol0-launcher.spec at build time. Populated
PE metadata (ProductName, version, CompanyName, ...) is a positive trust signal for AV
heuristics and makes the exe look like "a real app" in Windows Explorer -> Properties
-> Details, instead of a blank unsigned binary. Read from VERSION so it never drifts
(same single source of truth the .iss reads at compile time).

Usage in a .spec (which runs as Python):
    from version_info import version_resource
    exe = EXE(..., version=version_resource("Protocol 0 Agent", "protocol0-agent.exe"))
"""
import os

from PyInstaller.utils.win32.versioninfo import (
    FixedFileInfo,
    StringFileInfo,
    StringStruct,
    StringTable,
    VarFileInfo,
    VarStruct,
    VSVersionInfo,
)

_COMPANY = "Thibault Lebrun"
_PRODUCT = "Protocol 0"


def _version_tuple():
    """(major, minor, patch, 0) parsed from the root VERSION file."""
    here = os.path.dirname(os.path.abspath(__file__))
    version_path = os.path.join(here, "..", "..", "VERSION")
    with open(version_path, encoding="utf-8") as f:
        raw = f.read().strip()
    parts = [int(p) for p in raw.split(".")]
    # PE version is a fixed 4-field tuple; pad/truncate to (major, minor, patch, build).
    parts = (parts + [0, 0, 0, 0])[:4]
    return tuple(parts), raw


def version_resource(file_description: str, original_filename: str) -> VSVersionInfo:
    """A VSVersionInfo for one exe, with metadata pulled from VERSION."""
    (major, minor, patch, build), raw = _version_tuple()
    return VSVersionInfo(
        ffi=FixedFileInfo(
            filevers=(major, minor, patch, build),
            prodvers=(major, minor, patch, build),
            mask=0x3F,
            flags=0x0,
            OS=0x40004,  # VOS_NT_WINDOWS32
            fileType=0x1,  # VFT_APP
            subtype=0x0,
        ),
        kids=[
            StringFileInfo([
                # 040904B0 = US English, Unicode codepage.
                StringTable("040904B0", [
                    StringStruct("CompanyName", _COMPANY),
                    StringStruct("FileDescription", file_description),
                    StringStruct("FileVersion", raw),
                    StringStruct("ProductName", _PRODUCT),
                    StringStruct("ProductVersion", raw),
                    StringStruct("OriginalFilename", original_filename),
                    StringStruct("LegalCopyright", "Thibault Lebrun. Open source."),
                ]),
            ]),
            VarFileInfo([VarStruct("Translation", [0x0409, 0x04B0])]),
        ],
    )

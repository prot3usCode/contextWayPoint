"""Minimal local build backend for offline editable installs."""

from __future__ import annotations

import base64
import hashlib
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile


PROJECT_ROOT = Path(__file__).resolve().parent
SRC_ROOT = PROJECT_ROOT / "src"
PACKAGE_ROOT = SRC_ROOT / "contextwaypoint"
PACKAGE_NAME = "contextwaypoint"
VERSION = "0.1.0"
DIST_INFO = f"{PACKAGE_NAME}-{VERSION}.dist-info"
WHEEL_NAME = f"{PACKAGE_NAME}-{VERSION}-py3-none-any.whl"


def _metadata_text() -> str:
    return "\n".join(
        [
            "Metadata-Version: 2.1",
            f"Name: {PACKAGE_NAME}",
            f"Version: {VERSION}",
            "Summary: Compiler and router for authored LLM context.",
            "Requires-Python: >=3.10",
            "Requires-Dist: PyYAML>=6.0",
            "",
        ]
    )


def _wheel_text() -> str:
    return "\n".join(
        [
            "Wheel-Version: 1.0",
            "Generator: contextwaypoint-local-backend",
            "Root-Is-Purelib: true",
            "Tag: py3-none-any",
            "",
        ]
    )


def _entry_points_text() -> str:
    return "\n".join(
        [
            "[console_scripts]",
            "contextwaypoint = contextwaypoint.cli:main",
            "",
        ]
    )


def _record_line(path: str, data: bytes) -> str:
    digest = hashlib.sha256(data).digest()
    encoded_digest = base64.urlsafe_b64encode(digest).rstrip(b"=").decode("ascii")
    return f"{path},sha256={encoded_digest},{len(data)}"


def _write_metadata_tree(metadata_dir: Path) -> None:
    metadata_dir.mkdir(parents=True, exist_ok=True)
    (metadata_dir / "METADATA").write_text(_metadata_text(), encoding="utf-8")
    (metadata_dir / "WHEEL").write_text(_wheel_text(), encoding="utf-8")
    (metadata_dir / "entry_points.txt").write_text(
        _entry_points_text(),
        encoding="utf-8",
    )


def _build_wheel_archive(wheel_directory: str, editable: bool) -> str:
    wheel_dir = Path(wheel_directory)
    wheel_dir.mkdir(parents=True, exist_ok=True)
    wheel_path = wheel_dir / WHEEL_NAME
    records: list[str] = []

    with ZipFile(wheel_path, "w", compression=ZIP_DEFLATED) as zip_file:
        if editable:
            pth_name = f"{PACKAGE_NAME}.pth"
            pth_data = f"{SRC_ROOT.resolve()}\n".encode("utf-8")
            zip_file.writestr(pth_name, pth_data)
            records.append(_record_line(pth_name, pth_data))
        else:
            for source_path in sorted(PACKAGE_ROOT.rglob("*")):
                if not source_path.is_file():
                    continue
                archive_name = source_path.relative_to(SRC_ROOT).as_posix()
                file_data = source_path.read_bytes()
                zip_file.writestr(archive_name, file_data)
                records.append(_record_line(archive_name, file_data))

        metadata_files = {
            f"{DIST_INFO}/METADATA": _metadata_text().encode("utf-8"),
            f"{DIST_INFO}/WHEEL": _wheel_text().encode("utf-8"),
            f"{DIST_INFO}/entry_points.txt": _entry_points_text().encode("utf-8"),
        }

        for archive_name, file_data in metadata_files.items():
            zip_file.writestr(archive_name, file_data)
            records.append(_record_line(archive_name, file_data))

        record_name = f"{DIST_INFO}/RECORD"
        record_lines = records + [f"{record_name},,"]
        record_data = "\n".join(record_lines).encode("utf-8")
        zip_file.writestr(record_name, record_data)

    return WHEEL_NAME


def build_wheel(
    wheel_directory: str,
    config_settings: dict | None = None,
    metadata_directory: str | None = None,
) -> str:
    return _build_wheel_archive(wheel_directory, editable=False)


def build_editable(
    wheel_directory: str,
    config_settings: dict | None = None,
    metadata_directory: str | None = None,
) -> str:
    return _build_wheel_archive(wheel_directory, editable=True)


def get_requires_for_build_wheel(config_settings: dict | None = None) -> list[str]:
    return []


def get_requires_for_build_editable(config_settings: dict | None = None) -> list[str]:
    return []


def prepare_metadata_for_build_wheel(
    metadata_directory: str,
    config_settings: dict | None = None,
) -> str:
    dist_info_dir = Path(metadata_directory) / DIST_INFO
    _write_metadata_tree(dist_info_dir)
    return DIST_INFO


def prepare_metadata_for_build_editable(
    metadata_directory: str,
    config_settings: dict | None = None,
) -> str:
    return prepare_metadata_for_build_wheel(metadata_directory, config_settings)


def _supported_features() -> list[str]:
    return ["build_editable"]

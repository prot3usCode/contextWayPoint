# Copyright (c) 2026 Daniel Bueno
# SPDX-License-Identifier: MIT
# See LICENSE for the full license text.

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
FORMATS_DIR = PROJECT_ROOT / "Formats"
OUTPUT_DIR = PROJECT_ROOT / "output"
DEFAULT_INDEX_FILE = OUTPUT_DIR / "contextIndex.json"
DEFAULT_PACKET_DIR = OUTPUT_DIR / "contextPackets"
DEFAULT_DEMO_OUTPUT_DIR = OUTPUT_DIR / "demos"
DEFAULT_GENERATED_YAML_DIR = OUTPUT_DIR / "generatedYaml"
DEMO_ROOT = PROJECT_ROOT / "demos" / "rag_vs_contextwaypoint"
YAML_SUFFIXES = {".yaml", ".yml"}


class ContextValidationError(Exception):
    def __init__(self, errors: list[str]) -> None:
        super().__init__("Validation failed")
        self.errors = errors


def display_path(path: Path) -> str:
    try:
        return str(path.relative_to(PROJECT_ROOT))
    except ValueError:
        return str(path)

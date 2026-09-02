"""Guardrails ensuring PRODX core remains independent of provider API credentials."""

from __future__ import annotations

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
KEY_NAME = "OPENAI" + "_API_KEY"
CODE_SUFFIXES = {".py", ".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs"}
IGNORED_PARTS = {".git", "node_modules", "__pycache__"}
OPENAI_IMPORT = re.compile(r"(?i)(?:from|import|require\s*\(|use)\s*[^\n;]*openai")


def repository_files():
    for path in ROOT.rglob("*"):
        if not path.is_file() or any(part in IGNORED_PARTS for part in path.parts):
            continue
        yield path


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


class AIProviderIndependence(unittest.TestCase):
    def test_openai_platform_api_key_is_not_referenced(self):
        violations = []
        for path in repository_files():
            if path == Path(__file__).resolve():
                continue
            if KEY_NAME in read_text(path):
                violations.append(str(path.relative_to(ROOT)))
        self.assertFalse(
            violations,
            "Core repository must not reference an OpenAI Platform API-key environment variable: "
            + ", ".join(violations),
        )

    def test_core_source_does_not_import_openai_sdk(self):
        violations = []
        for path in (ROOT / "src", ROOT / "frontend").__iter__():
            if not path.exists():
                continue
            for source in path.rglob("*"):
                if source.is_file() and source.suffix in CODE_SUFFIXES and OPENAI_IMPORT.search(read_text(source)):
                    violations.append(str(source.relative_to(ROOT)))
        self.assertFalse(
            violations,
            "Core application source must not import or invoke an OpenAI SDK: " + ", ".join(violations),
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)

from __future__ import annotations

import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from validate_defaults import validate_defaults  # noqa: E402


def copy_fixture() -> tuple[tempfile.TemporaryDirectory[str], Path]:
    temporary = tempfile.TemporaryDirectory(prefix="organization-defaults-")
    fixture = Path(temporary.name) / "repo"
    (fixture / ".github").mkdir(parents=True)
    (fixture / "scripts").mkdir()
    (fixture / "tests").mkdir()
    for relative in (
        "CHATGPT_PROJECT_INSTRUCTIONS.md",
        ".github/PULL_REQUEST_TEMPLATE.md",
        "scripts/validate_defaults.py",
        "tests/test_validate_defaults.py",
    ):
        source = ROOT / relative
        target = fixture / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
    return temporary, fixture


class OrganizationDefaultsTests(unittest.TestCase):
    def test_current_files_pass(self) -> None:
        self.assertEqual(validate_defaults(ROOT), [])

    def test_workflow_file_is_rejected(self) -> None:
        temporary, fixture = copy_fixture()
        self.addCleanup(temporary.cleanup)
        workflow = fixture / ".github/workflows/ci.yml"
        workflow.parent.mkdir(parents=True)
        workflow.write_text("name: prohibited\n", encoding="utf-8")
        errors = validate_defaults(fixture)
        self.assertTrue(any("hosted GitHub workflow is prohibited" in error for error in errors), errors)

    def test_execution_source_requirements_are_enforced(self) -> None:
        cases = (
            (
                "CHATGPT_PROJECT_INSTRUCTIONS.md",
                "Invoke the installed Superpowers plugin's `using-superpowers` skill",
            ),
            (
                "CHATGPT_PROJECT_INSTRUCTIONS.md",
                "Read live `Bjs-Projects/skills` `main`, inspect `SKILLS_INDEX.md`",
            ),
            (
                ".github/PULL_REQUEST_TEMPLATE.md",
                "No `.github/workflows` file, hosted workflow run, job, artifact, or runner was created or used.",
            ),
        )
        for relative, phrase in cases:
            with self.subTest(relative=relative, phrase=phrase):
                temporary, fixture = copy_fixture()
                self.addCleanup(temporary.cleanup)
                path = fixture / relative
                path.write_text(
                    path.read_text(encoding="utf-8").replace(phrase, "", 1),
                    encoding="utf-8",
                )
                errors = validate_defaults(fixture)
                self.assertTrue(any(phrase in error for error in errors), errors)


if __name__ == "__main__":
    unittest.main()

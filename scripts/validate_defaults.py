#!/usr/bin/env python3
"""Validate the minimal organization bootstrap."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_PATHS = (
    "CHATGPT_PROJECT_INSTRUCTIONS.md",
    ".github/PULL_REQUEST_TEMPLATE.md",
    "scripts/validate_defaults.py",
    "tests/test_validate_defaults.py",
)

REMOVED_PATHS = (
    ".github/workflows/defaults-check.yml",
    "workflow-templates/bjs-repository-contract.yml",
    "workflow-templates/bjs-repository-contract.properties.json",
)

REQUIRED_PR_HEADINGS = (
    "## Requested result",
    "## Delivery class",
    "## Repository and refs",
    "## Change summary",
    "## Verification performed",
    "## Required delivery",
    "## External prerequisite",
    "## Final checklist",
)

REQUIRED_PR_CHECKS = (
    "The live `Bjs-Projects/docs/WORKFLOW.md` was used as the sole process authority.",
    "The installed Superpowers plugin and every applicable Superpowers skill were used.",
    "Live `Bjs-Projects/skills` `main`, `SKILLS_INDEX.md`, and every relevant unchanged `SKILL.md` were read.",
    "No `.github/workflows` file, hosted workflow run, job, artifact, or runner was created or used.",
)

REQUIRED_BOOTSTRAP = (
    "Repository: Bjs-Projects/REPOSITORY-NAME",
    "make the first repository operation a live GitHub connector read",
    "read the live `Bjs-Projects/docs/WORKFLOW.md` from `main`",
    "follow it as the sole cross-project process",
    "Invoke the installed Superpowers plugin's `using-superpowers` skill",
    "Read live `Bjs-Projects/skills` `main`, inspect `SKILLS_INDEX.md`",
    "Use the skills catalog and installed Superpowers plugin together; neither substitutes for the other.",
    "Never create, modify, trigger, rerun, or rely on `.github/workflows`, hosted workflow runs, jobs, artifacts, or runners.",
)

def read_text(root: Path, relative: str, errors: list[str]) -> str:
    path = root / relative
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        errors.append(f"{relative}: cannot read: {exc}")
        return ""
    if text and not text.endswith("\n"):
        errors.append(f"{relative}: missing final newline")
    for number, line in enumerate(text.splitlines(), 1):
        if line.rstrip() != line:
            errors.append(f"{relative}:{number}: trailing whitespace")
    return text

def require_snippets(name: str, text: str, snippets: tuple[str, ...], errors: list[str]) -> None:
    for snippet in snippets:
        if snippet not in text:
            errors.append(f"{name}: missing required snippet: {snippet}")

def validate_defaults(root: Path = ROOT) -> list[str]:
    root = root.resolve()
    errors: list[str] = []

    for relative in REQUIRED_PATHS:
        if not (root / relative).is_file():
            errors.append(f"missing required path: {relative}")
    for relative in REMOVED_PATHS:
        if (root / relative).exists():
            errors.append(f"prohibited or obsolete path remains: {relative}")

    workflow_root = root / ".github" / "workflows"
    if workflow_root.exists():
        for path in sorted(item for item in workflow_root.rglob("*") if item.is_file()):
            errors.append(
                f"hosted GitHub workflow is prohibited: {path.relative_to(root)}"
            )

    bootstrap = read_text(root, "CHATGPT_PROJECT_INSTRUCTIONS.md", errors)
    pr_template = read_text(root, ".github/PULL_REQUEST_TEMPLATE.md", errors)
    read_text(root, "scripts/validate_defaults.py", errors)
    read_text(root, "tests/test_validate_defaults.py", errors)

    require_snippets("project instruction bootstrap", bootstrap, REQUIRED_BOOTSTRAP, errors)
    require_snippets("pull request template", pr_template, REQUIRED_PR_HEADINGS, errors)
    require_snippets("pull request template", pr_template, REQUIRED_PR_CHECKS, errors)

    return sorted(set(errors))

def main() -> int:
    errors = validate_defaults(ROOT)
    if errors:
        print("Organization defaults validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print(
        "Organization defaults validation passed: central workflow authority, "
        "mandatory skills sources, and no hosted GitHub workflows."
    )
    return 0

if __name__ == "__main__":
    raise SystemExit(main())

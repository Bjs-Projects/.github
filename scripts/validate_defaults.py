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

REQUIRED_BOOTSTRAP = (
    "Repository: Bjs-Projects/REPOSITORY-NAME",
    "Before any response or action, invoke the installed Superpowers plugin's `using-superpowers` skill, then every applicable Superpowers skill.",
    "read the live `Bjs-Projects/docs/WORKFLOW.md` from `main`",
    "follow it as the sole Bjs-specific policy",
)

REQUIRED_PR_HEADINGS = (
    "## Requested result",
    "## Repository and refs",
    "## Change summary",
    "## Verification evidence",
    "## Delivery",
    "## Limitations",
)

MIRRORED_RULES = (
    "SKILLS_INDEX.md",
    ".github/workflows",
    "Google Drive",
    "release-required",
    "release-exempt",
    "expected-head",
    "Final checklist",
    "branch head",
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
    for line_number, line in enumerate(text.splitlines(), 1):
        if line.rstrip() != line:
            errors.append(f"{relative}:{line_number}: trailing whitespace")
    return text


def require_snippets(name: str, text: str, snippets: tuple[str, ...], errors: list[str]) -> None:
    for snippet in snippets:
        if snippet not in text:
            errors.append(f"{name}: missing required snippet: {snippet}")


def reject_mirrors(name: str, text: str, errors: list[str]) -> None:
    for snippet in MIRRORED_RULES:
        if snippet in text:
            errors.append(f"{name}: mirrors central policy: {snippet}")


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
            errors.append(f"hosted GitHub workflow is prohibited: {path.relative_to(root)}")

    bootstrap = read_text(root, "CHATGPT_PROJECT_INSTRUCTIONS.md", errors)
    pr_template = read_text(root, ".github/PULL_REQUEST_TEMPLATE.md", errors)
    read_text(root, "scripts/validate_defaults.py", errors)
    read_text(root, "tests/test_validate_defaults.py", errors)

    require_snippets("project instruction bootstrap", bootstrap, REQUIRED_BOOTSTRAP, errors)
    require_snippets("pull request template", pr_template, REQUIRED_PR_HEADINGS, errors)

    if bootstrap.find("using-superpowers") >= bootstrap.find("docs/WORKFLOW.md"):
        errors.append("project instruction bootstrap: using-superpowers must precede the central workflow read")

    headings = tuple(line for line in pr_template.splitlines() if line.startswith("## "))
    if headings != REQUIRED_PR_HEADINGS:
        errors.append("pull request template: headings must equal the evidence-only canonical set")

    reject_mirrors("project instruction bootstrap", bootstrap, errors)
    reject_mirrors("pull request template", pr_template, errors)

    return sorted(set(errors))


def main() -> int:
    errors = validate_defaults(ROOT)
    if errors:
        print("Organization defaults validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print(
        "Organization defaults validation passed: minimal Superpowers-first bootstrap, "
        "evidence-only pull-request template, and no hosted workflows."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

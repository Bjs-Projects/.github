#!/usr/bin/env python3
"""Validate quota-efficient inherited Bjs-Projects workflow defaults."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED_PATHS = (
    ".github/PULL_REQUEST_TEMPLATE.md",
    ".github/workflows/defaults-check.yml",
    "workflow-templates/bjs-repository-contract.yml",
    "workflow-templates/bjs-repository-contract.properties.json",
    "scripts/validate_defaults.py",
)

CHECKOUT_PIN = "de0fac2e4500dabe0009e67214ff5f5447ce83dd"
SETUP_PYTHON_PIN = "a309ff8b426b58ec0e2a45f0f869d46889d02405"
LFS_ARCHIVE_SHA256 = "1c0b6ee5200ca708c5cebebb18fdeb0e1c98f1af5c1a9cba205a4c0ab5a5ec08"
FULL_SHA_RE = re.compile(r"^[0-9a-f]{40}$")
USES_RE = re.compile(r"^\s*uses:\s*([^\s#]+)(?:\s+#\s*(.+))?$", re.MULTILINE)
PUSH_TRIGGER_RE = re.compile(r"^\s{2}push:\s*$", re.MULTILINE)

REQUIRED_TEMPLATE_SNIPPETS = (
    "name: Bjs Repository Contract",
    "pull_request:",
    "branches: [ $default-branch ]",
    "workflow_dispatch:",
    "permissions:\n  contents: read",
    "cancel-in-progress: true",
    "submodules: recursive",
    "lfs: false",
    f"uses: actions/checkout@{CHECKOUT_PIN} # v6.0.2",
    f"uses: actions/setup-python@{SETUP_PYTHON_PIN} # v6.2.0",
    "git-lfs-linux-amd64-v3.7.1.tar.gz",
    LFS_ARCHIVE_SHA256,
    "git lfs pull",
    "git lfs fsck",
    "expected_oid = match.group(1)",
    "actual_oid = hashlib.sha256(data).hexdigest()",
    "50 * 1024 * 1024",
    "100 * 1024 * 1024",
    "Require immutable external GitHub Action pins",
)

REQUIRED_PR_HEADINGS = (
    "## Requested result",
    "## Current change summary",
    "## Validation completed",
    "## Remaining work",
    "## Exact next action",
    "## Final checklist",
)

REQUIRED_PR_CHECKS = (
    "Every coherent change is committed and visible on the remote branch.",
    "This pull request was opened when implementation was ready for validation",
    "Required checks ran against the latest head commit.",
    "External GitHub Actions are pinned to reviewed full commit SHAs.",
)

FORBIDDEN_PHRASES = (
    ".chatgpt/CHECKPOINT.md",
    "bjs-checkpoint-v",
    "workspace ID",
    "archive/YYYYMMDDTHHMMSSZ",
    "GitHub App controller",
    "nightly compliance",
    "connector-only",
    "only GitHub connector",
)


def read_text(path: Path, errors: list[str]) -> str:
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        errors.append(f"{path.relative_to(ROOT)}: cannot read: {exc}")
        return ""
    if text and not text.endswith("\n"):
        errors.append(f"{path.relative_to(ROOT)}: missing final newline")
    for number, line in enumerate(text.splitlines(), 1):
        if line.rstrip() != line:
            errors.append(f"{path.relative_to(ROOT)}:{number}: trailing whitespace")
    return text


def validate_action_pins(path: Path, text: str, errors: list[str]) -> None:
    for spec, comment in USES_RE.findall(text):
        if spec.startswith("./"):
            continue
        if "@" not in spec:
            errors.append(f"{path.relative_to(ROOT)}: external Action missing ref: {spec}")
            continue
        action, ref = spec.rsplit("@", 1)
        if not FULL_SHA_RE.fullmatch(ref):
            errors.append(f"{path.relative_to(ROOT)}: mutable Action ref: {action}@{ref}")
        if not comment.strip():
            errors.append(f"{path.relative_to(ROOT)}: Action pin lacks release comment: {spec}")


def require_snippets(filename: str, text: str, snippets: tuple[str, ...], errors: list[str]) -> None:
    for snippet in snippets:
        if snippet not in text:
            errors.append(f"{filename}: missing required snippet: {snippet}")


def main() -> int:
    errors: list[str] = []
    for name in REQUIRED_PATHS:
        if not (ROOT / name).is_file():
            errors.append(f"missing required path: {name}")

    template_path = ROOT / "workflow-templates/bjs-repository-contract.yml"
    workflow_path = ROOT / ".github/workflows/defaults-check.yml"
    pr_path = ROOT / ".github/PULL_REQUEST_TEMPLATE.md"
    metadata_path = ROOT / "workflow-templates/bjs-repository-contract.properties.json"

    template = read_text(template_path, errors) if template_path.is_file() else ""
    workflow = read_text(workflow_path, errors) if workflow_path.is_file() else ""
    pr_template = read_text(pr_path, errors) if pr_path.is_file() else ""
    read_text(Path(__file__), errors)

    for path, text in ((template_path, template), (workflow_path, workflow)):
        validate_action_pins(path, text, errors)
        if PUSH_TRIGGER_RE.search(text):
            errors.append(
                f"{path.relative_to(ROOT)}: push trigger is forbidden; preservation pushes must not run CI"
            )
        if '"work/**"' in text or '"recovery/**"' in text:
            errors.append(f"{path.relative_to(ROOT)}: work/recovery branch CI trigger is forbidden")

    require_snippets("repository contract template", template, REQUIRED_TEMPLATE_SNIPPETS, errors)
    for heading in REQUIRED_PR_HEADINGS:
        if heading not in pr_template:
            errors.append(f"pull request template missing heading: {heading}")
    for checklist_item in REQUIRED_PR_CHECKS:
        if checklist_item not in pr_template:
            errors.append(f"pull request template missing final check: {checklist_item}")

    policy_surface = "\n".join((template, workflow, pr_template))
    for phrase in FORBIDDEN_PHRASES:
        if phrase.lower() in policy_surface.lower():
            errors.append(f"removed or tool-exclusive workflow concept present: {phrase}")

    require_snippets(
        "defaults-check workflow",
        workflow,
        (
            "name: Organization defaults check",
            "pull_request:",
            "workflow_dispatch:",
            "permissions:\n  contents: read",
            "cancel-in-progress: true",
            f"uses: actions/checkout@{CHECKOUT_PIN} # v6.0.2",
            f"uses: actions/setup-python@{SETUP_PYTHON_PIN} # v6.2.0",
            "python -m py_compile scripts/validate_defaults.py",
            "python scripts/validate_defaults.py",
        ),
        errors,
    )

    try:
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        errors.append(f"workflow template metadata cannot be read: {exc}")
        metadata = {}
    if metadata.get("name") != "Bjs Repository Contract":
        errors.append("workflow template metadata has incorrect name")
    description = metadata.get("description")
    if not isinstance(description, str) or not description.strip():
        errors.append("workflow template metadata requires description")
    icon_name = metadata.get("iconName")
    if not isinstance(icon_name, str) or not icon_name.startswith("octicon "):
        errors.append("workflow template metadata requires an Octicon iconName")
    categories = metadata.get("categories")
    if not isinstance(categories, list) or "Continuous integration" not in categories:
        errors.append("workflow template metadata requires Continuous integration category")

    if errors:
        print("Organization defaults validation failed:", file=sys.stderr)
        for error in sorted(set(errors)):
            print(f"- {error}", file=sys.stderr)
        return 1

    print(
        "Organization defaults validation passed: pull-request-only CI, concise validation-gate PRs, "
        "repository integrity checks, and no work-branch or duplicate post-merge validation triggers."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

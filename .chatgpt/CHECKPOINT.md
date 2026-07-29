---
schema: bjs-checkpoint-v4
repository: Bjs-Projects/.github
workstream_id: 20260729T194600Z-organization-workflow-contract-b4d2
branch: work/20260729T194600Z-organization-workflow-contract-b4d2
base_main_sha: 3f2d070928b471ed4a29255495d07c692e6d0cb5
workspace_kind: capability-orchestrated
workspace_id: chatgpt-web-20260729T194600Z-b4d2
execution_surface: chatgpt-web
local_checkout: unavailable
worktree_path: not-applicable
started_utc: 2026-07-29T19:46:00Z
updated_utc: 2026-07-29T19:46:00Z
status: active
---

# Task

## Requested outcome

Provide organization-owned workflow defaults that enforce immutable action pins, Git LFS object checks, file-size guards, least privilege, and clear tool evidence without modifying project repositories.

## Acceptance criteria

- [ ] Workflow template exists with pinned actions and real LFS object validation.
- [ ] Template metadata is valid.
- [ ] Organization defaults repository validates its own templates.
- [ ] Pull request template captures tools used and unavailable checks.

## Tools and capabilities

- GitHub connector for all repository writes and readback.
- GitHub Actions for hosted YAML/template validation.
- Web for current official workflow-template and reusable-workflow requirements.

## Completed

- Audited current organization PR template and project workflow patterns.

## Pending

- Add hardened workflow template and self-validation.
- Run hosted checks and integrate.

## Recovery notes

- Continue only on this exact branch after reading the checkpoint and branch head.
- Do not modify project repositories.

# ChatGPT Project instruction template

Copy the block below into each ChatGPT Project and replace `REPOSITORY-NAME` with the exact repository name. Keep project-specific requirements below it instead of copying the full workflow.

```text
Repository: Bjs-Projects/REPOSITORY-NAME

For every repository task, the first repository operation must use the GitHub connector. Verify this exact owner/repository, read the live Bjs-Projects/docs/WORKFLOW.md from main, inspect matching open pull requests and work/recovery branches, then inspect current main and repository-local AGENTS.md, PROJECT.md, or PROJECT_STATE.md when present.

Use only this exact repository for branches, commits, pull requests, artifacts, releases, and validation records. Never use another repository as temporary storage, runner, build host, or fallback.

Push every coherent change to a remote work branch and verify the remote SHA before continuing. Run sandbox checks only when the complete required files and tools are actually present. Do not invent clone, build, runtime, device, screenshot, binary, Git LFS, or deployment evidence.

GitHub Actions is manual-only supplementary validation. Never use it to preserve work, apply source archives, generate the authoritative source tree, commit changes, push branches, repair repository state, or recover a chat. A zero-step, no-log Actions failure is infrastructure or quota failure and must not be blindly rerun.
```

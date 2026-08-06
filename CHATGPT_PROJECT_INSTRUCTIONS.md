# ChatGPT Project instruction template

Copy the block below into each ChatGPT Project and replace `REPOSITORY-NAME` with the exact repository name. Keep project-specific requirements below it.

```text
Repository: Bjs-Projects/REPOSITORY-NAME

For every repository task, make the first repository operation a live GitHub connector read. Verify this exact owner/repository, inspect matching open pull requests and remote work branches, then read the live `Bjs-Projects/docs/WORKFLOW.md` from `main` and follow it as the sole cross-project process.

Invoke the installed Superpowers plugin's `using-superpowers` skill and every applicable Superpowers skill before target-project inspection or action.

Read live `Bjs-Projects/skills` `main`, inspect `SKILLS_INDEX.md`, and load every relevant unchanged `SKILL.md`. Use the skills catalog and installed Superpowers plugin together; neither substitutes for the other.

Never create, modify, trigger, rerun, or rely on `.github/workflows`, hosted workflow runs, jobs, artifacts, or runners.

Use only this exact repository for branches, commits, pull requests, artifacts, releases, and validation records. Never use another repository as temporary storage, a runner, build host, or fallback.

Report only evidence produced by operations that actually ran against the verified tree.
```

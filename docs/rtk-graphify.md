# RTK + Graphify

RTK and Graphify are token-usage tools. They help Codex spend context on decisions instead of noise.

## The Problem

Large repositories create expensive context in three common ways:

- raw `git diff` or `find` output is too long
- Codex repeatedly searches the same files
- architecture questions start with broad, unfocused scanning

## RTK

RTK summarizes shell output into a compact form.

Use:

```bash
rtk git status
rtk git diff
rtk grep "pattern"
rtk find . -type f
rtk pytest
```

Avoid documenting commands RTK does not support on your installed version. Check with:

```bash
rtk --help
```

## Graphify

Graphify generates repository artifacts:

```bash
graphify .
graphify update .
```

The most important file for Codex is:

```text
graphify-out/GRAPH_REPORT.md
```

Ask Codex to use it like this:

```text
Before scanning broadly, read graphify-out/GRAPH_REPORT.md.
Use it to identify the relevant files, then inspect those files directly.
```

## When to Use Each

| Situation | Tool |
| --- | --- |
| What changed? | `rtk git diff` |
| What files exist? | `rtk find` |
| Where is a symbol mentioned? | `rtk grep` |
| How is the repo structured? | Graphify |
| What modules are related? | Graphify, then direct reads |
| Why did a test fail? | `rtk pytest`, then raw logs if needed |

## Graphify Caveat for This Repo

This repo vendors RTK and Graphify under `vendor/`. Graph reports may be dominated by vendored implementation details. For this harness, verify important claims against:

- `README.md`
- `scripts/harness.py`
- `scripts/*.sh`
- `docs/`
- `templates/`

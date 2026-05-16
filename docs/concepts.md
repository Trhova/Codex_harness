# Concepts

## What Codex Is

Codex is OpenAI's coding agent. In practice, that means you can give it a software task and let it inspect a project, explain code, edit files, run commands, review diffs, and help verify the result.

Think of Codex as a junior-to-senior pair programmer whose usefulness depends on the context you give it. It can move quickly, but it still needs clear goals, boundaries, and verification steps.

Good beginner tasks:

- "Explain how this repository is organized."
- "Find where this feature is implemented."
- "Update this documentation page for beginners."
- "Fix this failing test and explain the change."
- "Review this diff for bugs and missing tests."

Less good first tasks:

- "Rewrite the whole app."
- "Make this production ready."
- "Fix everything."
- "Deploy this using my credentials."

## Ways to Use Codex

Codex has several surfaces. Use the one that matches where the work should happen.

| Surface | Use it when | Beginner mental model |
| --- | --- | --- |
| Codex CLI | You want Codex working in a terminal on local files. | "Pair with Codex in this folder." |
| Codex app | You want a desktop command center with threads, review, worktrees, and project actions. | "Manage several Codex tasks from one app." |
| Codex cloud/web | You want Codex to work in a cloud environment, often from a connected GitHub repo. | "Delegate a repo task and review the resulting change." |
| IDE extension | You want Codex close to the editor while you code. | "Ask Codex while looking at files." |

For the CLI, a normal session starts like this:

```bash
cd /path/to/project
codex
```

Then describe the goal, constraints, and checks:

```text
Update docs/concepts.md so beginners understand Codex.
Keep the change documentation-only.
Use official OpenAI docs language where possible.
Run git diff --check when done.
```

For app or cloud work, write the same kind of task, but assume Codex may work in a separate thread or environment. Mention the repository, branch, setup commands, files to avoid, and how you want the result reviewed.

## The Beginner Loop

Use this loop until it becomes natural:

1. Ask Codex to inspect first.
2. Ask for a short plan when the task is non-trivial.
3. Let Codex edit only the files needed.
4. Ask Codex to run the smallest useful checks.
5. Review the diff before committing or accepting changes.

Example:

```text
First inspect docs/README.md and docs/concepts.md.
Then update only those files so a new Codex user understands the main terms.
Do not change scripts or generated files.
After editing, run git diff --check and summarize the diff.
```

## AGENTS.md

`AGENTS.md` is Codex's project instruction file. It is where you write durable guidance that should apply every time Codex works in a repo.

Use it for:

- test commands
- formatting commands
- generated files to avoid
- repo-specific safety rules
- where architecture docs live
- how to use local tools such as RTK and Graphify

Codex can also read global guidance from your Codex home directory, usually `~/.codex/AGENTS.md`. Project instructions should be more specific than global preferences.

Good `AGENTS.md` guidance is short and concrete:

```markdown
## Commands

Run `npm test` after changing application code.
Run `npm run lint` before summarizing a completed change.

## Safety

Do not edit generated files under dist/.
Do not commit unless the user explicitly asks.
```

Avoid vague guidance:

```markdown
Be careful.
Make everything high quality.
Use best practices.
```

## Skills

Skills are reusable task instructions for Codex. A skill usually lives in a directory with a `SKILL.md` file, and may include helper scripts, references, or templates.

Use a skill when you repeat a workflow often, such as:

- polishing a slide deck
- following a release checklist
- using company-specific docs
- applying a standard code review process

Beginner mental model: `AGENTS.md` tells Codex how to behave in this repo; a skill teaches Codex a repeatable workflow it can load when needed.

## MCP

MCP means Model Context Protocol. It is a standard way to connect Codex to extra tools and context.

Examples:

- an MCP server for official OpenAI docs
- an MCP server for browser automation
- an MCP server for Figma
- an MCP server for internal documentation

MCP does not automatically mean "safe" or "read-only." Treat every connected tool like a capability you are handing to Codex. Prefer read-only servers when learning, and pay attention to approval prompts before tools can mutate external systems.

## Plugins

Plugins package reusable Codex capabilities. A plugin can bundle skills, app integrations, and MCP server configuration.

Use plugins when you want Codex to work with a larger tool or workflow, such as GitHub, Slack, Gmail, Google Drive, or a custom team workflow.

Beginner mental model: a skill is the recipe; MCP is a tool connection; a plugin can bundle recipes and connections so they are easier to install and reuse.

## Subagents

Subagents are extra Codex agents that can work in parallel and report back to the main thread. They are useful when the work can be split into independent pieces.

Good subagent tasks:

- one agent reviews security risks
- one agent checks test coverage
- one agent investigates docs
- one agent reads logs while the main agent edits

Be cautious with parallel editing. Multiple agents changing the same files can create conflicts and make review harder. For beginners, use subagents mostly for read-heavy investigation and review.

Example prompt:

```text
Use parallel subagents for review only.
Spawn one agent for correctness, one for missing tests, and one for documentation clarity.
Wait for all results, then summarize findings with file references.
Do not let subagents edit files.
```

## Sandboxing and Approvals

Sandboxing and approvals are Codex safety controls.

The sandbox is the technical boundary. It limits what Codex-run commands can access, such as which files they can write or whether they can use the network.

Approvals are the human checkpoint. If Codex wants to do something outside the current permission boundary, it may ask before continuing.

Beginner rules:

- Start with the default permissions.
- Read approval prompts before accepting them.
- Be more careful in unfamiliar repos.
- Avoid full-access modes until you understand the tradeoff.
- Do not give Codex secrets unless the task truly requires them.

If a command fails because of sandboxing, that is not always bad. It usually means Codex reached a boundary and needs you to decide whether the action is appropriate.

## What This Harness Adds

Codex Harness installs local support around Codex:

- RTK for compact command output.
- Graphify for repository structure reports.
- Codex instructions so future sessions know when to use those tools.
- Rollback tracking for files changed by the harness.

The harness does not replace Codex. It gives Codex better local habits for repository understanding and command output.

## What RTK Is

RTK is a command wrapper. It is useful when a raw command would produce too much output or output that is hard for Codex to scan.

Use RTK for commands such as:

```bash
rtk git status
rtk git diff
rtk grep "search term"
rtk find . -type f
rtk pytest
```

RTK does not replace every shell command. For tiny commands, raw shell output is fine.

## What Graphify Is

Graphify builds repository artifacts under `graphify-out/`, especially `GRAPH_REPORT.md`. That report gives Codex a structured starting point for architecture, ownership, communities, and important files.

Use Graphify before broad questions such as:

- Where is this feature implemented?
- What modules are related?
- What should a new contributor read first?
- Which files are likely affected by this change?

## Official References

OpenAI's Codex docs change over time, so use these as the source of truth for exact current behavior:

- [Codex CLI](https://developers.openai.com/codex/cli)
- [Codex app](https://developers.openai.com/codex/app)
- [Codex web/cloud](https://developers.openai.com/codex/cloud)
- [AGENTS.md](https://developers.openai.com/codex/guides/agents-md)
- [Skills](https://developers.openai.com/codex/skills)
- [MCP](https://developers.openai.com/codex/mcp)
- [Plugins](https://developers.openai.com/codex/plugins)
- [Subagents](https://developers.openai.com/codex/subagents)
- [Sandboxing](https://developers.openai.com/codex/concepts/sandboxing)
- [Agent approvals and security](https://developers.openai.com/codex/agent-approvals-security)

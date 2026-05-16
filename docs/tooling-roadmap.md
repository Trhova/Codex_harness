# Tooling Roadmap

This page tracks tools that could complement RTK and Graphify. The default harness should stay small, reversible, and beginner-friendly; these are candidates for optional recipes or experiments.

## Best Next Candidates

| Priority | Tool | Category | Why it is interesting | Harness fit |
| --- | --- | --- | --- | --- |
| P0 | [Serena](https://oraios.github.io/serena/01-about/020_programming-languages.html) | MCP/LSP semantic code tools | Gives agents symbol lookup, reference search, and targeted code navigation through language servers. | Prototype as an optional MCP integration for repos where language-server setup is reliable. |
| P0 | [ast-grep](https://ast-grep.github.io/) | Structural search/rewrite | Searches code by syntax instead of plain text, which can reduce noisy grep output and make codemods safer. | Add an optional recipe and examples such as `ast-grep -p 'console.log($$$)'`. |
| P1 | [Codebase-Memory MCP](https://github.com/DeusData/codebase-memory-mcp) | Persistent code knowledge graph | Builds a local tree-sitter knowledge graph exposed through MCP. | Benchmark against Graphify before adopting; likely experimental first. |
| P1 | [Repomix](https://repomix.com/) | AI context packaging | Packs repository contents into AI-friendly bundles with filtering and token counts. | Useful for portable handoff to cloud/app workflows, but should not encourage dumping huge repos into context. |
| P1 | [Zoekt](https://github.com/sourcegraph/zoekt) | Indexed code search | Fast indexed source search for large repositories or many repositories. | Useful for advanced large-codebase setups, not needed for small repos. |
| P1 | [Universal Ctags](https://ctags.io/) | Lightweight symbol indexing | Generates symbol indexes for many languages. | Possible Graphify fallback/enrichment path, but less semantic than LSP-based tools. |
| P1 | [mise](https://mise.jdx.dev/) | Tool/version manager | Pins developer tools and task commands per project. | Good candidate if the harness needs reproducible versions without requiring Nix. |
| P2 | [OpenGrep](https://www.opengrep.dev/) | Static pattern/security analysis | Runs Semgrep-style static rules with machine-readable output. | Advanced security/code-smell recipe, not a default token-efficiency tool. |

## Not Default For Now

| Tool | Why it is useful | Why it is not a default harness dependency |
| --- | --- | --- |
| [Aider repo-map](https://aider.chat/docs/repomap.html) | Proven tree-sitter/PageRank-style context strategy. | Aider is another coding agent; this harness should learn from the idea without installing a parallel agent by default. |
| [Sourcegraph Code Search](https://sourcegraph.com/docs/code-search/features) | Excellent organization-scale code search. | Too heavy for a local beginner harness; Zoekt captures the lighter local search core. |
| [OpenGrok](https://github.com/oracle/opengrok) | Mature source browser and cross-reference system. | Server-heavy and optimized for human browsing more than Codex context management. |
| [CodeQL](https://codeql.github.com/docs/codeql-overview/about-codeql/) | Powerful semantic/security analysis. | Valuable for security workflows, but too specialized for default Codex onboarding. |
| [Kythe](https://kythe.io/docs/kythe-overview.html) / [SCIP](https://sourcegraph.com/docs/code-search/code-navigation/writing_an_indexer) | Serious code-intelligence formats. | Too much indexing and build-system complexity for this repo's current goals. |
| [Nix flakes](https://nix.dev/concepts/flakes.html) / [Devbox](https://github.com/jetify-com/devbox) | Reproducible development environments. | Powerful, but higher conceptual overhead than `mise` for the target beginner audience. |

## Suggested Experiments

1. Prototype Serena on one Python repo and one JavaScript repo. Measure whether Codex opens fewer raw files when symbol lookup is available.
2. Add an ast-grep recipe page with safe search-only examples before documenting rewrite examples.
3. Compare Graphify, Codebase-Memory MCP, and Repomix on the same context-size fixtures in `experiments/context_size/`.
4. Test `mise` as an optional reproducible installer for RTK, Graphify, ast-grep, and future tools.

## Decision Rule

Add a tool only if it passes all three checks:

1. It reduces context noise or setup friction in a way beginners can understand.
2. It can be installed or activated reversibly.
3. It does not duplicate Codex itself or make the default workflow harder to explain.

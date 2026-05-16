# Context Size Experiment

This experiment measures whether a Codex Harness workflow using RTK-style command summaries and Graphify-style repo maps reduces token-relevant context/output size versus baseline raw commands and broad file scans.

The measurement is intentionally simple and reproducible. It does not use private Codex telemetry. Instead it counts transcript tokens with [`tiktoken`](https://github.com/openai/tiktoken) using the `o200k_base` tokenizer.

This is stronger than a character-count heuristic because it uses a real tokenizer. It still should not be presented as Codex billing telemetry: Codex may add hidden system/tool context, may cache context, and may choose a different internal tokenizer/model path.

## Current Results

The current suite has 14 fixtures created across frontend/3D, backend/data, ops/HPC, docs-heavy, and original smoke-test scenarios. It measures transcript tokens, not private Codex telemetry.

Summary:

- Total baseline transcript tokens: 27,541
- Total harness-style transcript tokens: 10,254
- Overall measured reduction: 62.8%
- Pooled family reduction range: 26.5% to 74.8%
- Individual replicate reduction range: 23.6% to 78.5%

![Context reduction by fixture family](results/context_reduction_by_family.svg)

The full per-scenario data is in [summary.csv](results/summary.csv). Family-level rollups are in [family_summary.csv](results/family_summary.csv).

The chart labels use pooled family reduction: `1 - sum(harness_tokens) / sum(baseline_tokens)` for all fixtures in that family. This is not the same as the arithmetic mean of replicate percentages, because larger fixtures contribute proportionally more to the pooled number.

## Scenarios

The fixtures under `scenarios/` are small local codebases. The current design uses replicated scenario families:

| Family | Replicates | Purpose |
| --- | --- |
| Frontend / 3D | 3 | UI-heavy codebases, including a richer 3D city operations dashboard. |
| Backend / data | 3 | APIs, auth/session logic, and ETL/data-processing code. |
| Ops / HPC | 3 | Batch jobs, CI/deploy workflows, quota recovery, logs, and runbooks. |
| Docs-heavy | 2 | Documentation-dominant repos where less raw code can be compressed. |
| Original smoke fixtures | 3 | Earlier Python service, HPC jobs, and simple 3D city scenarios. |

Each scenario has enough structure to make broad raw scans noisy while still being small enough to audit.

Each new replicate has a `scenario.json` file with the search pattern used by the experiment. That makes the retrieval task explicit instead of relying on hidden choices in the runner.

## What Is Compared

Baseline transcript:

- raw recursive file list
- broad search output
- full contents of all text files, as a stand-in for broad context gathering

Harness-style transcript:

- RTK-style file summary with directory and extension counts
- Graphify-style structural report with communities, symbols, imports, and likely entry points
- compact search hits with a small per-file cap

The harness-style transcript is generated locally by `run_experiment.py`; it does not invoke the actual Graphify extractor. This keeps the experiment deterministic and fast, but it means the result evaluates the workflow shape rather than Graphify extraction quality.

## Reproduce

From the repository root:

```bash
python3 -m pip install -r experiments/context_size/requirements.txt
python3 experiments/context_size/run_experiment.py
```

Outputs are written to `experiments/context_size/results/`:

- `summary.csv`
- `summary.json`
- `family_summary.csv`
- `context_reduction_by_family.svg`
- `context_reduction_by_family.png` if `matplotlib` is installed
- `transcripts/*.txt`

## What "Measured Tokens" Means

These are real tokenizer counts over generated transcript files:

- tokenizer library: `tiktoken`
- tokenizer encoding: `o200k_base`
- counted inputs: `results/transcripts/*.baseline.txt` and `results/transcripts/*.harness.txt`

This is more solid than a character-count proxy. It is still not identical to real Codex usage because Codex may add hidden system/tool context, cache context, summarize earlier turns, or decide to inspect different files.

## Limitations

- The token count is real for the generated transcripts and the `o200k_base` tokenizer, but it is not private Codex usage telemetry.
- The experiment measures context/output size, not task accuracy or elapsed time.
- The harness-style Graphify report is a deterministic approximation over these fixtures.
- Actual savings in Codex depend on agent behavior, task wording, repository size, and when raw logs are still needed.

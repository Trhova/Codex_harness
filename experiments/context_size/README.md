# Context Size Experiment

This experiment measures whether a Codex Harness workflow using RTK-style command summaries and Graphify-style repo maps reduces token-relevant context/output size versus baseline raw commands and broad file scans.

The measurement is intentionally simple and reproducible. It does not use private Codex telemetry. Instead it estimates tokens with:

```text
estimated_tokens = ceil(character_count / 4)
```

That proxy is useful for comparing transcript sizes, but it is not a tokenizer and should not be read as billable token usage.

## Scenarios

The fixtures under `scenarios/` are small local codebases:

| Scenario | Purpose |
| --- | --- |
| `python_service` | API/service layout with tests and docs. |
| `hpc_jobs` | Shell-oriented HPC job scripts and cluster docs. |
| `three_d_city` | Small Three.js-style city scene with buildings, traffic, and controls. |

Each scenario has enough structure to make broad raw scans noisy while still being small enough to audit.

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
python3 experiments/context_size/run_experiment.py
```

Outputs are written to `experiments/context_size/results/`:

- `summary.csv`
- `summary.json`
- `token_proxy_bar.svg`
- `token_proxy_bar.png` if `matplotlib` is installed
- `transcripts/*.txt`

## Limitations

- The token proxy is approximate and ignores model-specific tokenization.
- The experiment measures context/output size, not task accuracy or elapsed time.
- The harness-style Graphify report is a deterministic approximation over these fixtures.
- Actual savings in Codex depend on agent behavior, task wording, repository size, and when raw logs are still needed.

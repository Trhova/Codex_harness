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
- Median per-fixture reduction: 57.3%
- Reduction range: 23.6% to 78.5%

| Scenario | Without harness | With harness | Reduction |
| --- | ---: | ---: | ---: |
| `backend_replicates__billing_api` | 2,288 | 810 | 64.6% fewer |
| `backend_replicates__session_gateway` | 1,705 | 748 | 56.1% fewer |
| `backend_replicates__warehouse_etl` | 1,886 | 784 | 58.4% fewer |
| `docs_replicates__onboarding_handbook` | 854 | 604 | 29.3% fewer |
| `docs_replicates__policy_process` | 792 | 605 | 23.6% fewer |
| `frontend_replicates__collab_canvas_board` | 3,298 | 863 | 73.8% fewer |
| `frontend_replicates__material_lab_configurator` | 2,578 | 757 | 70.6% fewer |
| `frontend_replicates__metro_ops_3d` | 3,904 | 840 | 78.5% fewer |
| `hpc_jobs` | 1,190 | 613 | 48.5% fewer |
| `ops_replicates__ci_deploy_rollout` | 1,436 | 667 | 53.6% fewer |
| `ops_replicates__hpc_batch_pipeline` | 2,603 | 967 | 62.9% fewer |
| `ops_replicates__storage_quota_recovery` | 1,327 | 605 | 54.4% fewer |
| `python_service` | 1,617 | 717 | 55.7% fewer |
| `three_d_city` | 2,063 | 674 | 67.3% fewer |

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
python3 -m pip install -r experiments/context_size/requirements.txt
python3 experiments/context_size/run_experiment.py
```

Outputs are written to `experiments/context_size/results/`:

- `summary.csv`
- `summary.json`
- `token_proxy_bar.svg`
- `token_proxy_bar.png` if `matplotlib` is installed
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

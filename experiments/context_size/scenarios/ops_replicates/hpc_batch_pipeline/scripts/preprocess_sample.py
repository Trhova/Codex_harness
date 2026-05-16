#!/usr/bin/env python3
"""Tiny placeholder used by the Slurm fixture."""

import argparse
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sample", required=True)
    parser.add_argument("--fastq", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--threads", required=True)
    args = parser.parse_args()

    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=True)
    (output / "features.parquet").write_text(
        f"sample={args.sample}\nfastq={args.fastq}\nthreads={args.threads}\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
from __future__ import annotations

import ast
import csv
import json
import math
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SCENARIOS = ROOT / "scenarios"
RESULTS = ROOT / "results"
TRANSCRIPTS = RESULTS / "transcripts"

TEXT_SUFFIXES = {".md", ".py", ".sh", ".js", ".json", ".html", ".css", ".txt", ".sbatch"}
SEARCH_PATTERNS = {
    "python_service": re.compile(r"route|handler|database|cache|test|config", re.I),
    "hpc_jobs": re.compile(r"sbatch|module|queue|gpu|memory|checkpoint|array", re.I),
    "three_d_city": re.compile(r"scene|camera|building|traffic|render|geometry|control", re.I),
}


@dataclass(frozen=True)
class TextFile:
    path: Path
    relpath: str
    text: str


def estimate_tokens(text: str) -> int:
    return math.ceil(len(text) / 4)


def scenario_dirs() -> list[Path]:
    return sorted(path for path in SCENARIOS.iterdir() if path.is_dir())


def read_text_files(scenario: Path) -> list[TextFile]:
    files: list[TextFile] = []
    for path in sorted(scenario.rglob("*")):
        if not path.is_file() or path.suffix not in TEXT_SUFFIXES:
            continue
        relpath = path.relative_to(scenario).as_posix()
        files.append(TextFile(path=path, relpath=relpath, text=path.read_text(encoding="utf-8")))
    return files


def baseline_transcript(scenario: Path, files: list[TextFile]) -> str:
    pattern = SEARCH_PATTERNS[scenario.name]
    lines: list[str] = [
        f"# Baseline raw transcript for {scenario.name}",
        "",
        "$ find . -type f",
    ]
    lines.extend(f"./{file.relpath}" for file in files)
    lines.extend(["", f"$ rg -n '{pattern.pattern}' ."])
    for file in files:
        for number, line in enumerate(file.text.splitlines(), start=1):
            if pattern.search(line):
                lines.append(f"{file.relpath}:{number}:{line}")
    lines.extend(["", "$ broad context scan: full text files"])
    for file in files:
        lines.extend([f"--- {file.relpath} ---", file.text.rstrip(), ""])
    return "\n".join(lines).rstrip() + "\n"


def python_symbols(text: str) -> list[str]:
    try:
        module = ast.parse(text)
    except SyntaxError:
        return []
    symbols: list[str] = []
    for node in ast.walk(module):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            symbols.append(node.name)
    return symbols


def regex_symbols(relpath: str, text: str) -> list[str]:
    if relpath.endswith(".py"):
        return python_symbols(text)
    if relpath.endswith(".js"):
        patterns = [
            r"\bfunction\s+([A-Za-z_][A-Za-z0-9_]*)",
            r"\bclass\s+([A-Za-z_][A-Za-z0-9_]*)",
            r"\b(?:const|let|var)\s+([A-Za-z_][A-Za-z0-9_]*)\s*=",
        ]
    elif relpath.endswith((".sh", ".sbatch")):
        patterns = [r"^([A-Za-z_][A-Za-z0-9_]*)\(\)"]
    else:
        patterns = [r"^#{1,3}\s+(.+)$"]
    found: list[str] = []
    for pattern in patterns:
        found.extend(re.findall(pattern, text, flags=re.MULTILINE))
    return found


def import_lines(file: TextFile) -> list[str]:
    imports: list[str] = []
    for line in file.text.splitlines():
        stripped = line.strip()
        if stripped.startswith(("import ", "from ", "source ", ". ")):
            imports.append(stripped)
    return imports[:5]


def community_for(relpath: str) -> str:
    first = relpath.split("/", 1)[0]
    if first in {"src", "app"}:
        return "runtime"
    if first in {"tests", "test"}:
        return "tests"
    if first in {"docs", "README.md"}:
        return "docs"
    if first in {"scripts", "jobs"}:
        return "automation"
    if first in {"public", "styles"}:
        return "frontend-assets"
    return first


def graphify_style_report(scenario: Path, files: list[TextFile]) -> str:
    communities: dict[str, list[TextFile]] = defaultdict(list)
    ext_counts = Counter(file.path.suffix or "none" for file in files)
    symbol_counts: list[tuple[str, list[str]]] = []
    imports_by_file: list[tuple[str, list[str]]] = []

    for file in files:
        communities[community_for(file.relpath)].append(file)
        symbols = regex_symbols(file.relpath, file.text)
        if symbols:
            symbol_counts.append((file.relpath, symbols[:8]))
        imports = import_lines(file)
        if imports:
            imports_by_file.append((file.relpath, imports))

    lines: list[str] = [
        f"# Graphify-style report for {scenario.name}",
        "",
        f"Files: {len(files)}",
        "Extensions: " + ", ".join(f"{ext}:{count}" for ext, count in sorted(ext_counts.items())),
        "",
        "## Communities",
    ]
    for name, grouped in sorted(communities.items()):
        preview = ", ".join(file.relpath for file in grouped[:5])
        lines.append(f"- {name}: {len(grouped)} files ({preview})")

    lines.extend(["", "## Key Symbols"])
    for relpath, symbols in symbol_counts[:12]:
        lines.append(f"- {relpath}: {', '.join(symbols)}")

    lines.extend(["", "## Imports and Entrypoints"])
    for relpath, imports in imports_by_file[:10]:
        lines.append(f"- {relpath}: {'; '.join(imports)}")

    lines.extend(["", "## Suggested Next Reads"])
    for file in files[:3]:
        lines.append(f"- {file.relpath}")
    return "\n".join(lines).rstrip() + "\n"


def rtk_style_summary(scenario: Path, files: list[TextFile]) -> str:
    pattern = SEARCH_PATTERNS[scenario.name]
    dirs = Counter(file.relpath.split("/", 1)[0] for file in files)
    exts = Counter(file.path.suffix or "none" for file in files)
    hits_by_file: dict[str, list[str]] = defaultdict(list)
    for file in files:
        for number, line in enumerate(file.text.splitlines(), start=1):
            if pattern.search(line) and len(hits_by_file[file.relpath]) < 3:
                hits_by_file[file.relpath].append(f"L{number}: {line.strip()[:120].rstrip()}")

    lines: list[str] = [
        f"# RTK-style summaries for {scenario.name}",
        "",
        "$ rtk find . -type f",
        "dirs: " + ", ".join(f"{name}/ {count}" for name, count in sorted(dirs.items())),
        "ext: " + ", ".join(f"{ext}({count})" for ext, count in sorted(exts.items())),
        "sample: " + ", ".join(file.relpath for file in files[:8]),
        "",
        f"$ rtk grep '{pattern.pattern}' .",
    ]
    for relpath, hits in sorted(hits_by_file.items()):
        lines.append(f"{relpath}: {len(hits)} shown")
        lines.extend(f"  {hit}" for hit in hits)
    return "\n".join(lines).rstrip() + "\n"


def harness_transcript(scenario: Path, files: list[TextFile]) -> str:
    return rtk_style_summary(scenario, files) + "\n" + graphify_style_report(scenario, files)


def write_svg(rows: list[dict[str, object]], path: Path) -> None:
    width = 920
    height = 360
    margin_left = 130
    margin_bottom = 70
    plot_width = width - margin_left - 40
    plot_height = height - 80 - margin_bottom
    max_value = max(max(int(row["baseline_tokens"]), int(row["harness_tokens"])) for row in rows)
    group_width = plot_width / len(rows)
    bar_width = 34

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="#ffffff"/>',
        '<text x="24" y="34" font-family="Arial, sans-serif" font-size="20" font-weight="700">Token proxy by workflow</text>',
        '<text x="24" y="58" font-family="Arial, sans-serif" font-size="12" fill="#555">estimated tokens = ceil(characters / 4)</text>',
        f'<line x1="{margin_left}" y1="{height - margin_bottom}" x2="{width - 40}" y2="{height - margin_bottom}" stroke="#333"/>',
        f'<line x1="{margin_left}" y1="80" x2="{margin_left}" y2="{height - margin_bottom}" stroke="#333"/>',
    ]
    for i in range(5):
        value = round(max_value * i / 4)
        y = height - margin_bottom - (value / max_value * plot_height if max_value else 0)
        parts.append(f'<line x1="{margin_left}" y1="{y:.1f}" x2="{width - 40}" y2="{y:.1f}" stroke="#e6e6e6"/>')
        parts.append(f'<text x="{margin_left - 12}" y="{y + 4:.1f}" text-anchor="end" font-family="Arial, sans-serif" font-size="11" fill="#555">{value}</text>')

    for index, row in enumerate(rows):
        base = int(row["baseline_tokens"])
        harness = int(row["harness_tokens"])
        center = margin_left + group_width * index + group_width / 2
        for offset, value, color in [(-bar_width / 2 - 3, base, "#4c78a8"), (bar_width / 2 + 3, harness, "#f58518")]:
            bar_height = value / max_value * plot_height if max_value else 0
            x = center + offset - bar_width / 2
            y = height - margin_bottom - bar_height
            parts.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{bar_width}" height="{bar_height:.1f}" fill="{color}"/>')
            parts.append(f'<text x="{x + bar_width / 2:.1f}" y="{y - 5:.1f}" text-anchor="middle" font-family="Arial, sans-serif" font-size="11">{value}</text>')
        label = str(row["scenario"]).replace("_", " ")
        parts.append(f'<text x="{center:.1f}" y="{height - 42}" text-anchor="middle" font-family="Arial, sans-serif" font-size="12">{label}</text>')

    parts.extend([
        '<rect x="700" y="24" width="14" height="14" fill="#4c78a8"/>',
        '<text x="720" y="36" font-family="Arial, sans-serif" font-size="12">without harness</text>',
        '<rect x="700" y="44" width="14" height="14" fill="#f58518"/>',
        '<text x="720" y="56" font-family="Arial, sans-serif" font-size="12">with harness</text>',
        "</svg>",
    ])
    path.write_text("\n".join(parts) + "\n", encoding="utf-8")


def write_png_if_possible(rows: list[dict[str, object]], path: Path) -> bool:
    try:
        import matplotlib.pyplot as plt
    except Exception:
        return False

    labels = [str(row["scenario"]).replace("_", " ") for row in rows]
    baseline = [int(row["baseline_tokens"]) for row in rows]
    harness = [int(row["harness_tokens"]) for row in rows]
    positions = range(len(rows))
    width = 0.36

    fig, ax = plt.subplots(figsize=(8.5, 4.2))
    ax.bar([pos - width / 2 for pos in positions], baseline, width, label="without harness", color="#4c78a8")
    ax.bar([pos + width / 2 for pos in positions], harness, width, label="with harness", color="#f58518")
    ax.set_title("Token proxy by workflow")
    ax.set_ylabel("estimated tokens")
    ax.set_xticks(list(positions), labels)
    ax.legend()
    ax.text(0.01, -0.18, "estimated tokens = ceil(characters / 4)", transform=ax.transAxes, fontsize=9)
    fig.tight_layout()
    fig.savefig(path, dpi=160)
    plt.close(fig)
    return True


def run() -> list[dict[str, object]]:
    RESULTS.mkdir(parents=True, exist_ok=True)
    TRANSCRIPTS.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, object]] = []

    for scenario in scenario_dirs():
        files = read_text_files(scenario)
        baseline = baseline_transcript(scenario, files)
        harness = harness_transcript(scenario, files)
        (TRANSCRIPTS / f"{scenario.name}.baseline.txt").write_text(baseline, encoding="utf-8")
        (TRANSCRIPTS / f"{scenario.name}.harness.txt").write_text(harness, encoding="utf-8")

        baseline_tokens = estimate_tokens(baseline)
        harness_tokens = estimate_tokens(harness)
        rows.append(
            {
                "scenario": scenario.name,
                "files": len(files),
                "baseline_chars": len(baseline),
                "harness_chars": len(harness),
                "baseline_tokens": baseline_tokens,
                "harness_tokens": harness_tokens,
                "token_delta": harness_tokens - baseline_tokens,
                "token_delta_percent": round((harness_tokens - baseline_tokens) / baseline_tokens * 100, 1),
            }
        )

    with (RESULTS / "summary.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    (RESULTS / "summary.json").write_text(json.dumps(rows, indent=2) + "\n", encoding="utf-8")
    write_svg(rows, RESULTS / "token_proxy_bar.svg")
    write_png_if_possible(rows, RESULTS / "token_proxy_bar.png")
    return rows


def main() -> None:
    rows = run()
    print("scenario,baseline_tokens,harness_tokens,token_delta_percent")
    for row in rows:
        print(f"{row['scenario']},{row['baseline_tokens']},{row['harness_tokens']},{row['token_delta_percent']}")
    print(f"\nWrote results to {RESULTS.relative_to(Path.cwd())}")


if __name__ == "__main__":
    main()

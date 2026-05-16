#!/usr/bin/env python3
from __future__ import annotations

import ast
import csv
import json
import re
import statistics
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SCENARIOS = ROOT / "scenarios"
RESULTS = ROOT / "results"
TRANSCRIPTS = RESULTS / "transcripts"

TEXT_SUFFIXES = {".md", ".py", ".sh", ".js", ".json", ".html", ".css", ".txt", ".sbatch"}
DEFAULT_SEARCH_PATTERNS = {
    "python_service": "route|handler|database|cache|test|config",
    "hpc_jobs": "sbatch|module|queue|gpu|memory|checkpoint|array",
    "three_d_city": "scene|camera|building|traffic|render|geometry|control",
}
TOKENIZER = "o200k_base"
FAMILY_ORDER = [
    "Frontend / 3D",
    "Backend / data",
    "Ops / HPC",
    "Docs-heavy",
    "Original smoke fixtures",
]
FAMILY_COLORS = {
    "Frontend / 3D": "#2563eb",
    "Backend / data": "#059669",
    "Ops / HPC": "#d97706",
    "Docs-heavy": "#7c3aed",
    "Original smoke fixtures": "#475569",
}


@dataclass(frozen=True)
class TextFile:
    path: Path
    relpath: str
    text: str


def count_tokens(text: str) -> int:
    try:
        import tiktoken
    except ImportError as exc:
        raise SystemExit(
            "This experiment requires tiktoken for real tokenizer counts. "
            "Install it with: python3 -m pip install tiktoken"
        ) from exc

    encoding = tiktoken.get_encoding(TOKENIZER)
    return len(encoding.encode(text))


def scenario_dirs() -> list[Path]:
    scenarios: list[Path] = []
    for path in sorted([SCENARIOS / name for name in DEFAULT_SEARCH_PATTERNS] + list(SCENARIOS.rglob("scenario.json"))):
        if path.name == "scenario.json":
            path = path.parent
        if not path.is_dir():
            continue
        if path not in scenarios and read_text_files(path):
            scenarios.append(path)
    return scenarios


def scenario_id(scenario: Path) -> str:
    return scenario.relative_to(SCENARIOS).as_posix().replace("/", "__")


def scenario_family(name: str) -> str:
    if name.startswith("frontend_replicates__"):
        return "Frontend / 3D"
    if name.startswith("backend_replicates__"):
        return "Backend / data"
    if name.startswith("ops_replicates__"):
        return "Ops / HPC"
    if name.startswith("docs_replicates__"):
        return "Docs-heavy"
    return "Original smoke fixtures"


def scenario_label(name: str) -> str:
    label = name
    for prefix in (
        "frontend_replicates__",
        "backend_replicates__",
        "ops_replicates__",
        "docs_replicates__",
    ):
        if label.startswith(prefix):
            label = label.removeprefix(prefix)
            break
    return label.replace("_", " ")


def scenario_pattern(scenario: Path) -> re.Pattern[str]:
    metadata_path = scenario / "scenario.json"
    if metadata_path.exists():
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        pattern = metadata.get("search_pattern")
        if not pattern:
            raise ValueError(f"{metadata_path} must define search_pattern")
        return re.compile(pattern, re.I)

    pattern = DEFAULT_SEARCH_PATTERNS.get(scenario.name)
    if not pattern:
        raise ValueError(
            f"{scenario} must include scenario.json with a search_pattern "
            "so replicate measurements are explicit"
        )
    return re.compile(pattern, re.I)


def read_text_files(scenario: Path) -> list[TextFile]:
    files: list[TextFile] = []
    for path in sorted(scenario.rglob("*")):
        if not path.is_file() or path.suffix not in TEXT_SUFFIXES:
            continue
        relpath = path.relative_to(scenario).as_posix()
        files.append(TextFile(path=path, relpath=relpath, text=path.read_text(encoding="utf-8")))
    return files


def baseline_transcript(scenario: Path, files: list[TextFile]) -> str:
    pattern = scenario_pattern(scenario)
    lines: list[str] = [
        f"# Baseline raw transcript for {scenario_id(scenario)}",
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
        f"# Graphify-style report for {scenario_id(scenario)}",
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
    pattern = scenario_pattern(scenario)
    dirs = Counter(file.relpath.split("/", 1)[0] for file in files)
    exts = Counter(file.path.suffix or "none" for file in files)
    hits_by_file: dict[str, list[str]] = defaultdict(list)
    for file in files:
        for number, line in enumerate(file.text.splitlines(), start=1):
            if pattern.search(line) and len(hits_by_file[file.relpath]) < 3:
                hits_by_file[file.relpath].append(f"L{number}: {line.strip()[:120].rstrip()}")

    lines: list[str] = [
        f"# RTK-style summaries for {scenario_id(scenario)}",
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


def family_summaries(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    summaries: list[dict[str, object]] = []
    for family in FAMILY_ORDER:
        grouped = [row for row in rows if row["family"] == family]
        if not grouped:
            continue
        baseline = sum(int(row["baseline_tokens"]) for row in grouped)
        harness = sum(int(row["harness_tokens"]) for row in grouped)
        reductions = [-float(row["token_delta_percent"]) for row in grouped]
        summaries.append(
            {
                "family": family,
                "replicates": len(grouped),
                "baseline_tokens": baseline,
                "harness_tokens": harness,
                "overall_reduction_percent": round((1 - harness / baseline) * 100, 1),
                "median_reduction_percent": round(statistics.median(reductions), 1),
                "min_reduction_percent": round(min(reductions), 1),
                "max_reduction_percent": round(max(reductions), 1),
            }
        )
    return summaries


def write_family_summary(rows: list[dict[str, object]], path: Path) -> None:
    summaries = family_summaries(rows)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(summaries[0].keys()), lineterminator="\n")
        writer.writeheader()
        writer.writerows(summaries)


def write_reduction_svg(rows: list[dict[str, object]], path: Path) -> None:
    width = 1120
    row_height = 72
    header_height = 128
    footer_height = 112
    height = header_height + row_height * len(FAMILY_ORDER) + footer_height
    label_x = 230
    plot_x = 255
    plot_width = 700
    max_percent = 85
    total_baseline = sum(int(row["baseline_tokens"]) for row in rows)
    total_harness = sum(int(row["harness_tokens"]) for row in rows)
    overall = (1 - total_harness / total_baseline) * 100
    replicate_count = len(rows)
    summaries = {summary["family"]: summary for summary in family_summaries(rows)}
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" rx="0" fill="#f8fafc"/>',
        '<text x="28" y="38" font-family="Arial, sans-serif" font-size="24" font-weight="700" fill="#0f172a">Measured context reduction by fixture family</text>',
        f'<text x="28" y="66" font-family="Arial, sans-serif" font-size="13" fill="#475569">{replicate_count} fixture repositories. Dots are individual replicates; thick bars show each family range; vertical ticks show pooled family reductions. Tokenizer={TOKENIZER}.</text>',
        f'<text x="28" y="106" font-family="Arial, sans-serif" font-size="26" font-weight="700" fill="#0f172a">{overall:.1f}%</text>',
        '<text x="128" y="106" font-family="Arial, sans-serif" font-size="13" fill="#475569">overall fewer transcript tokens</text>',
    ]
    axis_label_y = height - footer_height + 34
    legend_y = height - 54
    note_y = height - 24
    for tick in range(0, 81, 20):
        x = plot_x + (tick / max_percent) * plot_width
        parts.append(f'<line x1="{x:.1f}" y1="{header_height - 12}" x2="{x:.1f}" y2="{height - footer_height}" stroke="#e2e8f0"/>')
        parts.append(f'<text x="{x:.1f}" y="{axis_label_y}" text-anchor="middle" font-family="Arial, sans-serif" font-size="11" fill="#64748b">{tick}%</text>')

    for index, family in enumerate(FAMILY_ORDER):
        grouped = sorted([row for row in rows if row["family"] == family], key=lambda row: float(row["reduction_percent"]))
        if not grouped:
            continue
        summary = summaries[family]
        color = FAMILY_COLORS[family]
        y = header_height + index * row_height
        center_y = y + 34
        min_reduction = float(summary["min_reduction_percent"])
        max_reduction = float(summary["max_reduction_percent"])
        overall_reduction = float(summary["overall_reduction_percent"])
        x_min = plot_x + (min_reduction / max_percent) * plot_width
        x_max = plot_x + (max_reduction / max_percent) * plot_width
        x_overall = plot_x + (overall_reduction / max_percent) * plot_width
        parts.append(f'<text x="28" y="{center_y - 8}" font-family="Arial, sans-serif" font-size="15" font-weight="700" fill="{color}">{family}</text>')
        parts.append(f'<text x="28" y="{center_y + 12}" font-family="Arial, sans-serif" font-size="11" fill="#64748b">{summary["replicates"]} replicates</text>')
        parts.append(f'<line x1="{x_min:.1f}" y1="{center_y}" x2="{x_max:.1f}" y2="{center_y}" stroke="{color}" stroke-width="14" stroke-linecap="round" opacity="0.22"/>')
        parts.append(f'<line x1="{x_overall:.1f}" y1="{center_y - 15}" x2="{x_overall:.1f}" y2="{center_y + 15}" stroke="{color}" stroke-width="3" opacity="0.95"/>')
        for dot_index, row in enumerate(grouped):
            reduction = float(row["reduction_percent"])
            x = plot_x + (reduction / max_percent) * plot_width
            offset = (dot_index - (len(grouped) - 1) / 2) * 7
            parts.append(f'<circle cx="{x:.1f}" cy="{center_y + offset:.1f}" r="5.2" fill="{color}" stroke="#ffffff" stroke-width="1.7"/>')
        parts.append(f'<text x="{plot_x + plot_width + 18}" y="{center_y - 6}" font-family="Arial, sans-serif" font-size="12" font-weight="700" fill="#0f172a">{overall_reduction:.1f}% pooled</text>')
        parts.append(f'<text x="{plot_x + plot_width + 18}" y="{center_y + 12}" font-family="Arial, sans-serif" font-size="11" fill="#64748b">range {min_reduction:.1f}-{max_reduction:.1f}%</text>')
    parts.extend([
        f'<line x1="{plot_x}" y1="{legend_y - 11}" x2="{plot_x}" y2="{legend_y + 11}" stroke="#2563eb" stroke-width="3"/>',
        f'<text x="{plot_x + 12}" y="{legend_y + 4}" font-family="Arial, sans-serif" font-size="11" fill="#64748b">pooled family reduction</text>',
        f'<circle cx="{plot_x + 190}" cy="{legend_y}" r="5.2" fill="#2563eb" stroke="#ffffff" stroke-width="1.7"/>',
        f'<text x="{plot_x + 202}" y="{legend_y + 4}" font-family="Arial, sans-serif" font-size="11" fill="#64748b">replicate</text>',
        f'<text x="{plot_x}" y="{note_y}" font-family="Arial, sans-serif" font-size="11" fill="#64748b">Measured on generated context-gathering transcripts, not private Codex billing telemetry.</text>',
        "</svg>",
    ])
    path.write_text("\n".join(parts) + "\n", encoding="utf-8")


def write_png_if_possible(rows: list[dict[str, object]], path: Path) -> bool:
    try:
        import matplotlib.pyplot as plt
    except Exception:
        return False

    summaries = {summary["family"]: summary for summary in family_summaries(rows)}
    fig, ax = plt.subplots(figsize=(10.5, 5.6))
    y_positions = list(range(len(FAMILY_ORDER)))
    for y_pos, family in zip(y_positions, FAMILY_ORDER):
        grouped = [row for row in rows if row["family"] == family]
        if not grouped:
            continue
        summary = summaries[family]
        color = FAMILY_COLORS[family]
        min_reduction = float(summary["min_reduction_percent"])
        max_reduction = float(summary["max_reduction_percent"])
        overall_reduction = float(summary["overall_reduction_percent"])
        ax.plot([min_reduction, max_reduction], [y_pos, y_pos], color=color, linewidth=12, alpha=0.22, solid_capstyle="round")
        ax.scatter([float(row["reduction_percent"]) for row in grouped], [y_pos] * len(grouped), color=color, edgecolors="white", linewidths=1.5, s=58, zorder=3)
        ax.plot([overall_reduction, overall_reduction], [y_pos - 0.18, y_pos + 0.18], color=color, linewidth=3, zorder=4)
        ax.text(max_reduction + 1.2, y_pos, f"{overall_reduction:.1f}% pooled", va="center", fontsize=9)
    ax.set_yticks(y_positions, FAMILY_ORDER)
    ax.invert_yaxis()
    ax.set_title("Measured context reduction by fixture family")
    ax.set_xlabel("fewer measured transcript tokens (%)")
    ax.set_xlim(0, 85)
    ax.grid(axis="x", color="#e2e8f0")
    total_baseline = sum(int(row["baseline_tokens"]) for row in rows)
    total_harness = sum(int(row["harness_tokens"]) for row in rows)
    overall = (1 - total_harness / total_baseline) * 100
    family_count = len({str(row["family"]) for row in rows})
    ax.text(
        0.0,
        -0.12,
        f"Overall: {overall:.1f}% fewer transcript tokens across {len(rows)} fixtures and {family_count} families. Tokenizer: {TOKENIZER}.",
        transform=ax.transAxes,
        fontsize=9,
    )
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
        name = scenario_id(scenario)
        (TRANSCRIPTS / f"{name}.baseline.txt").write_text(baseline, encoding="utf-8")
        (TRANSCRIPTS / f"{name}.harness.txt").write_text(harness, encoding="utf-8")

        baseline_tokens = count_tokens(baseline)
        harness_tokens = count_tokens(harness)
        rows.append(
            {
                "scenario": name,
                "family": scenario_family(name),
                "label": scenario_label(name),
                "tokenizer": TOKENIZER,
                "files": len(files),
                "baseline_chars": len(baseline),
                "harness_chars": len(harness),
                "baseline_tokens": baseline_tokens,
                "harness_tokens": harness_tokens,
                "token_delta": harness_tokens - baseline_tokens,
                "reduction_percent": round((1 - harness_tokens / baseline_tokens) * 100, 1),
                "token_delta_percent": round((harness_tokens - baseline_tokens) / baseline_tokens * 100, 1),
            }
        )

    with (RESULTS / "summary.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    (RESULTS / "summary.json").write_text(json.dumps(rows, indent=2) + "\n", encoding="utf-8")
    write_family_summary(rows, RESULTS / "family_summary.csv")
    write_reduction_svg(rows, RESULTS / "context_reduction_by_family.svg")
    write_png_if_possible(rows, RESULTS / "context_reduction_by_family.png")
    return rows


def main() -> None:
    rows = run()
    print(f"tokenizer={TOKENIZER}")
    print("scenario,baseline_tokens,harness_tokens,token_delta_percent")
    for row in rows:
        print(f"{row['scenario']},{row['baseline_tokens']},{row['harness_tokens']},{row['token_delta_percent']}")
    print(f"\nWrote results to {RESULTS.relative_to(Path.cwd())}")


if __name__ == "__main__":
    main()

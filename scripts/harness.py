#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import os
import platform
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PROJECT_ROOT = Path("/home/trhova/writer_skill")
DEFAULT_CODEX_HOME = Path.home() / ".codex"
MANIFEST_PATH = REPO_ROOT / "manifests" / "changes.json"
VENV_DIR = REPO_ROOT / ".venv"
BIN_DIR = REPO_ROOT / "bin"
GRAPHIFY_DIR = REPO_ROOT / "vendor" / "graphify"
RTK_DIR = REPO_ROOT / "vendor" / "rtk"

PROJECT_AGENT_START = "<!-- codex_harness:project:start -->"
PROJECT_AGENT_END = "<!-- codex_harness:project:end -->"


@dataclass
class InstallContext:
    project_root: Path
    codex_home: Path
    backup_dir: Path
    changes: list[dict]
    timestamp: str


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def load_json(path: Path, default: dict | list) -> dict | list:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def save_manifest(payload: dict) -> None:
    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST_PATH.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def load_manifest() -> dict:
    return load_json(MANIFEST_PATH, {"active_install": None})


def file_snapshot(path: Path) -> dict:
    if not path.exists():
        return {"exists": False}
    if path.is_dir():
        return {"exists": True, "type": "dir"}
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    return {
        "exists": True,
        "type": "file",
        "size": path.stat().st_size,
        "sha256": digest,
    }


def target_backup_path(backup_dir: Path, target: Path) -> Path:
    return backup_dir / target.resolve().relative_to(Path("/"))


def find_change(changes: list[dict], target: Path) -> dict | None:
    resolved = str(target.resolve())
    for change in changes:
        if change["path"] == resolved:
            return change
    return None


def ensure_backup(
    changes: list[dict],
    backup_dir: Path,
    target: Path,
    manager: str,
    reason: str,
) -> dict:
    existing = find_change(changes, target)
    if existing is not None:
        return existing

    existed_before = target.exists()
    before = file_snapshot(target)
    backup_path = target_backup_path(backup_dir, target) if existed_before else None
    if existed_before and backup_path and not backup_path.exists():
        backup_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(target, backup_path)

    entry = {
        "path": str(target.resolve()),
        "manager": manager,
        "reason": reason,
        "existed_before": existed_before,
        "backup_path": str(backup_path) if backup_path else None,
        "before": before,
        "after": before,
        "changed": False,
    }
    changes.append(entry)
    return entry


def update_after_snapshot(changes: list[dict], target: Path) -> None:
    entry = find_change(changes, target)
    if entry is None:
        return
    after = file_snapshot(target)
    entry["after"] = after
    entry["changed"] = entry["before"] != after


def render_template(path: Path) -> str:
    return path.read_text(encoding="utf-8").rstrip() + "\n"


def upsert_marked_block(existing: str, start_marker: str, end_marker: str, block: str) -> str:
    block = block.rstrip() + "\n"
    if start_marker in existing and end_marker in existing:
        before, remainder = existing.split(start_marker, 1)
        _, after = remainder.split(end_marker, 1)
        new_text = before.rstrip() + "\n\n" + block + "\n" + after.lstrip()
        return new_text.strip() + "\n"
    if existing.strip():
        return existing.rstrip() + "\n\n" + block
    return block


def ensure_executable(path: Path) -> None:
    path.chmod(path.stat().st_mode | 0o111)


def patch_codex_config(existing: str) -> str:
    lines = existing.splitlines()
    if not lines:
        return '[features]\nmulti_agent = true\n'

    in_features = False
    found_features = False
    found_multi_agent = False
    insert_at: int | None = None

    for index, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("[") and stripped.endswith("]"):
            if in_features and not found_multi_agent and insert_at is None:
                insert_at = index
            in_features = stripped == "[features]"
            if in_features:
                found_features = True
            continue
        if in_features and stripped.startswith("multi_agent"):
            lines[index] = "multi_agent = true"
            found_multi_agent = True

    if found_features:
        if not found_multi_agent:
            if insert_at is None:
                lines.append("multi_agent = true")
            else:
                lines.insert(insert_at, "multi_agent = true")
    else:
        if lines and lines[-1].strip():
            lines.append("")
        lines.extend(["[features]", "multi_agent = true"])
    return "\n".join(lines).rstrip() + "\n"


def install_project_files(ctx: InstallContext) -> None:
    agents_path = ctx.project_root / "AGENTS.md"
    ensure_backup(ctx.changes, ctx.backup_dir, agents_path, "codex_harness", "project graph/rtk guidance")
    project_agents = render_template(REPO_ROOT / "templates" / "AGENTS.md")
    write_text(
        agents_path,
        upsert_marked_block(read_text(agents_path), PROJECT_AGENT_START, PROJECT_AGENT_END, project_agents),
    )
    update_after_snapshot(ctx.changes, agents_path)

    graphifyignore_path = ctx.project_root / ".graphifyignore"
    ensure_backup(ctx.changes, ctx.backup_dir, graphifyignore_path, "codex_harness", "project graphify exclusions")
    graphifyignore = render_template(REPO_ROOT / "templates" / "project.graphifyignore")
    existing_ignore = read_text(graphifyignore_path)
    if graphifyignore.strip() not in existing_ignore:
        combined = existing_ignore.rstrip()
        if combined:
            combined += "\n\n"
        combined += graphifyignore
        write_text(graphifyignore_path, combined)
    update_after_snapshot(ctx.changes, graphifyignore_path)

    hooks_path = ctx.project_root / ".codex" / "hooks.json"
    ensure_backup(ctx.changes, ctx.backup_dir, hooks_path, "graphify", "project PreToolUse reminder")
    hooks = load_json(hooks_path, {"hooks": {}})
    pre_tool = hooks.setdefault("hooks", {}).setdefault("PreToolUse", [])
    pre_tool = [entry for entry in pre_tool if entry.get("codex_harness_managed") != "graphify"]
    pre_tool.append(
        {
            "matcher": "Bash",
            "codex_harness_managed": "graphify",
            "hooks": [
                {
                    "type": "command",
                    "command": (
                        "[ -f graphify-out/graph.json ] && "
                        """echo '{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"allow"},"systemMessage":"codex_harness: graphify graph available. Read graphify-out/GRAPH_REPORT.md before broad file searches."}' """
                        "|| true"
                    ),
                }
            ],
        }
    )
    hooks["hooks"]["PreToolUse"] = pre_tool
    write_text(hooks_path, json.dumps(hooks, indent=2) + "\n")
    update_after_snapshot(ctx.changes, hooks_path)


def install_codex_config(ctx: InstallContext) -> None:
    config_path = ctx.codex_home / "config.toml"
    ensure_backup(ctx.changes, ctx.backup_dir, config_path, "graphify", "enable Codex multi_agent")
    write_text(config_path, patch_codex_config(read_text(config_path)))
    update_after_snapshot(ctx.changes, config_path)


def run(cmd: list[str], env: dict[str, str] | None = None, cwd: Path | None = None, capture: bool = False) -> subprocess.CompletedProcess[str] | None:
    if capture:
        return subprocess.run(
            cmd,
            check=True,
            cwd=str(cwd) if cwd else None,
            env=env,
            text=True,
            capture_output=True,
        )
    subprocess.run(cmd, check=True, cwd=str(cwd) if cwd else None, env=env)
    return None


def create_venv() -> None:
    if not (VENV_DIR / "bin" / "python").exists():
        run([sys.executable, "-m", "venv", str(VENV_DIR)])


def install_graphify() -> None:
    create_venv()
    pip = VENV_DIR / "bin" / "pip"
    run([str(pip), "install", "--upgrade", "pip", "setuptools", "wheel"])
    run([str(pip), "install", "-e", f"{GRAPHIFY_DIR}[watch,leiden]"])


def detect_rtk_target() -> str:
    machine = platform.machine().lower()
    system = platform.system().lower()
    if system == "linux":
        if machine in {"x86_64", "amd64"}:
            return "x86_64-unknown-linux-musl"
        if machine in {"aarch64", "arm64"}:
            return "aarch64-unknown-linux-gnu"
    if system == "darwin":
        if machine in {"x86_64", "amd64"}:
            return "x86_64-apple-darwin"
        if machine in {"arm64", "aarch64"}:
            return "aarch64-apple-darwin"
    raise RuntimeError(f"Unsupported platform: {system} {machine}")


def install_rtk_binary() -> None:
    BIN_DIR.mkdir(parents=True, exist_ok=True)
    version = os.environ.get("RTK_VERSION", "").strip()
    if not version:
        described = (
            subprocess.check_output(
                ["git", "-C", str(RTK_DIR), "describe", "--tags", "--abbrev=0"],
                text=True,
            )
            .strip()
        )
        if re.fullmatch(r"v\d+\.\d+\.\d+", described):
            version = described
        else:
            api_response = subprocess.check_output(
                ["curl", "-fsSL", "https://api.github.com/repos/rtk-ai/rtk/releases/latest"],
                text=True,
            )
            version = json.loads(api_response)["tag_name"]
    target = detect_rtk_target()
    url = f"https://github.com/rtk-ai/rtk/releases/download/{version}/rtk-{target}.tar.gz"
    tmp_dir = REPO_ROOT / "state" / "tmp"
    tmp_dir.mkdir(parents=True, exist_ok=True)
    archive = tmp_dir / f"rtk-{target}.tar.gz"
    run(["curl", "-fsSL", url, "-o", str(archive)])
    if (BIN_DIR / "rtk").exists():
        (BIN_DIR / "rtk").unlink()
    extracted = tmp_dir / "rtk"
    if extracted.exists():
        extracted.unlink()
    run(["tar", "-xzf", str(archive), "-C", str(tmp_dir)])
    shutil.move(str(extracted), str(BIN_DIR / "rtk"))
    ensure_executable(BIN_DIR / "rtk")


def run_rtk_codex_init(ctx: InstallContext) -> dict:
    tracked_paths = [
        ctx.codex_home / "AGENTS.md",
        ctx.codex_home / "RTK.md",
    ]
    before = {str(path): file_snapshot(path) for path in tracked_paths}
    for path in tracked_paths:
        ensure_backup(ctx.changes, ctx.backup_dir, path, "rtk", "official Codex RTK init")

    env = os.environ.copy()
    env["PATH"] = f"{BIN_DIR}:{env.get('PATH', '')}"
    result = run([str(BIN_DIR / "rtk"), "init", "-g", "--codex"], env=env, capture=True)
    assert result is not None

    after = {}
    touched = []
    for path in tracked_paths:
        update_after_snapshot(ctx.changes, path)
        snapshot = file_snapshot(path)
        after[str(path)] = snapshot
        if before[str(path)] != snapshot:
            touched.append(str(path))

    return {
        "command": [str(BIN_DIR / "rtk"), "init", "-g", "--codex"],
        "stdout": result.stdout,
        "stderr": result.stderr,
        "tracked_files": [str(path) for path in tracked_paths],
        "touched_files": touched,
        "before": before,
        "after": after,
    }


def verify_install(ctx: InstallContext) -> None:
    run([str(VENV_DIR / "bin" / "graphify"), "--help"])
    run([str(BIN_DIR / "rtk"), "--version"])
    if not (ctx.project_root / "AGENTS.md").exists():
        raise RuntimeError("project AGENTS.md was not created")
    if not (ctx.codex_home / "RTK.md").exists():
        raise RuntimeError("global RTK.md was not created by rtk init")


def install(project_root: Path, codex_home: Path) -> None:
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    backup_dir = REPO_ROOT / "state" / "backups" / timestamp
    ctx = InstallContext(
        project_root=project_root,
        codex_home=codex_home,
        backup_dir=backup_dir,
        changes=[],
        timestamp=timestamp,
    )
    install_graphify()
    install_rtk_binary()
    install_project_files(ctx)
    install_codex_config(ctx)
    rtk_codex = run_rtk_codex_init(ctx)

    manifest = {
        "active_install": {
            "timestamp": timestamp,
            "repo_root": str(REPO_ROOT),
            "project_root": str(project_root),
            "codex_home": str(codex_home),
            "backup_dir": str(backup_dir),
            "graphify_bin": str(VENV_DIR / "bin" / "graphify"),
            "rtk_bin": str(BIN_DIR / "rtk"),
            "submodules": {
                "graphify": subprocess.check_output(["git", "-C", str(GRAPHIFY_DIR), "rev-parse", "HEAD"], text=True).strip(),
                "rtk": subprocess.check_output(["git", "-C", str(RTK_DIR), "rev-parse", "HEAD"], text=True).strip(),
            },
            "rtk_codex_init": rtk_codex,
            "changes": ctx.changes,
        }
    }
    save_manifest(manifest)
    verify_install(ctx)


def uninstall() -> None:
    manifest = load_manifest()
    active = manifest.get("active_install")
    if not active:
        print("No active install recorded.")
        return

    for change in reversed(active.get("changes", [])):
        target = Path(change["path"])
        backup_path = change.get("backup_path")
        if change.get("existed_before") and backup_path:
            backup = Path(backup_path)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(backup, target)
        elif target.exists():
            if target.is_dir():
                shutil.rmtree(target)
            else:
                target.unlink()

    if VENV_DIR.exists():
        shutil.rmtree(VENV_DIR)
    rtk_binary = BIN_DIR / "rtk"
    if rtk_binary.exists():
        rtk_binary.unlink()
    save_manifest({"active_install": None})


def main() -> None:
    if len(sys.argv) < 2 or sys.argv[1] not in {"install", "uninstall"}:
        raise SystemExit("Usage: harness.py [install|uninstall]")

    project_root = Path(os.environ.get("PROJECT_ROOT", str(DEFAULT_PROJECT_ROOT))).resolve()
    codex_home = Path(os.environ.get("CODEX_HOME", str(DEFAULT_CODEX_HOME))).resolve()

    if sys.argv[1] == "install":
        install(project_root, codex_home)
    else:
        uninstall()


if __name__ == "__main__":
    main()

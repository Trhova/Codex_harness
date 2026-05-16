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
DEFAULT_CODEX_HOME = Path.home() / ".codex"
SHELL_PROFILE = Path.home() / ".bashrc"
MANIFEST_PATH = REPO_ROOT / "manifests" / "changes.json"
VENV_DIR = REPO_ROOT / ".venv"
BIN_DIR = REPO_ROOT / "bin"
GRAPHIFY_DIR = REPO_ROOT / "vendor" / "graphify"
RTK_DIR = REPO_ROOT / "vendor" / "rtk"
ENV_DIR = REPO_ROOT / "env"
RTK_PATH_ENV = ENV_DIR / "rtk-path.sh"
SHELL_PATH_BEGIN = "# codex_harness:rtk-path:start"
SHELL_PATH_END = "# codex_harness:rtk-path:end"


@dataclass
class OperationContext:
    codex_home: Path
    backup_dir: Path
    changes: list[dict]
    commands: list[dict]
    timestamp: str
    project_root: Path | None = None


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def load_json(path: Path, default: dict | list) -> dict | list:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def manifest_default() -> dict:
    return {
        "bootstrap": None,
        "targets": {},
    }


def load_manifest() -> dict:
    return load_json(MANIFEST_PATH, manifest_default())


def save_manifest(payload: dict) -> None:
    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST_PATH.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def file_snapshot(path: Path) -> dict:
    if not path.exists():
        return {"exists": False}
    if path.is_dir():
        return {"exists": True, "type": "dir"}
    return {
        "exists": True,
        "type": "file",
        "size": path.stat().st_size,
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
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


def record_command(ctx: OperationContext, command: list[str], cwd: Path | None = None) -> None:
    ctx.commands.append(
        {
            "command": command,
            "cwd": str(cwd.resolve()) if cwd else None,
        }
    )


def run(
    cmd: list[str],
    env: dict[str, str] | None = None,
    cwd: Path | None = None,
    capture: bool = False,
) -> subprocess.CompletedProcess[str] | None:
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


def make_context(codex_home: Path, project_root: Path | None = None) -> OperationContext:
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    backup_dir = REPO_ROOT / "state" / "backups" / timestamp
    return OperationContext(
        codex_home=codex_home,
        backup_dir=backup_dir,
        changes=[],
        commands=[],
        timestamp=timestamp,
        project_root=project_root,
    )


def ensure_executable(path: Path) -> None:
    path.chmod(path.stat().st_mode | 0o111)


def ensure_rtk_path_env_file() -> None:
    ENV_DIR.mkdir(parents=True, exist_ok=True)
    content = (
        "#!/usr/bin/env sh\n"
        'RTK_PATH_SCRIPT=${BASH_SOURCE:-$0}\n'
        'RTK_PATH_SCRIPT_DIR=$(CDPATH= cd "$(dirname "$RTK_PATH_SCRIPT")" && pwd)\n'
        'export PATH="${RTK_PATH_SCRIPT_DIR}/../bin:$PATH"\n'
    )
    if read_text(RTK_PATH_ENV) != content:
        write_text(RTK_PATH_ENV, content)
    ensure_executable(RTK_PATH_ENV)


def render_shell_path_block() -> str:
    return (
        f"{SHELL_PATH_BEGIN}\n"
        f'. "{RTK_PATH_ENV}"\n'
        f"{SHELL_PATH_END}\n"
    )


def ensure_shell_path_block(ctx: OperationContext) -> dict:
    profile_path = SHELL_PROFILE
    before = file_snapshot(profile_path)
    ensure_backup(ctx.changes, ctx.backup_dir, profile_path, "rtk", "add harness PATH block")
    existing = read_text(profile_path)
    block = render_shell_path_block()
    if block not in existing:
        if existing and not existing.endswith("\n"):
            existing += "\n"
        if existing and not existing.endswith("\n\n"):
            existing += "\n"
        existing += block
        write_text(profile_path, existing)
    update_after_snapshot(ctx.changes, profile_path)
    after = file_snapshot(profile_path)
    return {
        "before": before,
        "after": after,
        "touched_files": [str(profile_path)] if before != after else [],
        "profile": str(profile_path),
        "env_file": str(RTK_PATH_ENV),
    }


def remove_shell_path_block() -> None:
    profile_path = SHELL_PROFILE
    if not profile_path.exists():
        return
    content = read_text(profile_path)
    start = content.find(SHELL_PATH_BEGIN)
    end = content.find(SHELL_PATH_END)
    if start == -1 or end == -1:
        return
    end = content.find("\n", end)
    if end == -1:
        end = len(content)
    else:
        end += 1
    new_content = content[:start] + content[end:]
    write_text(profile_path, new_content.rstrip() + "\n" if new_content.strip() else "")


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


def create_venv(ctx: OperationContext) -> None:
    if not (VENV_DIR / "bin" / "python").exists():
        command = [sys.executable, "-m", "venv", str(VENV_DIR)]
        record_command(ctx, command)
        run(command)


def install_graphify(ctx: OperationContext) -> None:
    create_venv(ctx)
    pip = VENV_DIR / "bin" / "pip"
    command = [str(pip), "install", "--upgrade", "pip", "setuptools", "wheel"]
    record_command(ctx, command)
    run(command)
    command = [str(pip), "install", "markitdown[all]"]
    record_command(ctx, command)
    run(command)
    command = [str(pip), "install", "-e", f"{GRAPHIFY_DIR}[watch,leiden]"]
    record_command(ctx, command)
    run(command)


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


def install_rtk_binary(ctx: OperationContext) -> None:
    BIN_DIR.mkdir(parents=True, exist_ok=True)
    version = os.environ.get("RTK_VERSION", "").strip()
    if not version:
        described = subprocess.check_output(
            ["git", "-C", str(RTK_DIR), "describe", "--tags", "--abbrev=0"],
            text=True,
        ).strip()
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

    command = ["curl", "-fsSL", url, "-o", str(archive)]
    record_command(ctx, command)
    run(command)

    binary_path = BIN_DIR / "rtk"
    if binary_path.exists():
        binary_path.unlink()
    extracted = tmp_dir / "rtk"
    if extracted.exists():
        extracted.unlink()

    command = ["tar", "-xzf", str(archive), "-C", str(tmp_dir)]
    record_command(ctx, command)
    run(command)

    shutil.move(str(extracted), str(binary_path))
    ensure_executable(binary_path)


def run_rtk_codex_init(ctx: OperationContext) -> dict:
    tracked_paths = [ctx.codex_home / "AGENTS.md", ctx.codex_home / "RTK.md"]
    before = {str(path): file_snapshot(path) for path in tracked_paths}
    for path in tracked_paths:
        ensure_backup(ctx.changes, ctx.backup_dir, path, "rtk", "official Codex RTK init")

    env = os.environ.copy()
    env["PATH"] = f"{BIN_DIR}:{env.get('PATH', '')}"
    command = [str(BIN_DIR / "rtk"), "init", "-g", "--codex"]
    record_command(ctx, command)
    result = run(command, env=env, capture=True)
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
        "command": command,
        "stdout": result.stdout,
        "stderr": result.stderr,
        "tracked_files": [str(path) for path in tracked_paths],
        "touched_files": touched,
        "before": before,
        "after": after,
    }


def ensure_markitdown_codex_guidance(ctx: OperationContext) -> dict:
    agents_path = ctx.codex_home / "AGENTS.md"
    before = file_snapshot(agents_path)
    ensure_backup(ctx.changes, ctx.backup_dir, agents_path, "markitdown", "prefer MarkItDown for document conversion")

    marker = "## MarkItDown\n\nPrefer `markitdown` for document-to-Markdown conversion and other supported office/document formats when it is the right tool. Use it first for reliable Markdown conversion, then fall back to specialized extractors only when MarkItDown cannot preserve the needed content or structure.\n"
    existing = read_text(agents_path)
    if marker not in existing:
        if existing and not existing.endswith("\n"):
            existing += "\n"
        if existing:
            existing += "\n"
        existing += marker
        write_text(agents_path, existing)

    update_after_snapshot(ctx.changes, agents_path)
    after = file_snapshot(agents_path)
    return {
        "before": before,
        "after": after,
        "touched_files": [str(agents_path)] if before != after else [],
        "command": None,
    }


def run_graphify_codex_install(ctx: OperationContext) -> dict:
    if ctx.project_root is None:
        raise RuntimeError("project_root is required for graphify activation")

    tracked_paths = [
        ctx.project_root / "AGENTS.md",
        ctx.project_root / ".codex" / "hooks.json",
        ctx.codex_home / "config.toml",
    ]
    before = {str(path): file_snapshot(path) for path in tracked_paths}
    for path in tracked_paths:
        ensure_backup(ctx.changes, ctx.backup_dir, path, "graphify", "official Codex install")

    env = os.environ.copy()
    env["PATH"] = f"{VENV_DIR / 'bin'}:{env.get('PATH', '')}"
    command = [str(VENV_DIR / "bin" / "graphify"), "codex", "install"]
    record_command(ctx, command, cwd=ctx.project_root)
    result = run(command, env=env, cwd=ctx.project_root, capture=True)
    assert result is not None

    after = {}
    touched = []
    for path in tracked_paths:
        update_after_snapshot(ctx.changes, path)
        snapshot = file_snapshot(path)
        after[str(path)] = snapshot
        if before[str(path)] != snapshot:
            touched.append(str(path))

    config_path = ctx.codex_home / "config.toml"
    config_before = file_snapshot(config_path)
    if not re.search(r"(?m)^\s*multi_agent\s*=\s*true\s*$", read_text(config_path)):
        multi_agent_source = "harness"
        ensure_backup(ctx.changes, ctx.backup_dir, config_path, "graphify", "enable Codex multi_agent")
        write_text(config_path, patch_codex_config(read_text(config_path)))
        update_after_snapshot(ctx.changes, config_path)
    else:
        multi_agent_source = "graphify"
    config_after = file_snapshot(config_path)

    return {
        "command": command,
        "stdout": result.stdout,
        "stderr": result.stderr,
        "tracked_files": [str(path) for path in tracked_paths],
        "touched_files": touched,
        "before": before,
        "after": after,
        "multi_agent_source": multi_agent_source,
        "config_before": config_before,
        "config_after": config_after,
    }


def build_bootstrap_record(ctx: OperationContext, rtk_codex: dict) -> dict:
    return {
        "timestamp": ctx.timestamp,
        "repo_root": str(REPO_ROOT),
        "codex_home": str(ctx.codex_home),
        "backup_dir": str(ctx.backup_dir),
        "graphify_bin": str(VENV_DIR / "bin" / "graphify"),
        "rtk_bin": str(BIN_DIR / "rtk"),
        "submodules": {
            "graphify": subprocess.check_output(["git", "-C", str(GRAPHIFY_DIR), "rev-parse", "HEAD"], text=True).strip(),
            "rtk": subprocess.check_output(["git", "-C", str(RTK_DIR), "rev-parse", "HEAD"], text=True).strip(),
        },
        "rtk_codex_init": rtk_codex,
        "changes": ctx.changes,
        "commands": ctx.commands,
    }


def build_target_record(ctx: OperationContext, graphify_codex: dict) -> dict:
    if ctx.project_root is None:
        raise RuntimeError("project_root is required for target record")
    return {
        "timestamp": ctx.timestamp,
        "project_root": str(ctx.project_root),
        "codex_home": str(ctx.codex_home),
        "backup_dir": str(ctx.backup_dir),
        "graphify_bin": str(VENV_DIR / "bin" / "graphify"),
        "graphify_codex_install": graphify_codex,
        "changes": ctx.changes,
        "commands": ctx.commands,
    }


def revert_changes(changes: list[dict]) -> None:
    for change in reversed(changes):
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


def verify_bootstrap(codex_home: Path) -> None:
    run([str(VENV_DIR / "bin" / "graphify"), "--help"])
    run([str(BIN_DIR / "rtk"), "--version"])
    run(["bash", "-lc", f'source "{SHELL_PROFILE}" >/dev/null 2>&1; command -v rtk'])
    if not (codex_home / "RTK.md").exists():
        raise RuntimeError("global RTK.md was not created by rtk init")


def verify_target(project_root: Path) -> None:
    if not (project_root / "AGENTS.md").exists():
        raise RuntimeError("project AGENTS.md was not created")
    if not (project_root / ".codex" / "hooks.json").exists():
        raise RuntimeError("project .codex/hooks.json was not created")


def bootstrap(codex_home: Path) -> None:
    manifest = load_manifest()
    if manifest.get("bootstrap"):
        raise RuntimeError("bootstrap already recorded; run uninstall before bootstrapping again")

    ctx = make_context(codex_home)
    install_graphify(ctx)
    install_rtk_binary(ctx)
    ensure_rtk_path_env_file()
    rtk_codex = run_rtk_codex_init(ctx)
    markitdown_codex = ensure_markitdown_codex_guidance(ctx)
    shell_path = ensure_shell_path_block(ctx)
    manifest["bootstrap"] = build_bootstrap_record(ctx, rtk_codex)
    manifest["bootstrap"]["markitdown_codex_guidance"] = markitdown_codex
    manifest["bootstrap"]["shell_path"] = shell_path
    save_manifest(manifest)
    verify_bootstrap(codex_home)


def activate(project_root: Path, codex_home: Path) -> None:
    manifest = load_manifest()
    if not manifest.get("bootstrap"):
        raise RuntimeError("bootstrap must be completed before activating a target project")

    project_root = project_root.resolve()
    project_key = str(project_root)
    if manifest["targets"].get(project_key):
        raise RuntimeError(f"target already activated: {project_key}")

    ctx = make_context(codex_home, project_root)
    graphify_codex = run_graphify_codex_install(ctx)
    manifest["targets"][project_key] = build_target_record(ctx, graphify_codex)
    save_manifest(manifest)
    verify_target(project_root)


def deactivate(project_root: Path) -> None:
    manifest = load_manifest()
    project_key = str(project_root.resolve())
    target = manifest.get("targets", {}).get(project_key)
    if not target:
        print(f"No active target recorded for {project_key}.")
        return

    revert_changes(target.get("changes", []))
    del manifest["targets"][project_key]
    save_manifest(manifest)


def uninstall() -> None:
    manifest = load_manifest()
    for target_key in list(manifest.get("targets", {}).keys()):
        revert_changes(manifest["targets"][target_key].get("changes", []))
        del manifest["targets"][target_key]

    bootstrap_record = manifest.get("bootstrap")
    if bootstrap_record:
        revert_changes(bootstrap_record.get("changes", []))
        remove_shell_path_block()

    if VENV_DIR.exists():
        shutil.rmtree(VENV_DIR)
    rtk_binary = BIN_DIR / "rtk"
    if rtk_binary.exists():
        rtk_binary.unlink()
    if RTK_PATH_ENV.exists():
        RTK_PATH_ENV.unlink()

    save_manifest(manifest_default())


def migrate_legacy_manifest() -> bool:
    manifest = load_manifest()
    if "active_install" not in manifest:
        return False

    legacy = manifest.get("active_install")
    upgraded = manifest_default()
    if legacy:
        bootstrap_record = {
            "timestamp": legacy["timestamp"],
            "repo_root": legacy["repo_root"],
            "codex_home": legacy["codex_home"],
            "backup_dir": legacy["backup_dir"],
            "graphify_bin": legacy["graphify_bin"],
            "rtk_bin": legacy["rtk_bin"],
            "submodules": legacy["submodules"],
            "rtk_codex_init": legacy["rtk_codex_init"],
            "changes": [change for change in legacy["changes"] if change["manager"] == "rtk"],
            "commands": [command for command in legacy.get("commands", []) if "graphify" not in " ".join(command["command"])],
        }
        upgraded["bootstrap"] = bootstrap_record

        project_root = legacy.get("project_root")
        graphify_changes = [change for change in legacy["changes"] if change["manager"] == "graphify"]
        if project_root and graphify_changes:
            upgraded["targets"][project_root] = {
                "timestamp": legacy["timestamp"],
                "project_root": project_root,
                "codex_home": legacy["codex_home"],
                "backup_dir": legacy["backup_dir"],
                "graphify_bin": legacy["graphify_bin"],
                "graphify_codex_install": legacy.get("graphify_codex_install"),
                "changes": graphify_changes,
                "commands": [command for command in legacy.get("commands", []) if "graphify" in " ".join(command["command"])],
            }

    save_manifest(upgraded)
    return True


def usage() -> str:
    return (
        "Usage: harness.py [bootstrap|activate|deactivate|uninstall] [project_root]\n"
        "  bootstrap                 prepare reusable harness tooling only\n"
        "  activate <project_root>   activate Graphify for one target project\n"
        "  deactivate <project_root> remove Graphify setup from one target project\n"
        "  uninstall                 remove all targets and bootstrap tooling\n"
    )


def main() -> None:
    migrate_legacy_manifest()

    if len(sys.argv) < 2:
        raise SystemExit(usage())

    command = sys.argv[1]
    codex_home = Path(os.environ.get("CODEX_HOME", str(DEFAULT_CODEX_HOME))).resolve()

    if command == "bootstrap":
        if len(sys.argv) != 2:
            raise SystemExit(usage())
        bootstrap(codex_home)
        return

    if command == "activate":
        if len(sys.argv) != 3:
            raise SystemExit(usage())
        activate(Path(sys.argv[2]), codex_home)
        return

    if command == "deactivate":
        if len(sys.argv) != 3:
            raise SystemExit(usage())
        deactivate(Path(sys.argv[2]))
        return

    if command == "uninstall":
        if len(sys.argv) != 2:
            raise SystemExit(usage())
        uninstall()
        return

    raise SystemExit(usage())


if __name__ == "__main__":
    main()

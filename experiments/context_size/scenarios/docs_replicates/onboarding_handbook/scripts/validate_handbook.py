from pathlib import Path


REQUIRED_TERMS = ["onboarding", "setup", "approval", "workflow", "troubleshooting"]


def read_docs(root: Path) -> str:
    return "\n".join(path.read_text(encoding="utf-8") for path in sorted((root / "docs").glob("*.md")))


def missing_terms(text: str) -> list[str]:
    lowered = text.lower()
    return [term for term in REQUIRED_TERMS if term not in lowered]


if __name__ == "__main__":
    missing = missing_terms(read_docs(Path(__file__).resolve().parents[1]))
    if missing:
        raise SystemExit(f"Missing handbook terms: {', '.join(missing)}")
    print("Handbook validation passed")

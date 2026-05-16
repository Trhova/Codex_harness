from pathlib import Path


def policy_files(root: Path) -> list[Path]:
    return sorted((root / "docs").glob("*.md"))


def count_policy_mentions(root: Path) -> dict[str, int]:
    terms = ["policy", "exception", "owner", "risk", "review", "audit"]
    text = "\n".join(path.read_text(encoding="utf-8").lower() for path in policy_files(root))
    return {term: text.count(term) for term in terms}


if __name__ == "__main__":
    for term, count in count_policy_mentions(Path(__file__).resolve().parents[1]).items():
        print(f"{term}: {count}")

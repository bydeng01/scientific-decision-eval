"""Save a locally entered key without printing it or putting it in shell history."""

import getpass
import os
from pathlib import Path


def main():
    path = Path(__file__).resolve().parents[1] / ".env.local"
    key = os.environ.get("OPENROUTER_API_KEY") or getpass.getpass("OpenRouter API key (hidden): ")
    key = key.strip()
    if not key or any(c.isspace() for c in key):
        raise SystemExit("No key saved: enter a nonempty key without whitespace.")
    lines = path.read_text().splitlines() if path.exists() else []
    lines = [line for line in lines if not line.startswith("OPENROUTER_API_KEY=")]
    lines.append("OPENROUTER_API_KEY=" + key)
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    os.fchmod(fd, 0o600)
    with os.fdopen(fd, "w") as stream:
        stream.write("\n".join(lines) + "\n")
    print("Saved .env.local with owner-only permissions. No API request was made.")


if __name__ == "__main__":
    main()

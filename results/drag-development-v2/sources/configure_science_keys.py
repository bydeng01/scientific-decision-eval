"""Enter research API credentials locally; never print credential values."""

import argparse
import getpass
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
KEY_NAMES = {"openai": "OPENAI_API_KEY", "anthropic": "ANTHROPIC_API_KEY",
             "openrouter": "OPENROUTER_API_KEY", "typesafe": "TYPESAFE_API_KEY"}


def load_key(provider):
    name = KEY_NAMES[provider]
    if os.environ.get(name, "").strip():
        return os.environ[name].strip()
    path = ROOT / ".env.local"
    if path.exists():
        for line in path.read_text().splitlines():
            key, sep, value = line.partition("=")
            if sep and key.strip() == name:
                return value.strip().strip("\"'")
    return ""


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("providers", nargs="*", choices=list(KEY_NAMES))
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.check:
        for provider in KEY_NAMES:
            print(f"{provider}: {'configured' if load_key(provider) else 'missing'}")
        return
    if not args.providers:
        parser.error("name the providers to configure, or use --check")
    if not sys.stdin.isatty():
        raise SystemExit("Run in your own interactive terminal for hidden key entry.")
    path = ROOT / ".env.local"
    lines = path.read_text().splitlines() if path.exists() else []
    for provider in args.providers:
        value = getpass.getpass(f"{provider} API key (hidden; blank keeps current): ").strip()
        if not value:
            continue
        if any(c.isspace() for c in value):
            raise SystemExit("Key not saved: unexpected whitespace.")
        name = KEY_NAMES[provider]
        lines = [line for line in lines if line.partition("=")[0].strip() != name]
        lines.append(name + "=" + value)
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    os.fchmod(fd, 0o600)
    with os.fdopen(fd, "w") as stream:
        stream.write("\n".join(lines) + "\n")
    print("Saved local credentials with owner-only permissions. No API call made.")


if __name__ == "__main__":
    main()

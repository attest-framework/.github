#!/usr/bin/env python3
"""Rewrite the generated claim regions of profile/README.md from `attest-engine capabilities --json`.

Usage: generate-profile.py CAPABILITIES_JSON [--check]
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

README = Path(__file__).resolve().parent.parent / "profile" / "README.md"
COST = {
    "free": "Free",
    "provider_dependent": "Depends on provider",
    "plugin_defined": "Plugin-defined",
}


def layers_table(caps: dict) -> str:
    rows = ["| Layer | Checks | Assertion types | Cost |", "|-------|--------|-----------------|------|"]
    for layer in caps["layers"]:
        is_plugin = "plugin" in layer["assertion_types"]
        label = layer["name"] if is_plugin else f"L{layer['id']} {layer['name']}"
        types = ", ".join(f"`{t}`" for t in layer["assertion_types"])
        rows.append(f"| {label} | {layer['description']} | {types} | {COST[layer['cost']]} |")
    return "\n".join(rows)


def adapters_table(caps: dict) -> str:
    langs = caps["sdk_languages"]
    by_module: dict[str, dict] = {}
    for lang in langs:
        for a in caps["adapters"][lang]:
            entry = by_module.setdefault(a["module"], {"name": a["name"].removesuffix(".js")})
            entry[lang] = a["maturity"]
    head = "| Adapter | " + " | ".join(l.capitalize() if l != "typescript" else "TypeScript" for l in langs) + " |"
    rows = [head, "|---------|" + "|".join("-------------" for _ in langs) + "|"]
    for e in by_module.values():
        rows.append(f"| {e['name']} | " + " | ".join(e.get(l, "—") for l in langs) + " |")
    defs = "\n".join(f"- **{k}**: {v}" for k, v in sorted(caps["maturity_definitions"].items()))
    return "\n".join(rows) + "\n\n" + defs


def render(text: str, name: str, body: str) -> str:
    pat = re.compile(rf"(<!-- claims:{name}:start -->\n)(?:.*?\n)?(<!-- claims:{name}:end -->)", re.S)
    if not pat.search(text):
        sys.exit(f"markers for claims:{name} not found in {README}")
    return pat.sub(lambda m: m.group(1) + body + "\n" + m.group(2), text)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("capabilities", type=Path)
    ap.add_argument("--check", action="store_true", help="fail if the README regions differ")
    args = ap.parse_args()
    caps = json.loads(args.capabilities.read_text())
    old = README.read_text()
    new = render(render(old, "layers", layers_table(caps)), "adapters", adapters_table(caps))
    if args.check:
        if new != old:
            print("profile/README.md generated regions are stale; run generate-profile.py", file=sys.stderr)
            return 1
        return 0
    README.write_text(new)
    return 0


if __name__ == "__main__":
    sys.exit(main())

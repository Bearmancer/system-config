"""Generate references/routing.md from registry/registry.yaml. Run after every registry edit."""
from __future__ import annotations

import sys
from pathlib import Path

from . import registry

OUT = registry.ROOT / "references" / "routing.md"


def render(reg: dict) -> str:
    lines = [
        "# Routing table (generated)",
        "",
        "Generated from `registry/registry.yaml` by `scripts/gen_routing_table.py`. Do not edit by hand.",
        "",
        "## Rounds",
        "",
        "| Round | Paradigms |",
        "|---|---|",
    ]
    for i, group in enumerate(reg["round_order"], 1):
        lines.append(f"| R{i} | {', '.join(group)} |")
    lines += ["", "## Fetch ladder", ""]
    lines += [f"{i}. `{sid}`" for i, sid in enumerate(reg["fetch_ladder"], 1)]
    lines += ["", "## Surfaces", "", "| Surface | Paradigm | Ladder | Cost | Wired | MCP | CLI | POST/HTTP/local |", "|---|---|---|---|---|---|---|---|"]
    for s in registry.surfaces(reg).values():
        def col(kind: str) -> str:
            return "<br>".join(f"`{x}`" for x in s.routes.get(kind, [])) or "-"

        other = "<br>".join(f"{k}: `{x}`" for k in ("post", "http", "local") for x in s.routes.get(k, [])) or "-"
        lines.append(f"| `{s.id}` | {s.paradigm} | {s.ladder} | {s.cost} | {'yes' if s.wired else 'no'} | {col('mcp')} | {col('cli')} | {other} |")
    lines += ["", "## Error classes", "", "| Server | Class | Codes | Verified |", "|---|---|---|---|"]
    for name, srv in reg["servers"].items():
        if not srv.get("keyed"):
            continue
        for cls in registry.ERROR_CLASSES:
            codes = (srv.get("errors") or {}).get(cls, [])
            verified = cls not in srv.get("unverified", [])
            lines.append(f"| {name} | {cls} | {', '.join(f'`{c}`' for c in codes) or '-'} | {'yes' if verified else 'no'} |")
    return "\n".join(lines) + "\n"


def main() -> int:
    text = render(registry.load())
    if "--check" in sys.argv:
        return 0 if OUT.exists() and OUT.read_text(encoding="utf-8") == text else 1
    OUT.write_text(text, encoding="utf-8")
    print(f"wrote {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

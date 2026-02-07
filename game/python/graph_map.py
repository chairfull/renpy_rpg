#!/usr/bin/env python3
"""
Generate a DOT graph of the world layout: locations, their links, and where each
character currently lives.

Usage:
    python tools/graph_world.py --out world_graph.dot

If --out is omitted, the DOT text is printed to stdout. Output is an undirected
Graphviz graph suitable for `neato` or `sfdp`.
"""
from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
import re

BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "data"

sys.path.insert(0, str(BASE_DIR / "game" / "python"))
try:  # pragma: no cover - optional
    import compile_data as cd  # type: ignore
except Exception:  # pragma: no cover
    cd = None


def parse_markdown(path: Path):
    if cd:
        return cd.parse_markdown(str(path))
    try:
        content = path.read_text(encoding="utf-8")
    except Exception:
        return None, None
    if "---" not in content:
        return None, None
    parts = content.split("---", 2)
    if len(parts) < 3:
        return None, None
    header_lines = [ln for ln in parts[1].split("\n") if ln.strip()]
    props = {}
    for line in header_lines:
        if ":" not in line or line.lstrip().startswith("-"):
            continue
        k, v = line.split(":", 1)
        props[k.strip()] = v.strip().strip('"').strip("'")
    body = parts[2].strip()
    return props, body


def parse_yaml_list(lines):
    if cd:
        return cd.parse_yaml_list(lines)
    if not lines:
        return []
    cleaned = "\n".join(lines)
    try:
        import yaml  # type: ignore

        data = yaml.safe_load(cleaned)
        return data if isinstance(data, list) else []
    except Exception:
        return []


def safe_int(val, default=0):
    try:
        return int(val)
    except Exception:
        return default


def slugify(text: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")
    return slug or "root"


@dataclass
class Location:
    loc_id: str
    name: str
    x: int
    y: int
    parent: Optional[str]
    links: List[str]


@dataclass
class Character:
    char_id: str
    name: str
    location: Optional[str]


def load_locations() -> Dict[str, Location]:
    locations: Dict[str, Location] = {}
    for path in (DATA_DIR / "locations").glob("*.md"):
        props, body = parse_markdown(path)
        if not props or (props.get("type") or "").lower() != "location":
            continue
        loc_id = (props.get("id") or props.get("name") or path.stem).lower()
        name = props.get("name", loc_id)
        parent = props.get("parent")
        x = safe_int(props.get("map_x", 0))
        y = safe_int(props.get("map_y", 0))

        raw_entities = props.get("entities", [])
        entities = parse_yaml_list(raw_entities) if isinstance(raw_entities, list) else []
        links = [e.get("id") for e in entities if isinstance(e, dict) and e.get("type") == "link" and e.get("id")]

        locations[loc_id] = Location(loc_id=loc_id, name=name, x=x, y=y, parent=parent, links=links)
    return locations


def load_characters() -> Dict[str, Character]:
    chars: Dict[str, Character] = {}
    for path in (DATA_DIR / "characters").glob("*.md"):
        props, body = parse_markdown(path)
        if not props or (props.get("type") or "").lower() != "character":
            continue
        cid = (props.get("id") or props.get("name") or path.stem).lower()
        name = props.get("name", cid)
        chars[cid] = Character(char_id=cid, name=name, location=props.get("location"))
    return chars


def emit_dot(locations: Dict[str, Location], chars: Dict[str, Character], out_path: Optional[Path]):
    lines: List[str] = [
        "graph world_graph {",
        "  layout=neato;",
        "  overlap=false;",
        "  splines=true;",
        "  node [fontname=\"Helvetica\"];\n",
    ]

    for loc in locations.values():
        label = f"{loc.name}\\n({loc.loc_id})"
        pos = f" pos=\"{loc.x},{loc.y}!\"" if loc.x or loc.y else ""
        lines.append(f'  "loc:{loc.loc_id}" [shape=box label="{label}"{pos}];')

    for char in chars.values():
        label = f"{char.name}\\n({char.char_id})"
        lines.append(f'  "char:{char.char_id}" [shape=ellipse style=dashed label="{label}"];')

    # Link edges (location <-> location)
    seen_link_edges: Set[Tuple[str, str, str]] = set()
    for loc in locations.values():
        for target in loc.links:
            a, b = f"loc:{loc.loc_id}", f"loc:{target}"
            if a == b:
                continue
            edge_key = tuple(sorted([a, b])) + ("link",)
            if edge_key in seen_link_edges:
                continue
            seen_link_edges.add(edge_key)
            lines.append(f'  "{edge_key[0]}" -- "{edge_key[1]}" [label="link"];')

    # Parent edges
    for loc in locations.values():
        if loc.parent:
            a, b = f"loc:{loc.loc_id}", f"loc:{loc.parent}"
            lines.append(f'  "{a}" -- "{b}" [style=dotted label="parent"];')

    # Character placement
    for char in chars.values():
        if not char.location:
            continue
        loc_node = f"loc:{char.location}"
        if loc_node not in {f"loc:{lid}" for lid in locations.keys()}:
            lines.append(f'  "{loc_node}" [shape=box style=dashed label="{char.location}"];')
        lines.append(f'  "char:{char.char_id}" -- "{loc_node}" [style=dashed color="#888"];')

    lines.append("}\n")

    output = "\n".join(lines)
    if out_path:
        out_path.write_text(output, encoding="utf-8")
    else:
        print(output)


def main():
    parser = argparse.ArgumentParser(description="Generate a DOT graph of locations and character placements.")
    parser.add_argument("--out", type=Path, help="Path to write DOT output. Prints to stdout if omitted.")
    args = parser.parse_args()

    locations = load_locations()
    chars = load_characters()
    emit_dot(locations, chars, args.out)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Generate a DOT graph of story origins, quests, goals, and the flow jumps between them.

Usage:
    python tools/graph_story.py --out story_graph.dot

If --out is omitted, the DOT text is printed to stdout. The script relies only on
standard library modules and reads the markdown in the local data/ directory.
"""
from __future__ import annotations

import argparse
import re
import shlex
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "data"

# Try to reuse the repo's compile_data helpers (parsing is forgiving even if missing)
sys.path.insert(0, str(BASE_DIR / "game" / "python"))
try:  # pragma: no cover - optional
    import compile_data as cd  # type: ignore
except Exception:  # pragma: no cover - optional fallback
    cd = None


@dataclass
class Doc:
    obj_id: str
    otype: str
    name: str
    body: str
    props: Dict[str, str]
    path: Path


@dataclass
class FlowBlock:
    node_id: str
    owner: Doc
    section: str
    text: str


@dataclass
class Node:
    node_id: str
    label: str
    kind: str


def slugify(text: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")
    return slug or "root"


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


def nearest_heading(body: str, pos: int) -> Optional[str]:
    matches = list(re.finditer(r"(?m)^#{1,6}\s*(.+)$", body[:pos]))
    if not matches:
        return None
    return matches[-1].group(1).strip()


def extract_flows(doc: Doc) -> List[FlowBlock]:
    flows: List[FlowBlock] = []
    flow_re = re.compile(r"```flow.*?\n(.*?)\n```", re.DOTALL)
    for idx, match in enumerate(flow_re.finditer(doc.body or "")):
        section = nearest_heading(doc.body, match.start()) or "flow"
        node_id = f"flow:{doc.otype}:{doc.obj_id}:{slugify(section)}:{idx}"
        flows.append(FlowBlock(node_id=node_id, owner=doc, section=section, text=match.group(1).strip()))
    return flows


def parse_goals(body: str) -> List[Tuple[str, str, str]]:
    """Return list of (goal_id, goal_name, goal_body)."""
    goals: List[Tuple[str, str, str]] = []
    sections = re.split(r"(?m)^##\s*", body or "")
    for sec in sections[1:]:
        lines = sec.split("\n", 1)
        name = lines[0].strip()
        goal_body = lines[1] if len(lines) > 1 else ""
        goals.append((slugify(name), name, goal_body))
    return goals


def flow_targets(flow_text: str):
    targets = []
    for raw in flow_text.splitlines():
        line = raw.strip()
        if not line or line.startswith("$") or line.startswith("#"):
            continue
        cmd_match = re.match(r"^([A-Z]+)\s+(.*)$", line)
        if not cmd_match:
            continue
        cmd, rest = cmd_match.group(1), cmd_match.group(2).strip()
        try:
            parts = shlex.split(rest)
        except Exception:
            parts = rest.split()
        if not parts:
            continue

        if cmd == "JUMP":
            targets.append(("jump", parts[0]))
        elif cmd == "CALL":
            targets.append(("call", parts[0]))
        elif cmd == "COND" and len(parts) >= 2:
            # parts[0] is the expression
            if len(parts) >= 2:
                targets.append(("cond", parts[1]))
            if len(parts) >= 3:
                targets.append(("cond", parts[2]))
        elif cmd == "CHECK" and len(parts) >= 3:
            targets.append(("check", parts[2]))
            if len(parts) >= 4:
                targets.append(("check", parts[3]))
        elif cmd == "QUEST" and len(parts) >= 2:
            op = parts[0].lower()
            qid = parts[1]
            if op == "start":
                targets.append(("quest-start", qid))
            elif op == "complete":
                targets.append(("quest-complete", qid))
        elif cmd == "GOAL":
            op = parts[0].lower()
            if len(parts) == 2:
                qid, gid = None, parts[1]
            elif len(parts) >= 3:
                qid, gid = parts[1], parts[2]
            else:
                continue
            targets.append((f"goal-{op}", (qid, gid)))
        elif cmd == "TRAVEL":
            targets.append(("travel", parts[0]))
    return targets


def ensure_node(nodes: Dict[str, Node], node_id: str, label: str, kind: str) -> str:
    if node_id not in nodes:
        nodes[node_id] = Node(node_id=node_id, label=label, kind=kind)
    return node_id


def emit_dot(nodes: Dict[str, Node], edges: Set[Tuple[str, str, str]], out_path: Optional[Path]):
    shape_for = {
        "origin": "diamond",
        "quest": "box",
        "goal": "ellipse",
        "flow": "note",
        "location": "oval",
        "external": "plaintext",
    }
    lines = ["digraph story_graph {", "  rankdir=LR;", "  node [fontname=\"Helvetica\"];\n"]
    for n in nodes.values():
        shape = shape_for.get(n.kind, "box")
        safe_label = n.label.replace("\"", r"\"")
        lines.append(f'  "{n.node_id}" [label="{safe_label}" shape={shape}];')
    lines.append("")
    for src, dst, kind in sorted(edges):
        lines.append(f'  "{src}" -> "{dst}" [label="{kind}"];')
    lines.append("}\n")

    output = "\n".join(lines)
    if out_path:
        out_path.write_text(output, encoding="utf-8")
    else:
        print(output)


def build_graph():
    docs: List[Doc] = []
    for path in DATA_DIR.rglob("*.md"):
        props, body = parse_markdown(path)
        if not props:
            continue
        otype = (props.get("type") or "").lower()
        if otype == "origin":
            otype = "story_origin"
        if otype not in {"story_origin", "quest", "scene"}:
            continue
        obj_id = (props.get("id") or props.get("name") or path.stem).lower()
        name = props.get("name", obj_id)
        docs.append(Doc(obj_id=obj_id, otype=otype, name=name, body=body or "", props=props, path=path))

    nodes: Dict[str, Node] = {}
    edges: Set[Tuple[str, str, str]] = set()
    quest_goals: Dict[str, List[Tuple[str, str, str]]] = {}

    for doc in docs:
        if doc.otype == "story_origin":
            ensure_node(nodes, f"origin:{doc.obj_id}", f"Origin: {doc.name}", "origin")
        elif doc.otype == "quest":
            ensure_node(nodes, f"quest:{doc.obj_id}", f"Quest: {doc.name}", "quest")
            quest_goals[doc.obj_id] = parse_goals(doc.body)
        elif doc.otype == "scene":
            ensure_node(nodes, f"scene:{doc.obj_id}", f"Scene: {doc.name}", "flow")

    # Quest -> Goal structural edges
    for qid, goals in quest_goals.items():
        for gid, gname, _ in goals:
            goal_node = ensure_node(nodes, f"goal:{qid}:{gid}", f"Goal: {gname}\n({qid})", "goal")
            edges.add((f"quest:{qid}", goal_node, "has-goal"))

    # Default origin->quest link when IDs match
    quest_ids = set(quest_goals.keys())
    origin_ids = {d.obj_id for d in docs if d.otype == "story_origin"}
    for oid in origin_ids:
        if oid in quest_ids:
            edges.add((f"origin:{oid}", f"quest:{oid}", "starts"))

    # Flow parsing
    for doc in docs:
        flows = extract_flows(doc)
        goals_for_doc = quest_goals.get(doc.obj_id, []) if doc.otype == "quest" else []
        for flow in flows:
            # Register flow node
            flow_label = f"{doc.obj_id} / {flow.section}"
            ensure_node(nodes, flow.node_id, flow_label, "flow")

            # Connect owner -> flow (or goal -> flow)
            attached = False
            if goals_for_doc:
                # if the section name matches a goal, attach to that goal
                section_slug = slugify(flow.section)
                for gid, _gname, _body in goals_for_doc:
                    if gid == section_slug:
                        edges.add((f"goal:{doc.obj_id}:{gid}", flow.node_id, "flow"))
                        attached = True
                        break
            if not attached:
                owner_id = f"{doc.otype}:{doc.obj_id}" if doc.otype in {"quest", "story_origin", "scene"} else flow.owner.obj_id
                edges.add((owner_id, flow.node_id, "flow"))

            # Extract target edges
            for kind, target in flow_targets(flow.text):
                if kind in {"jump", "call", "cond", "check"}:
                    dst = ensure_node(nodes, f"ext:{target}", target, "external")
                elif kind.startswith("quest"):
                    dst = ensure_node(nodes, f"quest:{target}", f"Quest: {target}", "quest")
                elif kind.startswith("goal"):
                    qid, gid = target
                    if qid is None and doc.otype == "quest":
                        qid = doc.obj_id
                    node_id = f"goal:{qid}:{gid}" if qid else f"goal:unknown:{gid}"
                    dst = ensure_node(nodes, node_id, f"Goal: {gid}\n({qid or 'unspecified'})", "goal")
                elif kind == "travel":
                    dst = ensure_node(nodes, f"loc:{target}", f"Location: {target}", "location")
                else:
                    dst = ensure_node(nodes, f"ext:{target}", target, "external")
                edges.add((flow.node_id, dst, kind))

    return nodes, edges


def main():
    parser = argparse.ArgumentParser(description="Generate a DOT graph for story/quest flows.")
    parser.add_argument("--out", type=Path, help="Path to write DOT output. Prints to stdout if omitted.")
    args = parser.parse_args()

    nodes, edges = build_graph()
    emit_dot(nodes, edges, args.out)


if __name__ == "__main__":
    main()

import re, yaml
from pathlib import Path

_fm   = re.compile(r"^---\s*\n(.*?)\n---\s*\n?", re.S)
_head = re.compile(r"^(#{1,6})\s+(.+)", re.M)
_code = re.compile(r"```(\w+)?\n(.*?)```", re.S)

md_codeblock_parsers = {
    "yaml": lambda code: yaml.safe_load(code)
}

import re, yaml
from itertools import islice

_fm   = re.compile(r"^---\s*\n(.*?)\n---\s*\n?", re.S)
_head = re.compile(r"^(#{1,6})\s+(.+)", re.M)
_code = re.compile(r"```(\w+)?\n(.*?)```", re.S)

def parse_markdown(text: str):
    fm_match = _fm.match(text)
    frontmatter = yaml.safe_load(fm_match.group(1)) if fm_match else {}
    body = text[fm_match.end():] if fm_match else text

    headings = {}
    stack = []  # [(depth, name)]

    matches = list(_head.finditer(body))
    for i, h in enumerate(matches):
        depth = len(h.group(1))
        name  = h.group(2).strip()

        while stack and stack[-1][0] >= depth:
            stack.pop()
        stack.append((depth, name))

        hid = "#".join(n for _, n in stack)

        start = h.end()
        end   = matches[i+1].start() if i+1 < len(matches) else len(body)
        section = body[start:end]

        blocks = []
        for lang, code in _code.findall(section):
            lang = (lang or "").lower()
            if lang in md_codeblock_parsers:
                parsed = md_codeblock_parsers[lang](code)
                blocks.append({"language": lang, "parsed": parsed})
            else:
                blocks.append({"language": lang, "content": code})
        
        headings[hid] = {
            "name": name,
            "depth": depth,
            "codeblocks": blocks,
        }

    return frontmatter or {}, headings



# usage
# text = Path("file.md").read_text(encoding="utf-8")
# fm, heads = parse_markdown(text)

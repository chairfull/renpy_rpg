import re, yaml
from pathlib import Path

_fm   = re.compile(r"^---\s*\n(.*?)\n---\s*\n?", re.S)
_head = re.compile(r"^(#{1,6})\s+(.+)", re.M)
_code = re.compile(r"```(\w+)?\n(.*?)```", re.S)

re_flow_action = re.compile(
    r'^(?P<head>[A-Z]{3,}[A-Z0-9_]*)'
    r'(?:\s+(?:(?P<kw>[a-zA-Z_]\w*)='
    r'(?P<kwval>"[^"]*"|\[[^\]]*\]|[^\s]+)'
    r'|(?P<arg>"[^"]*"|\[[^\]]*\]|[^\s]+)))*$'
)

def flow_to_rpy(code):
    rpy = []
    for line in code.splitlines(): 
        line = line.strip()
        if not line:
            continue

        # Code line.
        if line.startswith("$"):
            rpy.append(line)
            continue
        
        # Action line.
        m = re_flow_action.match(line)
        if m:
            head = m.group("head")
            tokens = line.split()[1:]
            args = []
            kwargs = []
            for t in tokens:
                if "=" in t and not t.startswith('"'):
                    k, v = t.split("=", 1)
                    kwargs.append(f"{k}={v}")
                else:
                    args.append(t)
            
            rpy.append(f"$ {head.lower()}({', '.join(args + kwargs)})")
            continue
        
        # Speaker.
        if ": " in line:
            head, rest = line.split(":", 1)
            rpy.append(f'{head} "{rest.strip()}"')
            continue
        
        # No speaker text.
        rpy.append(f'"{line}"')
    return "\n".join(rpy)

md_codeblock_parsers = {
    "yaml": lambda code: yaml.safe_load(code),
    "flow": lambda code: flow_to_rpy(code),
 }

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
            # else:
            #     blocks.append({"language": lang, "content": code})
        
        headings[hid] = {
            "name": name,
            "depth": depth,
            "codeblocks": blocks,
        }

    return frontmatter or {}, headings



# usage
# text = Path("file.md").read_text(encoding="utf-8")
# fm, heads = parse_markdown(text)

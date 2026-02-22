import re, yaml
from pathlib import Path

re_md_front_matter = re.compile(r"^---\s*\n(.*?)\n---\s*\n?", re.S)
re_md_heading = re.compile(r"^(#{1,6})\s+(.+)", re.M)
re_md_code_block = re.compile(r"```(\w+)?\n(.*?)```", re.S)

re_flow_action_head = re.compile(r'^[A-Z]{3,}[A-Z0-9_]*')

def safe_var(md_id, var):
    if var.startswith("#"): return f'"{md_id}{var}"'.replace("-", "_")
    if var.replace("-", "_") == md_id: return f'"{md_id}"'.replace("-", "_")
    return var

def safe_key(key):
    if key in ["from", "to"]:
        return "_" + key
    return key

def flow_action_tokenize(md_id, s):
    tokens = []
    buf = []
    depth = 0
    quote = None

    for c in s:
        if quote:
            buf.append(c)
            if c == quote:
                quote = None
            continue

        if c in ('"', "'"):
            quote = c
            buf.append(c)
            continue

        if c in "([{":
            depth += 1
        elif c in ")]}":
            depth -= 1

        if c.isspace() and depth == 0:
            if buf:
                tokens.append("".join(buf))
                buf = []
        else:
            buf.append(c)

    if buf:
        tokens.append("".join(buf))

    head = tokens[0]
    args = []
    kwargs = []

    for tok in tokens[1:]:
        if "=" in tok:
            k, v = tok.split("=", 1)
            kwargs.append(f"{safe_key(k)}={safe_var(md_id, v)}")
        else:
            args.append(safe_var(md_id, tok))
    
    return head, args, kwargs


def flow_to_rpy(md_id, code, actions):
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
        m = re_flow_action_head.match(line)
        if m:
            head, args, kwargs = flow_action_tokenize(md_id, line)
            actions[head] = actions.get(head, 0) + 1
            rpy.append(f"$ call_flow_action({head}, {', '.join(args + kwargs)})")
            continue
        
        # Speaker.
        if ": " in line:
            head, rest = line.split(":", 1)
            rpy.append(f'{head} "{rest.strip()}"')
            continue
        
        # No speaker text.
        rpy.append(f'"{line}"')
    return "\n".join(rpy)

def parse_yaml(text: str):
    return yaml.safe_load(text)

def parse_markdown(text: str):
    fm_match = re_md_front_matter.match(text)
    frontmatter = yaml.safe_load(fm_match.group(1)) if fm_match else {}
    body = text[fm_match.end():] if fm_match else text

    headings = {}
    stack = [] # [(depth, name)]

    matches = list(re_md_heading.finditer(body))
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
        for lang, code in re_md_code_block.findall(section):
            blocks.append({"lang": lang, "code": code})
        
        headings[hid] = { "name": name, "depth": depth, "codeblocks": blocks, }

    return frontmatter or {}, headings

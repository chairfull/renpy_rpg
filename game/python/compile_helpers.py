import re
import yaml
from typing import List, Tuple, Dict, Any

def parse_markdown(filepath: str):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            raw_lines = f.read().splitlines()
    except Exception as e:
        return None, None, None, None

    delim_idxs = [i for i, line in enumerate(raw_lines) if line.strip() == "---"]
    if len(delim_idxs) < 2:
        return None, None, None, None

    start = delim_idxs[0]
    end = delim_idxs[1]
    props_lines = raw_lines[start + 1:end]
    body_raw_lines = raw_lines[end + 1:]
    body_start_line = end + 2  # 1-based

    props: Dict[str, Any] = {}
    i = 0
    while i < len(props_lines):
        line = props_lines[i]
        if not line.strip():
            i += 1
            continue
        if ':' in line and not line.strip().startswith('-'):
            k, v = line.split(':', 1)
            k, v = k.strip(), v.strip().strip('"').strip("'")
            if not v: # Block value
                block = []
                j = i + 1
                while j < len(props_lines) and (not props_lines[j].strip() or props_lines[j].startswith(' ') or props_lines[j].strip().startswith('-')):
                    if props_lines[j].strip():
                        block.append(props_lines[j])
                    j += 1
                props[k] = block
                i = j
                continue
            props[k] = v
        i += 1

    body = "\n".join(body_raw_lines).strip()
    body_lines = [(body_start_line + i, line) for i, line in enumerate(body_raw_lines)]
    return props, body, body_start_line, body_lines

def parse_yaml_list(lines: List[str]):
    if not lines:
        return []
    try:
        yaml_content = "\n".join(lines)
        data = yaml.safe_load(yaml_content)
        if isinstance(data, list):
            return data
        elif isinstance(data, dict):
            return [data]
        return []
    except Exception:
        return []

def parse_yaml_block(value, default=None):
    if value is None:
        return default if default is not None else {}
    if isinstance(value, dict):
        return value
    if isinstance(value, str):
        try:
            data = yaml.safe_load(value)
            return data if data is not None else (default if default is not None else {})
        except Exception:
            return default if default is not None else {}
    if isinstance(value, list):
        try:
            data = yaml.safe_load("\n".join(value))
            return data if data is not None else (default if default is not None else {})
        except Exception:
            return default if default is not None else {}
    return default if default is not None else {}

def parse_counts(val) -> Dict[str, int]:
    res: Dict[str, int] = {}
    if isinstance(val, list):
        for item in val:
            if isinstance(item, dict):
                for k, v in item.items():
                    try:
                        res[str(k).strip()] = int(v)
                    except Exception:
                        continue
            elif isinstance(item, str) and ':' in item:
                k, v = item.split(':', 1)
                try:
                    res[k.strip()] = int(v.strip())
                except Exception:
                    continue
    elif isinstance(val, dict):
        for k, v in val.items():
            try:
                res[str(k).strip()] = int(v)
            except Exception:
                continue
    return res

def parse_csv(value) -> List[str]:
    if not value:
        return []
    if isinstance(value, list):
        result = []
        for item in value:
            item_str = str(item)
            cleaned = item_str.strip()
            if cleaned.startswith('- '):
                cleaned = cleaned[2:].strip()
            elif cleaned.startswith('-'):
                cleaned = cleaned[1:].strip()
            result.extend([x.strip() for x in cleaned.split(',') if x.strip()])
        return result
    if isinstance(value, str):
        cleaned = value.strip()
        if cleaned.startswith('[') and cleaned.endswith(']'):
            cleaned = cleaned[1:-1]
        return [x.strip() for x in cleaned.split(',') if x.strip()]
    return []

def parse_bool(value, default=False):
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in ("1", "true", "yes", "y", "on")

def parse_int(value, default=None):
    if value is None or value == "":
        return default
    try:
        return int(value)
    except Exception:
        return default

def parse_float(value, default=None):
    if value is None or value == "":
        return default
    try:
        return float(value)
    except Exception:
        return default

def parse_kv_block(lines: List[str]):
    result = {}
    if not isinstance(lines, list):
        return result
    for line in lines:
        line = line.strip()
        if ':' in line:
            k, v = line.split(':', 1)
            k = k.strip().replace('- ', '')
            try:
                result[k] = int(v.strip())
            except ValueError:
                try:
                    result[k] = float(v.strip())
                except ValueError:
                    result[k] = v.strip()
    return result

def slugify_segment(text: str) -> str:
    if text is None:
        return "loc"
    s = str(text).strip().lower()
    s = re.sub(r'[^a-z0-9\s_-]', '', s)
    s = s.replace('_', '-')
    s = re.sub(r'\s+', '-', s)
    s = re.sub(r'-+', '-', s).strip('-')
    return s or "loc"

def label_safe(text: str) -> str:
    if text is None:
        return "id"
    s = re.sub(r'[^0-9a-zA-Z_]+', '_', str(text))
    s = re.sub(r'_+', '_', s).strip('_')
    return s or "id"

def _lines_to_text(lines_with_no: List[Tuple[int, str]]) -> str:
    return "\n".join(line for _, line in lines_with_no).strip()

def extract_flow_blocks(lines_with_no: List[Tuple[int, str]]):
    blocks = []
    in_block = False
    block_lines = []
    start_line = None
    for line_no, line in lines_with_no:
        if not in_block:
            if re.match(r'^\s*```flow\b', line):
                in_block = True
                block_lines = []
                start_line = (line_no + 1) if line_no is not None else None
            continue
        if line.strip().startswith("``"):
            end_line = block_lines[-1][0] if block_lines else start_line
            blocks.append({
                "lines": block_lines,
                "start_line": start_line,
                "end_line": end_line
            })
            in_block = False
            block_lines = []
            start_line = None
            continue
        block_lines.append((line_no, line))
    if in_block:
        end_line = block_lines[-1][0] if block_lines else start_line
        blocks.append({
            "lines": block_lines,
            "start_line": start_line,
            "end_line": end_line
        })
    return blocks

def extract_yaml_block(lines_with_no: List[Tuple[int, str]]):
    if not lines_with_no:
        return {}, lines_with_no
    start = None
    end = None
    for i, (_, line) in enumerate(lines_with_no):
        if line.strip().startswith("```yaml"):
            start = i
            break
    if start is None:
        return {}, lines_with_no
    for j in range(start + 1, len(lines_with_no)):
        if lines_with_no[j][1].strip().startswith("``"):
            end = j
            break
    if end is None:
        return {}, lines_with_no
    yaml_lines = [line for _, line in lines_with_no[start + 1:end]]
    yaml_text = "\n".join(yaml_lines)
    try:
        data = yaml.safe_load(yaml_text) or {}
    except Exception:
        data = {}
    cleaned_lines = lines_with_no[:start] + lines_with_no[end + 1:]
    return data, cleaned_lines

def find_named_section(body_lines: List[Tuple[int, str]], title: str):
    if not body_lines:
        return [], None
    start = None
    base_level = None
    title_re = re.compile(r'^(#+)\s*' + re.escape(title) + r'\s*$', re.IGNORECASE)
    for i, (_, line) in enumerate(body_lines):
        m = title_re.match(line.strip())
        if m:
            start = i
            base_level = len(m.group(1))
            break
    if start is None:
        return [], None
    end = len(body_lines)
    for j in range(start + 1, len(body_lines)):
        m = re.match(r'^(#+)\s+', body_lines[j][1])
        if m and len(m.group(1)) <= base_level:
            end = j
            break
    section_lines = body_lines[start + 1:end]
    return section_lines, base_level

def extract_named_section(body_lines: List[Tuple[int, str]], title: str):
    """Extract a markdown section by heading title, return (section_lines, clean_lines, base_level)."""
    if not body_lines:
        return [], body_lines, None
    start = None
    base_level = None
    title_re = re.compile(r'^(#+)\s*' + re.escape(title) + r'\s*$', re.IGNORECASE)
    for i, (_, line) in enumerate(body_lines):
        m = title_re.match(line.strip())
        if m:
            start = i
            base_level = len(m.group(1))
            break
    if start is None:
        return [], body_lines, None
    end = len(body_lines)
    for j in range(start + 1, len(body_lines)):
        m = re.match(r'^(#+)\s+', body_lines[j][1])
        if m and len(m.group(1)) <= base_level:
            end = j
            break
    section_lines = body_lines[start + 1:end]
    clean_lines = body_lines[:start] + body_lines[end:]
    return section_lines, clean_lines, base_level

def extract_locations_section(body_lines: List[Tuple[int, str]]):
    if not body_lines:
        return [], body_lines
    start = None
    base_level = None
    for i, (_, line) in enumerate(body_lines):
        m = re.match(r'^(#+)\s*Locations\s*$', line.strip(), re.IGNORECASE)
        if m:
            start = i
            base_level = len(m.group(1))
            break
    if start is None:
        return [], body_lines
    end = len(body_lines)
    for j in range(start + 1, len(body_lines)):
        m = re.match(r'^(#+)\s+', body_lines[j][1])
        if m and len(m.group(1)) <= base_level:
            end = j
            break
    section_lines = body_lines[start + 1:end]
    clean_lines = body_lines[:start] + body_lines[end:]
    nodes = []
    stack = []
    current = None
    for line_no, line in section_lines:
        m = re.match(r'^(#+)\s+(.*)$', line)
        if m:
            level = len(m.group(1))
            title = m.group(2).strip()
            if level <= base_level:
                break
            while stack and stack[-1]["level"] >= level:
                stack.pop()
            parent = stack[-1] if stack else None
            node = {
                "title": title,
                "level": level,
                "slug": slugify_segment(title),
                "content_lines": [],
                "parent": parent,
                "children": []
            }
            nodes.append(node)
            if parent:
                parent["children"].append(node)
            stack.append(node)
            current = node
            continue
        if current:
            current["content_lines"].append((line_no, line))
    return nodes, clean_lines

def split_sections(body_lines: List[Tuple[int, str]]):
    sections = []
    stack = []
    current = None
    for line_no, line in body_lines:
        m = re.match(r'^(#+)\s+(.*)$', line)
        if m:
            level = len(m.group(1))
            title = m.group(2).strip()
            slug = label_safe(title).lower()
            while stack and stack[-1][0] >= level:
                stack.pop()
            stack.append((level, slug))
            path = "__".join(item[1] for item in stack)
            if current:
                sections.append(current)
            current = {
                "heading": title,
                "path": path,
                "heading_line": line_no,
                "lines": []
            }
            continue
        if current:
            current["lines"].append((line_no, line))
    if current:
        sections.append(current)
    return sections

__all__ = [
    "parse_markdown", "parse_yaml_list", "parse_yaml_block", "parse_counts", "parse_csv",
    "parse_bool", "parse_int", "parse_float", "parse_kv_block", "slugify_segment",
    "label_safe", "_lines_to_text", "extract_flow_blocks", "extract_yaml_block",
    "find_named_section", "split_sections"
]

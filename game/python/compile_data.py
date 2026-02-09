import os
import re
import json
import yaml
import argparse
import sys
import shlex

def parse_markdown(filepath):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            raw_lines = f.read().splitlines()
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return None, None, None, None
    
    delim_idxs = [i for i, line in enumerate(raw_lines) if line.strip() == "---"]
    if len(delim_idxs) < 2:
        return None, None, None, None
    
    start = delim_idxs[0]
    end = delim_idxs[1]
    props_lines = raw_lines[start + 1:end]
    body_raw_lines = raw_lines[end + 1:]
    body_start_line = end + 2  # 1-based
    
    props = {}
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

def parse_yaml_list(lines):
    """Safely parse a block of YAML lines into a list of dictionaries."""
    if not lines:
        return []
    try:
        # Join the lines with newlines to form a valid YAML block string
        yaml_content = "\n".join(lines)
        data = yaml.safe_load(yaml_content)
        if isinstance(data, list):
            return data
        elif isinstance(data, dict):
             # Sometimes it might be a single dict if not starting with "-"
             return [data]
        return []
    except Exception as e:
        print(f"Error parsing YAML list block: {e}")
        return []

def parse_yaml_block(value, default=None):
    """Safely parse a block of YAML lines into a dict or list."""
    if value is None:
        return default if default is not None else {}
    if isinstance(value, (dict, list)):
        return value
    if isinstance(value, str):
        try:
            data = yaml.safe_load(value)
            return data if data is not None else (default if default is not None else {})
        except Exception as e:
            print(f"Error parsing YAML block: {e}")
            return default if default is not None else {}
    if isinstance(value, list):
        try:
            data = yaml.safe_load("\n".join(value))
            return data if data is not None else (default if default is not None else {})
        except Exception as e:
            print(f"Error parsing YAML block: {e}")
            return default if default is not None else {}
    return default if default is not None else {}

def parse_counts(val):
    """Parse a YAML list/dict of counts into a {id: count} dict."""
    res = {}
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

def parse_csv(value):
    """Safely parse a comma-separated value that might be a string, list, or empty."""
    if not value:
        return []
    if isinstance(value, list):
        # Already a list - flatten and clean
        result = []
        for item in value:
            if isinstance(item, str):
                # Clean YAML list markers if present
                cleaned = item.strip()
                if cleaned.startswith('- '):
                    cleaned = cleaned[2:].strip()
                elif cleaned.startswith('-'):
                    cleaned = cleaned[1:].strip()
                
                # Split by comma in case it's a mix
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

def parse_kv_block(lines):
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

def slugify_segment(text):
    if text is None:
        return "loc"
    s = str(text).strip().lower()
    s = re.sub(r'[^a-z0-9\s_-]', '', s)
    s = s.replace('_', '-')
    s = re.sub(r'\s+', '-', s)
    s = re.sub(r'-+', '-', s).strip('-')
    return s or "loc"

def label_safe(text):
    if text is None:
        return "id"
    s = re.sub(r'[^0-9a-zA-Z_]+', '_', str(text))
    s = re.sub(r'_+', '_', s).strip('_')
    return s or "id"

def _lines_to_text(lines_with_no):
    return "\n".join(line for _, line in lines_with_no).strip()

def extract_locations_section(body_lines):
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

def extract_named_section(body_lines, title):
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

def find_named_section(body_lines, title):
    """Find a markdown section by heading title, return (section_lines, base_level)."""
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

def split_sections(body_lines):
    sections = []
    current = None
    for line_no, line in body_lines:
        m = re.match(r'^(#+)\s+(.*)$', line)
        if m:
            if current:
                sections.append(current)
            current = {
                "heading": m.group(2).strip(),
                "heading_line": line_no,
                "lines": []
            }
            continue
        if current:
            current["lines"].append((line_no, line))
    if current:
        sections.append(current)
    return sections

def extract_flow_blocks(lines_with_no):
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
        if line.strip().startswith("```"):
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

def extract_yaml_block(lines_with_no):
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
        if lines_with_no[j][1].strip().startswith("```"):
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

FLOW_COMMANDS = {
    "event",
    "flag",
    "give",
    "take",
    "gold",
    "travel",
    "rest",
    "scavenge",
    "jump",
    "call",
    "cond",
    "quest",
    "goal",
    "check",
    "notify",
    "companion",
    "perk",
    "status",
    "bond",
    "item",
}

def is_caps_command(line):
    stripped = line.strip()
    if not stripped:
        return False
    token = stripped.split()[0]
    if token.endswith(':'):
        token = token[:-1]
    return token.isupper() and token.lower() in FLOW_COMMANDS

def directive_to_python(line):
    raw = line.strip()
    if raw.startswith('@'):
        raw = raw[1:].strip()
    if not raw:
        return None
    try:
        parts = shlex.split(raw)
    except Exception:
        return None
    if not parts:
        return None
    cmd = parts[0]
    if cmd.endswith(':'):
        cmd = cmd[:-1]
    cmd = cmd.lower()
    if cmd == "event":
        if len(parts) < 2:
            return None
        event = parts[1]
        kwargs = []
        for token in parts[2:]:
            if '=' not in token:
                continue
            k, v = token.split('=', 1)
            try:
                val = yaml.safe_load(v)
            except Exception:
                val = v
            kwargs.append(f"{k}={repr(val)}")
        if kwargs:
            return f"event_manager.dispatch({event!r}, {', '.join(kwargs)})"
        return f"event_manager.dispatch({event!r})"
    if cmd == "flag":
        if len(parts) < 3:
            return None
        op = parts[1].lower()
        name = parts[2]
        if op == "set":
            val = True
            if len(parts) > 3:
                try:
                    val = yaml.safe_load(parts[3])
                except Exception:
                    val = parts[3]
            return f"flag_set({name!r}, {repr(val)})"
        if op == "clear":
            return f"flag_clear({name!r})"
        if op == "toggle":
            return f"flag_toggle({name!r})"
    if cmd == "give":
        if len(parts) < 2:
            return None
        item_id = parts[1]
        count = None
        src = None
        dst = None
        for token in parts[2:]:
            if token.isdigit():
                count = int(token)
                continue
            if ':' in token:
                k, v = token.split(':', 1)
                k = k.strip().lower()
                v = v.strip()
                if k == "from":
                    src = v
                elif k == "to":
                    dst = v
                elif k == "count":
                    try:
                        count = int(v)
                    except Exception:
                        pass
        if src or dst:
            return f"give_item_between({item_id!r}, {src!r}, {dst!r}, {count or 1})"
        count = count or (int(parts[2]) if len(parts) > 2 and parts[2].isdigit() else 1)
        return f"give_item({item_id!r}, {count})"
    if cmd == "take":
        if len(parts) < 2:
            return None
        item_id = parts[1]
        count = int(parts[2]) if len(parts) > 2 else 1
        return f"take_item({item_id!r}, {count})"
    if cmd == "gold":
        if len(parts) < 2:
            return None
        try:
            amt = int(parts[1])
        except Exception:
            return None
        return f"add_gold({amt})"
    if cmd == "travel":
        if len(parts) < 2:
            return None
        loc_id = parts[1]
        return f"rpg_world.move_to({loc_id!r})"
    if cmd == "rest":
        hours = int(parts[1]) if len(parts) > 1 else 1
        return f"rest({hours})"
    if cmd == "scavenge":
        return "scavenge_location()"
    if cmd == "jump":
        if len(parts) < 2:
            return None
        label = parts[1]
        return f"renpy.jump({label!r})"
    if cmd == "call":
        if len(parts) < 2:
            return None
        label = parts[1]
        return f"renpy.call({label!r})"
    if cmd == "quest":
        if len(parts) < 3: return None
        sub = parts[1].lower()
        qid = parts[2]
        if sub == "start": return f"quest_manager.start_quest({qid!r})"
        if sub == "complete": return f"quest_manager.complete_quest({qid!r})"
        if sub == "fail": return f"quest_manager.fail_quest({qid!r})"
    if cmd == "goal":
        if len(parts) < 3: return None
        sub = parts[1].lower()
        if len(parts) > 3:
            qid, gid = parts[2], parts[3]
        else:
            qid, gid = "None", parts[2]
        
        status = {"show": "active", "hide": "hidden", "complete": "complete", "active": "active"}.get(sub, "active")
        return f"quest_manager.update_goal({qid!r} if {qid!r} != 'None' else None, {gid!r}, {status!r})"
    if cmd == "cond":
        if len(parts) < 3:
            return None
        expr = parts[1]
        label_true = parts[2]
        label_false = parts[3] if len(parts) > 3 else None
        return f"cond_jump({expr!r}, {label_true!r}, {label_false!r})"
    if cmd == "quest":
        if len(parts) < 3:
            return None
        op = parts[1].lower()
        qid = parts[2]
        if op == "start":
            return f"quest_manager.start_quest({qid!r})"
        if op == "complete":
            return f"quest_manager.complete_quest({qid!r})"
        if op == "fail":
            return f"quest_manager.fail_quest({qid!r})"
    if cmd == "goal":
        if len(parts) < 3:
            return None
        op = parts[1].lower()
        if len(parts) >= 4:
            qid = parts[2]
            gid = parts[3]
        else:
            qid = None
            gid = parts[2]
        qid_expr = repr(qid) if qid is not None else "None"
        if op in ["show", "active"]:
            return f"quest_manager.update_goal({qid_expr}, {gid!r}, status='active')"
        if op == "hide":
            return f"quest_manager.update_goal({qid_expr}, {gid!r}, status='hidden')"
        if op == "complete":
            return f"quest_manager.update_goal({qid_expr}, {gid!r}, status='complete')"
    if cmd == "check":
        if len(parts) < 4:
            return None
        stat = parts[1]
        try:
            dc = int(parts[2])
        except Exception:
            return None
        label_true = parts[3]
        label_false = parts[4] if len(parts) > 4 else None
        return f"contested_check({stat!r}, {dc}, success_label={label_true!r}, fail_label={label_false!r})"
    if cmd == "notify":
        if len(parts) < 2:
            return None
        text = " ".join(parts[1:])
        return f"renpy.notify({text!r})"
    if cmd == "companion":
        if len(parts) < 3:
            return None
        op = parts[1].lower()
        cid = parts[2]
        if op == "add":
            return f"companion_add({cid!r})"
        if op == "remove":
            return f"companion_remove({cid!r})"
    if cmd == "perk":
        if len(parts) < 3:
            return None
        op = parts[1].lower()
        pid = parts[2]
        if op == "add":
            mins = int(parts[3]) if len(parts) > 3 else None
            return f"perk_add({pid!r}, {mins})"
        if op == "remove":
            return f"perk_remove({pid!r})"
    if cmd == "status":
        if len(parts) < 3:
            return None
        op = parts[1].lower()
        sid = parts[2]
        if op == "add":
            mins = int(parts[3]) if len(parts) > 3 else None
            return f"status_add({sid!r}, {mins})"
        if op == "remove":
            return f"status_remove({sid!r})"
    if cmd == "bond":
        if len(parts) < 4:
            return None
        op = parts[1].lower()
        other = parts[2]
        name = parts[3]
        if op == "add":
            if len(parts) < 5:
                return None
            try:
                delta = int(parts[4])
            except Exception:
                return None
            return f"bond_add_stat(pc.id, {other!r}, {name!r}, {delta})"
        if op == "set":
            if len(parts) < 5:
                return None
            try:
                value = int(parts[4])
            except Exception:
                return None
            return f"bond_set_stat(pc.id, {other!r}, {name!r}, {value})"
        if op == "tag":
            if len(parts) < 5:
                return None
            tag = parts[4]
            return f"bond_add_tag(pc.id, {other!r}, {tag!r})"
        if op == "untag":
            if len(parts) < 5:
                return None
            tag = parts[4]
            return f"bond_remove_tag(pc.id, {other!r}, {tag!r})"
    if cmd == "item":
        if len(parts) < 2:
            return None
        op = parts[1].lower()
        if op in ["show", "display"]:
            item_id = parts[2] if len(parts) > 2 else None
            if item_id:
                return f"item_show_image({item_id!r})"
            return "item_show_image(None)"
        if op in ["hide", "clear"]:
            return "item_hide_image()"
    return None

def compile(lint_only=False):
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    game_dir = os.path.join(base_dir, "game")
    data_dir = os.path.join(base_dir, "data") # Moved to root
    # JSON goes to a hidden folder; labels go to a non-hidden .rpy so Ren'Py loads them.
    gen_dir = os.path.join(game_dir, ".generated")
    if not os.path.exists(gen_dir):
        os.makedirs(gen_dir)
    
    labels_file = os.path.join(gen_dir, "generated_labels.rpy")
    json_file = os.path.join(gen_dir, "generated_json.json")
    
    script_parts = ["# AUTOMATICALLY GENERATED LABELS - DO NOT EDIT\n"]
    data_consolidated = {
        "items": {},
        "characters": {},
        "locations": {},
        "quests": {},
        "containers": {},
        "stats": {},
        "factions": {},
        "slots": {},
        "body_types": {},
        "dialogue": {},
        "story_origins": {},
        "shops": {},
        "recipes": {},
        "notes": {},
        "achievements": {},
        "perks": {},
        "status_effects": {},
        "bonds": {}
    }
    errors = []
    warnings = []
    source_info = {}

    def _is_origin_path(rel_path):
        rel_norm = rel_path.replace(os.sep, "/")
        return rel_norm.startswith("quests/origins/")
    
    def parse_quest_ticks(body, qid):
        def slug(s): return s.lower().replace(' ', '_')
        ticks = []
        sections = re.split(r'(?m)^##\s*', body)
        for sec in sections[1:]: # Skip intro
            lines = sec.split('\n', 1)
            name = lines[0].strip()
            sid = slug(name)
            content = lines[1] if len(lines) > 1 else ""
            
            trigger = {}
            trig_match = re.search(r'```trigger\s*\n(.*?)\n```', content, re.DOTALL)
            if trig_match:
                try:
                    trigger = yaml.safe_load(trig_match.group(1))
                except:
                    print(f"Error parsing trigger for {qid}:{sid}")
            
            ticks.append({
                "id": sid,
                "name": name,
                "trigger": trigger,
                "label": f"QUEST__{qid}__{sid}"
            })
        return ticks

    for root, dirs, files in os.walk(data_dir):
        for f in files:
            if not f.endswith(".md"):
                continue
            
            full_path = os.path.join(root, f)
            rel_path = os.path.relpath(full_path, data_dir)
            props, body, body_start_line, body_lines = parse_markdown(full_path)
            
            if not props:
                continue
            source_path = os.path.join("data", rel_path).replace(os.sep, "/")
            if body_lines is None:
                body_lines = []
            
            obj_id = props.get('id', props.get('name', 'unknown')).lower()
            otype = str(props.get('type', 'location')).strip().lower()
            if otype in ["origin", "story_origin"]:
                # Origins are treated as quests with an origin flag.
                otype = "quest"
                if "origin" not in props:
                    props["origin"] = True
                if not _is_origin_path(rel_path):
                    warnings.append(f"origin quest {obj_id}: consider moving to data/quests/origins/")
            
            # Store in JSON data
            if otype == 'item':
                stack_size = parse_int(props.get('stack_size'), 1) or 1
                data_consolidated["items"][obj_id] = {
                    "name": props.get('name', obj_id),
                    "description": props.get('description', ''),
                    "image": props.get('image'),
                    "weight": float(props.get('weight', 0)),
                    "volume": float(props.get('volume', 0) or 0),
                    "value": int(props.get('value', 0)),
                    "tags": parse_csv(props.get('tags', '')),
                    "factions": parse_csv(props.get('factions', '')),
                    "equip_slots": parse_csv(props.get('equip_slots', '')),
                    "outfit_part": props.get('outfit_part'),
                    "stackable": parse_bool(props.get('stackable', False)) or stack_size > 1,
                    "stack_size": stack_size
                }
            elif otype == 'location':
                # Parse list of entities/links
                raw_ents = props.get('entities', [])
                if isinstance(raw_ents, list):
                    entities = parse_yaml_list(raw_ents)
                else:
                    entities = []
                
                raw_enc = props.get('encounters', [])
                if isinstance(raw_enc, list):
                    encounters = parse_yaml_list(raw_enc)
                else:
                    encounters = []
                
                raw_scav = props.get('scavenge', [])
                if isinstance(raw_scav, list):
                    scavenge = parse_yaml_list(raw_scav)
                else:
                    scavenge = []
                # Extract child locations from body (# Locations section)
                child_nodes, cleaned_lines = extract_locations_section(body_lines)
                cleaned_body = _lines_to_text(cleaned_lines) if cleaned_lines is not None else (body or "")
                data_consolidated["locations"][obj_id] = {
                    "name": props.get('name', obj_id),
                    "description": props.get('description', ''),
                    "map_image": props.get('map_image'),
                    "obstacles": props.get('obstacles', []),
                    "entities": entities,
                    "encounters": encounters,
                    "scavenge": scavenge,
                    "body": cleaned_body if cleaned_body is not None else body, # Store body for second pass
                    # Map Fields
                    "parent": props.get('parent'),
                    "map_type": props.get('map_type', 'world'),
                    "map_x": int(props.get('map_x', 0)),
                    "map_y": int(props.get('map_y', 0)),
                    "zoom_range": parse_csv(props.get('zoom_range', '0.0, 99.0')),
                    "floor_idx": int(props.get('floor_idx', 0)),
                    "tags": parse_csv(props.get('tags', '')),
                    "factions": parse_csv(props.get('factions', ''))
                }
                source_info[("locations", obj_id)] = {
                    "path": source_path,
                    "body_lines": cleaned_lines if cleaned_lines is not None else []
                }
                # Add child locations defined in the body
                if child_nodes:
                    def _as_list(val):
                        if val is None:
                            return []
                        if isinstance(val, list):
                            return val
                        if isinstance(val, dict):
                            return [val]
                        return []

                    def _build_child(node, parent_id, parent_loc):
                        full_id = f"{parent_id}#{node['slug']}"
                        if full_id in data_consolidated["locations"]:
                            warnings.append(f"location {full_id}: duplicate child id, skipped")
                            return
                        raw_lines = node.get("content_lines", []) or []
                        yaml_props, child_body_lines = extract_yaml_block(raw_lines)
                        child_body = _lines_to_text(child_body_lines)
                        # Inherit map values from parent unless overridden
                        map_type = yaml_props.get('map_type', parent_loc.get('map_type', 'world'))
                        map_x = parse_int(yaml_props.get('map_x'), parent_loc.get('map_x', 0))
                        map_y = parse_int(yaml_props.get('map_y'), parent_loc.get('map_y', 0))
                        zoom_range = parse_csv(yaml_props.get('zoom_range', parent_loc.get('zoom_range', '0.0, 99.0')))
                        floor_idx = parse_int(yaml_props.get('floor_idx'), parent_loc.get('floor_idx', 0))
                        entities = _as_list(yaml_props.get('entities', []))
                        encounters = _as_list(yaml_props.get('encounters', []))
                        scavenge = _as_list(yaml_props.get('scavenge', []))
                        child_loc = {
                            "name": yaml_props.get('name', node.get('title') or node.get('slug')),
                            "description": yaml_props.get('description', ''),
                            "map_image": yaml_props.get('map_image'),
                            "obstacles": yaml_props.get('obstacles', []),
                            "entities": entities,
                            "encounters": encounters,
                            "scavenge": scavenge,
                            "body": child_body,
                            "parent": parent_id,
                            "map_type": map_type,
                            "map_x": int(map_x) if map_x is not None else 0,
                            "map_y": int(map_y) if map_y is not None else 0,
                            "zoom_range": zoom_range,
                            "floor_idx": int(floor_idx) if floor_idx is not None else 0,
                            "tags": parse_csv(yaml_props.get('tags', '')),
                            "factions": parse_csv(yaml_props.get('factions', ''))
                        }
                        data_consolidated["locations"][full_id] = child_loc
                        source_info[("locations", full_id)] = {
                            "path": source_path,
                            "body_lines": child_body_lines
                        }
                        for child in node.get("children", []):
                            _build_child(child, full_id, child_loc)

                    parent_loc = data_consolidated["locations"][obj_id]
                    # Only top-level child nodes should be attached to this parent
                    for node in child_nodes:
                        if node.get("parent") is None:
                            _build_child(node, obj_id, parent_loc)
            elif otype == 'character':
                pos = props.get('pos', '0,0').split(',')
                # Parse equipment block
                equipment_raw = parse_yaml_block(props.get('equipment'), {})
                equipment = {}
                if isinstance(equipment_raw, list):
                    for entry in equipment_raw:
                        if isinstance(entry, dict):
                            for k, v in entry.items():
                                if v is not None and str(v).strip():
                                    equipment[str(k).strip()] = str(v).strip()
                elif isinstance(equipment_raw, dict):
                    for k, v in equipment_raw.items():
                        if v is not None and str(v).strip():
                            equipment[str(k).strip()] = str(v).strip()
                # Parse stats block if present
                stats_raw = props.get('stats', {})
                stats_dict = {}
                if isinstance(stats_raw, list):
                    stats_dict = parse_kv_block(stats_raw)
                # Parse schedule block
                schedule_raw = props.get('schedule', [])
                schedule = {}
                if isinstance(schedule_raw, list):
                    for line in schedule_raw:
                        line = line.strip()
                        if ':' in line:
                            # expecting "HH:MM: location_id" or "HH:MM: location_id"
                            # Split by FIRST colon for time, but here we have 08:00: loc
                            # So we might split by first space or handle safely
                            # Actually, YAML style: "08:00: market"
                            parts = line.split(':', 2)
                            if len(parts) >= 3:
                                # 08, 00, market
                                time_str = f"{parts[0].strip()}:{parts[1].strip()}"
                                loc_id = parts[2].strip()
                                schedule[time_str] = loc_id
                            elif len(parts) == 2:
                                # maybe "8:00 market" - irregular but possible
                                # Or just key: value
                                k, v = parts
                                schedule[k.strip()] = v.strip()

                # Extract Give section (for item gifting flows)
                give_section, body_lines, give_base = extract_named_section(body_lines, "Give")
                body = _lines_to_text(body_lines)
                give_flows = []
                give_map = {}
                if give_section and give_base is not None:
                    current = None
                    for line_no, line in give_section:
                        m = re.match(r'^(#+)\s+(.*)$', line)
                        if m and len(m.group(1)) > give_base:
                            if current:
                                give_flows.append(current)
                            current = {"title": m.group(2).strip(), "content_lines": []}
                            continue
                        if current:
                            current["content_lines"].append((line_no, line))
                    if current:
                        give_flows.append(current)
                parsed_give_flows = []
                for entry in give_flows:
                    item_title = entry.get("title", "").strip()
                    if not item_title:
                        continue
                    item_id = label_safe(item_title).lower()
                    flow_blocks = extract_flow_blocks(entry.get("content_lines") or [])
                    if not flow_blocks:
                        continue
                    flow_lines = flow_blocks[0].get("lines") or []
                    flow_content = "\n".join(line for _, line in flow_lines).strip()
                    if not flow_content:
                        continue
                    label_name = f"GIVE__{label_safe(obj_id)}__{label_safe(item_id)}"
                    give_map[item_id] = label_name
                    parsed_give_flows.append({
                        "item_id": item_id,
                        "label": label_name,
                        "flow": flow_content,
                        "flow_lines": flow_lines
                    })

                data_consolidated["characters"][obj_id] = {
                    "name": props.get('name'),
                    "description": props.get('description', ''),
                    "location": props.get('location'),
                    "items": parse_csv(props.get('items', '')),
                    "base_image": props.get('base_image'),
                    "td_sprite": props.get('sprite'), # Map to td_sprite for characters
                    "x": int(pos[0]) if len(pos) > 1 else 0,
                    "y": int(pos[1]) if len(pos) > 1 else 0,
                    "tags": parse_csv(props.get('tags', '')),
                    "factions": parse_csv(props.get('factions', '')),
                    "body_type": props.get('body_type', 'humanoid'),
                    "gender": props.get('gender'),
                    "age": props.get('age'),
                    "height": props.get('height'),
                    "weight": props.get('weight'),
                    "hair_color": props.get('hair_color'),
                    "hair_style": props.get('hair_style'),
                    "eye_color": props.get('eye_color'),
                    "face_shape": props.get('face_shape'),
                    "breast_size": props.get('breast_size'),
                    "dick_size": props.get('dick_size'),
                    "foot_size": props.get('foot_size'),
                    "skin_tone": props.get('skin_tone'),
                    "build": props.get('build'),
                    "distinctive_feature": props.get('distinctive_feature'),
                    "equipment": equipment,
                    "stats": stats_dict,
                    "affinity": int(props.get('affinity', 0)),
                    "schedule": schedule,
                    "max_weight": parse_float(props.get('max_weight')),
                    "max_slots": parse_int(props.get('max_slots')),
                    "companion_mods": parse_kv_block(props.get('companion_mods', [])) if isinstance(props.get('companion_mods', []), list) else {},
                    "body": body,
                    "give": give_map,
                    "give_flows": parsed_give_flows
                }
                source_info[("characters", obj_id)] = {
                    "path": source_path,
                    "body_lines": body_lines
                }
                
                # Check for nested Dialogue section
                dialogue_section, dialogue_base = find_named_section(body_lines, "Dialogue")
                if dialogue_section and dialogue_base is not None:
                    current = None
                    options = []
                    for line_no, line in dialogue_section:
                        m = re.match(r'^(#+)\s+(.*)$', line)
                        if m and len(m.group(1)) > dialogue_base:
                            if current:
                                options.append(current)
                            current = {
                                "title": m.group(2).strip(),
                                "heading_line": line_no,
                                "content_lines": []
                            }
                            continue
                        if current:
                            current["content_lines"].append((line_no, line))
                    if current:
                        options.append(current)

                    for opt in options:
                        opt_name = opt.get("title", "")
                        if not opt_name:
                            continue
                        opt_id = f"{obj_id}_{opt_name.lower().replace(' ', '_')}"
                        opt_body = "\n".join(line for _, line in (opt.get("content_lines") or []))

                        # Extract Config YAML block
                        config = {}
                        config_match = re.search(r'```yaml\s*\n(.*?)\n```', opt_body, re.DOTALL)
                        if config_match:
                            config = yaml.safe_load(config_match.group(1)) or {}

                        # Extract Flow block with line numbers
                        flow_blocks = extract_flow_blocks(opt.get("content_lines") or [])
                        if not flow_blocks:
                            continue
                        flow_lines = flow_blocks[0].get("lines") or []
                        flow_content = "\n".join(line for _, line in flow_lines).strip()

                        data_consolidated["dialogue"][opt_id] = {
                            "short": config.get('short', opt_name),
                            "long": config.get('long', opt_name),
                            "emoji": config.get('emoji', ''),
                            "chars": [obj_id],
                            "tags": config.get('tags', []),
                            "memory": config.get('memory', False),
                            "reason": config.get('reason'),
                            "cond": str(config.get('cond', 'True')),
                            "label": f"CHOICE__{opt_id}",
                            "body": f"```flow\n{flow_content}\n```"
                        }
                        source_info[("dialogue", opt_id)] = {
                            "path": source_path,
                            "flow_blocks": flow_blocks
                        }
            elif otype == 'quest':
                rewards_raw = parse_yaml_block(props.get('rewards'), {})
                prereqs_raw = parse_yaml_block(props.get('prereqs'), {})
                start_trigger = parse_yaml_block(props.get('start_trigger'), {})
                reward_items = parse_counts(rewards_raw.get('items', {})) if isinstance(rewards_raw, dict) else {}
                reward_flags = rewards_raw.get('flags', []) if isinstance(rewards_raw, dict) else []
                if isinstance(reward_flags, list):
                    reward_flags = [str(f).strip() for f in reward_flags if str(f).strip()]
                else:
                    reward_flags = parse_csv(reward_flags)
                tags = parse_csv(props.get('tags', ''))
                category = props.get('category', 'side')
                origin_flag = parse_bool(props.get('origin', False)) or str(category).lower() == "origin" or ("origin" in [t.lower() for t in tags])
                data_consolidated["quests"][obj_id] = {
                    "name": props.get('name', obj_id),
                    "description": props.get('description', ''),
                    "category": category,
                    "giver": props.get('giver'),
                    "location": props.get('location'),
                    "tags": tags,
                    "origin": origin_flag,
                    "pc_id": props.get('pc_id'),
                    "image": props.get('image'),
                    "prereqs": {
                        "quests": parse_csv(prereqs_raw.get('quests', [])) if isinstance(prereqs_raw, dict) else [],
                        "flags": parse_csv(prereqs_raw.get('flags', [])) if isinstance(prereqs_raw, dict) else [],
                        "not_flags": parse_csv(prereqs_raw.get('not_flags', [])) if isinstance(prereqs_raw, dict) else [],
                        "cond": (prereqs_raw.get('cond') if isinstance(prereqs_raw, dict) else None),
                    },
                    "rewards": {
                        "gold": int(rewards_raw.get('gold', 0)) if isinstance(rewards_raw, dict) and rewards_raw.get('gold') is not None else 0,
                        "items": reward_items,
                        "flags": reward_flags,
                    },
                    "start_trigger": start_trigger if isinstance(start_trigger, dict) else {},
                    "ticks": parse_quest_ticks(body, obj_id),
                    "body": body
                }
                source_info[("quests", obj_id)] = {
                    "path": source_path,
                    "body_lines": body_lines
                }
            elif otype == 'container':
                pos = props.get('pos', '0,0').split(',')
                data_consolidated["containers"][obj_id] = {
                    "name": props.get('name', obj_id),
                    "description": props.get('description', ''),
                    "location": props.get('location'),
                    "items": parse_csv(props.get('items', '')),
                    "x": int(pos[0]) if len(pos) > 1 else 0,
                    "y": int(pos[1]) if len(pos) > 1 else 0,
                    "blocked_tags": parse_csv(props.get('blocked_tags', '')),
                    "allowed_tags": parse_csv(props.get('allowed_tags', '')),
                    "tags": parse_csv(props.get('tags', '')),
                    "factions": parse_csv(props.get('factions', '')),
                    "max_weight": parse_float(props.get('max_weight')),
                    "max_slots": parse_int(props.get('max_slots')),
                    "body": body
                }
                source_info[("containers", obj_id)] = {
                    "path": source_path,
                    "body_lines": body_lines
                }
            elif otype == 'stat':
                data_consolidated["stats"][obj_id] = {
                    "name": props.get('name', obj_id),
                    "description": props.get('description', ''),
                    "default": int(props.get('default', 10)),
                    "min": int(props.get('min', 0)),
                    "max": int(props.get('max', 100))
                }
            elif otype == 'faction':
                data_consolidated["factions"][obj_id] = {
                    "name": props.get('name', obj_id),
                    "description": props.get('description', ''),
                    "allies": parse_csv(props.get('allies', '')),
                    "enemies": parse_csv(props.get('enemies', ''))
                }
            elif otype == 'slot':
                data_consolidated["slots"][obj_id] = {
                    "name": props.get('name', obj_id),
                    "unequips": parse_csv(props.get('unequips', ''))
                }
            elif otype == 'body_type':
                data_consolidated["body_types"][obj_id] = {
                    "name": props.get('name', obj_id),
                    "slots": parse_csv(props.get('slots', ''))
                }
            elif otype == 'dialogue':
                data_consolidated["dialogue"][obj_id] = {
                    "short": props.get('short', '...'),
                    "long": props.get('long', '...'),
                    "emoji": props.get('emoji', '💬'),
                    "chars": parse_csv(props.get('chars', '')),
                    "tags": parse_csv(props.get('tags', '')),
                    "memory": str(props.get('memory', 'False')).lower() == 'true',
                    "reason": props.get('reason'),
                    "label": props.get('label'),
                    "cond": props.get('cond', 'True'),
                    "body": body
                }
                source_info[("dialogue", obj_id)] = {
                    "path": source_path,
                    "body_lines": body_lines
                }
            elif otype == 'story_origin':
                data_consolidated["story_origins"][obj_id] = {
                    "name": props.get('name', obj_id),
                    "description": props.get('description', ''),
                    "pc_id": props.get('pc_id'),
                    "intro_label": props.get('intro_label'),
                    "image": props.get('image'),
                    "body": body
                }
                source_info[("story_origins", obj_id)] = {
                    "path": source_path,
                    "body_lines": body_lines
                }
            elif otype == 'recipe':
                req_skill = {}
                rs_raw = props.get('req_skill')
                # If req_skill is a dict (from markdown) or list
                if rs_raw: 
                    if isinstance(rs_raw, dict): req_skill = rs_raw
                    elif isinstance(rs_raw, list): req_skill = parse_counts(rs_raw)
                    else: req_skill = {} # Handle scalar?

                data_consolidated["recipes"][obj_id] = {
                    "name": props.get('name', obj_id),
                    "inputs": parse_counts(props.get('inputs', [])),
                    "output": parse_counts(props.get('output', [])),
                    "req_skill": req_skill,
                    "tags": parse_csv(props.get('tags', ''))
                }
            elif otype == 'note':
                data_consolidated["notes"][obj_id] = {
                    "name": props.get('name', obj_id),
                    "tags": parse_csv(props.get('tags', '')),
                    "body": body
                }
                source_info[("notes", obj_id)] = {
                    "path": source_path,
                    "body_lines": body_lines
                }
            elif otype == 'shop':
                data_consolidated["shops"][obj_id] = {
                    "name": props.get('name', obj_id),
                    "description": props.get('description', ''),
                    "buy_mult": float(props.get('buy_mult', 1.2)),
                    "sell_mult": float(props.get('sell_mult', 0.6)),
                    "items": parse_csv(props.get('items', '')),
                    "body": body
                }
                source_info[("shops", obj_id)] = {
                    "path": source_path,
                    "body_lines": body_lines
                }
            elif otype == 'achievement':
                trigger_raw = props.get('trigger', {})
                trigger = {}
                if isinstance(trigger_raw, list):
                    try:
                        trigger = yaml.safe_load("\n".join(trigger_raw))
                    except:
                        print(f"Error parsing achievement trigger for {obj_id}")
                elif isinstance(trigger_raw, dict):
                    trigger = trigger_raw

                data_consolidated["achievements"][obj_id] = {
                    "name": props.get('name', obj_id),
                    "description": props.get('description', ''),
                    "icon": props.get('icon', '🏆'),
                    "rarity": props.get('rarity', 'common'),
                    "tags": parse_csv(props.get('tags', '')),
                    "trigger": trigger,
                    "ticks": int(props.get('ticks', 1))
                }
            elif otype == 'perk':
                mods = parse_kv_block(props.get('mods', [])) if isinstance(props.get('mods', []), list) else {}
                data_consolidated["perks"][obj_id] = {
                    "name": props.get('name', obj_id),
                    "description": props.get('description', ''),
                    "mods": mods,
                    "tags": parse_csv(props.get('tags', '')),
                    "duration": props.get('duration')
                }
            elif otype == 'status':
                mods = parse_kv_block(props.get('mods', [])) if isinstance(props.get('mods', []), list) else {}
                data_consolidated["status_effects"][obj_id] = {
                    "name": props.get('name', obj_id),
                    "description": props.get('description', ''),
                    "mods": mods,
                    "tags": parse_csv(props.get('tags', '')),
                    "duration": props.get('duration')
                }
            elif otype == 'bond':
                stats = parse_kv_block(props.get('stats', [])) if isinstance(props.get('stats', []), list) else {}
                data_consolidated["bonds"][obj_id] = {
                    "a": props.get('a'),
                    "b": props.get('b'),
                    "tags": parse_csv(props.get('tags', '')),
                    "stats": stats
                }
            
    def _append_script_line(text, source_path=None, line_no=None):
        line = text.rstrip("\n")
        if source_path and line_no:
            line = f"{line} # @{source_path}:{line_no}"
        script_parts.append(line + "\n")

    def _emit_flow(flow_lines, source_path):
        for line_no, raw in flow_lines:
            line = raw.strip()
            if not line:
                continue
            if line.startswith('$'):
                _append_script_line(f"    {line}", source_path, line_no)
                continue
            if line.startswith('@') or is_caps_command(line):
                py = directive_to_python(line)
                if py:
                    _append_script_line(f"    $ {py}", source_path, line_no)
                else:
                    _append_script_line(f"    # {line}", source_path, line_no)
                continue
            if ':' in line:
                cid, txt = line.split(':', 1)
                txt = txt.strip().replace('"', '\\"')
                _append_script_line(f"    {cid.strip().lower()} \"{txt}\"", source_path, line_no)
            else:
                txt = line.strip().replace('"', '\\"')
                _append_script_line(f"    \"{txt}\"", source_path, line_no)

    # Second pass: Process bodies to link labels and generate RPY
    generated_labels = set()  # Track generated label names to avoid duplicates

    for otype, collection in [("location", "locations"), ("character", "characters"), ("item", "items"), ("quest", "quests"), ("container", "containers"), ("dialogue", "dialogue"), ("story_origin", "story_origins"), ("shop", "shops"), ("recipe", "recipes"), ("note", "notes")]:
        for oid, data in data_consolidated[collection].items():
            if 'body' not in data:
                continue
            body = data.pop('body')
            src = source_info.get((collection, oid), {})
            source_path = src.get("path")
            body_lines = src.get("body_lines")
            flow_blocks_override = src.get("flow_blocks")
            if body_lines is None:
                body_lines = [(None, line) for line in (body or "").splitlines()]
            safe_oid = label_safe(oid)
            prefix = {"character":"CHAR", "scene":"SCENE", "quest":"QUEST", "container":"CONT", "item":"ITEM", "shop":"SHOP", "story_origin":"QUEST"}.get(otype, "LOC")
            
            # Check for flow blocks in ALL types, but specifically handle naming for Dialogue, StoryOrigin, and Character
            flow_blocks = flow_blocks_override if flow_blocks_override is not None else extract_flow_blocks(body_lines)

            if flow_blocks:
                # Determine label name based on type
                if otype == 'dialogue':
                    label_name = f"CHOICE__{safe_oid}"
                    if not data.get('label'):
                        data['label'] = label_name
                elif otype == 'story_origin':
                    label_name = f"QUEST__{safe_oid}__started"
                elif otype == 'character':
                    label_name = f"CHAR__{safe_oid}"
                    if not data.get('label'):
                        data['label'] = label_name
                else:
                    label_name = f"{prefix}__{safe_oid}__flow"

                # Skip if this label was already generated
                if label_name in generated_labels:
                    if otype in ['dialogue', 'story_origin']:
                        continue
                else:
                    generated_labels.add(label_name)
                    label_line_no = flow_blocks[0].get("start_line")
                    if label_line_no is None and flow_blocks[0].get("lines"):
                        label_line_no = flow_blocks[0]["lines"][0][0]
                    _append_script_line(f"label {label_name}:", source_path, label_line_no)
                    for block in flow_blocks:
                        _emit_flow(block.get("lines") or [], source_path)
                    return_line_no = flow_blocks[-1].get("end_line")
                    if return_line_no is None and flow_blocks[-1].get("lines"):
                        return_line_no = flow_blocks[-1]["lines"][-1][0]
                    _append_script_line("    return", source_path, return_line_no)
                    script_parts.append("\n")
                
                # If specific types, we might skip the old section loop or mix it?
                # User preference "minimise labels generated outside of markdown" -> prefer flows.
                # We can continue to process sections if present, but flow usually replaces main body logic.
                if otype in ['dialogue']:
                    continue

            # Character Give flows (from # Give section)
            if otype == "character":
                for gf in (data.get("give_flows") or []):
                    label_name = gf.get("label")
                    flow_lines = gf.get("flow_lines") or []
                    if not label_name or not flow_lines:
                        continue
                    if label_name in generated_labels:
                        continue
                    generated_labels.add(label_name)
                    label_line_no = flow_lines[0][0] if flow_lines else None
                    _append_script_line(f"label {label_name}:", source_path, label_line_no)
                    _emit_flow(flow_lines, source_path)
                    return_line_no = flow_lines[-1][0] if flow_lines else label_line_no
                    _append_script_line("    return", source_path, return_line_no)
                    script_parts.append("\n")
                if "give_flows" in data:
                    data.pop("give_flows", None)

            sections = split_sections(body_lines)
            for sec in sections:
                heading_raw = sec.get("heading", "").strip()
                if not heading_raw:
                    continue
                heading = heading_raw.lower().replace(' ', '_')
                content_lines = sec.get("lines", [])

                flow_blocks = extract_flow_blocks(content_lines)
                if flow_blocks:
                    for block in flow_blocks:
                        if otype == "dialogue":
                            label_name = f"CHOICE__{safe_oid}"
                            # Set label on the dialogue option object if not set
                            if not data.get('label'):
                                data['label'] = label_name
                        else:
                            label_name = f"{prefix}__{safe_oid}__{label_safe(heading)}"
                        
                        # Skip if this label was already generated
                        if label_name in generated_labels:
                            continue
                        generated_labels.add(label_name)

                        if otype == "item":
                            data.setdefault("actions", [])
                            if heading_raw.strip().lower() != "inspect":
                                data["actions"].append({
                                    "name": heading_raw.strip(),
                                    "label": label_name
                                })

                        label_line_no = block.get("start_line")
                        if label_line_no is None and block.get("lines"):
                            label_line_no = block["lines"][0][0]
                        _append_script_line(f"label {label_name}:", source_path, label_line_no)
                        
                        # Link label to character/entity
                        if otype == "character" and heading == "talk":
                            data['label'] = label_name
                        elif otype == "location":
                            # Check if heading matches an entity ID
                            for ent in data.get('entities', []):
                                if not isinstance(ent, dict):
                                    continue
                                if ent.get('id', '').lower() == heading:
                                    ent['label'] = label_name

                        _emit_flow(block.get("lines") or [], source_path)
                        
                        return_line_no = block.get("end_line")
                        if return_line_no is None and block.get("lines"):
                            return_line_no = block["lines"][-1][0]
                        _append_script_line("    return", source_path, return_line_no)
                        script_parts.append("\n")

    # Cross-reference validation
    loc_ids = set(data_consolidated["locations"].keys())
    char_ids = set(data_consolidated["characters"].keys())
    item_ids = set(data_consolidated["items"].keys())
    slot_ids = set(data_consolidated["slots"].keys())
    body_ids = set(data_consolidated["body_types"].keys())

    for cid, c in data_consolidated["characters"].items():
        if c.get("location") and c["location"] not in loc_ids:
            errors.append(f"character {cid}: unknown location '{c['location']}'")
        if c.get("body_type") and c["body_type"] not in body_ids:
            errors.append(f"character {cid}: unknown body_type '{c['body_type']}'")
        for itm in c.get("items", []):
            if itm not in item_ids:
                errors.append(f"character {cid}: unknown item '{itm}'")
        for itm in (c.get("give", {}) or {}).keys():
            if itm not in item_ids:
                warnings.append(f"character {cid}: unknown give item '{itm}'")
        equip = c.get("equipment", {})
        if isinstance(equip, dict):
            for slot_id, item_id in equip.items():
                if slot_id not in slot_ids:
                    warnings.append(f"character {cid}: unknown slot '{slot_id}' in equipment")
                if item_id and item_id not in item_ids:
                    errors.append(f"character {cid}: unknown equipment item '{item_id}'")
    for lid, l in data_consolidated["locations"].items():
        ents = l.get("entities", []) or []
        for ent in ents:
            if not isinstance(ent, dict):
                continue
            if ent.get("type") == "link" and ent.get("id") and ent["id"] not in loc_ids:
                errors.append(f"location {lid}: link target '{ent['id']}' missing")
        for entry in l.get("scavenge", []) or []:
            if not isinstance(entry, dict):
                continue
            item_id = entry.get("item")
            if item_id and item_id not in item_ids:
                warnings.append(f"location {lid}: scavenge item '{item_id}' missing")
    for rid, r in data_consolidated["recipes"].items():
        for iid in list(r.get("inputs", {}).keys()) + list(r.get("output", {}).keys()):
            if iid not in item_ids:
                errors.append(f"recipe {rid}: unknown item '{iid}'")
    for iid, it in data_consolidated["items"].items():
        for slot in it.get("equip_slots", []):
            if slot not in slot_ids:
                warnings.append(f"item {iid}: unknown slot '{slot}'")

    if lint_only:
        if errors:
            print("Lint failed:")
            for e in errors:
                print(f" - {e}")
            sys.exit(1)
        if warnings:
            print("Lint warnings:")
            for w in warnings:
                print(f" - {w}")
        else:
            print("Lint passed.")
        return

    if errors:
        print("Warnings (non-fatal):")
        for e in errors:
            print(f" - {e}")

    # Write RPY
    with open(labels_file, "w", encoding="utf-8") as out:
        out.write("".join(script_parts))
    print(f"Compiled labels to {labels_file}")
    
    # Write JSON
    with open(json_file, "w", encoding="utf-8") as out:
        json.dump(data_consolidated, out, indent=4)
    print(f"Compiled data to {json_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--lint", action="store_true", help="Validate data without generating output")
    args = parser.parse_args()
    compile(lint_only=args.lint)

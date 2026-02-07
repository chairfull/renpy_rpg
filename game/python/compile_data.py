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
            content = f.read()
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return None, None
    
    if "---" not in content:
        return None, None
    
    parts = content.split("---", 2)
    if len(parts) < 3:
        return None, None
    
    props = {}
    lines = parts[1].split('\n')
    i = 0
    while i < len(lines):
        line = lines[i]
        if not line.strip():
            i += 1
            continue
        if ':' in line and not line.strip().startswith('-'):
            k, v = line.split(':', 1)
            k, v = k.strip(), v.strip().strip('"').strip("'")
            if not v: # Block value
                block = []
                j = i + 1
                while j < len(lines) and (not lines[j].strip() or lines[j].startswith(' ') or lines[j].strip().startswith('-')):
                    if lines[j].strip(): block.append(lines[j])
                    j += 1
                props[k] = block
                i = j
                continue
            props[k] = v
        i += 1
    
    return props, parts[2].strip()

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
        count = int(parts[2]) if len(parts) > 2 else 1
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
    return None

def compile(lint_only=False):
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    game_dir = os.path.join(base_dir, "game")
    data_dir = os.path.join(base_dir, "data") # Moved to root
    # JSON and Labels both go to a hidden folder
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
            props, body = parse_markdown(full_path)
            
            if not props:
                continue
            
            obj_id = props.get('id', props.get('name', 'unknown')).lower()
            otype = str(props.get('type', 'location')).strip().lower()
            if otype == "origin":
                otype = "story_origin"
            if otype == "story_origin" and not _is_origin_path(rel_path):
                warnings.append(f"story_origin {obj_id}: move to data/quests/origins/ (ignored)")
                continue
            
            # Store in JSON data
            if otype == 'item':
                stack_size = parse_int(props.get('stack_size'), 1) or 1
                data_consolidated["items"][obj_id] = {
                    "name": props.get('name', obj_id),
                    "description": props.get('description', ''),
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

                data_consolidated["locations"][obj_id] = {
                    "name": props.get('name', obj_id),
                    "description": props.get('description', ''),
                    "map_image": props.get('map_image'),
                    "obstacles": props.get('obstacles', []),
                    "entities": entities,
                    "encounters": encounters,
                    "scavenge": scavenge,
                    "body": body, # Store body for second pass
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
                    "body": body
                }
                
                # Check for nested Dialogue section
                dialogue_match = re.search(r'# Dialogue\s*\n(.*?)(?=\n# |$)', body, re.DOTALL)
                if dialogue_match:
                    dialogue_section = dialogue_match.group(1)
                    # Find all ## options
                    options = re.findall(r'## (.*?)\s*\n(.*?)(?=\n## |$)', dialogue_section, re.DOTALL)
                    for opt_name, opt_body in options:
                        opt_id = f"{obj_id}_{opt_name.lower().replace(' ', '_')}"
                        
                        # Extract Config YAML block
                        config = {}
                        config_match = re.search(r'```yaml\s*\n(.*?)\n```', opt_body, re.DOTALL)
                        if config_match:
                            config = yaml.safe_load(config_match.group(1)) or {}
                        
                        # Extract Flow block
                        flow_match = re.search(r'```flow\s*\n(.*?)\n```', opt_body, re.DOTALL)
                        flow_content = flow_match.group(1).strip() if flow_match else ""
                        
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
                data_consolidated["quests"][obj_id] = {
                    "name": props.get('name', obj_id),
                    "description": props.get('description', ''),
                    "category": props.get('category', 'side'),
                    "giver": props.get('giver'),
                    "location": props.get('location'),
                    "tags": parse_csv(props.get('tags', '')),
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
                    "ticks": parse_quest_ticks(body, obj_id)
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
            elif otype == 'story_origin':
                data_consolidated["story_origins"][obj_id] = {
                    "name": props.get('name', obj_id),
                    "description": props.get('description', ''),
                    "pc_id": props.get('pc_id'),
                    "intro_label": props.get('intro_label', f"SCENE__{obj_id}__intro"),
                    "image": props.get('image'),
                    "body": body
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
            elif otype == 'shop':
                data_consolidated["shops"][obj_id] = {
                    "name": props.get('name', obj_id),
                    "description": props.get('description', ''),
                    "buy_mult": float(props.get('buy_mult', 1.2)),
                    "sell_mult": float(props.get('sell_mult', 0.6)),
                    "items": parse_csv(props.get('items', '')),
                    "body": body
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
            
    def _emit_flow(flow_body, script_parts):
        for line in flow_body.split('\n'):
            line = line.strip()
            if not line:
                continue
            if line.startswith('$'):
                script_parts.append(f"    {line}\n")
                continue
            if line.startswith('@') or is_caps_command(line):
                py = directive_to_python(line)
                if py:
                    script_parts.append(f"    $ {py}\n")
                else:
                    script_parts.append(f"    # {line}\n")
                continue
            if ':' in line:
                cid, txt = line.split(':', 1)
                txt = txt.strip().replace('"', '\\"')
                script_parts.append(f"    {cid.strip().lower()} \"{txt}\"\n")
            else:
                txt = line.strip().replace('"', '\\"')
                script_parts.append(f"    \"{txt}\"\n")

    # Second pass: Process bodies to link labels and generate RPY
    generated_labels = set()  # Track generated label names to avoid duplicates

    for otype, collection in [("location", "locations"), ("character", "characters"), ("item", "items"), ("quest", "quests"), ("container", "containers"), ("dialogue", "dialogue"), ("story_origin", "story_origins"), ("shop", "shops"), ("recipe", "recipes"), ("note", "notes")]:
        for oid, data in data_consolidated[collection].items():
            if 'body' not in data: continue
            body = data.pop('body')
            prefix = {"character":"CHAR", "scene":"SCENE", "quest":"QUEST", "container":"CONT", "item":"ITEM", "shop":"SHOP", "story_origin":"QUEST"}.get(otype, "LOC")
            
            # Check for flow blocks in ALL types, but specifically handle naming for Dialogue, StoryOrigin, and Character
            flows = re.findall(r'```flow.*?\s*\n(.*?)\n```', body, re.DOTALL)
            if not flows:
                flows = re.findall(r'```flow.*?\n(.*?)\n```', body, re.DOTALL)
            
            if flows:
                # Determine label name based on type
                if otype == 'dialogue':
                    label_name = f"CHOICE__{oid}"
                    if not data.get('label'): data['label'] = label_name
                elif otype == 'story_origin':
                    label_name = f"QUEST__{oid}__started"
                    # We might update data['intro_label'] if not present, but usually explicit or convention
                elif otype == 'character':
                    label_name = f"CHAR__{oid}"
                    if not data.get('label'): data['label'] = label_name
                else:
                    label_name = f"{prefix}__{oid}__flow"

                # Skip if this label was already generated
                if label_name in generated_labels:
                    if otype in ['dialogue', 'story_origin']:
                        continue
                else:
                    generated_labels.add(label_name)
                    script_parts.append(f"label {label_name}:\n")
                    for flow_body in flows:
                        _emit_flow(flow_body, script_parts)
                    script_parts.append("    return\n\n")
                
                # If specific types, we might skip the old section loop or mix it?
                # User preference "minimise labels generated outside of markdown" -> prefer flows.
                # We can continue to process sections if present, but flow usually replaces main body logic.
                if otype in ['dialogue']:
                    continue

            sections = re.split(r'(?m)^#+\s*', body)
            for sec in sections:
                if not sec.strip(): continue
                lines = sec.split('\n', 1)
                heading_raw = lines[0].strip()
                heading = heading_raw.lower().replace(' ', '_')
                content = lines[1] if len(lines) > 1 else ""
                
                flows = re.findall(r'```flow.*?\s*\n(.*?)\n```', content, re.DOTALL)
                if not flows:
                    flows = re.findall(r'```flow.*?\n(.*?)\n```', content, re.DOTALL)

                if flows:
                    for flow_body in flows:
                        if otype == "dialogue":
                            label_name = f"CHOICE__{oid}"
                            # Set label on the dialogue option object if not set
                            if not data.get('label'):
                                data['label'] = label_name
                        else:
                            label_name = f"{prefix}__{oid}__{heading}"
                        
                        # Skip if this label was already generated
                        if label_name in generated_labels:
                            continue
                        generated_labels.add(label_name)
                        
                        script_parts.append(f"label {label_name}:\n")
                        
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

                        _emit_flow(flow_body, script_parts)
                        
                        script_parts.append("    return\n\n")

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

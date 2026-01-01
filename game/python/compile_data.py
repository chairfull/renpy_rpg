import os
import re
import json
import yaml

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
    items = []
    current_item = None
    for line in lines:
        stripped = line.strip()
        if not stripped: continue
        
        # New item start
        if line.lstrip().startswith('- '):
            if current_item: items.append(current_item)
            current_item = {}
            # Check for inline content after "- "
            content = line.lstrip()[2:].strip() # remove "- "
            if ':' in content:
                k, v = content.split(':', 1)
                val = v.strip()
                # Simple integer conversion
                if val.isdigit(): val = int(val)
                # Simple list conversion [x, y]
                elif val.startswith('[') and val.endswith(']'):
                     val = [int(x.strip()) if x.strip().isdigit() else x.strip() for x in val[1:-1].split(',')]
                else:
                     val = val.strip('"\'')
                current_item[k.strip()] = val
        
        # Property
        elif ':' in stripped:
            if current_item is not None:
                k, v = stripped.split(':', 1)
                val = v.strip()
                if val.isdigit(): val = int(val)
                elif val.startswith('[') and val.endswith(']'):
                     val = [int(x.strip()) if x.strip().isdigit() else x.strip() for x in val[1:-1].split(',')]
                else:
                     val = val.strip('"\'')
                current_item[k.strip()] = val
    
    if current_item: items.append(current_item)
    return items

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
        return [x.strip() for x in value.split(',') if x.strip()]
    return []

def compile():
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
        "shops": {}
    }
    
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
            otype = props.get('type', 'location')
            
            # Store in JSON data
            if otype == 'item':
                data_consolidated["items"][obj_id] = {
                    "name": props.get('name', obj_id),
                    "description": props.get('description', ''),
                    "weight": float(props.get('weight', 0)),
                    "value": int(props.get('value', 0)),
                    "tags": parse_csv(props.get('tags', '')),
                    "factions": parse_csv(props.get('factions', '')),
                    "equip_slots": parse_csv(props.get('equip_slots', '')),
                    "outfit_part": props.get('outfit_part')
                }
            elif otype == 'location':
                # Parse list of entities/links
                raw_ents = props.get('entities', [])
                if isinstance(raw_ents, list):
                    entities = parse_yaml_list(raw_ents)
                else:
                    entities = []

                data_consolidated["locations"][obj_id] = {
                    "name": props.get('name', obj_id),
                    "description": props.get('description', ''),
                    "map_image": props.get('map_image'),
                    "obstacles": props.get('obstacles', []),
                    "entities": entities,
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
                # Parse stats block if present
                stats_raw = props.get('stats', {})
                stats_dict = {}
                if isinstance(stats_raw, list):
                    for line in stats_raw:
                        line = line.strip()
                        if ':' in line:
                            k, v = line.split(':', 1)
                            try:
                                stats_dict[k.strip().replace('- ', '')] = int(v.strip())
                            except ValueError:
                                stats_dict[k.strip().replace('- ', '')] = v.strip()
                data_consolidated["characters"][obj_id] = {
                    "name": props.get('name'),
                    "description": props.get('description', ''),
                    "location": props.get('location'),
                    "items": parse_csv(props.get('items', '')),
                    "base_image": props.get('base_image'),
                    "x": int(pos[0]) if len(pos) > 1 else 0,
                    "y": int(pos[1]) if len(pos) > 1 else 0,
                    "tags": parse_csv(props.get('tags', '')),
                    "factions": parse_csv(props.get('factions', '')),
                    "body_type": props.get('body_type', 'humanoid'),
                    "stats": stats_dict,
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
                            "cond": str(config.get('cond', 'True')),
                            "label": f"CHOICE__{opt_id}",
                            "body": f"```flow\n{flow_content}\n```"
                        }
            elif otype == 'quest':
                data_consolidated["quests"][obj_id] = {
                    "name": props.get('name', obj_id),
                    "description": props.get('description', '')
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
            elif otype == 'shop':
                data_consolidated["shops"][obj_id] = {
                    "name": props.get('name', obj_id),
                    "description": props.get('description', ''),
                    "buy_mult": float(props.get('buy_mult', 1.2)),
                    "sell_mult": float(props.get('sell_mult', 0.6)),
                    "items": parse_csv(props.get('items', '')),
                    "body": body
                }
            
    # Second pass: Process bodies to link labels and generate RPY
    for otype, collection in [("location", "locations"), ("character", "characters"), ("item", "items"), ("quest", "quests"), ("container", "containers"), ("dialogue", "dialogue"), ("story_origin", "story_origins"), ("shop", "shops")]:
        for oid, data in data_consolidated[collection].items():
            if 'body' not in data: continue
            body = data.pop('body')
            prefix = {"character":"CHAR", "scene":"SCENE", "quest":"QUEST", "container":"CONT", "item":"ITEM", "shop":"SHOP"}.get(otype, "LOC")
            
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
                    label_name = f"SCENE__{oid}__intro"
                    # We might update data['intro_label'] if not present, but usually explicit or convention
                elif otype == 'character':
                    label_name = f"CHAR__{oid}"
                    if not data.get('label'): data['label'] = label_name
                else:
                    label_name = f"{prefix}__{oid}__flow"

                script_parts.append(f"label {label_name}:\n")
                for flow_body in flows:
                    for line in flow_body.split('\n'):
                            line = line.strip()
                            if not line: continue
                            if line.startswith('$'):
                                script_parts.append(f"    {line}\n")
                            elif ':' in line:
                                cid, txt = line.split(':', 1)
                                txt = txt.strip().replace('"', '\\"')
                                script_parts.append(f"    {cid.strip().lower()} \"{txt}\"\n")
                            else:
                                txt = line.strip().replace('"', '\\"')
                                script_parts.append(f"    \"{txt}\"\n")
                script_parts.append("    return\n\n")
                
                # If specific types, we might skip the old section loop or mix it?
                # User preference "minimise labels generated outside of markdown" -> prefer flows.
                # We can continue to process sections if present, but flow usually replaces main body logic.
                if otype in ['dialogue', 'story_origin']:
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
                        
                        script_parts.append(f"label {label_name}:\n")
                        
                        # Link label to character/entity
                        if otype == "character" and heading == "talk":
                            data['label'] = label_name
                        elif otype == "location":
                            # Check if heading matches an entity ID
                            for ent in data.get('entities', []):
                                if ent.get('id', '').lower() == heading:
                                    ent['label'] = label_name

                        for line in flow_body.split('\n'):
                            line = line.strip()
                            if not line: continue
                            if line.startswith('$'):
                                script_parts.append(f"    {line}\n")
                            elif ':' in line:
                                cid, txt = line.split(':', 1)
                                txt = txt.strip().replace('"', '\\"')
                                script_parts.append(f"    {cid.strip().lower()} \"{txt}\"\n")
                            else:
                                txt = line.strip().replace('"', '\\"')
                                script_parts.append(f"    \"{txt}\"\n")
                        
                        script_parts.append("    return\n\n")

    # Write RPY
    with open(labels_file, "w", encoding="utf-8") as out:
        out.write("".join(script_parts))
    print(f"Compiled labels to {labels_file}")
    
    # Write JSON
    with open(json_file, "w", encoding="utf-8") as out:
        json.dump(data_consolidated, out, indent=4)
    print(f"Compiled data to {json_file}")

if __name__ == "__main__":
    compile()

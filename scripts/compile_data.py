import os
import re
import json

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

def compile():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    game_dir = os.path.join(base_dir, "game")
    data_dir = os.path.join(game_dir, "data")
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
        "containers": {}
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
                    "entities": entities
                }
            elif otype == 'character':
                pos = props.get('pos', '0,0').split(',')
                data_consolidated["characters"][obj_id] = {
                    "name": props.get('name'),
                    "description": props.get('description', ''),
                    "location": props.get('location'),
                    "x": int(pos[0]) if len(pos) > 1 else 0,
                    "y": int(pos[1]) if len(pos) > 1 else 0
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
                    "items": [i.strip() for i in props.get('items', '').split(',') if i.strip()],
                    "x": int(pos[0]) if len(pos) > 1 else 0,
                    "y": int(pos[1]) if len(pos) > 1 else 0
                }
            
            # Generate Labels
            prefix = {"character":"CHAR", "scene":"SCENE", "quest":"QUEST", "container":"CONT", "item":"ITEM"}.get(otype, "LOC")
            
            sections = re.split(r'(?m)^#+\s*', body)
            for sec in sections:
                if not sec.strip():
                    continue
                lines = sec.split('\n', 1)
                heading = lines[0].strip().lower().replace(' ', '_')
                content = lines[1] if len(lines) > 1 else ""
                
                flows = re.findall(r'```flow.*?\s*\n(.*?)\n```', content, re.DOTALL)
                if not flows:
                    flows = re.findall(r'```flow.*?\n(.*?)\n```', content, re.DOTALL)

                if flows:
                    for flow_body in flows:
                        label_name = f"{prefix}__{obj_id}__{heading}"
                        script_parts.append(f"label {label_name}:\n")
                        for line in flow_body.split('\n'):
                            line = line.strip()
                            if not line:
                                continue
                            if line.startswith('$'):
                                script_parts.append(f"    {line}\n")
                            elif ':' in line:
                                cid, txt = line.split(':', 1)
                                txt = txt.strip().replace('"', '\\"')
                                script_parts.append(f"    {cid.strip().lower()} \"{txt}\"\n")
                            else:
                                txt = line.strip().replace('"', '\\"')
                                script_parts.append(f"    \"{txt}\"\n")
                        
                        if prefix == "ITEM":
                            script_parts.append("    return\n\n")
                        else:
                            script_parts.append("    jump world_loop\n\n")

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

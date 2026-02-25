from pathlib import Path
from .helpers import (parse_markdown, parse_yaml, flow_to_rpy)

# TODO: Add spoken line counts over characters.
# TODO: Show how quests and zones connect to each other.

type_convert = {
    "goal": "quest_tick",
    "shop": "has_trade",
}

types = {
    "award": { "define": True },
    "lore": { "define": True },
    "item": { "define": True },
    "quest": { "define": True, "autoname": True },
    "quest_tick": { "define": True, "autoname": True },
    "choice": { "define": True },
    "flag": { "define": True },
    "craft": { "define": True },

    "being": {},
    "inventory": {},
    "dialogue": {},
    "shop": {},
    "has_trade": {},
    
    "zone": { "define": True, "autoname": True },
    "item_filters": { "define": True },

    "clan": { "define": True },
    "perk": { "define": True },
    "stat": { "define": True },
    "trait": { "define": True },
    "appearance": { "define": True },
}

def to_camel_case(s):
    return "".join(word.capitalize() for word in s.split("_"))

def str_to_var(obj_id, key, val):
    if key == "event":
        return f"engine.{val}"
    if isinstance(val, str) and "#" in val:
        return val.replace("#", "__")
    return repr(val)

def compile_data():
    all_ids = {} # To test for collisions.
    data_consolidated = {k: {} for k in types.keys()}

    base_dir = Path(__file__).resolve().parents[2]
    data_dir = base_dir / "data"
    total_files = 0
    for md_file in data_dir.rglob("*.md"):
        md_data = md_file.read_text(encoding="utf-8")
        fm, heads = parse_markdown(md_data)
        if "type" in fm:
            obj_type = type_convert.get(fm["type"], fm["type"])
            obj_id = fm.get("id") or fm.get("name", md_file.stem).lower().replace(" ", "_")
            if obj_type in types:
                if obj_id in all_ids:
                    print(f"Warning: Duplicate ID '{obj_id}' found in {md_file} (also in {all_ids[obj_id]})")
                all_ids[obj_id] = obj_type
                data_consolidated[obj_type][obj_id] = (fm, heads)
                total_files += 1
            else:
                print(f"Warning: Unknown type '{obj_type}' in {md_file}. Skipping.")
        else:
            print(f"Warning: No type specified in {md_file}. Skipping.")
    print(f"Processed {total_files} data files across {len(types)} types.")

    script = []
    labels = []
    conditions = {}

    def replace_cond(kwargs):
        if "cond" in kwargs:
            cond = kwargs["cond"]
            cond_hash = str(hash(cond)).replace("-", "_")
            conditions[cond_hash] = f"    def _cond_{cond_hash}(): return {cond}"
            kwargs["cond"] = cond_hash

    flow_action_counts = {}
    for type, type_data in types.items():
        type = type_convert.get(type, type)
        type_class = type_data.get("class", to_camel_case(type)) # Assuming class names are capitalized versions of types
        script.append(f"\n#region {type.capitalize()}s x{len(data_consolidated[type])}")
        defaults = []
        type_define = "define" if type_data.get("define", False) else "default"
        for obj_id, obj_data in data_consolidated[type].items():
            obj_data, obj_heads = obj_data
            replace_cond(obj_data)
            kwarg_str = ", ".join(f"{k}={str_to_var(obj_id, k, v)}" for k, v in obj_data.items() if k not in ["id", "type"])
            defaults.append(f'# {obj_data.get("name", obj_id.capitalize())}. {obj_data.get("desc", "")}')
            defaults.append(f'{type_define} {obj_id} = {type_class}("{obj_id}", {kwarg_str})')
            
            labels_local = []

            for head_id, head_data in obj_heads.items():
                head_id = head_data.get("id", head_data['name'].replace(" ", "_").lower())
                codeblocks = head_data.get("codeblocks", [])
                for codeblock in codeblocks:
                    # create a flow label.
                    if codeblock["lang"] == "flow":
                        flow_rpy = flow_to_rpy(obj_id, codeblock["code"], flow_action_counts)
                        if flow_rpy:
                            label_suffix = head_id
                            labels_local.append(f"    label .{label_suffix}:")
                            labels_local.append("        " + flow_rpy.replace("\n", "\n        "))
                            labels_local.append(f"        return")
                    # create an object.
                    elif codeblock["lang"] == "yaml":
                        yaml_data = parse_yaml(codeblock["code"])
                        replace_cond(yaml_data)
                        if "type" in yaml_data:
                            subtype = yaml_data["type"]
                            subtype = type_convert.get(subtype, subtype)
                            # Use headings as a name if none were defined.
                            if types[subtype].get("autoname", False) == True and "name" not in yaml_data:
                                yaml_data["name"] = head_data["name"]
                            subtype_id = obj_id + "__" + head_id
                            subtype_class = to_camel_case(subtype)
                            yaml_args = ", ".join(f"{k}={str_to_var(obj_id, k, v)}" for k, v in yaml_data.items() if k not in ["id", "type"])
                            defaults.append(f'{type_define} {subtype_id} = {subtype_class}(\"{subtype_id}\", {yaml_args})')
                        else:
                            print(f"Warning: YAML codeblock in {obj_id}#{head_id} is missing 'type'. Skipping.")
            
            if labels_local:
                labels.append(f"label {obj_id}:")
                labels.extend(labels_local)
                labels.append(f"    return")

        script += defaults
        script.append("#endregion")

    enums = []
    enums.append("    from classes.flow_actions import (")
    for action, count in sorted(flow_action_counts.items(), key=lambda x: x[1], reverse=True):
        enums.append(f"        {action}, # x{count}")
    enums.append("    )")

    script = ["# This file is auto-generated by compile_data_v2.py. Do not edit manually.",
              "init python:",
              "    from classes import *"]\
        + enums\
        + ["    #region Conditions."]\
        + list(conditions.values())\
        + ["    #endregion"]\
        + script\
        + [f"#region Labels x{len(labels)}"]\
        + labels\
        + ["#endregion"]

    rpy_output_file = base_dir / "game" / "generated" / "autogenerated_dont_edit.rpy"
    with rpy_output_file.open("w", encoding="utf-8") as f:
        f.write("\n".join(script))
    print(f"RPY definitions written to {rpy_output_file}")

compile_data()
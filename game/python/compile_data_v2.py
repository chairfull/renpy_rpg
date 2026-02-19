from pathlib import Path
from .helpers import (parse_markdown, parse_yaml, flow_to_rpy)

# TODO: Add spoken line counts over characters.
# TODO: Show how quests and zones connect to each other.

types = {
    "award": {},
    "being": {},
    "craft": {},
    "dialogue": {},
    "choice": {},
    "flag": {},
    "lore": {},
    "quest": {},
    "shop": {},
    
    "zone": {
        "subtypes": { "zone": False }
    },
    
    "inventory": {},
    "item": {},
    "item_filters": {},

    "clan": {},
    "perk": {},
    "stat": {},
    "trait": {},
    "appearance": {},
}

def to_camel_case(s):
    return "".join(word.capitalize() for word in s.split("_"))

def str_to_var(id, s):
    return repr(s)

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
            obj_type = fm["type"]
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
        type_class = type_data.get("class", to_camel_case(type)) # Assuming class names are capitalized versions of types
        script.append(f"\n#region {type.capitalize()}s x{len(data_consolidated[type])}")
        defaults = []
        defines = [f"# All {type}s.", f"define all_{type}s = {{"]
        labels.append(f"label {type}:")
        for obj_id, obj_data in data_consolidated[type].items():
            obj_data, obj_heads = obj_data
            replace_cond(obj_data)
            kwarg_str = ", ".join(f"{k}={str_to_var(obj_id, v)}" for k, v in obj_data.items() if k not in ["id", "type"])
            defaults.append(f'# {obj_data.get("name", obj_id.capitalize())}. {obj_data.get("desc", "")}')
            defaults.append(f'default {obj_id} = {type_class}("{obj_id}", {kwarg_str})')
            defines.append(f'    "{obj_id}": {obj_id},')
            labels.append(f"    label .{obj_id}:")

            for head_id, head_data in obj_heads.items():
                codeblocks = head_data.get("codeblocks", [])
                for codeblock in codeblocks:
                    # create a flow label.
                    if codeblock["lang"] == "flow":
                        flow_rpy = flow_to_rpy(obj_id, codeblock["code"], flow_action_counts)
                        label_suffix = head_data['name'].replace(" ", "_").lower()
                        labels.append(f"        label .{label_suffix}:")
                        labels.append("            " + flow_rpy.replace("\n", "\n            "))
                        labels.append(f"            return")
                    # create an object.
                    elif codeblock["lang"] == "yaml":
                        yaml_data = parse_yaml(codeblock["code"])
                        replace_cond(yaml_data)
                        if "type" in yaml_data:
                            subtype = yaml_data["type"]
                            subtype_id = obj_id + "__" + head_data["name"].replace(" ", "_").lower()
                            subtype_class = to_camel_case(subtype)
                            yaml_args = ", ".join(f"{k}={str_to_var(obj_id, v)}" for k, v in yaml_data.items() if k not in ["type"])
                            defaults.append(f'default {subtype_id} = {subtype_class}(\"{subtype_id}\", {yaml_args})')
                        else:
                            print(f"Warning: YAML codeblock in {obj_id}#{head_id} is missing 'type'. Skipping.")
            
            labels.append(f"        return")
        labels.append(f"    return")

        defines.append("}")
        script += defaults + defines
        script.append("#endregion")

    enums = []
    enums.append("    #region Flow actions. Sorted.")
    for action, count in sorted(flow_action_counts.items(), key=lambda x: x[1], reverse=True):
        enums.append(f"    {action} = \"{action}\" # x{count}")
    enums.append("    #endregion")

    script = ["# This file is auto-generated by compile_data_v2.py. Do not edit manually.",
              "init python:"]\
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
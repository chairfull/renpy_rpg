default persistent.met_characters = set()
default persistent.unlocked_notes = set()
default persistent.known_character_locations = {}
default persistent.achievement_progress = {}
default persistent.unlocked_scenes = set()
default world_flags = {}
default encounter_history = set()
default scavenge_history = {}
default allow_unvisited_travel = False
default item_inspect_image = None
default item_inspect_title = ""
default pending_inspect_item_id = None
default _return_to_inventory = False
default inspect_force = False
default inspect_resolved_label = None
default inspect_resolved_item = None
default preselected_origin_id = None

init -10 python:
    # Initialize Persistent Data Defaults (Legacy safety)
    if persistent.met_characters is None:
        persistent.met_characters = set()
    if persistent.unlocked_notes is None:
        persistent.unlocked_notes = set()

    import json
    import random
    import copy
    import ast
    import math

    SAFE_FUNC_NAMES = {"len", "int", "float", "str", "max", "min"}

    def _ast_safe(node):
        """Whitelist a small subset of Python expressions for data-driven conditions."""
        allowed = (
            ast.Expression, ast.BoolOp, ast.UnaryOp, ast.BinOp, ast.Compare,
            ast.Name, ast.Load, ast.Attribute, ast.Constant,
            ast.And, ast.Or, ast.Not, ast.Eq, ast.NotEq, ast.Lt, ast.LtE,
            ast.Gt, ast.GtE, ast.In, ast.NotIn, ast.Is, ast.IsNot,
            ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Mod, ast.USub
        )
        if isinstance(node, ast.Call):
            # Allow basic builtins and kwargs.get only
            func = node.func
            if isinstance(func, ast.Name) and func.id in SAFE_FUNC_NAMES:
                pass
            elif isinstance(func, ast.Attribute) and func.attr == "get" and isinstance(func.value, ast.Name) and func.value.id == "kwargs":
                pass
            else:
                return False
            return all(_ast_safe(arg) for arg in node.args) and all(_ast_safe(kw.value) for kw in node.keywords)
        if not isinstance(node, allowed):
            return False
        for child in ast.iter_child_nodes(node):
            if not _ast_safe(child):
                return False
        return True

    def safe_eval_bool(expr, env):
        """Evaluate small boolean expressions safely; returns False on error."""
        try:
            tree = ast.parse(str(expr), mode="eval")
        except Exception:
            return False
        if not _ast_safe(tree):
            return False
        try:
            builtins_obj = __builtins__
            safe_funcs = {}
            for n in SAFE_FUNC_NAMES:
                fn = getattr(builtins_obj, n, None) if hasattr(builtins_obj, n) else builtins_obj.get(n) if isinstance(builtins_obj, dict) else None
                if fn:
                    safe_funcs[n] = fn
            return bool(eval(compile(tree, "<cond>", "eval"), {"__builtins__": {}, **safe_funcs}, env))
        except Exception:
            return False

    def flag_get(name, default=False):
        return world_flags.get(name, default)

    def flag_set(name, value=True):
        world_flags[name] = value
        return value

    def flag_clear(name):
        if name in world_flags:
            del world_flags[name]

    def flag_toggle(name):
        world_flags[name] = not world_flags.get(name, False)
        return world_flags[name]

    def bracket_label(text, color="#ff3b3b", bracket_color="#ffffff"):
        return "{color=%s}[{/color}{color=%s}%s{/color}{color=%s}]{/color}" % (
            bracket_color, color, text, bracket_color
        )

    def _hex_to_rgb(col):
        c = str(col).lstrip("#")
        if len(c) == 3:
            c = "".join([ch * 2 for ch in c])
        if len(c) != 6:
            return (255, 255, 255)
        return tuple(int(c[i:i+2], 16) for i in (0, 2, 4))

    def _rgb_to_hex(rgb, alpha=None):
        r, g, b = rgb
        r = max(0, min(255, int(r)))
        g = max(0, min(255, int(g)))
        b = max(0, min(255, int(b)))
        if alpha is None:
            return "#%02x%02x%02x" % (r, g, b)
        a = max(0, min(255, int(alpha)))
        return "#%02x%02x%02x%02x" % (r, g, b, a)

    def _tint_color(col, factor):
        r, g, b = _hex_to_rgb(col)
        return (r * factor, g * factor, b * factor)

    def text_outline_fx(color, outline_factor=0.45, shadow_factor=0.2, shadow_alpha=80):
        outline = _rgb_to_hex(_tint_color(color, outline_factor))
        shadow = _rgb_to_hex(_tint_color(color, shadow_factor), shadow_alpha)
        return [(2, outline, 0, 0), (2, shadow, 0, 2)]

    def find_item_by_tag(tag):
        for it in pc.items:
            if it.has_tag(tag):
                return it
        return None

    def consume_item_by_tag(tag):
        it = find_item_by_tag(tag)
        if it:
            pc.remove_item(it, count=1, reason="consume")
            return it
        return None

    class Bond(object):
        def __init__(self, id, a_id, b_id, tags=None, stats=None, relations=None):
            self.id = id
            self.a_id = a_id
            self.b_id = b_id
            self.tags = set(tags or [])
            self.stats = stats or {}
            # relations: list of dicts with keys: id, type, a_label, b_label, weight, note
            self.relations = []
            if relations:
                try:
                    if isinstance(relations, dict):
                        # single relation
                        self.relations = [relations]
                    elif isinstance(relations, list):
                        self.relations = relations
                except Exception:
                    self.relations = []
        
        def other(self, cid):
            return self.b_id if cid == self.a_id else self.a_id
        
        def get_stat(self, name, default=0):
            try:
                return int(self.stats.get(name, default))
            except Exception:
                return default
        
        def set_stat(self, name, value):
            self.stats[name] = int(value)
        
        def add_stat(self, name, delta):
            self.set_stat(name, self.get_stat(name, 0) + int(delta))
        
        def has_tag(self, tag):
            return tag in self.tags
        
        def add_tag(self, tag):
            self.tags.add(tag)
        
        def remove_tag(self, tag):
            self.tags.discard(tag)

        # Relation helpers
        def add_relation(self, rel_id, rel_type=None, a_label=None, b_label=None, weight=0, note=None):
            # Replace if id exists
            for r in self.relations:
                if r.get('id') == rel_id:
                    r.update({
                        'type': rel_type or r.get('type'),
                        'a_label': a_label or r.get('a_label'),
                        'b_label': b_label or r.get('b_label'),
                        'weight': int(weight or r.get('weight', 0)),
                        'note': note or r.get('note')
                    })
                    return r
            r = {'id': rel_id, 'type': rel_type, 'a_label': a_label, 'b_label': b_label, 'weight': int(weight or 0), 'note': note}
            self.relations.append(r)
            return r

        def get_relations(self):
            return list(self.relations)

        def get_relation(self, rel_id):
            for r in self.relations:
                if r.get('id') == rel_id:
                    return r
            return None

        def remove_relation(self, rel_id):
            for i, r in enumerate(self.relations):
                if r.get('id') == rel_id:
                    return self.relations.pop(i)
            return None

    class BondManager:
        def __init__(self):
            self.bonds = {}
        
        def _key(self, a, b):
            return tuple(sorted([a, b]))
        
        def register(self, bond):
            self.bonds[self._key(bond.a_id, bond.b_id)] = bond

        def set_relation(self, a, b, rel_id, rel_type=None, a_label=None, b_label=None, weight=0, note=None):
            bobj = self.ensure(a, b)
            if not bobj:
                return None
            return bobj.add_relation(rel_id, rel_type=rel_type, a_label=a_label, b_label=b_label, weight=weight, note=note)

        def remove_relation(self, a, b, rel_id):
            bobj = self.get_between(a, b)
            if not bobj:
                return None
            return bobj.remove_relation(rel_id)

        def get_relations_for(self, a, b):
            bobj = self.get_between(a, b)
            return bobj.get_relations() if bobj else []

        def get_primary_relation(self, a, b):
            """Return the highest-weight relation between a and b or None."""
            rels = self.get_relations_for(a, b)
            if not rels:
                return None
            try:
                rels_sorted = sorted(rels, key=lambda r: int(r.get('weight', 0)), reverse=True)
                return rels_sorted[0]
            except Exception:
                return rels[0]
        
        def get_between(self, a, b):
            if not a or not b or a == b:
                return None
            return self.bonds.get(self._key(a, b))
        
        def ensure(self, a, b):
            if not a or not b or a == b:
                return None
            key = self._key(a, b)
            if key not in self.bonds:
                bid = f"{key[0]}__{key[1]}"
                self.bonds[key] = Bond(bid, key[0], key[1])
            return self.bonds[key]
        
        def get_for(self, cid):
            res = []
            for bond in self.bonds.values():
                if bond.a_id == cid or bond.b_id == cid:
                    res.append(bond)
            return res

    bond_manager = BondManager()

    def bond_get_stat(a_id, b_id, stat, default=0):
        b = bond_manager.get_between(a_id, b_id)
        return b.get_stat(stat, default) if b else default

    def bond_stat(other_id, stat, default=0):
        return bond_get_stat(pc.id, other_id, stat, default)

    def bond_set_stat(a_id, b_id, stat, value):
        b = bond_manager.ensure(a_id, b_id)
        if not b:
            return False
        b.set_stat(stat, value)
        return True

    def bond_add_stat(a_id, b_id, stat, delta):
        b = bond_manager.ensure(a_id, b_id)
        if not b:
            return False
        b.add_stat(stat, delta)
        return True

    def bond_has_tag(a_id, b_id, tag):
        b = bond_manager.get_between(a_id, b_id)
        return b.has_tag(tag) if b else False

    def bond_add_tag(a_id, b_id, tag):
        b = bond_manager.ensure(a_id, b_id)
        if not b:
            return False
        b.add_tag(tag)
        return True

    def bond_remove_tag(a_id, b_id, tag):
        b = bond_manager.get_between(a_id, b_id)
        if not b:
            return False
        b.remove_tag(tag)
        return True

    def bond_tags(a_id, b_id):
        b = bond_manager.get_between(a_id, b_id)
        return list(b.tags) if b else []

    def bond_add_relation(a_id, b_id, rel_id, rel_type=None, a_label=None, b_label=None, weight=0, note=None):
        return bond_manager.set_relation(a_id, b_id, rel_id, rel_type=rel_type, a_label=a_label, b_label=b_label, weight=weight, note=note)

    def bond_get_relations(a_id, b_id):
        return bond_manager.get_relations_for(a_id, b_id)

    def bond_get_primary(a_id, b_id):
        rel = bond_manager.get_primary_relation(a_id, b_id)
        return rel

    def bond_remove_relation(a_id, b_id, rel_id):
        return bond_manager.remove_relation(a_id, b_id, rel_id)

    def bond_level_from_value(val):
        if val <= -50: return "Hostile"
        if val <= -20: return "Cold"
        if val < 20: return "Neutral"
        if val < 50: return "Warm"
        return "Allied"

    def bond_level(a_id, b_id, stat):
        return bond_level_from_value(bond_get_stat(a_id, b_id, stat, 0))

    def give_item(item_id, count=1):
        count = max(1, int(count))
        it = item_manager.get(item_id)
        if it:
            return pc.add_item(it, count=count, reason="give")
        return False

    def take_item(item_id, count=1):
        count = max(1, int(count))
        return pc.remove_items_by_id(item_id, count=count, reason="take")

    def add_gold(amount):
        pc.gold = max(0, int(pc.gold + amount))
        return pc.gold

    def cond_jump(expr, label_true, label_false=None):
        ok = safe_eval_bool(expr, {"pc": pc, "rpg_world": rpg_world, "flags": world_flags, "flag_get": flag_get, "bond": bond_get_stat, "bond_has_tag": bond_has_tag, "bond_level": bond_level, "faction_get": faction_manager.get_reputation})
        if ok and label_true and renpy.has_label(label_true):
            renpy.jump(label_true)
        elif (not ok) and label_false and renpy.has_label(label_false):
            renpy.jump(label_false)
        return ok

    def perk_add(perk_id, duration_minutes=None):
        p = perk_manager.get(perk_id)
        if not p:
            renpy.notify("Unknown perk")
            return False
        duration = duration_minutes if duration_minutes is not None else p.duration_minutes
        ok, msg = pc.add_perk(perk_id, duration)
        renpy.notify(msg)
        return ok

    def perk_remove(perk_id):
        ok = pc.remove_perk(perk_id)
        if ok:
            renpy.notify("Perk removed")
        return ok

    def status_add(status_id, duration_minutes=None):
        s = status_manager.get(status_id)
        if not s:
            renpy.notify("Unknown status")
            return False
        duration = duration_minutes if duration_minutes is not None else s.duration_minutes
        ok, msg = pc.add_status(status_id, duration)
        renpy.notify(msg)
        return ok

    def status_remove(status_id):
        ok = pc.remove_status(status_id)
        if ok:
            renpy.notify("Status removed")
        return ok

    class Perk(object):
        def __init__(self, id, name, description="", mods=None, tags=None, duration_minutes=None):
            self.id = id
            self.name = name
            self.description = description
            self.mods = mods or {}
            self.tags = set(tags or [])
            self.duration_minutes = duration_minutes

    class StatusEffect(object):
        def __init__(self, id, name, description="", mods=None, tags=None, duration_minutes=None):
            self.id = id
            self.name = name
            self.description = description
            self.mods = mods or {}
            self.tags = set(tags or [])
            self.duration_minutes = duration_minutes

    class PerkManager:
        def __init__(self): self.registry = {}
        def register(self, p): self.registry[p.id] = p
        def get(self, pid): return self.registry.get(pid)
        def get_all(self): return sorted(self.registry.values(), key=lambda x: x.name)

    class StatusManager:
        def __init__(self): self.registry = {}
        def register(self, s): self.registry[s.id] = s
        def get(self, sid): return self.registry.get(sid)
        def get_all(self): return sorted(self.registry.values(), key=lambda x: x.name)

    perk_manager = PerkManager()
    status_manager = StatusManager()

    # --- BASE MIXINS (must be defined first) ---
    class SpatialObject(object):
        """Mixin for objects with position data"""
        def __init__(self, x=0, y=0, **kwargs):
            self.x, self.y = x, y
        
        def distance_to(self, other):
            return ((self.x - other.x) ** 2 + (self.y - other.y) ** 2) ** 0.5
        
        def move_to(self, x, y):
            self.x, self.y = x, y

    TAG_TAXONOMY = {
        "type": {"weapon", "armor", "consumable", "tool", "material", "quest", "key", "currency", "container"},
        "consumable": {"food", "drink", "medical", "buff", "ammo"},
        "rarity": {"common", "uncommon", "rare", "epic", "legendary"},
        "damage": {"melee", "ranged", "magic", "thrown"},
        "utility": {"light", "lockpick", "repair", "crafting"},
    }
    TAG_ALIASES = {
        "quest_item": "quest",
        "credits": "currency",
        "coin": "currency",
        "coins": "currency",
        "health": "medical",
        "med": "medical",
        "meds": "medical",
        "ammo_pack": "ammo",
        "mats": "material",
    }

    def _canonical_tag(tag):
        if tag is None:
            return None
        t = str(tag).strip().lower().replace(" ", "_")
        return TAG_ALIASES.get(t, t)

    def _normalize_tags(tags):
        if not tags:
            return set()
        return set(_canonical_tag(t) for t in tags if str(t).strip())

    class TaggedObject(object):
        """Mixin for objects with tags for filtering"""
        def __init__(self, tags=None, **kwargs):
            self.tags = _normalize_tags(tags)
        
        def has_tag(self, tag):
            return _canonical_tag(tag) in self.tags
        
        def has_any_tag(self, tags):
            return bool(self.tags & _normalize_tags(tags))
        
        def has_all_tags(self, tags):
            return _normalize_tags(tags) <= self.tags
        
        def add_tag(self, tag):
            self.tags.add(_canonical_tag(tag))
        
        def remove_tag(self, tag):
            self.tags.discard(_canonical_tag(tag))

    # --- ITEM SYSTEM ---
    class Item(TaggedObject):
        def __init__(self, name="Unknown", description="", weight=0, value=0, volume=0, tags=None, factions=None, equip_slots=None, outfit_part=None, stackable=False, stack_size=1, quantity=1, owner_id=None, stolen=False, image=None, actions=None, id=None, **kwargs):
            TaggedObject.__init__(self, tags)
            self.id = id
            self.factions = set(factions or [])
            self.name, self.description, self.weight, self.value = name, description, weight, value
            self.volume = float(volume) if volume is not None else 0
            self.image = image
            self.actions = actions or []
            self.stack_size = max(1, int(stack_size or 1))
            self.stackable = bool(stackable) or self.stack_size > 1
            self.quantity = max(1, int(quantity or 1))
            self.owner_id = owner_id
            self.stolen = bool(stolen)
            self.equip_slots = equip_slots or []
            # Legacy compatibility - map outfit_part to equip_slots if provided
            if outfit_part and not equip_slots:
                self.equip_slots = [outfit_part]
            self.outfit_part = outfit_part

    class ItemManager:
        def __init__(self): self.registry = {}
        def register(self, sid, obj): self.registry[sid.lower()] = obj
        def get(self, sid):
            base = self.registry.get(sid.lower())
            return copy.copy(base) if base else None
        def get_id_of(self, obj):
            if not obj: return "unknown"
            if getattr(obj, "id", None):
                return str(obj.id).lower()
            for k, v in self.registry.items():
                if v.name == obj.name: return k
            if getattr(obj, "name", None):
                return str(obj.name).lower().replace(" ", "_")
            return "unknown"

    item_manager = ItemManager()

    def item_show_image(item_or_id=None):
        """Show item image overlay if available."""
        item = item_or_id
        if isinstance(item_or_id, str):
            item = item_manager.get(item_or_id)
        if item is None:
            renpy.store.item_inspect_image = None
            renpy.store.item_inspect_title = ""
            return
        image = getattr(item, "image", None)
        if image and not renpy.loadable(image):
            image = None
        if image is None:
            candidate = f"images/items/{item_manager.get_id_of(item)}.png"
            if renpy.loadable(candidate):
                image = candidate
        renpy.store.item_inspect_image = image
        renpy.store.item_inspect_title = item.name
        renpy.show_screen("item_inspect_image")

    def item_hide_image():
        renpy.hide_screen("item_inspect_image")
        renpy.store.item_inspect_image = None
        renpy.store.item_inspect_title = ""

    def get_item_icon(item_or_id, fallback=None):
        """Return an item icon path, falling back to a generic icon."""
        item = item_or_id
        if isinstance(item_or_id, str):
            item = item_manager.get(item_or_id)
        if item is None:
            return None
        icon = getattr(item, "image", None)
        if icon and renpy.loadable(icon):
            return icon
        item_id = item_manager.get_id_of(item)
        for ext in ("png", "webp", "jpg", "jpeg"):
            candidate = f"images/items/{item_id}.{ext}"
            if renpy.loadable(candidate):
                return candidate
        if fallback is None:
            fallback = "images/items/unknown.webp"
        if fallback and renpy.loadable(fallback):
            return fallback
        alt = "images/icons/unknown.webp"
        return alt if renpy.loadable(alt) else None

    def _get_item_actions(item):
        actions = []
        for act in getattr(item, "actions", []) or []:
            label = act.get("label") if isinstance(act, dict) else None
            name = act.get("name") if isinstance(act, dict) else None
            if label and renpy.has_label(label):
                actions.append((name or label, label))
        return actions

    def inspect_item(item_or_id):
        """Resolve an inventory item's inspect label and store it for calling."""
        item = item_or_id
        if isinstance(item_or_id, str):
            item = item_manager.get(item_or_id)
        if not item:
            return

        # If we're inside an interaction, queue a safe inspect label and exit.
        if not getattr(store, "inspect_force", False):
            try:
                if renpy.in_interaction():
                    queue_inspect_item(item)
                    return
            except Exception:
                pass

        item_id = item_manager.get_id_of(item)
        sep = "__"

        # Try inspect label first, then flow label as fallback
        inspect_label = sep.join(["ITEM", item_id, "inspect"])
        if not renpy.has_label(inspect_label):
            alt_label = sep.join(["ITEM", item_id, "Inspect"])
            if renpy.has_label(alt_label):
                inspect_label = alt_label
        if not renpy.has_label(inspect_label):
            flow_label = sep.join(["ITEM", item_id, "flow"])
            if renpy.has_label(flow_label):
                inspect_label = flow_label

        # Store results for _inspect_item_pending to use
        if renpy.has_label(inspect_label):
            store.inspect_resolved_label = inspect_label
        else:
            store.inspect_resolved_label = None
        store.inspect_resolved_item = item

    def queue_inspect_item(item_or_id):
        item = item_or_id
        if isinstance(item_or_id, str):
            item = item_manager.get(item_or_id)
        if not item:
            return
        store.pending_inspect_item_id = item_manager.get_id_of(item)
        if hasattr(store, "flow_queue"):
            store.flow_queue.queue_label("inspect_item_pending")

label inspect_item_pending:
    $ store.inspect_force = True
    $ iid = store.pending_inspect_item_id
    $ store.pending_inspect_item_id = None
    if not iid:
        $ store.inspect_force = False
        return

    # Resolve the label
    $ inspect_item(iid)
    $ resolved_label = store.inspect_resolved_label
    $ resolved_item = store.inspect_resolved_item
    $ store.inspect_force = False

    # Hide phone UI during inspection
    $ old_phone_state = phone_state
    $ old_phone_app = phone_current_app
    $ phone_state = "mini"
    $ phone_transition = None

    if resolved_label:
        call expression resolved_label
    elif resolved_item and resolved_item.description:
        $ item_show_image(resolved_item)
        "[resolved_item.description]"
        $ item_hide_image()

    $ item_hide_image()

    # Restore phone UI
    $ phone_state = old_phone_state
    $ phone_current_app = old_phone_app

    if store._return_to_inventory:
        $ store._return_to_inventory = False
        call screen inventory_screen
    return

init -10 python:
    def _resolve_inventory(ref):
        if ref in (None, "", "none"):
            return None
        if isinstance(ref, Inventory):
            return ref
        if isinstance(ref, RPGCharacter):
            return ref
        key = str(ref).lower()
        if key in ("player", "pc"):
            return pc
        if key == "char":
            return getattr(store, "_interact_target_char", None)
        if key in rpg_world.characters:
            return rpg_world.characters.get(key)
        if key in rpg_world.shops:
            return rpg_world.shops.get(key)
        return None

    def give_item_between(item_id, source_id=None, target_id=None, count=1, assign_owner=True):
        """Transfer an item between inventories (used by GIVE flows)."""
        count = max(1, int(count))
        src = _resolve_inventory(source_id)
        tgt = _resolve_inventory(target_id)
        if not src or not tgt:
            return False
        it = item_manager.get(item_id)
        if not it:
            return False
        return src.transfer_to(it, tgt, count=count, reason="gift", assign_owner=assign_owner)

    def get_give_label(char, item_or_id):
        item = item_or_id
        if isinstance(item_or_id, str):
            item = item_manager.get(item_or_id)
        if not item or not char:
            return None
        item_id = item_manager.get_id_of(item)
        give_map = getattr(char, "give_flows", {}) or {}
        return give_map.get(item_id)

    def is_givable(char, item_or_id):
        return bool(get_give_label(char, item_or_id))

    class Recipe(object):
        def __init__(self, id, name, inputs, output, req_skill=None, tags=None):
            self.id = id
            self.name = name
            self.inputs = inputs # {item_id: count}
            self.output = output # {item_id: count}
            self.req_skill = req_skill # {skill_name: level}
            self.tags = set(tags or [])

    class CraftingManager:
        def __init__(self):
            self.recipes = {}
        
        def register(self, recipe):
            self.recipes[recipe.id] = recipe
            
        def get_all(self):
            return sorted(self.recipes.values(), key=lambda x: x.name)

        def can_craft(self, recipe, inventory):
            for item_id, count in recipe.inputs.items():
                current_count = inventory.get_item_count(item_id=item_id)
                if current_count < count:
                    return False, f"Missing {item_id}"
            
            if recipe.req_skill:
                for skill, level in recipe.req_skill.items():
                    if pc.stats.get(skill) < level:
                        return False, f"Need {skill} {level}"
            
            return True, "OK"

        def craft(self, recipe, inventory):
            can, msg = self.can_craft(recipe, inventory)
            if not can:
                renpy.notify(msg)
                return False
            
            # Consume inputs
            for item_id, count in recipe.inputs.items():
                inventory.remove_items_by_id(item_id, count=count, reason="craft")
            
            # Grant outputs
            for item_id, count in recipe.output.items():
                new_item = item_manager.get(item_id)
                if new_item:
                    inventory.add_item(new_item, count=count, force=True, reason="craft")
            
            renpy.notify(f"Crafted {recipe.name}")
            event_manager.dispatch("ITEM_CRAFTED", item=recipe.output, recipe=recipe.id)
            return True

    crafting_manager = CraftingManager()

    class EventManager:
        def __init__(self):
            self.listeners = {}

        def subscribe(self, etype, fn):
            self.listeners.setdefault(etype, set()).add(fn)

        def unsubscribe(self, etype, fn):
            if etype in self.listeners and fn in self.listeners[etype]:
                self.listeners[etype].remove(fn)

        def dispatch(self, etype, **kwargs):
            quest_manager.handle_event(etype, **kwargs)
            if "ach_mgr" in globals() and ach_mgr is not None:
                ach_mgr.handle_event(etype, **kwargs)
            for fn in list(self.listeners.get(etype, [])):
                try:
                    fn(etype, **kwargs)
                except Exception:
                    pass

    event_manager = EventManager()

    class CharacterFixture(object):
        """A place or object a character can fixate to (seat, bed, table, floor spot)."""
        def __init__(self, id, name, fixture_type="seat", location_id=None, x=0, y=0, tags=None):
            self.id = id
            self.name = name
            self.fixture_type = fixture_type or "seat"
            self.location_id = location_id
            self.x = x
            self.y = y
            self.tags = set(tags or [])
            self.occupied_by = None

        def is_occupied(self):
            return self.occupied_by is not None

        def fixate(self, char):
            if self.occupied_by and self.occupied_by != char.id:
                return False, "Occupied"
            # Unfixate from previous fixture if needed
            if getattr(char, "fixated_to", None) and getattr(char, "fixated_to") != self.id:
                fixture_manager.unfixate_char(char)
            self.occupied_by = char.id
            char.fixated_to = self.id
            if self.x is not None and self.y is not None:
                char.x, char.y = self.x, self.y
            event_manager.dispatch("CHARACTER_FIXATED", actor=char.id, fixture=self.id, fixture_type=self.fixture_type, location=self.location_id)
            return True, "Fixated"

        def unfixate(self, char=None):
            target_id = self.occupied_by
            if char is not None and target_id and target_id != char.id:
                return False, "Not occupied by this character"
            self.occupied_by = None
            if char is not None:
                char.fixated_to = None
            event_manager.dispatch("CHARACTER_UNFIXATED", actor=target_id, fixture=self.id, fixture_type=self.fixture_type, location=self.location_id)
            return True, "Unfixated"

    class FixtureManager(object):
        def __init__(self):
            self.registry = {}

        def register(self, fixture):
            if fixture:
                self.registry[fixture.id] = fixture

        def get(self, fixture_id):
            return self.registry.get(fixture_id)

        def _build_fixture_id(self, location_id, entity_id):
            loc = location_id or "unknown"
            ent = entity_id or "fixture"
            return f"{loc}#{ent}"

        def get_by_entity(self, location_id, entity):
            if not isinstance(entity, dict):
                return None
            ent_id = entity.get("fixture_id") or entity.get("id")
            fixture_id = self._build_fixture_id(location_id, ent_id)
            existing = self.registry.get(fixture_id)
            if existing:
                return existing
            name = entity.get("name") or ent_id or "Fixture"
            ftype = entity.get("fixture_type") or entity.get("fixture") or entity.get("use") or "seat"
            fixture = CharacterFixture(
                fixture_id,
                name,
                fixture_type=ftype,
                location_id=location_id,
                x=entity.get("x", 0),
                y=entity.get("y", 0),
                tags=entity.get("tags", [])
            )
            self.register(fixture)
            return fixture

        def fixate_char(self, char, fixture):
            if isinstance(fixture, str):
                fixture = self.get(fixture)
            if not fixture or not char:
                return False, "Invalid"
            return fixture.fixate(char)

        def unfixate_char(self, char):
            if not char or not getattr(char, "fixated_to", None):
                return False, "Not fixated"
            fixture = self.get(char.fixated_to)
            if not fixture:
                char.fixated_to = None
                return False, "Missing fixture"
            return fixture.unfixate(char)

    fixture_manager = FixtureManager()

    class TimeManager(object):
        def __init__(self, hour=8, minute=0, day=1):
            self.hour, self.minute = hour, minute
            self.day = day
        
        @property
        def time_string(self): return "{:02d}:{:02d} (Day {})".format(self.hour, self.minute, self.day)
        
        @property
        def time_of_day(self):
            if 5 <= self.hour < 12: return "Morning"
            elif 12 <= self.hour < 17: return "Afternoon"
            elif 17 <= self.hour < 21: return "Evening"
            else: return "Night"
        
        @property
        def total_minutes(self):
            return self.day * 1440 + self.hour * 60 + self.minute

        def advance(self, mins):
            self.minute += mins
            while self.minute >= 60:
                self.minute -= 60
                self.hour += 1
            while self.hour >= 24:
                self.hour -= 24
                self.day += 1
            
            # notify world of time change
            rpg_world.update_schedules()
            # tick timed effects
            try:
                pc.tick_effects()
            except Exception:
                pass

    time_manager = TimeManager()

    class QuestTick:
        def __init__(self, id, name):
            self.id, self.name = id, name
            self.state, self.flow_label, self.trigger_data, self.guidance = "hidden", None, {}, {}

            self.current_value, self.required_value = 0, 1
        def check_trigger(self, etype, **kwargs):
            if self.state not in ["shown", "active"]: 
                return False
            # event compare (case-insensitive)
            if str(self.trigger_data.get("event")).upper() != str(etype).upper():
                return False
            for k, v in self.trigger_data.items():
                if k in ["event", "cond", "total"]: 
                    continue
                actual = kwargs.get(k)
                if isinstance(v, list):
                    if actual not in v:
                        return False
                else:
                    try:
                        if isinstance(actual, (int, float)) and str(v).replace('.', '', 1).isdigit():
                            if float(actual) != float(v):
                                return False
                        else:
                            if str(actual) != str(v):
                                return False
                    except Exception:
                        if str(actual) != str(v):
                            return False
            if self.trigger_data.get("cond"):
                try:
                    if not safe_eval_bool(self.trigger_data["cond"], {"player": pc, "rpg_world": rpg_world, "kwargs": kwargs, "flags": world_flags, "flag_get": flag_get, "bond": bond_get_stat, "bond_has_tag": bond_has_tag, "bond_level": bond_level, "faction_get": faction_manager.get_reputation}): 
                        return False
                except Exception as e:
                    renpy.log(f"Error evaluating tick cond for {self.id}: {e}")
                    return False
            self.current_value = int(kwargs.get("total", self.current_value + 1))
            try:
                required = int(self.trigger_data.get("total", self.required_value))
            except Exception:
                required = self.required_value
            if self.current_value >= required:
                self.state = "complete"
                return True
            return False

    class DialogueOption(object):
        def __init__(self, id, chars, short_text, long_text, emoji, label, cond=None, tags=None, memory=False, reason=None):
            self.id = id
            self.chars = set(chars or [])
            self.short_text = short_text
            self.long_text = long_text
            self.emoji = emoji
            self.label = label
            self.cond = cond
            self.tags = tags or []
            self.memory = memory
            self.reason = reason
        
        def is_available(self, char):
            if self.chars and char.id not in self.chars and "*" not in self.chars:
                return False
            if self.cond and str(self.cond).strip() and str(self.cond) != "True":
                return safe_eval_bool(self.cond, {"pc": pc, "char": char, "rpg_world": rpg_world, "quest_manager": quest_manager, "flags": world_flags, "flag_get": flag_get, "bond": bond_get_stat, "bond_has_tag": bond_has_tag, "bond_level": bond_level, "faction_get": faction_manager.get_reputation})
            return True

        def availability_status(self, char):
            if self.chars and char.id not in self.chars and "*" not in self.chars:
                return False, "Not for this character."
            if self.cond and str(self.cond).strip() and str(self.cond) != "True":
                ok = safe_eval_bool(self.cond, {"pc": pc, "char": char, "rpg_world": rpg_world, "quest_manager": quest_manager, "flags": world_flags, "flag_get": flag_get, "faction_get": faction_manager.get_reputation})
                if not ok:
                    return False, self.reason or "Locked."
            return True, "Available."

    class DialogueManager:
        def __init__(self):
            self.options = {}
        def register(self, opt):
            self.options[opt.id] = opt
        def get_for_char(self, char):
            opts = [opt for opt in self.options.values() if (not opt.chars or char.id in opt.chars or "*" in opt.chars)]
            return sorted(opts, key=lambda x: x.id)
        def get_available(self, char):
            opts = [opt for opt in self.options.values() if opt.is_available(char)]
            return sorted(opts, key=lambda x: x.id)

    dialogue_manager = DialogueManager()

    class StoryOrigin(object):
        def __init__(self, id, name, description, character, intro_label, image=None):
            self.id = id
            self.name = name
            self.description = description
            self.character = character
            self.intro_label = intro_label
            self.image = image

    class StoryOriginManager:
        def __init__(self):
            self.origins = {}
        def register(self, origin):
            self.origins[origin.id] = origin
        def get_all(self):
            return sorted(self.origins.values(), key=lambda x: x.name)
        def get(self, origin_id):
            return self.origins.get(origin_id)

    story_origin_manager = StoryOriginManager()

    class Quest:
        def __init__(self, id, name, description="", category="side", giver=None, location=None, tags=None, prereqs=None, rewards=None, start_trigger=None, origin=False, character=None, image=None, outcomes=None):
            self.id = id
            self.name = name
            self.description = description
            self.category = category or "side"
            self.giver = giver
            self.location = location
            self.tags = set(tags or [])
            self.prereqs = prereqs or {}
            self.rewards = rewards or {}
            self.outcomes = outcomes or []
            self.start_trigger = start_trigger or {}
            self.origin = bool(origin)
            self.character = character
            self.image = image
            self.state = "unknown"
            self.ticks = []
            self.rewards_applied = False
        def add_tick(self, t): self.ticks.append(t)
        def can_start(self):
            # Quest prereqs: quests passed + flags set + optional condition.
            req = self.prereqs or {}
            for qid in req.get("quests", []) or []:
                q = quest_manager.quests.get(qid)
                if not q or q.state != "passed":
                    return False
            for flag in req.get("flags", []) or []:
                if not flag_get(flag, False):
                    return False
            for flag in req.get("not_flags", []) or []:
                if flag_get(flag, False):
                    return False
            cond = req.get("cond")
            if cond and str(cond).strip():
                if not safe_eval_bool(cond, {"pc": pc, "rpg_world": rpg_world, "flags": world_flags, "flag_get": flag_get, "quest_manager": quest_manager, "faction_get": faction_manager.get_reputation}):
                    return False
            return True
        def start(self):
            if self.state in ["unknown", "known"]:
                if not self.can_start():
                    renpy.notify(f"Quest Locked: {self.name}")
                    event_manager.dispatch("QUEST_START_BLOCKED", quest=self.id)
                    return False
                self.state = "active"
                if self.ticks:
                    self.ticks[0].state = "active"
                renpy.notify(f"Quest Started: {self.name}")
                event_manager.dispatch("QUEST_STARTED", quest=self.id)
                if renpy.has_label(f"QUEST__{self.id}__started"): renpy.call(f"QUEST__{self.id}__started")
                return True
            return False
        def _apply_rewards(self, rewards):
            if self.rewards_applied:
                return
            rewards = rewards or {}
            gold = int(rewards.get("gold", 0) or 0)
            if gold:
                add_gold(gold)
            for item_id, count in (rewards.get("items", {}) or {}).items():
                give_item(item_id, count)
            for flag in rewards.get("flags", []) or []:
                flag_set(flag, True)
            # Reputation changes: allow 'reputation' or 'reputations' mapping
            rep_map = rewards.get('reputation') or rewards.get('reputations') or {}
            if isinstance(rep_map, dict):
                for fid, delta in rep_map.items():
                    try:
                        faction_manager.modify_reputation(str(fid), int(delta))
                    except Exception:
                        try:
                            faction_manager.modify_reputation(str(fid), float(delta))
                        except Exception:
                            renpy.log(f"Invalid reputation delta for faction {fid}: {delta}")
            # Faction membership changes
            for fid in rewards.get('factions_add', []) or []:
                try:
                    pc.join_faction(fid)
                except Exception:
                    renpy.log(f"Failed to add PC to faction {fid}")
            for fid in rewards.get('factions_remove', []) or []:
                try:
                    pc.leave_faction(fid)
                except Exception:
                    renpy.log(f"Failed to remove PC from faction {fid}")
            self.rewards_applied = True

        def _choose_outcome(self, outcome_id=None):
            """Evaluate outcomes (list of dicts) and return the first matching outcome dict.
            Each outcome may contain a 'cond' expression evaluated with safe_eval_bool.
            If none match, return None."""
            try:
                for o in (self.outcomes or []):
                    if not isinstance(o, dict):
                        continue
                    # If outcome_id specified, match by id immediately
                    if outcome_id and (str(o.get('id')) == str(outcome_id) or str(o.get('name')) == str(outcome_id)):
                        return o
                    cond = o.get('cond')
                    if not cond or str(cond).strip() == '':
                        # No condition -> default outcome (lowest priority)
                        default = o
                        continue
                    try:
                        ok = safe_eval_bool(cond, {"pc": pc, "rpg_world": rpg_world, "flags": world_flags, "flag_get": flag_get, "quest_manager": quest_manager, "faction_get": faction_manager.get_reputation})
                    except Exception as e:
                        renpy.log(f"Error evaluating outcome cond for quest {self.id}: {e}")
                        ok = False
                    if ok:
                        return o
                # If none matched, return default if present
                if 'default' in locals() and default:
                    return default
            except Exception as e:
                renpy.log(f"Error choosing outcome for quest {self.id}: {e}")
            return None
        def complete(self, outcome_id=None):
            self.state = "passed"
            # If outcomes are defined, evaluate and apply the matching outcome's rewards/flags
            outcome = None
            if self.outcomes:
                outcome = self._choose_outcome(outcome_id=outcome_id)
            if outcome and isinstance(outcome, dict):
                rewards = outcome.get('rewards', {}) or {}
                self._apply_rewards(rewards)
                # Apply any additional flags from outcome
                for flag in outcome.get('flags', []) or []:
                    flag_set(flag, True)
                # Apply faction membership changes if present at outcome level
                for fid in outcome.get('factions_add', []) or []:
                    try:
                        pc.join_faction(fid)
                    except Exception:
                        renpy.log(f"Failed to add PC to faction {fid} via outcome")
                for fid in outcome.get('factions_remove', []) or []:
                    try:
                        pc.leave_faction(fid)
                    except Exception:
                        renpy.log(f"Failed to remove PC from faction {fid} via outcome")
                renpy.log(f"Quest {self.id} completed with outcome: {outcome.get('id') or outcome.get('name')}")
            else:
                # Fallback to default rewards defined on the quest
                self._apply_rewards(self.rewards)

            renpy.notify(f"Quest Completed: {self.name}")
            event_manager.dispatch("QUEST_COMPLETED", quest=self.id)
            if renpy.has_label(f"QUEST__{self.id}__passed"): renpy.call(f"QUEST__{self.id}__passed")
            if quest_manager.active_quest_id == self.id:
                quest_manager.set_active_quest(None)
        def fail(self):
            self.state = "failed"
            renpy.notify(f"Quest Failed: {self.name}")
            event_manager.dispatch("QUEST_FAILED", quest=self.id)
            if renpy.has_label(f"QUEST__{self.id}__failed"): renpy.call(f"QUEST__{self.id}__failed")
            if quest_manager.active_quest_id == self.id:
                quest_manager.set_active_quest(None)

    class QuestManager:
        def __init__(self):
            self.quests, self.start_triggers = {}, {}
            self.active_quest_id = None
            self.trigger_index = {}
        def add_quest(self, q): self.quests[q.id] = q
        def get_origins(self):
            origins = [q for q in self.quests.values() if getattr(q, "origin", False)]
            return sorted(origins, key=lambda x: x.name)
        def start_quest(self, qid):
            q = self.quests.get(qid)
            if q and q.start():
                if not self.active_quest_id:
                    self.set_active_quest(q.id)
                return True
            return False
        def set_active_quest(self, qid):
            prev = self.active_quest_id
            if not qid or qid not in self.quests:
                self.active_quest_id = None
            else:
                self.active_quest_id = qid
            if prev != self.active_quest_id:
                event_manager.dispatch("QUEST_ACTIVE_CHANGED", quest=self.active_quest_id, previous=prev)
            return self.active_quest_id
        def get_active_quest(self):
            if self.active_quest_id and self.active_quest_id in self.quests:
                return self.quests[self.active_quest_id]
            return None
        def get_current_guidance(self):
            q = self.get_active_quest()
            if not q or q.state != "active": return None
            for t in q.ticks:
                if t.state == "active":
                    return t.guidance
            return None

        def complete_quest(self, qid):
            q = self.quests.get(qid)
            if q: q.complete()
        def fail_quest(self, qid):
            q = self.quests.get(qid)
            if q: q.fail()
        def update_goal(self, qid, gid, status="active"):
            target_quests = [self.quests[qid]] if qid and qid in self.quests else self.quests.values()
            
            for q in target_quests:
                for t in q.ticks:
                    if t.id == gid:
                        t.state = status
                        if status == "complete":
                            t.current_value = t.required_value
                            event_manager.dispatch("QUEST_TICK_COMPLETED", quest=q.id, tick=t.id)
                # Check for quest completion if manual update
                if status == "complete":
                    all_c = True
                    for t in q.ticks:
                        if t.state != "complete":
                            all_c = False
                            break
                    if all_c: q.complete()
                event_manager.dispatch("QUEST_UPDATED", quest=q.id)
        def register_start_trigger(self, qid, data): self.start_triggers[qid] = data
        def load_trigger_index(self, index):
            try:
                self.trigger_index = index or {}
            except Exception:
                self.trigger_index = {}
        def handle_event(self, etype, **kwargs):
            # Start triggers (unchanged)
            for qid, trigger in self.start_triggers.items():
                q = self.quests.get(qid)
                if q and q.state == "unknown" and self._match(trigger, etype, **kwargs): q.start()

            # Fast-path: use precompiled trigger index when available
            processed = set()
            ev_key = str(etype).upper()
            entries = self.trigger_index.get(ev_key, []) if getattr(self, 'trigger_index', None) else []
            if entries:
                for ent in entries:
                    qid = ent.get('quest')
                    tick_id = ent.get('tick')
                    q = self.quests.get(qid)
                    if not q or q.state != 'active':
                        continue
                    for t in q.ticks:
                        if t.id != tick_id:
                            continue
                        # check trigger with tick's stored trigger data
                        try:
                            if t.check_trigger(etype, **kwargs):
                                processed.add((q.id, t.id))
                                event_manager.dispatch("QUEST_TICK_COMPLETED", quest=q.id, tick=t.id)
                                if t.flow_label:
                                    if renpy.has_label(t.flow_label):
                                        renpy.call(t.flow_label)
                                    else:
                                        renpy.log(f"Missing flow label for quest {q.id} tick {t.id}: {t.flow_label}")
                        except Exception as e:
                            renpy.log(f"Error checking trigger for {q.id}.{t.id}: {e}")

            # Fallback scan for any other active quests/ticks not covered by index
            for q in self.quests.values():
                if q.state == "active":
                    any_done = False
                    for t in q.ticks:
                        if (q.id, t.id) in processed:
                            continue
                        if t.check_trigger(etype, **kwargs):
                            any_done = True
                            event_manager.dispatch("QUEST_TICK_COMPLETED", quest=q.id, tick=t.id)
                            if t.flow_label and renpy.has_label(t.flow_label):
                                renpy.call(t.flow_label)
                            elif t.flow_label:
                                renpy.log(f"Missing flow label for quest {q.id} tick {t.id}: {t.flow_label}")
                    if any_done:
                        all_c = True
                        for t in q.ticks:
                            if t.state != "complete":
                                all_c = False
                                if t.state in ["hidden", "shown"]: t.state = "active"
                                break
                        if all_c: q.complete()
                        event_manager.dispatch("QUEST_UPDATED", quest=q.id)
        def _match(self, t, etype, **kwargs):
            if str(t.get("event")).upper() != str(etype).upper(): return False
            for k, v in t.items():
                if k in ["event", "cond"]: continue
                actual = kwargs.get(k)
                # Support list membership
                if isinstance(v, list):
                    if actual not in v:
                        return False
                else:
                    try:
                        # numeric compare when possible
                        if isinstance(actual, (int, float)) and str(v).replace('.', '', 1).isdigit():
                            if float(actual) != float(v):
                                return False
                        else:
                            if str(actual) != str(v):
                                return False
                    except Exception:
                        if str(actual) != str(v):
                            return False
            if t.get("cond"):
                try:
                    return safe_eval_bool(t["cond"], {"player": pc, "rpg_world": rpg_world, "kwargs": kwargs, "flags": world_flags, "flag_get": flag_get, "bond": bond_get_stat, "bond_has_tag": bond_has_tag, "bond_level": bond_level, "faction_get": faction_manager.get_reputation})
                except Exception as e:
                    renpy.log(f"Error evaluating start trigger cond for {t}: {e}")
                    return False
            return True

    quest_manager = QuestManager()

    def quest_get_choices_for_menu(menu_id, char=None):
        """Return list of available quest-provided choices for a given menu target (char id or menu id).
        Each entry: {quest, id, text, label}.
        """
        res = []
        try:
            for q in quest_manager.quests.values():
                if q.state != 'active':
                    continue
                for choice in getattr(q, 'choices', []) or []:
                    # Menu matching: None means global; allow list or single
                    menu = choice.get('menu')
                    if menu:
                        if isinstance(menu, list):
                            if str(menu_id) not in [str(m) for m in menu]:
                                continue
                        else:
                            if str(menu) != str(menu_id) and not (hasattr(char, 'id') and str(menu) == str(getattr(char, 'id'))):
                                continue
                    # Evaluate condition
                    cond = choice.get('cond', True)
                    ok = safe_eval_bool(cond, {"pc": pc, "rpg_world": rpg_world, "flags": world_flags, "flag_get": flag_get, "bond": bond_get_stat, "bond_has_tag": bond_has_tag, "bond_level": bond_level, "faction_get": faction_manager.get_reputation, "char": (getattr(char, 'id', None))})
                    if ok:
                        res.append({"quest": q.id, "id": choice.get('id'), "text": choice.get('text'), "label": choice.get('label')})
        except Exception as e:
            renpy.log(f"Error while gathering quest choices for menu {menu_id}: {e}")
        return res

    # Small UI toast for goal/tick updates to give micro-feedback to the player.
    def _on_quest_tick(etype, **kwargs):
        try:
            qid = kwargs.get('quest')
            tick_id = kwargs.get('tick')
            q = quest_manager.quests.get(qid)
            t = None
            if q:
                for tt in q.ticks:
                    if tt.id == tick_id:
                        t = tt
                        break
            if q and t:
                renpy.notify(f"Goal updated: {q.name} — {t.name}")
            elif q:
                renpy.notify(f"Goal updated: {q.name}")
            else:
                renpy.notify(f"Goal updated")
        except Exception:
            pass

    event_manager.subscribe("QUEST_TICK_COMPLETED", _on_quest_tick)

    def set_character_known_location(char_id, location_id):
        """Mark a character's location as known (persisted) and notify systems.
        Can be called from flows or quest code to reveal where a person is even
        if the player hasn't met them yet.
        """
        try:
            if persistent.known_character_locations is None:
                persistent.known_character_locations = {}
            persistent.known_character_locations[str(char_id)] = str(location_id)
            # Update runtime object if present
            if getattr(rpg_world, 'characters', None) and str(char_id) in rpg_world.characters:
                setattr(rpg_world.characters[str(char_id)], 'known_location_id', str(location_id))
            renpy.notify(f"Location revealed: {char_id} @ {location_id}")
            event_manager.dispatch("CHAR_LOCATION_KNOWN", char=char_id, location=location_id)
            return True
        except Exception as e:
            renpy.log(f"Error setting known location for {char_id}: {e}")
            return False

    # --- DEBUG HELPERS ---
    def q_force_tick(qid, tick_idx):
        q = quest_manager.quests.get(qid)
        if q and tick_idx < len(q.ticks):
            t = q.ticks[tick_idx]
            t.state = "complete"
            t.current_value = t.required_value
            # Check for next tick or quest completion
            all_c = True
            for i, tick in enumerate(q.ticks):
                if tick.state != "complete":
                    all_c = False
                    if tick.state in ["hidden", "shown"]:
                        tick.state = "active"
                    break
            if all_c:
                q.complete()
            renpy.notify(f"Forced tick: {t.name}")

    def q_complete(qid):
        q = quest_manager.quests.get(qid)
        if q:
            for t in q.ticks:
                t.state = "complete"
                t.current_value = t.required_value
            q.complete()
            renpy.notify(f"Forced quest complete: {q.name}")

    # --- CORE ENTITY ---
    class Entity(SpatialObject, TaggedObject):
        def __init__(self, id, name, description="", label=None, x=0, y=0, tags=None, factions=None, sprite=None, **kwargs):
            SpatialObject.__init__(self, x, y)
            TaggedObject.__init__(self, tags)
            self.factions = set(factions or [])
            self.id, self.name, self.description, self.label = id, name, description, label
            self.sprite = sprite
        def interact(self):
            if self.label: renpy.jump(self.label)
            else: renpy.say(None, f"You see {self.name}. {self.description}")

    class Inventory(Entity):
        def __init__(self, id, name, items=None, blocked_tags=None, allowed_tags=None, max_weight=None, max_slots=None, owner_id=None, **kwargs):
            super(Inventory, self).__init__(id, name, **kwargs)
            self.items, self.gold = [], 0
            self.blocked_tags = _normalize_tags(blocked_tags)
            self.allowed_tags = _normalize_tags(allowed_tags)  # empty = allow all
            self.max_weight = float(max_weight) if max_weight is not None else None
            self.max_slots = int(max_slots) if max_slots is not None else None
            self.owner_id = owner_id
            self._encumbrance_state = "none"
            if items:
                for item_id in items:
                    it = item_manager.get(item_id)
                    if it:
                        self.add_item(it, count=None, force=True, reason="seed")

        def _item_id(self, item):
            return item_manager.get_id_of(item)

        def _stackable(self, item):
            return bool(getattr(item, "stackable", False) or getattr(item, "stack_size", 1) > 1)

        def _stack_size(self, item):
            try:
                return max(1, int(getattr(item, "stack_size", 1)))
            except Exception:
                return 1

        def _item_qty(self, item, count):
            if count is None:
                return max(1, int(getattr(item, "quantity", 1)))
            return max(1, int(count))

        def _same_ownership(self, a, b):
            return getattr(a, "owner_id", None) == getattr(b, "owner_id", None) and bool(getattr(a, "stolen", False)) == bool(getattr(b, "stolen", False))

        def get_total_weight(self):
            return sum(getattr(i, "weight", 0) * max(1, int(getattr(i, "quantity", 1))) for i in self.items)

        def get_used_slots(self):
            return len(self.items)

        def get_item_count(self, item_id=None, name=None):
            total = 0
            for itm in self.items:
                if item_id and self._item_id(itm) != item_id:
                    continue
                if name and itm.name != name:
                    continue
                total += max(1, int(getattr(itm, "quantity", 1)))
            return total

        def _estimate_new_stack_slots(self, item, qty):
            if not self._stackable(item):
                return qty
            stack_size = self._stack_size(item)
            item_id = self._item_id(item)
            free = 0
            for stack in self.items:
                if self._item_id(stack) != item_id or not self._stackable(stack):
                    continue
                if not self._same_ownership(stack, item):
                    continue
                free += max(0, stack_size - max(1, int(getattr(stack, "quantity", 1))))
            remaining = max(0, qty - free)
            if remaining <= 0:
                return 0
            return int(math.ceil(float(remaining) / float(stack_size)))

        def _can_accept_capacity(self, item, qty):
            if self.max_weight is not None:
                if self.get_total_weight() + (getattr(item, "weight", 0) * qty) > self.max_weight:
                    return False, "overweight"
            if self.max_slots is not None:
                new_slots = self._estimate_new_stack_slots(item, qty)
                if self.get_used_slots() + new_slots > self.max_slots:
                    return False, "full"
            return True, "ok"

        def _tags_allow(self, item):
            item_tags = getattr(item, "tags", set())
            if self.blocked_tags and item_tags & self.blocked_tags:
                return False
            if self.allowed_tags and not (item_tags & self.allowed_tags):
                return False
            return True

        def can_accept_item(self, item, qty=1):
            """Check if item can be added based on tag restrictions and capacity."""
            if not self._tags_allow(item):
                return False
            ok, _reason = self._can_accept_capacity(item, qty)
            return ok

        def _update_encumbrance(self):
            if self.max_weight is None or self.max_weight <= 0:
                return
            ratio = self.get_total_weight() / float(self.max_weight)
            if ratio < 0.7:
                state = "light"
            elif ratio < 0.9:
                state = "medium"
            elif ratio <= 1.0:
                state = "heavy"
            else:
                state = "over"
            if state != self._encumbrance_state:
                prev = self._encumbrance_state
                self._encumbrance_state = state
                event_manager.dispatch("ENCUMBRANCE_CHANGED", inventory=self.id, state=state, previous=prev, ratio=ratio)

        def get_encumbrance_ratio(self):
            if self.max_weight is None or self.max_weight <= 0:
                return 0.0
            return self.get_total_weight() / float(self.max_weight)

        def get_encumbrance_state(self):
            return self._encumbrance_state

        def _post_inventory_change(self, item, delta, added, reason=None):
            item_id = self._item_id(item)
            total = self.get_item_count(item_id=item_id)
            payload = {
                "item": item.name,
                "item_id": item_id,
                "quantity": int(delta),
                "total": total,
                "inventory": self.id,
                "reason": reason or "unspecified",
                "owner_id": getattr(item, "owner_id", None),
                "stolen": bool(getattr(item, "stolen", False)),
            }
            event_manager.dispatch("ITEM_GAINED" if added else "ITEM_REMOVED", **payload)
            event_manager.dispatch("INVENTORY_CHANGED", inventory=self.id, item_id=item_id, delta=int(delta), total=total)
            self._update_encumbrance()

        def add_item(self, i, count=None, force=False, reason=None):
            if not i:
                return False
            qty = self._item_qty(i, count)
            if getattr(i, "owner_id", None) is None and self.owner_id is not None:
                i.owner_id = self.owner_id
                i.stolen = False
            if not force:
                if not self._tags_allow(i):
                    event_manager.dispatch("INVENTORY_BLOCKED", inventory=self.id, item_id=self._item_id(i), quantity=qty, reason="tags")
                    return False
                ok, cap_reason = self._can_accept_capacity(i, qty)
                if not ok:
                    event_manager.dispatch("INVENTORY_BLOCKED", inventory=self.id, item_id=self._item_id(i), quantity=qty, reason=cap_reason)
                    return False

            item_id = self._item_id(i)
            use_original = i not in self.items
            if self._stackable(i):
                stack_size = self._stack_size(i)
                remaining = qty
                for stack in self.items:
                    if self._item_id(stack) != item_id or not self._stackable(stack):
                        continue
                    if not self._same_ownership(stack, i):
                        continue
                    free = stack_size - max(1, int(getattr(stack, "quantity", 1)))
                    if free <= 0:
                        continue
                    add = min(remaining, free)
                    stack.quantity += add
                    remaining -= add
                    if remaining <= 0:
                        break
                while remaining > 0:
                    add = min(remaining, stack_size)
                    if use_original:
                        new_item = i
                        use_original = False
                    else:
                        new_item = copy.copy(i)
                    new_item.quantity = add
                    self.items.append(new_item)
                    remaining -= add
            else:
                for _ in range(qty):
                    if use_original:
                        new_item = i
                        use_original = False
                    else:
                        new_item = copy.copy(i)
                    new_item.quantity = 1
                    self.items.append(new_item)

            self._post_inventory_change(i, qty, added=True, reason=reason)
            return True

        def remove_item(self, i, count=1, reason=None):
            if i not in self.items:
                return None
            qty = max(1, int(getattr(i, "quantity", 1)))
            take = max(1, int(count))
            take = min(take, qty)
            if self._stackable(i) and qty > take:
                i.quantity = qty - take
                removed = copy.copy(i)
                removed.quantity = take
                self._post_inventory_change(i, take, added=False, reason=reason)
                return removed
            self.items.remove(i)
            self._post_inventory_change(i, qty, added=False, reason=reason)
            return i

        def remove_items_by_id(self, item_id, count=1, reason=None):
            remaining = max(1, int(count))
            removed = 0
            for itm in list(self.items):
                if self._item_id(itm) != item_id:
                    continue
                qty = max(1, int(getattr(itm, "quantity", 1)))
                if qty <= remaining:
                    self.items.remove(itm)
                    self._post_inventory_change(itm, qty, added=False, reason=reason)
                    removed += qty
                    remaining -= qty
                else:
                    itm.quantity = qty - remaining
                    self._post_inventory_change(itm, remaining, added=False, reason=reason)
                    removed += remaining
                    remaining = 0
                if remaining <= 0:
                    break
            return removed

        def transfer_to(self, i, target, count=1, reason="transfer", assign_owner=False):
            probe = i
            if assign_owner:
                probe = copy.copy(i)
                probe.owner_id = target.owner_id
                probe.stolen = False
            if not target.can_accept_item(probe, count):
                return False
            removed = self.remove_item(i, count=count, reason="transfer_out")
            if not removed:
                return False
            if assign_owner:
                removed.owner_id = target.owner_id
                removed.stolen = False
            else:
                if getattr(removed, "owner_id", None) and target.owner_id != removed.owner_id:
                    if not getattr(removed, "stolen", False):
                        removed.stolen = True
                        event_manager.dispatch("ITEM_STOLEN", item_id=self._item_id(removed), owner=removed.owner_id, source=self.id, target=target.id, reason=reason)
                elif getattr(removed, "owner_id", None) and target.owner_id == removed.owner_id:
                    removed.stolen = False
            event_manager.dispatch("ITEM_OWNERSHIP_CHANGED", item_id=self._item_id(removed), owner=removed.owner_id, stolen=bool(getattr(removed, "stolen", False)))
            if not target.add_item(removed, count=None, reason=reason):
                self.add_item(removed, count=None, force=True, reason="transfer_rollback")
                return False
            event_manager.dispatch("ITEM_TRANSFERRED", source=self.id, target=target.id, item_id=self._item_id(removed), quantity=max(1, int(getattr(removed, "quantity", 1))))
            return True

        def get_items_with_tag(self, tag):
            t = _canonical_tag(tag)
            return [i for i in self.items if hasattr(i, 'tags') and t in i.tags]

        def get_items_without_tag(self, tag):
            t = _canonical_tag(tag)
            return [i for i in self.items if not hasattr(i, 'tags') or t not in i.tags]

    class Container(Inventory):
        def __init__(self, id, name, **kwargs):
            super(Container, self).__init__(id, name, **kwargs)
        def interact(self): renpy.show_screen("container_screen", container=self)

    class Shop(Inventory):
        def __init__(self, id, name, buy_mult=1.2, sell_mult=0.6, owner_id=None, **kwargs):
            super(Shop, self).__init__(id, name, owner_id=owner_id or id, **kwargs)
            self.buy_mult, self.sell_mult = buy_mult, sell_mult
        def get_buy_price(self, i): return int(i.value * self.buy_mult)
        def get_sell_price(self, i): return int(i.value * self.sell_mult)
        def interact(self): renpy.show_screen("shop_screen", shop=self)

    # --- STAT SYSTEM ---
    class StatBlock:
        """Flexible stat container that loads stats from data"""
        def __init__(self, stats_dict=None):
            self._stats = stats_dict or {}

        
        def __getattr__(self, name):
            if name.startswith('_'):
                raise AttributeError(name)
            return self._stats.get(name, 0)
        
        def __setattr__(self, name, value):
            if name.startswith('_'):
                super().__setattr__(name, value)
            else:
                self._stats[name] = value
        
        def get(self, name, default=0):
            return self._stats.get(name, default)
        
        def set(self, name, value):
            self._stats[name] = value
        
        def keys(self):
            return self._stats.keys()
        
        def items(self):
            return self._stats.items()



    # --- SLOT SYSTEM ---
    class SlotRegistry:
        """Manages equipment slot definitions and body types"""
        def __init__(self):
            self.slots = {}  # slot_id -> {"name": str, "unequips": set}
            self.body_types = {}  # body_type_id -> [slot_ids]
        
        def register_slot(self, slot_id, name, unequips=None):
            self.slots[slot_id] = {"name": name, "unequips": set(unequips or [])}
        
        def register_body_type(self, type_id, name, slots):
            self.body_types[type_id] = {"name": name, "slots": slots}
        
        def get_slots_for_body(self, body_type):
            bt = self.body_types.get(body_type, {})
            return bt.get("slots", [])
        
        def get_conflicting_slots(self, slot_id):
            """Get slots that would be unequipped when equipping to slot_id"""
            conflicts = set()
            slot_def = self.slots.get(slot_id, {})
            # Direct unequips from this slot
            conflicts.update(slot_def.get("unequips", []))
            # Reverse: slots that list this slot in their unequips
            for other_id, other_def in self.slots.items():
                if slot_id in other_def.get("unequips", []):
                    conflicts.add(other_id)
            return conflicts

    slot_registry = SlotRegistry()

    # --- CHARACTER ---
    class RPGCharacter(Inventory):
        def __init__(self, id, name, stats=None, location_id=None, factions=None, body_type="humanoid", base_image=None, td_sprite=None, affinity=0, schedule=None, companion_mods=None, is_companion=False, owner_id=None, gender=None, age=None, height=None, weight=None, hair_color=None, eye_color=None, hair_style=None, face_shape=None, breast_size=None, dick_size=None, foot_size=None, skin_tone=None, build=None, distinctive_feature=None, equipment=None, **kwargs):
            super(RPGCharacter, self).__init__(id, name, owner_id=(owner_id or id), **kwargs)
            self.stats = stats if isinstance(stats, StatBlock) else StatBlock(stats) if stats else StatBlock()
            if self.max_weight is None:
                base_weight = 50
                self.max_weight = base_weight + (self.stats.get("strength", 0) * 5)
            if self.max_slots is None:
                base_slots = 24
                self.max_slots = base_slots + max(0, int(self.stats.get("strength", 0) // 2))
            self._update_encumbrance()
            self.factions = set(factions or [])
            self.affinity = affinity  # -100 to 100
            self.schedule = schedule or {}  # "HH:MM": "loc_id"
            self.body_type = body_type
            self.base_image = base_image
            self.companion_mods = companion_mods or {}
            self.is_companion = is_companion
            self.following = False
            self.give_flows = {}
            
            # Determine TD Sprite
            if td_sprite:
                self.td_sprite = td_sprite
            else:
                # Default to gender-based sprite if base_image hints at it
                if base_image and "female" in base_image.lower():
                    self.td_sprite = "images/topdown/chars/female_base.png"
                else:
                    self.td_sprite = "images/topdown/chars/male_base.png"
            self.equipped_slots = {}  # slot_id -> Item
            self.location_id = location_id
            self.pchar = Character(name)
            self.gold = 100
            self.dialogue_history = set()
            # Legacy compatibility
            self.equipped_items = self.equipped_slots
            self.active_perks = []
            self.active_statuses = []
            self.fixated_to = None
            # Appearance metadata
            self.gender = gender
            self.age = age
            self.height = height
            self.weight = weight
            self.height_in = self._parse_height_to_inches(height)
            self.weight_lbs = self._parse_weight_to_lbs(weight)
            self.hair_color = hair_color
            self.hair_style = hair_style
            self.eye_color = eye_color
            self.face_shape = face_shape
            self.breast_size = breast_size
            self.dick_size = dick_size
            self.foot_size = foot_size
            self.skin_tone = skin_tone
            self.build = build
            self.distinctive_feature = distinctive_feature
            self.appearance = {
                "gender": gender,
                "age": age,
                "height": height,
                "weight": weight,
                "height_in": self.height_in,
                "weight_lbs": self.weight_lbs,
                "hair_color": hair_color,
                "hair_style": hair_style,
                "eye_color": eye_color,
                "face_shape": face_shape,
                "breast_size": breast_size,
                "dick_size": dick_size,
                "foot_size": foot_size,
                "skin_tone": skin_tone,
                "build": build,
                "distinctive_feature": distinctive_feature,
            }
            self.equipment_template = equipment or {}
            if self.equipment_template:
                self.apply_equipment(self.equipment_template)

        def _parse_height_to_inches(self, value):
            if value is None:
                return None
            if isinstance(value, (int, float)):
                return float(value)
            s = str(value).strip().lower()
            if not s:
                return None
            # 5'10" or 5 ft 10 in
            if "'" in s or "ft" in s:
                ft = 0.0
                inch = 0.0
                # normalize separators
                s = s.replace("feet", "ft").replace("foot", "ft").replace("inches", "in").replace("inch", "in").replace("\"", "in")
                parts = s.replace("ft", " ft ").replace("in", " in ").replace("'", " ft ").split()
                for i in range(len(parts)):
                    token = parts[i]
                    if token.replace(".", "", 1).isdigit():
                        num = float(token)
                        unit = parts[i + 1] if i + 1 < len(parts) else ""
                        if unit == "ft":
                            ft = num
                        elif unit == "in":
                            inch = num
                return ft * 12.0 + inch
            if "cm" in s:
                try:
                    num = float(s.replace("cm", "").strip())
                    return num / 2.54
                except Exception:
                    return None
            if "m" in s:
                try:
                    num = float(s.replace("m", "").strip())
                    return (num * 100.0) / 2.54
                except Exception:
                    return None
            if "in" in s:
                try:
                    return float(s.replace("in", "").strip())
                except Exception:
                    return None
            try:
                return float(s)
            except Exception:
                return None

        def _parse_weight_to_lbs(self, value):
            if value is None:
                return None
            if isinstance(value, (int, float)):
                return float(value)
            s = str(value).strip().lower()
            if not s:
                return None
            if "kg" in s:
                try:
                    num = float(s.replace("kg", "").strip())
                    return num * 2.20462
                except Exception:
                    return None
            if "g" in s and "kg" not in s:
                try:
                    num = float(s.replace("g", "").strip())
                    return num * 0.00220462
                except Exception:
                    return None
            if "lb" in s or "lbs" in s:
                try:
                    return float(s.replace("lbs", "").replace("lb", "").strip())
                except Exception:
                    return None
            try:
                return float(s)
            except Exception:
                return None

        def apply_equipment(self, equipment):
            """Seed and equip a character from a slot -> item_id map."""
            if not equipment:
                return
            if not isinstance(equipment, dict):
                return
            for slot_id, item_id in equipment.items():
                if not item_id:
                    continue
                target_id = str(item_id).lower()
                itm = None
                for owned in self.items:
                    if self._item_id(owned) == target_id and owned not in self.equipped_slots.values():
                        itm = owned
                        break
                if itm is None:
                    itm = item_manager.get(item_id)
                    if not itm:
                        continue
                    if getattr(itm, "owner_id", None) is None:
                        itm.owner_id = self.id
                    # Seed into inventory so equip removes it cleanly
                    self.add_item(itm, count=1, force=True, reason="equip_seed")
                    if itm not in self.items:
                        for owned in self.items:
                            if self._item_id(owned) == target_id and owned not in self.equipped_slots.values():
                                itm = owned
                                break
                ok, _msg = self.equip(itm, slot_id)
                if not ok:
                    # Fall back to inventory if equip fails (invalid slot or tag mismatch)
                    if itm not in self.items:
                        self.add_item(itm, count=1, force=True, reason="equip_seed")
        
        def change_affinity(self, amount):
            self.affinity = max(-100, min(100, self.affinity + amount))
            status = "Neutral"
            if self.affinity >= 50: status = "Friendly"
            elif self.affinity <= -50: status = "Hostile"
            renpy.notify(f"{self.name} is now {status} ({self.affinity})")

        def check_schedule(self):
            """Move character if current time matches a schedule entry"""
            tm = time_manager
            current_time_str = "{:02d}:00".format(tm.hour) # Simple hourly check for now
            
            # Find best match (exact or previous hour?)
            # For now, let's just check if we are AT or PAST a schedule point that puts us somewhere new
            # Better: iterate schedule, find latest time <= current time
            target_loc = None
            latest_time = -1
            
            current_mins = tm.hour * 60 + tm.minute
            
            for time_str, loc_id in self.schedule.items():
                try:
                    h, m = map(int, time_str.split(':'))
                    mins = h * 60 + m
                    if mins <= current_mins and mins > latest_time:
                        latest_time = mins
                        target_loc = loc_id
                except: continue
                
            if target_loc and target_loc != self.location_id:
                self.location_id = target_loc
                # If player is in same location, maybe show notification?
                # renpy.notify(f"{self.name} moved to {target_loc}")
        
        def next_schedule_entry(self):
            """Return (time_str, loc_id) for the next scheduled move after current time."""
            if not self.schedule:
                return None, None
            tm = time_manager
            now = tm.hour * 60 + tm.minute
            future = []
            for time_str, loc_id in self.schedule.items():
                try:
                    h, m = map(int, time_str.split(':'))
                    mins = h*60 + m
                    if mins >= now:
                        future.append((mins, time_str, loc_id))
                except:
                    continue
            if not future:
                return None, None
            future.sort(key=lambda x: x[0])
            return future[0][1], future[0][2]
        
        def __call__(self, what, *args, **kwargs):
            return self.pchar(what, *args, **kwargs)
        
        def interact(self):
            # Show the character hub menu via the flow queue for context safety
            renpy.store._interact_target_char = self
            import store
            store.flow_queue.queue_label("_char_interaction_wrapper")
        
        def mark_as_met(self):
            wiki_manager.unlock(self.name, self.description)
        
        def is_member_of(self, faction_id):
            return faction_id in self.factions
        
        def join_faction(self, faction_id):
            self.factions.add(faction_id)
        
        def leave_faction(self, faction_id):
            self.factions.discard(faction_id)
        
        def can_equip_to_slot(self, item, slot_id):
            """Check if item can be equipped to slot"""
            valid_slots = slot_registry.get_slots_for_body(self.body_type)
            if slot_id not in valid_slots:
                return False, "Invalid slot for this body type"
            item_slots = getattr(item, 'equip_slots', [])
            if item_slots and slot_id not in item_slots:
                return False, "Item cannot be equipped to this slot"
            return True, "OK"
        
        def equip(self, item, slot_id):
            """Equip item to slot, handling conflicts"""
            can, msg = self.can_equip_to_slot(item, slot_id)
            if not can:
                return False, msg
            
            # Unequip conflicting slots
            conflicts = slot_registry.get_conflicting_slots(slot_id)
            for conflict_slot in conflicts:
                if conflict_slot in self.equipped_slots:
                    self.unequip(conflict_slot)
            
            # Unequip current item in target slot
            if slot_id in self.equipped_slots:
                self.unequip(slot_id)
            
            # Equip
            equipped = item
            if item in self.items:
                removed = self.remove_item(item, count=1, reason="equip")
                if removed:
                    equipped = removed
            self.equipped_slots[slot_id] = equipped
            event_manager.dispatch("ITEM_EQUIPPED", actor=self.id, slot=slot_id, item_id=item_manager.get_id_of(equipped))
            return True, "Equipped"
        
        def unequip(self, slot_id):
            """Unequip item from slot back to inventory"""
            if slot_id not in self.equipped_slots:
                return False
            item = self.equipped_slots.pop(slot_id)
            self.add_item(item, count=None, force=True, reason="unequip")
            event_manager.dispatch("ITEM_UNEQUIPPED", actor=self.id, slot=slot_id, item_id=item_manager.get_id_of(item))
            return True
        
        def apply_story_origin(self, origin):
            """Deprecated: logic moved to intro flow"""
            pass
        
        def get_equipped_in_slot(self, slot_id):
            return self.equipped_slots.get(slot_id)
        
        def tick_effects(self):
            now = time_manager.total_minutes
            for arr, manager, label in [
                (self.active_perks, perk_manager, "Perk"),
                (self.active_statuses, status_manager, "Status")
            ]:
                expired = []
                for e in arr:
                    if e.get("expires_at") is not None and now >= e["expires_at"]:
                        expired.append(e["id"])
                if expired:
                    arr[:] = [e for e in arr if e["id"] not in expired]
                    for eid in expired:
                        obj = manager.get(eid)
                        if obj:
                            renpy.notify(f"{label} expired: {obj.name}")
        
        def add_perk(self, perk_id, duration_minutes=None):
            p = perk_manager.get(perk_id)
            if not p:
                return False, "Unknown perk"
            expires = None
            if duration_minutes:
                expires = time_manager.total_minutes + int(duration_minutes)
            for e in self.active_perks:
                if e["id"] == perk_id:
                    e["expires_at"] = expires
                    return True, "Perk refreshed"
            self.active_perks.append({"id": perk_id, "expires_at": expires})
            return True, "Perk added"
        
        def remove_perk(self, perk_id):
            before = len(self.active_perks)
            self.active_perks[:] = [e for e in self.active_perks if e["id"] != perk_id]
            return len(self.active_perks) != before
        
        def add_status(self, status_id, duration_minutes=None):
            s = status_manager.get(status_id)
            if not s:
                return False, "Unknown status"
            expires = None
            if duration_minutes:
                expires = time_manager.total_minutes + int(duration_minutes)
            for e in self.active_statuses:
                if e["id"] == status_id:
                    e["expires_at"] = expires
                    return True, "Status refreshed"
            self.active_statuses.append({"id": status_id, "expires_at": expires})
            return True, "Status added"
        
        def remove_status(self, status_id):
            before = len(self.active_statuses)
            self.active_statuses[:] = [e for e in self.active_statuses if e["id"] != status_id]
            return len(self.active_statuses) != before

        def is_fixated(self, fixture_id=None):
            if not self.fixated_to:
                return False
            if fixture_id is None:
                return True
            return self.fixated_to == fixture_id

        def fixate(self, fixture):
            return fixture_manager.fixate_char(self, fixture)

        def unfixate(self):
            return fixture_manager.unfixate_char(self)
        
        def get_stat_total(self, name):
            base = self.stats.get(name, 0)
            mod = 0
            for e in self.active_perks:
                p = perk_manager.get(e["id"])
                if p:
                    mod += int(p.mods.get(name, 0))
            for e in self.active_statuses:
                s = status_manager.get(e["id"])
                if s:
                    mod += int(s.mods.get(name, 0))
            try:
                mod += party_manager.get_stat_bonus(name)
            except Exception:
                pass
            return base + mod
        
        def get_stat_mod(self, name):
            return self.get_stat_total(name) - self.stats.get(name, 0)

    class Lock(object):
        def __init__(self, ltype="physical", difficulty=1, keys=None, locked=True):
            self.type = ltype
            self.difficulty = difficulty
            self.keys = set(keys or [])
            self.locked = locked
        
        def unlock(self, key_id):
            if key_id in self.keys:
                self.locked = False
                return True
            return False
            
        def pick(self, skill_level=0):
            # Simple check for now (placeholder for minigame)
            # Roll or stat check
            if skill_level + renpy.random.randint(1, 20) >= self.difficulty + 10:
                self.locked = False
                return True
            return False
            
        def lock(self):
            self.locked = True

    class Location(SpatialObject, TaggedObject):
        def __init__(self, id, name, description, map_image=None, obstacles=None, entities=None, encounters=None, scavenge=None, x=0, y=0, tags=None, factions=None,
                parent_id=None, ltype="world", map_x=0, map_y=0, zoom_range=(0.0, 99.0), floor_idx=0):
            SpatialObject.__init__(self, x, y)
            TaggedObject.__init__(self, tags)
            self.factions = set(factions or [])
            self.id, self.name, self.description = id, name, description
            self.map_image = map_image
            self.obstacles = obstacles or set()
            self.entities = entities or []
            self.encounters = encounters or []
            self.scavenge = scavenge or []
            self.visited = False
            
            # Map Hierarchy Fields
            self.parent_id = parent_id
            self.ltype = ltype # world, country, city, structure, floor
            self.map_x = map_x
            self.map_y = map_y
            self.min_zoom, self.max_zoom = zoom_range
            self.floor_idx = floor_idx
        
        @property
        def characters(self):
            return [c for c in rpg_world.characters.values() if getattr(c, 'location_id', None) == self.id and c.id != pc.id]
        
        def get_entities_with_tag(self, tag):
            return [e for e in self.entities if hasattr(e, 'tags') and tag in e.get('tags', [])]
        
        @property
        def children(self):
            # Return immediate children based on parent_id
            return [l for l in rpg_world.locations.values() if l.parent_id == self.id]

    class MapManager:
        def __init__(self):
            self.zoom = 1.0
            self.target_zoom = 1.0  # For smooth zoom animation
            self.cam_x = 0
            self.cam_y = 0
            self.search_query = ""
            self.selected_structure = None
            self.selected_location = None  # For location info popup
            self.hover_location = None
            self.hover_tooltip = None
        
        def set_zoom(self, z):
            """Set target zoom for smooth animation"""
            self.target_zoom = max(0.5, min(z, 5.0))
        
        def update_zoom(self, adj_x, adj_y, view_w, view_h):
            """Lerp zoom toward target while maintaining center point"""
            if abs(self.zoom - self.target_zoom) < 0.001:
                return None  # Already at target, no update needed
            
            # Get current center point in world coords BEFORE zoom changes
            old_zoom = self.zoom
            center_world_x = (adj_x.value + view_w / 2) / old_zoom
            center_world_y = (adj_y.value + view_h / 2) / old_zoom
            
            # Lerp zoom (fast but smooth), snap when very close
            if abs(self.zoom - self.target_zoom) < 0.01:
                self.zoom = self.target_zoom
            else:
                lerp_factor = 0.2
                self.zoom = self.zoom + (self.target_zoom - self.zoom) * lerp_factor
            
            # Calculate new scroll position to maintain center (always, including final frame)
            new_adj_x = center_world_x * self.zoom - view_w / 2
            new_adj_y = center_world_y * self.zoom - view_h / 2
            
            return (new_adj_x, new_adj_y)
            
        def get_visible_markers(self):
            # Return list of locations relevant to current zoom
            visible = []
            for loc in rpg_world.locations.values():
                # Search Filter
                if self.search_query and self.search_query.lower() not in loc.name.lower():
                    continue
                
                # Zoom Filter (if not searching)
                if not self.search_query:
                    if loc.min_zoom > self.zoom or loc.max_zoom < self.zoom:
                        continue
                    
                    # Hierarchy Filter: If structure is selected, only show its floors (if zoomed appropriately?)
                    # Simplified: Just show everything in range.
                    # Or: If zoomed in high (structure level), show floors?
                    pass

                visible.append(loc)
            return visible

        def update_hover(self, adj_x, adj_y, pad, view_w, view_h, radius=28):
            """Manual hover detection for map markers (robust across viewports)."""
            try:
                mx, my = renpy.get_mouse_pos()
            except Exception:
                mx, my = None, None
            if mx is None or my is None:
                if self.hover_tooltip:
                    self.hover_tooltip = None
                    self.hover_location = None
                    renpy.restart_interaction()
                return

            nearest = None
            nearest_dist = None
            for loc in self.get_visible_markers():
                px = (loc.map_x + pad) * self.zoom
                py = (loc.map_y + pad) * self.zoom
                sx = px - adj_x.value
                sy = py - adj_y.value
                if sx < -radius or sx > view_w + radius or sy < -radius or sy > view_h + radius:
                    continue
                dist = math.hypot(mx - sx, my - sy)
                if dist <= radius and (nearest is None or dist < nearest_dist):
                    nearest = loc
                    nearest_dist = dist

            if nearest:
                can_travel = allow_unvisited_travel or nearest.visited or (rpg_world.current_location_id == nearest.id)
                tip = nearest.name if can_travel else bracket_label("Undiscovered", "#ff3b3b")
                if tip != self.hover_tooltip:
                    self.hover_tooltip = tip
                    self.hover_location = nearest
                    set_tooltip(tip)
                    renpy.restart_interaction()
            else:
                if self.hover_tooltip:
                    self.hover_tooltip = None
                    self.hover_location = None
                    set_tooltip(None)
                    renpy.restart_interaction()
            
        def search(self, query):
            self.search_query = query.strip()

        def select_location(self, loc):
            """Select a location - opens info popup"""
            self.selected_location = loc
            if loc.ltype == 'structure':
                self.selected_structure = loc
            else:
                self.selected_structure = None
        
        def close_location_popup(self):
            """Close the location info popup"""
            self.selected_location = None
        
        def travel_to_location(self, loc):
            """Travel to the selected location"""
            if not loc:
                return False
            if not allow_unvisited_travel and not loc.visited and loc.id != rpg_world.current_location_id:
                renpy.notify("You haven't discovered this location yet.")
                return False
            # Advance time based on map distance
            curr = rpg_world.current_location
            if curr and loc.id != curr.id:
                dx = float(loc.map_x - curr.map_x)
                dy = float(loc.map_y - curr.map_y)
                dist = (dx * dx + dy * dy) ** 0.5
                travel_mins = max(5, int(dist / 100.0 * 10))
                time_manager.advance(travel_mins)
                renpy.notify(f"Traveled to {loc.name} (+{travel_mins}m)")
            if rpg_world.move_to(loc.id):
                self.selected_location = None
                # Hide map and show the new location
                renpy.hide_screen("map_browser")
                if renpy.has_label("_post_travel_setup"):
                    renpy.call("_post_travel_setup")
                return True
            return False
        
        def center_on_player(self, adj_x, adj_y, view_w, view_h, pad):
            """Center the map view on the player's current location"""
            if not rpg_world.current_location_id:
                return
                
            loc = rpg_world.locations.get(rpg_world.current_location_id)
            if not loc:
                return
                
            # Calculate center position in map coords (including padding)
            center_x = (loc.map_x + pad) * self.zoom
            center_y = (loc.map_y + pad) * self.zoom
            
            # Update adjustments to center the view
            adj_x.value = center_x - view_w / 2
            adj_y.value = center_y - view_h / 2
            
        def input_search(self):
            renpy.call_in_new_context("map_search_input_label")

    map_manager = MapManager()

    class GameWorld:
        def __init__(self): self.locations, self.characters, self.shops, self.current_location_id = {}, {}, {}, None
        @property
        def actor(self): return pc
        @property
        def current_location(self): return self.locations.get(self.current_location_id)
        
        def update_schedules(self):
            for c in self.characters.values():
                if c.id != "player":
                    if not getattr(c, "following", False):
                        c.check_schedule()
            party_manager.sync_followers()

        def add_location(self, l):
            self.locations[l.id] = l
            if not self.current_location_id: self.current_location_id = l.id
        def add_character(self, c):
            self.characters[c.id] = c
            # Inject directly into Ren'Py store to ensure accessibility across contexts
            renpy.store.__dict__[c.id] = c
        def move_to(self, lid):
            if lid in self.locations:
                self.current_location_id = lid
                was_visited = self.locations[lid].visited
                self.locations[lid].visited = True
                if not was_visited:
                    renpy.notify(f"Discovered {self.locations[lid].name}")
                    event_manager.dispatch("LOCATION_DISCOVERED", location=lid)
                    flag_set(f"discover_{lid}", True)
                event_manager.dispatch("LOCATION_VISITED", location=lid)
                self._maybe_trigger_encounter(self.locations[lid])
                party_manager.sync_followers()
                return True
            return False

        def _maybe_trigger_encounter(self, location):
            if not location or not location.encounters:
                return
            candidates = []
            for enc in location.encounters:
                if not isinstance(enc, dict):
                    continue
                label = enc.get("label")
                if not label or not renpy.has_label(label):
                    continue
                enc_id = enc.get("id", label)
                if enc.get("once") and enc_id in encounter_history:
                    continue
                cond = enc.get("cond")
                if cond and not safe_eval_bool(cond, {"pc": pc, "rpg_world": rpg_world, "flags": world_flags, "flag_get": flag_get, "bond": bond_get_stat, "bond_has_tag": bond_has_tag, "bond_level": bond_level, "faction_get": faction_manager.get_reputation}):
                    continue
                try:
                    chance = float(enc.get("chance", 1.0))
                except Exception:
                    chance = 1.0
                if chance > 1.0:
                    chance = chance / 100.0
                if renpy.random.random() <= chance:
                    candidates.append((enc_id, label, enc.get("once")))
            if not candidates:
                return
            enc_id, label, once = renpy.random.choice(candidates)
            if once:
                encounter_history.add(enc_id)
            try:
                import store
                if hasattr(store, "flow_queue"):
                    store.flow_queue.queue_label(label)
                    return
            except Exception:
                pass
            renpy.call_in_new_context(label)

    rpg_world = GameWorld()
    pc = RPGCharacter("player", "Player", base_image="chars/male_fit.png")
    rpg_world.add_character(pc)

    class PartyManager:
        def __init__(self):
            self.followers = []
            self.max_followers = 2
        
        def add_follower(self, char_id):
            c = rpg_world.characters.get(char_id)
            if not c:
                return False, "Unknown follower"
            if c.id in self.followers:
                return False, "Already following"
            if len(self.followers) >= self.max_followers:
                return False, "Party full"
            c.following = True
            c.location_id = pc.location_id
            self.followers.append(c.id)
            renpy.notify(f"{c.name} is now following you.")
            return True, "Follower added"
        
        def remove_follower(self, char_id):
            if char_id not in self.followers:
                return False, "Not following"
            c = rpg_world.characters.get(char_id)
            if c:
                c.following = False
            self.followers.remove(char_id)
            return True, "Follower removed"
        
        def get_followers(self):
            return [rpg_world.characters[cid] for cid in self.followers if cid in rpg_world.characters]
        
        def get_stat_bonus(self, stat_name):
            bonus = 0
            for c in self.get_followers():
                bonus += int(c.companion_mods.get(stat_name, 0))
            return bonus
        
        def sync_followers(self):
            for c in self.get_followers():
                c.location_id = pc.location_id

    party_manager = PartyManager()

    def companion_add(char_id):
        ok, msg = party_manager.add_follower(char_id)
        renpy.notify(msg)
        return ok

    def companion_remove(char_id):
        ok, msg = party_manager.remove_follower(char_id)
        if ok:
            renpy.notify(msg)
        return ok
    
    # --- ACHIEVEMENT SYSTEM ---
    class Achievement(object):
        """Represents an unlockable achievement with rarity tiers and event triggers."""
        RARITY_COLORS = {
            "common": "#9d9d9d",      # Gray
            "uncommon": "#1eff00",    # Green
            "rare": "#0070dd",        # Blue
            "epic": "#a335ee",        # Purple
            "legendary": "#ff8000",   # Orange
        }
        RARITY_POINTS = {
            "common": 5,
            "uncommon": 10,
            "rare": 25,
            "epic": 50,
            "legendary": 100,
        }
        
        def __init__(self, id, name, description, icon="🏆", rarity="common", tags=None, trigger=None, ticks_required=1):
            self.id = id
            self.name = name
            self.description = description
            self.icon = icon
            self.rarity = rarity.lower() if rarity else "common"
            self.tags = set(tags or [])
            self.trigger = trigger or {}  # {event: "EVENT_NAME", key: value, cond: "..."}
            self.ticks_required = max(1, int(ticks_required))
        
        @property
        def color(self):
            return self.RARITY_COLORS.get(self.rarity, "#9d9d9d")
        
        @property
        def points(self):
            return self.RARITY_POINTS.get(self.rarity, 5)
        
        def check_trigger(self, etype, **kwargs):
            """Check if an event matches this achievement's trigger."""
            if not self.trigger or self.trigger.get("event") != etype:
                return False
            # Check all key-value pairs in trigger (except reserved keys)
            for k, v in self.trigger.items():
                if k not in ["event", "cond"] and str(kwargs.get(k)) != str(v):
                    return False
            # Check condition if present
            if self.trigger.get("cond"):
                if not safe_eval_bool(self.trigger["cond"], {"player": pc, "rpg_world": rpg_world, "kwargs": kwargs, "flags": world_flags, "flag_get": flag_get, "bond": bond_get_stat, "bond_has_tag": bond_has_tag, "bond_level": bond_level, "faction_get": faction_manager.get_reputation}):
                    return False
            return True
    
    class AchievementManager:
        """Manages achievement definitions, tracking, and event-based unlocks."""
        def __init__(self):
            self.registry = {}  # id -> Achievement
        
        def register(self, achievement):
            """Register an achievement definition."""
            self.registry[achievement.id] = achievement
        
        def get(self, ach_id):
            """Get achievement by ID."""
            return self.registry.get(ach_id)
        
        def get_progress(self, ach_id):
            """Get current tick progress for an achievement."""
            if persistent.achievement_progress is None:
                persistent.achievement_progress = {}
            return persistent.achievement_progress.get(ach_id, 0)
        
        def add_tick(self, ach_id, count=1):
            """Add ticks to an achievement's progress. Auto-unlocks when complete."""
            if persistent.achievement_progress is None:
                persistent.achievement_progress = {}
            
            ach = self.registry.get(ach_id)
            if not ach or self.is_unlocked(ach_id):
                return False
            
            current = persistent.achievement_progress.get(ach_id, 0)
            new_progress = current + count
            persistent.achievement_progress[ach_id] = new_progress
            
            if new_progress >= ach.ticks_required:
                self.unlock(ach_id)
                return True
            return False
        
        def handle_event(self, etype, **kwargs):
            """Check all achievements for matching triggers."""
            for ach in self.registry.values():
                if not self.is_unlocked(ach.id) and ach.check_trigger(etype, **kwargs):
                    self.add_tick(ach.id)
        
        def unlock(self, ach_id):
            """Unlock an achievement for the player."""
            if persistent.achievements is None:
                persistent.achievements = set()
            
            if ach_id in self.registry and ach_id not in persistent.achievements:
                persistent.achievements.add(ach_id)
                ach = self.registry[ach_id]
                renpy.show_screen("achievement_toast", ach=ach)
                renpy.restart_interaction()
                return True
            return False
        
        def is_unlocked(self, ach_id):
            """Check if achievement is unlocked."""
            if persistent.achievements is None:
                return False
            return ach_id in persistent.achievements
        
        def get_all(self):
            """Get all registered achievements."""
            return sorted(self.registry.values(), key=lambda x: (x.rarity != "legendary", x.rarity != "epic", x.name))
        
        def get_unlocked(self):
            """Get all unlocked achievements."""
            if persistent.achievements is None:
                return []
            return [self.registry[aid] for aid in persistent.achievements if aid in self.registry]
        
        def get_locked(self):
            """Get all locked achievements."""
            if persistent.achievements is None:
                return list(self.registry.values())
            return [a for a in self.registry.values() if a.id not in persistent.achievements]
        
        @property
        def total_points(self):
            """Calculate total achievement points."""
            return sum(a.points for a in self.get_unlocked())
        
        @property
        def progress_text(self):
            """Get progress as text (e.g., '3/10')."""
            unlocked = len(self.get_unlocked())
            total = len(self.registry)
            return f"{unlocked}/{total}"

    ach_mgr = AchievementManager()
    achievements = ach_mgr  # Global alias

    def contested_check(stat_name, difficulty=10, target=None, success_label=None, fail_label=None):
        """
        Roll 1d20 + stat modifier against a difficulty or opposing stat (if target provided).
        If success_label/fail_label are provided and exist, jump accordingly; otherwise returns bool.
        """
        roll = renpy.random.randint(1, 20)
        actor_stat = pc.get_stat_total(stat_name)
        target_dc = difficulty
        if target and hasattr(target, "stats"):
            target_dc = target.get_stat_total(stat_name) if hasattr(target, "get_stat_total") else getattr(target.stats, stat_name, difficulty)
        total = roll + (actor_stat - 10) // 2
        passed = total >= target_dc
        renpy.notify(f"Check {stat_name}: {total} vs {target_dc} ({'pass' if passed else 'fail'})")
        if success_label and passed and renpy.has_label(success_label):
            renpy.jump(success_label)
        elif fail_label and not passed and renpy.has_label(fail_label):
            renpy.jump(fail_label)
        return passed

    def rest(hours=1, require_safe=True, allow_camp=True, camp_ambush_chance=0.2):
        loc = rpg_world.current_location
        used_camp = False
        if require_safe and loc and "safe" not in loc.tags:
            if allow_camp:
                kit = consume_item_by_tag("camp")
                if kit:
                    used_camp = True
                    renpy.notify("You set up a small camp.")
                    event_manager.dispatch("CAMP_USED", location=loc.id if loc else None)
                else:
                    renpy.notify("This doesn't feel safe enough to rest.")
                    return False
            else:
                renpy.notify("This doesn't feel safe enough to rest.")
                return False
        time_manager.advance(int(hours * 60))
        heal = int(hours * 10)
        pc.stats.hp = min(pc.stats.max_hp, pc.stats.hp + heal)
        renpy.notify(f"Rested {hours}h. HP +{heal}.")
        if loc:
            event_manager.dispatch("RESTED", hours=hours, location=loc.id, used_camp=used_camp)
        if used_camp and renpy.random.random() < camp_ambush_chance:
            label = "SCENE__camp_ambush__flow"
            try:
                import store
                if renpy.has_label(label) and hasattr(store, "flow_queue"):
                    store.flow_queue.queue_label(label)
                elif renpy.has_label(label):
                    renpy.call_in_new_context(label)
                else:
                    event_manager.dispatch("CAMP_AMBUSH", location=loc.id if loc else None)
            except Exception:
                event_manager.dispatch("CAMP_AMBUSH", location=loc.id if loc else None)
        return True

    def scavenge_location(loc=None):
        if not loc:
            loc = rpg_world.current_location
        if not loc:
            renpy.notify("There's nowhere to search.")
            return False
        if not getattr(loc, "scavenge", None):
            renpy.notify("You don't find anything useful here.")
            return False
        key = f"{loc.id}:{time_manager.day}"
        if scavenge_history.get(key):
            renpy.notify("You've already searched here today.")
            return False
        results = []
        for entry in loc.scavenge:
            if not isinstance(entry, dict):
                continue
            cond = entry.get("cond")
            if cond and not safe_eval_bool(cond, {"pc": pc, "rpg_world": rpg_world, "flags": world_flags, "flag_get": flag_get, "bond": bond_get_stat, "bond_has_tag": bond_has_tag, "bond_level": bond_level}):
                continue
            try:
                chance = float(entry.get("chance", 1.0))
            except Exception:
                chance = 1.0
            if chance > 1.0:
                chance = chance / 100.0
            if renpy.random.random() > chance:
                continue
            item_id = entry.get("item")
            if not item_id:
                continue
            if "min" in entry or "max" in entry:
                lo = int(entry.get("min", 1))
                hi = int(entry.get("max", lo))
                count = renpy.random.randint(lo, hi)
            else:
                count = int(entry.get("count", 1))
            count = max(1, count)
            it = item_manager.get(item_id)
            if it and pc.add_item(it, count=count, reason="scavenge"):
                results.append(f"{item_id} x{count}")
        scavenge_history[key] = True
        if results:
            renpy.notify("Found: " + ", ".join(results))
            event_manager.dispatch("SCAVENGED", location=loc.id, items=results)
            return True
        renpy.notify("You come up empty-handed.")
        return False

    class Note(object):
        def __init__(self, id, name, content, tags=None):
            self.id = id
            self.name = name
            self.content = content
            self.tags = set(tags or [])

    class JournalManager:
        def __init__(self):
            self.entries = {} # People: name -> description
            self.notes = {}   # Notes: id -> Note object
        
        # --- People Logic (Legacy Wiki) ---
        def register(self, n, d): 
            self.entries[n] = d
            
        def unlock(self, n, d=None):
            if n not in persistent.met_characters:
                persistent.met_characters.add(n)
                if d: self.register(n, d)
                renpy.notify(f"New Person Met: {n}")
                event_manager.dispatch("CHAR_MET", char=n)
        
        @property
        def met_list(self): 
            return [(n, self.entries.get(n, "No data.")) for n in sorted(persistent.met_characters)]

        # --- Note Logic ---
        def register_note(self, note):
            self.notes[note.id] = note
            
        def unlock_note(self, note_id):
            if note_id in self.notes:
                if persistent.unlocked_notes is None:
                    persistent.unlocked_notes = set()
                
                if note_id not in persistent.unlocked_notes:
                    persistent.unlocked_notes.add(note_id)
                    renpy.notify(f"Note Found: {self.notes[note_id].name}")
                    event_manager.dispatch("NOTE_UNLOCKED", note=note_id)
        
        def get_unlocked_notes(self):
            if persistent.unlocked_notes is None:
                return []
            return [self.notes[nid] for nid in persistent.unlocked_notes if nid in self.notes]

    wiki_manager = JournalManager()
    journal_manager = wiki_manager # Alias

    class FactionManager:
        def __init__(self):
            self.factions = {}
        def register(self, fid, data):
            self.factions[fid] = data or {}
        def get(self, fid):
            return self.factions.get(fid)
        def get_all(self):
            return list(self.factions.values())
        def ensure_reputation_store(self):
            if not hasattr(persistent, 'faction_reputation') or persistent.faction_reputation is None:
                persistent.faction_reputation = {}
        def get_reputation(self, fid):
            self.ensure_reputation_store()
            return int(persistent.faction_reputation.get(fid, 0) or 0)
        def set_reputation(self, fid, val):
            self.ensure_reputation_store()
            persistent.faction_reputation[fid] = int(val)
        def modify_reputation(self, fid, delta):
            self.ensure_reputation_store()
            cur = int(persistent.faction_reputation.get(fid, 0) or 0)
            persistent.faction_reputation[fid] = int(cur + delta)

    faction_manager = FactionManager()

    def from_dict(cls, data, id=None, **defaults):
        """
        Convert a YAML dict to class constructor kwargs.
        Merges defaults with data (data takes precedence).
        Optionally injects 'id' if provided.
        """
        params = dict(defaults)
        params.update(data)
        if id is not None:
            params['id'] = id
        return cls(**params)

    def reset_game_data():
        """Clear runtime registries before reloading generated data."""
        item_manager.registry.clear()
        slot_registry.slots.clear()
        slot_registry.body_types.clear()
        crafting_manager.recipes.clear()
        dialogue_manager.options.clear()
        story_origin_manager.origins.clear()
        quest_manager.quests.clear()
        quest_manager.start_triggers.clear()
        ach_mgr.registry.clear()
        perk_manager.registry.clear()
        status_manager.registry.clear()
        bond_manager.bonds.clear()
        wiki_manager.entries.clear()
        wiki_manager.notes.clear()
        rpg_world.locations.clear()
        rpg_world.shops.clear()
        rpg_world.characters.clear()
        rpg_world.current_location_id = None
        # Re-register the player to keep references stable across reloads
        rpg_world.add_character(pc)
    
    def instantiate_all():
        reset_game_data()
        try:
            # Use a more robust path check for renpy.file
            json_path = "generated/generated_json.json"
            if not renpy.loadable(json_path):
                # Fallback check
                json_path = game_dir + "/generated/generated_json.json"

            with renpy.file(json_path) as f:
                content = f.read().decode('utf-8')
                data = json.loads(content)
        except Exception as e:
            with open("debug_load.txt", "a") as df:
                df.write("JSON Load Error: {}\n".format(str(e)))
            return

        # Load precompiled trigger index (event -> quest ticks)
        try:
            quest_manager.load_trigger_index(data.get("quest_trigger_index", {}))
        except Exception:
            pass

        # Slots (must be loaded before body types and characters)
        for oid, p in data.get("slots", {}).items():
            slot_registry.register_slot(oid, p.get('name', oid), p.get('unequips', []))
        
        # Body Types (must be loaded before characters)
        for oid, p in data.get("body_types", {}).items():
            slot_registry.register_body_type(oid, p.get('name', oid), p.get('slots', []))

        # Items (now with tags and equip_slots)
        for oid, p in data.get("items", {}).items():
            try:
                item_manager.register(oid, from_dict(Item, p, id=oid))
            except Exception as e:
                with open("debug_load.txt", "a") as df:
                    df.write("Item Load Error ({}): {}\n".format(oid, str(e)))


        
        # Locations
        for oid, p in data.get("locations", {}).items():
            obstacles = set(tuple(obs) for obs in p.get("obstacles", [])) if isinstance(p.get("obstacles"), list) else set()
            
            # Parse zoom range
            z_raw = p.get('zoom_range', [])
            if z_raw and len(z_raw) >= 2:
                try: z_range = (float(z_raw[0]), float(z_raw[1]))
                except: z_range = (0.0, 99.0)
            else:
                z_range = (0.0, 99.0)

            try:
                loc = Location(
                    oid, p.get('name', oid), p.get('description', ''), 
                    p.get('map_image'), obstacles, p.get('entities'), p.get('encounters'), p.get('scavenge'),
                    tags=p.get('tags', []),
                    factions=p.get('factions', []),
                    parent_id=p.get('parent'),
                    ltype=p.get('map_type', 'world'),
                    map_x=int(p.get('map_x', 0) or 0),
                    map_y=int(p.get('map_y', 0) or 0),
                    zoom_range=z_range,
                    floor_idx=int(p.get('floor_idx', 0) or 0)
                )
                rpg_world.add_location(loc)
            except Exception as e:
                with open("debug_load.txt", "a") as df:
                    df.write("Location Load Error ({}): {}\n".format(oid, str(e)))
            
        # Characters (now with factions, body_type, stats, and tags)
        for oid, p in data.get("characters", {}).items():
            stats_data = p.get('stats', {})
            stats = StatBlock(stats_data) if stats_data else None
            try:
                char = RPGCharacter(
                    oid, p.get('name', oid),
                    stats=stats,
                    description=p.get('description', ''),
                    location_id=p.get('location'),
                    base_image=p.get('base_image'),
                    td_sprite=p.get('td_sprite'),
                    x=p.get('x', 0) or 0,
                    y=p.get('y', 0) or 0,
                    label=p.get('label'),
                    factions=p.get('factions', []),
                    body_type=p.get('body_type', 'humanoid'),
                    gender=p.get('gender'),
                    age=p.get('age'),
                    height=p.get('height'),
                    weight=p.get('weight'),
                    hair_color=p.get('hair_color'),
                    hair_style=p.get('hair_style'),
                    eye_color=p.get('eye_color'),
                    face_shape=p.get('face_shape'),
                    breast_size=p.get('breast_size'),
                    dick_size=p.get('dick_size'),
                    foot_size=p.get('foot_size'),
                    skin_tone=p.get('skin_tone'),
                    build=p.get('build'),
                    distinctive_feature=p.get('distinctive_feature'),
                    equipment=p.get('equipment', {}),
                    items=p.get('items', []),
                    tags=p.get('tags', []),
                    affinity=int(p.get('affinity', 0) or 0),
                    max_weight=p.get('max_weight'),
                    max_slots=p.get('max_slots'),
                    schedule=p.get('schedule', {}),
                    companion_mods=p.get('companion_mods', {}),
                    is_companion=bool(p.get('companion_mods'))
                )
                char.give_flows = p.get('give', {}) or {}
                rpg_world.add_character(char)
            except Exception as e:
                with open("debug_load.txt", "a") as df:
                    df.write("Character Load Error ({}): {}\n".format(oid, str(e)))
                
        # Dialogue Options
        for oid, p in data.get("dialogue", {}).items():
            dialogue_manager.register(DialogueOption(
                oid,
                chars=p.get('chars', []),
                short_text=p.get('short', '...'),
                long_text=p.get('long', '...'),
                emoji=p.get('emoji', '💬'),
                label=p.get('label'),
                cond=p.get('cond'),
                tags=p.get('tags', []),
                memory=(str(p.get('memory', 'False')).lower() == 'true'),
                reason=p.get('reason')
            ))

        # Story Origins
        for oid, p in data.get("story_origins", {}).items():
            story_origin_manager.register(StoryOrigin(
                oid,
                name=p.get('name', oid),
                description=p.get('description', ''),
                character=(p.get('character') or p.get('pc_id')),
                intro_label=p.get('intro_label'),
                image=p.get('image')
            ))

        # Shops
        for oid, p in data.get("shops", {}).items():
            # Shops are inventories with multipliers
            shop = Shop(
                oid,
                p.get('name', oid),
                buy_mult=p.get('buy_mult', 1.2),
                sell_mult=p.get('sell_mult', 0.6),
                items=p.get('items', [])
            )
            # Register in world shops
            # They are globals, but separated from characters to avoid map-spawn issues
            rpg_world.shops[oid] = shop
            renpy.store.__dict__[oid] = shop

        # Recipes
        for oid, p in data.get("recipes", {}).items():
            crafting_manager.register(Recipe(
                oid,
                p.get('name', oid),
                p.get('inputs', {}),
                p.get('output', {}),
                req_skill=p.get('req_skill'),
                tags=p.get('tags', [])
            ))

        # Notes
        for oid, p in data.get("notes", {}).items():
            wiki_manager.register_note(Note(
                oid,
                p.get('name', oid),
                p.get('body', ''),
                tags=p.get('tags', [])
            ))

        # Quests
        for oid, p in data.get("quests", {}).items():
            try:
                q = Quest(
                    oid,
                    p.get('name', oid),
                    p.get('description', ''),
                    category=p.get('category', 'side'),
                    giver=p.get('giver'),
                    location=p.get('location'),
                    tags=p.get('tags', []),
                    prereqs=p.get('prereqs', {}),
                    rewards=p.get('rewards', {}),
                    start_trigger=p.get('start_trigger', {}),
                    outcomes=p.get('outcomes', []),
                    origin=p.get('origin', False),
                    character=(p.get('character') or p.get('pc_id')),
                    image=p.get('image')
                )
                for t_idx, tp in enumerate(p.get('ticks', [])):
                    tick = QuestTick(tp['id'], tp['name'])
                    tick.trigger_data = tp.get('trigger', {})
                    tick.guidance = tp.get('guidance', {})
                    try:
                        tick.required_value = int(tick.trigger_data.get("total", 1) or 1)
                    except Exception:
                        tick.required_value = 1
                    tick.flow_label = tp.get('label')
                    q.add_tick(tick)
                # Attach compiled choices (if any)
                try:
                    q.choices = p.get('choices', []) or []
                except Exception:
                    q.choices = []
                quest_manager.add_quest(q)
                if q.start_trigger:
                    quest_manager.register_start_trigger(oid, q.start_trigger)
                # (no-op)
            except Exception as e:
                with open("debug_load.txt", "a") as df:
                    df.write("Quest Load Error ({}): {}\n".format(oid, str(e)))

        # Achievements
        for oid, p in data.get("achievements", {}).items():
            ach_mgr.register(Achievement(
                oid,
                p.get('name', oid),
                p.get('description', ''),
                icon=p.get('icon', '🏆'),
                rarity=p.get('rarity', 'common'),
                tags=p.get('tags', []),
                trigger=p.get('trigger', {}),
                ticks_required=p.get('ticks', 1)
            ))
        # Factions
        for fid, fdata in data.get('factions', {}).items():
            try:
                faction_manager.register(fid, fdata)
            except Exception as e:
                with open("debug_load.txt", "a") as df:
                    df.write("Faction Load Error ({}): {}\n".format(fid, str(e)))
        
        # Perks
        for oid, p in data.get("perks", {}).items():
            duration = p.get("duration")
            try:
                duration = int(duration) if duration is not None else None
            except Exception:
                duration = None
            perk_manager.register(Perk(
                oid,
                p.get('name', oid),
                p.get('description', ''),
                mods=p.get('mods', {}),
                tags=p.get('tags', []),
                duration_minutes=duration
            ))
        
        # Status Effects
        for oid, p in data.get("status_effects", {}).items():
            duration = p.get("duration")
            try:
                duration = int(duration) if duration is not None else None
            except Exception:
                duration = None
            status_manager.register(StatusEffect(
                oid,
                p.get('name', oid),
                p.get('description', ''),
                mods=p.get('mods', {}),
                tags=p.get('tags', []),
                duration_minutes=duration
            ))
        
        # Bonds
        for oid, p in data.get("bonds", {}).items():
            a = p.get("a")
            b = p.get("b")
            if a and b:
                bond = Bond(
                    oid,
                    a,
                    b,
                    tags=p.get("tags", []),
                    stats=p.get("stats", {}),
                    relations=p.get("relations", [])
                )
                bond_manager.register(bond)

    instantiate_all()

default persistent.achievements = set()
default persistent.met_characters = set()

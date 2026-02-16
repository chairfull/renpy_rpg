default item_manager = ItemManager()

init -10 python:
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

    class ItemManager:
        def __init__(self): 
            self.items = {}
    
    
    def reload_item_manager(data):
        item_manager.items = {}
        for item_id, p in data.get("items", {}).items():
            try:
                item_manager.items[item_id] = from_dict(Item, p, id=item_id)
            except Exception as e:
                with open("debug_load.txt", "a") as df:
                    df.write("Item Load Error ({}): {}\n".format(item_id, str(e)))
    

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

transform item_popup_bounce:
    on show:
        yalign 1.5
        pause 0.1
        easein_back 0.6 yalign 0.25
    on hide:
        easeout_back 0.6 yalign 1.5

label show_item(item_id):
    show screen item_inspect_screen(item_id)
    return

label hide_item:
    hide screen item_inspect_screen
    return

screen item_inspect_screen(item_id):
    $ item = item_manager.get(item_id)
    $ icon = get_item_icon(item)
    zorder 200
    frame at item_popup_bounce:
        xalign 0.5
        padding (20, 20)
        vbox:
            spacing 10
            if item.name:
                text "[item.name]" size 22 color "#ffd700" xalign 0.5
            if icon:
                add icon xalign 0.5 yalign 0.5
            else:
                text "No icon available." size 16 color "#999" xalign 0.5
default loop_queue = [] # Labels and screens queued.
default td_screen = TopDownScreen()

init -2000 python:
    import math

    _early = []
    _initialised = False

    def onstart(*args, **kwargs):
        _early.append((args, kwargs))
    
    def initialise():
        global _initialised
        if _initialised:
            return
        # Call early functions.
        for args, kwargs in _early:
            fn = args[0]
            if callable(fn):
                try:
                    fn(*args[1:], **kwargs)
                except Exception:
                    pass
        _initialised = True

    # TODO: Replace
    def safe_eval_bool(expr, context):
        return True if True else False

    def cond_jump(expr, label_true, label_false=None):
        if callable(expr):
            try:
                ok = bool(expr())
            except Exception:
                ok = False
        else:
            ok = safe_eval_bool(expr, {"character": character, "world": world, "flags": world_flags, "flag_get": flag_get, "bond": bond_get_stat, "bond_has_tag": bond_has_tag, "bond_level": bond_level, "faction_get": faction_manager.get_reputation})
        if ok and label_true and renpy.has_label(label_true):
            renpy.jump(label_true)
        elif (not ok) and label_false and renpy.has_label(label_false):
            renpy.jump(label_false)
        return ok

    # Mixin for objects with tags for filtering.
    class TaggedObject:
        def __init__(self, tags=None, **kwargs):
            self.tags = _normalize_tags(tags)
        
        def has_tag(self, tag):
            return tag in self.tags
        
        def has_any_tag(self, tags):
            return bool(self.tags & tags)
        
        def has_all_tags(self, tags):
            return tags <= self.tags
        
        def add_tag(self, tag):
            self.tags.add(tag)
        
        def remove_tag(self, tag):
            self.tags.discard(tag)
    
    # Mixin for objects with flags for filtering
    class FlaggedObject:
        def __init__(self, flags=None, **kwargs):
            self.flags = flags or {}
        
        def has_flag(self, flag):
            return self.flags.get(flag, False)
        
        def set_flag(self, flag, value=True):
            self.flags[flag] = value
        
        def clear_flag(self, flag):
            if flag in self.flags:
                del self.flags[flag]
        
        def toggle_flag(self, flag):
            self.flags[flag] = not self.flags.get(flag, False)

    def queue(qtype, *args, **kwargs):
        loop_queue.append((qtype, args, kwargs))
    
    def queue_label(label, *args, **kwargs):
        if renpy.has_label(label):
            queue("label", label, *args, **kwargs)
        else:
            raise ValueError(f"Label '{label}' does not exist.")

    def queue_screen(screen, *args, **kwargs):
        if renpy.has_screen(screen):
            queue("screen", screen, *args, **kwargs)
        else:
            raise ValueError(f"Screen '{screen}' does not exist.")

    def test_function(f_id):
        return True if getattr(globals(), f_id) else False

    # Objects drawn to the screen.
    class ScreenElement(Vector3):
        def __init__(self, position=Vector3(), tooltip=None, action=None, transform=None, sprite=None):
            Vector3.__init__(self, position)
            self.tooltip = tooltip
            self.sprite = sprite
            self.transform = transform
            self.action = action if action is not None else []
            self.rotation = rotation
            self.anchor = (0.5, 0.5)
            self.size = (120, 120)
            
        def transform(self):
            return self.transform
        
        def action(self):
            return self.action
    
    # Objects in the world, often drawn to screen.
    class Entity(TaggedObject, ScreenElement):
        def __init__(self, position, sprite, action=None, tooltip=None, idle_anim=False, sprite_tint=None, label=None, depth=None, is_player=False, rotation=0, requires_approach=False, hit_anchor=(0.5, 0.5), hit_size=(120, 120), id=None, **kwargs):
            TaggedObject.__init__(self, kwargs.get("tags", None))
            ScreenElement.__init__(self, position=position, tooltip=tooltip, action=action, transform=kwargs.get("transform", None), sprite=sprite)
            self.id = id
            self.idle_anim = idle_anim
            self.sprite_tint = sprite_tint
            self.label = label
            self.requires_approach = requires_approach
            self.hit_anchor = hit_anchor
            self.hit_size = hit_size
        
        def interact(self):
            if self.label: renpy.jump(self.label)
            else: renpy.say(None, f"You see {self.name}. {self.desc}")

    class Camera(Vector3):
        def __init__(self, position=Vector3(), zoom=1.0):
            Vector3.__init__(self, position)
            self.screen_size = Vector2(1920, 1080)
            self.screen_center = self.screen_size / 2.0
            self.zoom = zoom
            self.target_zoom = zoom
            self._snapped = False # Camera snap flag - skip lerp on first frame after setup
        
        def update(self, dt):
            target_cam = character.xz - self.screen_center
            
            # Skip lerp if camera was just snapped (first frame after setup)
            if self._snapped:
                self.xz = target_cam
                self._snapped = False
            else:
                lerp_speed = dt * 5.0
                self.xz = Vector2(
                    lerp(self.x, target_cam.x, lerp_speed),
                    lerp(self.z, target_cam.y, lerp_speed)
                )
        
            if abs(self.zoom - self.target_zoom) < 0.001:
                return None # Already at target, no update needed
            else:
                # Get current center point in world coords BEFORE zoom changes
                old_zoom = self.zoom
                center_world = (self.xz + self.screen_center) / old_zoom
                
                # Lerp zoom (fast but smooth), snap when very close
                if abs(self.zoom - self.target_zoom) < 0.01:
                    self.zoom = self.target_zoom
                else:
                    self.zoom = lerp(self.zoom, self.target_zoom, 0.2)
                
                # Calculate new scroll position to maintain center (always, including final frame)
                self.xz = center_world * self.zoom - self.screen_center

        def set_zoom(self, z):
            self.target_zoom = clamp(z, 0.5, 5.0)

        def snap_to(self, target):
            self.xz = target.xz - self.screen_center
        
        def world_to_screen(self, wx, wy):
            return (wx - self.x, wy - self.z)
        
        def screen_to_world(self, sx, sy):
            rel = (Vector2(sx, sy) - self.screen_center) / self.zoom
            return rel + self.screen_center + self.xz

    class TopDownScreen:
        def __init__(self):
            self.update_dt =  1.0 / 60.0
            self.show_reachability = False
            self.last_update = 0
            self.cell_size = 40 # Grid size for pathfinding
            self.current_location = None
            self.screen_center = Vector2(1920, 1080) // 2
            self.camera = Camera()
            self.interaction_callback = None

        def get_sorted_entities(self):
            return sorted(location.entities, key=lambda e: e.y)

        # def setup(self, location):
        #     self.entities = {}
        #     if location is None: return

        #     self.center_player()
        #     self.snap_camera()
        #     self._camera_snapped = True  # Mark camera as snapped to skip lerp on first frame

        #     for item in location.entities:
        #         itype = item.get('type', 'object')
        #         ix, iy = item.get('x', 0), item.get('y', 0)
        #         iid = item.get('id', 'unknown')
                
        #         if itype == 'link':
        #             dest_id = iid
        #             dest_loc = world.locations.get(dest_id)
        #             dest_name = dest_loc.name if dest_loc else dest_id.capitalize()
        #             tooltip_text = f"Go to {dest_name}"
                    
        #             ent = TopDownEntity(ix, iy,
        #                                 sprite="images/topdown/chars/male_base.png",
        #                                 action=Function(self.walk_to_exit, dest_id),
        #                                 tooltip=tooltip_text,
        #                                 sprite_tint=TintMatrix("#00ff00"),
        #                                 requires_approach=False,
        #                                 id=dest_id)
        #             self.entities.append(ent)
                
        #         else:
        #             lock_data = item.get('lock')
        #             if lock_data:
        #                 keys_list = lock_data.get('keys', [])
        #                 if isinstance(keys_list, str): keys_list = [k.strip() for k in keys_list.split(',')]
        #                 item['lock_obj'] = Lock(
        #                     ltype=lock_data.get('type', 'physical'),
        #                     difficulty=int(lock_data.get('difficulty', 1)),
        #                     keys=keys_list,
        #                     locked=True
        #                 )

        #             ent = TopDownEntity(ix, iy,
        #                                 sprite=item.get('sprite', "images/topdown/chars/male_base.png"),
        #                                 action=Function(td_engine.interact, item),
        #                                 tooltip=item.get('name', "Entity"),
        #                                 idle_anim=item.get('idle_anim', True),
        #                                 label=item.get('label'),
        #                                 requires_approach=True,
        #                                 id=iid)
        #             self.entities.append(ent)

        #     for char in location.characters:
        #         ent = TopDownEntity(char.x, char.y,
        #                             sprite=char.td_sprite,
        #                             action=Function(td_engine.interact, char),
        #                             tooltip=char.name,
        #                             idle_anim=True,
        #                             label=f"char_{char.id}_interact",
        #                             requires_approach=True,
        #                             hit_anchor=(0.5, 1.0),
        #                             hit_size=(120, 160),
        #                             id=char.id)
        #         self.entities.append(ent)
            
        #     # Create player entity and add to entities list
        #     self.player_entity = TopDownEntity(
        #         world.actor.x, world.actor.y,
        #         sprite=character.td_sprite,
        #         action=NullAction(),
        #         tooltip=character.name,
        #         idle_anim=False,
        #         is_player=True,
        #         requires_approach=False,
        #         hit_anchor=(0.5, 1.0),
        #         hit_size=(120, 160),
        #         id=getattr(character, 'id', 'player')
        #     )
        #     self.entities.append(self.player_entity)

        #     self.current_location = location
        #     self.obstacles = location.obstacles
        #     self.moving = False
        #     self.path = []

        

        def update(self, dt):
            # target_rot = self.target_rotation
            # diff = (target_rot - self.player_rotation + 180) % 360 - 180
            # if abs(diff) > 0.1:
            #     self.player_rotation = (self.player_rotation + diff * dt * self.rotation_lerp_speed) % 360

            camera.update(dt)

            for ent in self.entities:
                ent.update(dt)
        
        def click_to_move(self):
            mx, my = renpy.get_mouse_pos()
            wx, wy = self.screen_to_world(mx, my, self.zoom)
            # If click is near an interactable, auto-approach and interact.
            nearest = None
            nearest_dist = 1e9
            for ent in td_manager.entities:
                if ent.is_player:
                    continue
                dx = ent.x - wx
                dy = ent.y - wy
                dist = math.hypot(dx, dy)
                if dist < nearest_dist:
                    nearest_dist = dist
                    nearest = ent
            if nearest and nearest_dist <= 120:
                self.clicked_entity(nearest)
            else:
                self.set_target(wx, wy)
        
        def clicked_ground(self):
            mx, my = renpy.get_mouse_pos()
            wx, wy = self.screen_to_world(mx, my)
            # self.set_target(wx, wy)

        def clicked_entity(self, entity):
            entity.interact()
            # if not entity:
            #     return
            # if entity.is_player:
            #     _open_inventory_screen()
            #     renpy.restart_interaction()
            #     return
            # if getattr(entity, "requires_approach", False):
            #     self.walk_to_entity(entity.x, entity.y, lambda: renpy.run(entity.action))
            # else:
            #     renpy.run(entity.action)
            
        # def interact(self, obj):
        #     # Determine if it's an NPC or a raw dict object
        #     is_npc = hasattr(obj, 'id') and not isinstance(obj, dict)
            
        #     # Lock Check for Dict Objects (Entities)
        #     if not is_npc and isinstance(obj, dict):
        #         lock = obj.get('lock_obj')
        #         if lock and lock.locked:
        #             renpy.call_screen("lock_interaction_screen", lock, obj.get('name', 'Object'))
        #             return

        #     if is_npc:
        #         obj.interact()
        #     elif obj.get('type') == 'fixture':
        #         fixture = fixture_manager.get_by_entity(world.current_location_id, obj)
        #         if not fixture:
        #             renpy.notify("Nothing to use here.")
        #             return
        #         if fixture.occupied_by == character.id:
        #             fixture.unfixate(character)
        #             renpy.notify(f"You leave {fixture.name}.")
        #             return
        #         if fixture.occupied_by and fixture.occupied_by != character.id:
        #             renpy.notify(f"{fixture.name} is occupied.")
        #             return
        #         ok, _msg = fixture.fixate(character)
        #         if ok:
        #             renpy.notify(f"You settle at {fixture.name}.")
        #         return
        #     elif obj.get('type') == 'container':
        #         # Initialize Inventory object for the container if it doesn't exist
        #         if not isinstance(obj.get('inventory'), Inventory):
        #             inv_id = f"inv_{obj.get('id', 'anon')}"
        #             items = obj.get('items', [])
        #             # Create the inventory and store it back in the object
        #             owner_id = obj.get('owner_id') or obj.get('owner')
        #             obj['inventory'] = Inventory(inv_id, obj.get('name', 'Container'), items=items, owner_id=owner_id)
                
        #         # Check for Lock
        #         lock = obj.get('lock_obj')
        #         if lock and lock.locked:
        #             renpy.show_screen("lock_interaction_screen", lock, obj.get('name', 'Container'))
        #         else:
        #             # Show side-by-side transfer screen
        #             renpy.show_screen("container_transfer_screen", obj['inventory'])
        #     elif 'label' in obj:
        #         queue('label', obj['label'])
        #     else:
        #         renpy.notify(f"Interacted with {obj.get('name')}")
        
        # def travel_to_location(self, loc):
        #     """Travel to the selected location"""
        #     if not loc:
        #         return False
        #     if not allow_unvisited_travel and not loc.visited and loc.id != world.current_location_id:
        #         renpy.notify("You haven't discovered this location yet.")
        #         return False
        #     # Advance time based on map distance
        #     curr = world.current_location
        #     if curr and loc.id != curr.id:
        #         dx = float(loc.map_x - curr.map_x)
        #         dy = float(loc.map_y - curr.map_y)
        #         dist = (dx * dx + dy * dy) ** 0.5
        #         travel_mins = max(5, int(dist / 100.0 * 10))
        #         time_manager.advance(travel_mins)
        #         renpy.notify(f"Traveled to {loc.name} (+{travel_mins}m)")
        #     if world.move_to(loc.id):
        #         self.selected_location = None
        #         # Hide map and show the new location
        #         renpy.hide_screen("map_browser")
        #         if renpy.has_label("_post_travel_setup"):
        #             renpy.call("_post_travel_setup")
        #         return True
        #     return False

transform td_cinematic_enter:
    subpixel True
    zoom 2.0 alpha 0.0
    align (0.5, 0.5)
    anchor (0.5, 0.5)
    parallel:
        easein 0.5 alpha 1.0
    parallel:
        easein 2.0 zoom 1.0

transform td_interactive_zoom(z):
    subpixel True
    zoom z
    align (0.5, 0.5)
    anchor (0.5, 0.5)

screen top_down_screen():
    if location is None:
        text "Loading..." align (0.5, 0.5)
    zorder 10
    on "show" action [Function(td_screen.setup, location)]
    
    # Zoom Controls
    key "K_PLUS" action If(meta_menu.minimised, SetVariable("td_zoom", min(2.5, td_zoom + 0.1)), NullAction())
    key "K_EQUALS" action If(meta_menu.minimised, SetVariable("td_zoom", min(2.5, td_zoom + 0.1)), NullAction())
    key "K_MINUS" action If(meta_menu.minimised, SetVariable("td_zoom", max(0.5, td_zoom - 0.1)), NullAction())
    key "mousedown_4" action If(meta_menu.minimised, SetVariable("td_zoom", min(2.5, td_zoom + 0.1)), NullAction())
    key "mousedown_5" action If(meta_menu.minimised, SetVariable("td_zoom", max(0.5, td_zoom - 0.1)), NullAction())
    key "c" action Function(td_manager.snap_camera)
    key "h" action ToggleVariable("show_reachability")
    
    # Update Loop - Paused when phone is open
    # timer td_update_dt repeat True action [
    #     If(map_ui_active or phone_state != "mini",
    #         Function(_td_noop),
    #         [Function(td_manager.update, td_update_dt), Function(_td_update_hover_tooltip)]
    #     )
    # ]
    
    # Main Map Container with Zoom/Cinematic
    frame:
        background None
        padding (0, 0)
        xfill True
        yfill True
        
        # Apply transforms based on state
        if not intro_cinematic_done:
            at td_cinematic_enter
            timer 2.0 action SetVariable("intro_cinematic_done", True)
        else:
            at td_interactive_zoom(td_zoom)
        
        fixed:
            xfill True
            yfill True
            
            $ cam_x = int(td_screen.camera.x)
            $ cam_z = int(td_screen.camera.z)
            
            # 1. Background Map
            if location.map_image:
                add location.map_image pos (-cam_x, -cam_z)
            else:
                add Solid("#222") pos (-cam_x, -cam_z)
            
            # 2. Click-to-Move Ground Layer
            button:
                area (0, 0, 1920, 1080)
                action Function(td_screen.clicked_ground)
                background None

            # 3. Interactive Entities (NPCs, Exits, Objects, Player) - Depth Sorted
            for entity in td_screen.get_sorted_entities():
                $ ent_x = int(entity.x - td_screen.camera.x)
                $ ent_z = int(entity.y - td_screen.camera.z)
                $ reach_color = None
                # if show_reachability and not entity.is_player:
                #     $ path_ok = bool(td_engine.find_path((int(td_engine.player_pos[0]), int(td_engine.player_pos[1])), (int(entity.x), int(entity.y))))
                #     $ reach_color = TintMatrix("#44ff44") if path_ok else TintMatrix("#ff4444")
                
                imagebutton:
                    anchor entity.anchor
                    pos (ent_x, ent_z)
                    action entity.action
                    tooltip entity.tooltip
                    focus_mask None
                    background None
                    
                    # Visuals - Different rendering for player vs other entities
                    # if entity.is_player:
                    #     add Transform(
                    #         entity.sprite,
                    #         zoom=0.35,
                    #         rotate=entity.rotation,
                    #         anchor=(0.5, 1.0),
                    #         align=(0.5, 1.0),
                    #         transform_anchor=True,
                    #         subpixel=True
                    #     )
                    # else:
                    #     fixed at button_hover_effect:
                    #         if entity.sprite_tint:
                    #             # For colored markers (like exits)
                    #             add Transform(entity.sprite, zoom=0.3, matrixcolor=entity.sprite_tint) align (0.5, 0.5)
                    #         else:
                    #             # For characters/objects
                    #                 if entity.idle_anim:
                    #                     add At(Transform(entity.sprite, zoom=0.35, matrixcolor=reach_color), char_idle_anim) align (0.5, 0.5)
                    #                 else:
                    #                     add Transform(entity.sprite, zoom=0.35, matrixcolor=reach_color) align (0.5, 0.5)
                                    
                    #                 # Quest Highlight
                    #                 $ guidance = quest_manager.get_current_guidance()
                    #                 if guidance and entity.id in guidance.get('objects', []):
                    #                     add "images/ui/quest_marker.png" at quest_pulse yoffset -100 align (0.5, 0.5)

    frame:
        align (0.5, 0.02)
        background "#00000088"
        padding (20, 8)
        textbutton "[location.name]":
            action [Function(meta_menu.open, "locations")]
            text_size 28
            text_color "#ffffff"
            text_hover_color "#ffd700"
            background None
            hover_background None
    
    frame:
        align (0.18, 0.02)
        background "#00000088"
        padding (12, 10)
        vbox:
            spacing 6
            text "Time: [time_manager.time_string]" size 18 color "#ffd700"
            hbox:
                spacing 6
                textbutton "+15m" action Function(time_manager.advance, 15) text_size 14
                textbutton "+1h" action Function(time_manager.advance, 60) text_size 14
                text "[time_manager.time_of_day]" size 14 color "#ccc"
            text "Here now:" size 14 color "#aaa"
            vbox:
                spacing 2
                for c in location.characters:
                    $ nxt_time, nxt_loc = c.next_schedule_entry()
                    hbox:
                        spacing 6
                        text c.name size 14 color "#fff"
                        if nxt_time and nxt_loc:
                            text f"→ {nxt_loc} @ {nxt_time}" size 12 color "#777"
    
    frame:
        align (0.02, 0.98)
        background "#000a"
        padding (10, 10)
        hbox:
            spacing 10
            textbutton "DEV" action Show("dev_mode_screen") text_size 14 text_color "#ff3333"
    
    use meta_menu_screen

# Idle breathing animation (Removed zoom pulse as per user request)
# transform char_idle_anim:
#     subpixel True
#     anchor (0.5, 0.5)
#     parallel:
#         ease 1.5 rotate -1.5
#         ease 1.5 rotate 1.5
#         repeat

# label _char_interaction_wrapper:
#     $ char = getattr(store, '_interact_target_char', None)
#     if not char:
#         return
#     jump char_interaction_show

# label char_interaction_show:
#     $ char = getattr(store, '_interact_target_char', None)
#     if not char:
#         return
#     $ char_interaction_state = "menu"
#     $ char_interaction_pending_label = None
#     $ renpy.show_screen("char_interaction_menu", char, show_preview=False, show_backdrop=False)

#     # show character on right
#     if char.base_image:
#         show expression Transform(char.base_image, xzoom=-1) as char_right at right
#         with dissolve

#     # move player in from left
#     if character.base_image:
#         show expression character.base_image as char_left at left
#         with moveinleft

#     jump char_interaction_loop

# label char_interaction_loop:
#     $ char = getattr(store, '_interact_target_char', None)
#     if not char:
#         jump char_interaction_end
#     $ char_interaction_state = "menu"
#     $ char_interaction_pending_label = None
#     $ renpy.show_screen("char_interaction_menu", char, show_preview=False, show_backdrop=False)
#     while True:
#         $ renpy.pause(0.05)
#         if not getattr(store, '_interact_target_char', None):
#             $ char_interaction_state = "exit"
#         if char_interaction_state == "exit":
#             jump char_interaction_end
#         if char_interaction_pending_label:
#             $ _lbl = char_interaction_pending_label
#             $ char_interaction_pending_label = None
#             $ renpy.hide_screen("char_interaction_menu")
#             $ renpy.with_statement(Dissolve(0.2))
#             if renpy.has_label(_lbl):
#                 call expression _lbl from _call_npc_label_wrapper
#             $ renpy.show_screen("char_interaction_menu", char, show_preview=False, show_backdrop=False)
#             $ renpy.with_statement(Dissolve(0.2))
#             $ char_interaction_state = "menu"

# label _char_interaction_run_pending:
#     $ _lbl = char_interaction_pending_label
#     $ char_interaction_pending_label = None
#     if not _lbl:
#         return
#     $ _char = getattr(store, '_interact_target_char', None)
#     if not _char:
#         return
#     $ renpy.hide_screen("char_interaction_menu")
#     $ renpy.with_statement(Dissolve(0.2))
#     if renpy.has_label(_lbl):
#         call expression _lbl
#     $ renpy.show_screen("char_interaction_menu", _char, show_preview=False, show_backdrop=False)
#     $ renpy.with_statement(Dissolve(0.2))
#     return

# label char_interaction_end:
#     hide screen char_interaction_menu
#     if character.base_image:
#         show expression Transform(character.base_image, xzoom=-1) as char_left at offscreenleft with moveoutleft
#     hide char_right with dissolve
#     hide char_left
#     $ _interact_target_char = None
#     return

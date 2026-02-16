default td_zoom = 1.0
default show_reachability = False
default td_update_dt = 1.0 / 60.0

init -10 python:
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
            for loc in world.locations.values():
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
            if not allow_unvisited_travel and not loc.visited and loc.id != world.current_location_id:
                renpy.notify("You haven't discovered this location yet.")
                return False
            # Advance time based on map distance
            curr = world.current_location
            if curr and loc.id != curr.id:
                dx = float(loc.map_x - curr.map_x)
                dy = float(loc.map_y - curr.map_y)
                dist = (dx * dx + dy * dy) ** 0.5
                travel_mins = max(5, int(dist / 100.0 * 10))
                time_manager.advance(travel_mins)
                renpy.notify(f"Traveled to {loc.name} (+{travel_mins}m)")
            if world.move_to(loc.id):
                self.selected_location = None
                # Hide map and show the new location
                renpy.hide_screen("map_browser")
                if renpy.has_label("_post_travel_setup"):
                    renpy.call("_post_travel_setup")
                return True
            return False
        
        def center_on_player(self, adj_x, adj_y, view_w, view_h, pad):
            """Center the map view on the player's current location"""
            if not world.current_location_id:
                return
                
            loc = world.locations.get(world.current_location_id)
            if not loc:
                return
                
            # Calculate center position in map coords (including padding)
            center_x = (loc.map_x + pad) * self.zoom
            center_y = (loc.map_y + pad) * self.zoom
            
            # Update adjustments to center the view
            adj_x.value = center_x - view_w / 2
            adj_y.value = center_y - view_h / 2

    map_manager = MapManager()

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

screen top_down_map(location):
    if location is None:
        text "Loading..." align (0.5, 0.5)
    zorder 10
    on "show" action [Function(td_manager.setup, location)]
    
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
            xsize 1920
            ysize 1080
            
            $ cam_x = int(td_manager.camera_offset[0])
            $ cam_y = int(td_manager.camera_offset[1])
            
            # 1. Background Map
            if location.map_image:
                add location.map_image pos (-cam_x, -cam_y)
            else:
                add Solid("#222") pos (-cam_x, -cam_y)
            
            # 2. Click-to-Move Ground Layer
            button:
                area (0, 0, 1920, 1080)
                action Function(_td_click_to_move)
                background None

            # 3. Interactive Entities (NPCs, Exits, Objects, Player) - Depth Sorted
            for entity in td_manager.get_sorted_entities():
                $ sx = int(entity.x - cam_x)
                $ sy = int(entity.y - cam_y)
                $ reach_color = None
                if show_reachability and not entity.is_player:
                    $ path_ok = bool(td_manager.find_path((int(td_manager.player_pos[0]), int(td_manager.player_pos[1])), (int(entity.x), int(entity.y))))
                    $ reach_color = TintMatrix("#44ff44") if path_ok else TintMatrix("#ff4444")
                
                $ h_anchor = getattr(entity, "hit_anchor", (0.5, 0.5))
                $ h_size = getattr(entity, "hit_size", (120, 120))
                button:
                    anchor h_anchor
                    pos (sx, sy)
                    xsize h_size[0]
                    ysize h_size[1]
                    action Function(_td_click_entity, entity)
                    tooltip entity.tooltip
                    focus_mask None
                    
                    background None
                    
                    # Visuals - Different rendering for player vs other entities
                    if entity.is_player:
                        add Transform(
                            entity.sprite,
                            zoom=0.35,
                            rotate=entity.rotation,
                            anchor=(0.5, 1.0),
                            align=(0.5, 1.0),
                            transform_anchor=True,
                            subpixel=True
                        )
                    else:
                        fixed at button_hover_effect:
                            if entity.sprite_tint:
                                # For colored markers (like exits)
                                add Transform(entity.sprite, zoom=0.3, matrixcolor=entity.sprite_tint) align (0.5, 0.5)
                            else:
                                # For characters/objects
                                    if entity.idle_anim:
                                        add At(Transform(entity.sprite, zoom=0.35, matrixcolor=reach_color), char_idle_anim) align (0.5, 0.5)
                                    else:
                                        add Transform(entity.sprite, zoom=0.35, matrixcolor=reach_color) align (0.5, 0.5)
                                    
                                    # Quest Highlight
                                    $ guidance = quest_manager.get_current_guidance()
                                    if guidance and entity.id in guidance.get('objects', []):
                                        add "images/ui/quest_marker.png" at quest_pulse yoffset -100 align (0.5, 0.5)

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
            textbutton "CENTER" action Function(td_manager.snap_camera) text_size 12 text_color "#ccc"
            textbutton "SEARCH" action Function(scavenge_location, location) text_size 12 text_color "#ccc"
    
    use meta_menu_screen

# Idle breathing animation (Removed zoom pulse as per user request)
transform char_idle_anim:
    subpixel True
    anchor (0.5, 0.5)
    parallel:
        ease 1.5 rotate -1.5
        ease 1.5 rotate 1.5
        repeat

init python:
    import math
    def _td_noop():
        return None

    def _td_click_to_move():
        zoom = getattr(store, "td_zoom", 1.0)
        mx, my = renpy.get_mouse_pos()
        wx, wy = td_manager.screen_to_world(mx, my, zoom)
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
            _td_click_entity(nearest)
        else:
            td_manager.set_target(wx, wy)



init -5 python:
    def _td_interact_core(obj):
        # Determine if it's an NPC or a raw dict object
        is_npc = hasattr(obj, 'id') and not isinstance(obj, dict)
        
        # Lock Check for Dict Objects (Entities)
        if not is_npc and isinstance(obj, dict):
            lock = obj.get('lock_obj')
            if lock and lock.locked:
                renpy.call_screen("lock_interaction_screen", lock, obj.get('name', 'Object'))
                return

        if is_npc:
            obj.interact()
        elif obj.get('type') == 'fixture':
            fixture = fixture_manager.get_by_entity(world.current_location_id, obj)
            if not fixture:
                renpy.notify("Nothing to use here.")
                return
            if fixture.occupied_by == character.id:
                fixture.unfixate(character)
                renpy.notify(f"You leave {fixture.name}.")
                return
            if fixture.occupied_by and fixture.occupied_by != character.id:
                renpy.notify(f"{fixture.name} is occupied.")
                return
            ok, _msg = fixture.fixate(character)
            if ok:
                renpy.notify(f"You settle at {fixture.name}.")
            return
        elif obj.get('type') == 'container':
            # Initialize Inventory object for the container if it doesn't exist
            if not isinstance(obj.get('inventory'), Inventory):
                inv_id = f"inv_{obj.get('id', 'anon')}"
                items = obj.get('items', [])
                # Create the inventory and store it back in the object
                owner_id = obj.get('owner_id') or obj.get('owner')
                obj['inventory'] = Inventory(inv_id, obj.get('name', 'Container'), items=items, owner_id=owner_id)
            
            # Check for Lock
            lock = obj.get('lock_obj')
            if lock and lock.locked:
                renpy.show_screen("lock_interaction_screen", lock, obj.get('name', 'Container'))
            else:
                # Show side-by-side transfer screen
                renpy.show_screen("container_transfer_screen", obj['inventory'])
        elif 'label' in obj:
            flow_queue.queue_label(obj['label'])
        else:
            renpy.notify(f"Interacted with {obj.get('name')}")

    # Backwards-compatible alias used by setup bindings.
    def _td_interact(obj):
        return _td_interact_core(obj)

    def _run_action(action):
        if action:
            renpy.run(action)


    def _td_click_entity(entity):
        if not entity:
            return
        if entity.is_player:
            _open_inventory_screen()
            renpy.restart_interaction()
            return
        if getattr(entity, "requires_approach", False):
            td_manager.walk_to_entity(entity.x, entity.y, lambda: _run_action(entity.action))
        else:
            _run_action(entity.action)

    class TopDownEntity(object):
        def __init__(self, x, y, sprite, action=None, tooltip=None, idle_anim=False, sprite_tint=None, label=None, depth=None, is_player=False, rotation=0, requires_approach=False, hit_anchor=(0.5, 0.5), hit_size=(120, 120), id=None):
            self.x = x
            self.y = y
            self.sprite = sprite
            self.action = action
            self.tooltip = tooltip
            self.idle_anim = idle_anim
            self.sprite_tint = sprite_tint
            self.label = label
            self.depth = depth  # None = use y position
            self.is_player = is_player
            self.rotation = rotation  # Only used for player
            self.requires_approach = requires_approach
            self.hit_anchor = hit_anchor
            self.hit_size = hit_size
            self.id = id

    class TopDownManager(object):
        def __init__(self):
            self.player_pos = [960, 540] # Default center
            self.target_pos = None
            self.path = []
            self.speed = 300 # Pixels per second
            self.moving = False
            self.last_update = 0
            self.cell_size = 40 # Grid size for pathfinding
            self.obstacles = set()
            self.current_location = None
            
            # Camera
            self.camera_offset = [0, 0]
            self.screen_center = (1920//2, 1080//2)
            self.camera_lerp_speed = 5.0
            
            # Interaction
            self.interaction_callback = None
            self.entities = []
            
            # Character Rotation
            self.player_rotation = 0
            self.target_rotation = 0
            self.rotation_lerp_speed = 10.0
            
            # Exit Logic
            self.pending_exit = None
            
            # Player entity reference (set in setup)
            self.player_entity = None
            
            # Camera snap flag - skip lerp on first frame after setup
            self._camera_snapped = False

        def get_sorted_entities(self):
            """Return all entities (including player) sorted by depth (Y position)"""
            def get_depth(e):
                if e.depth is not None:
                    return e.depth
                return e.y
            return sorted(self.entities, key=get_depth)

        def setup(self, location):
            self.entities = []
            if location is None: return

            self.center_player()
            self.snap_camera()
            self._camera_snapped = True  # Mark camera as snapped to skip lerp on first frame

            for item in location.entities:
                itype = item.get('type', 'object')
                ix, iy = item.get('x', 0), item.get('y', 0)
                iid = item.get('id', 'unknown')
                
                if itype == 'link':
                    dest_id = iid
                    dest_loc = world.locations.get(dest_id)
                    dest_name = dest_loc.name if dest_loc else dest_id.capitalize()
                    tooltip_text = f"Go to {dest_name}"
                    
                    ent = TopDownEntity(ix, iy,
                                        sprite="images/topdown/chars/male_base.png",
                                        action=Function(self.walk_to_exit, dest_id),
                                        tooltip=tooltip_text,
                                        sprite_tint=TintMatrix("#00ff00"),
                                        requires_approach=False,
                                        id=dest_id)
                    self.entities.append(ent)
                
                else:
                    lock_data = item.get('lock')
                    if lock_data:
                        keys_list = lock_data.get('keys', [])
                        if isinstance(keys_list, str): keys_list = [k.strip() for k in keys_list.split(',')]
                        item['lock_obj'] = Lock(
                            ltype=lock_data.get('type', 'physical'),
                            difficulty=int(lock_data.get('difficulty', 1)),
                            keys=keys_list,
                            locked=True
                        )

                    ent = TopDownEntity(ix, iy,
                                        sprite=item.get('sprite', "images/topdown/chars/male_base.png"),
                                        action=Function(_td_interact, item),
                                        tooltip=item.get('name', "Entity"),
                                        idle_anim=item.get('idle_anim', True),
                                        label=item.get('label'),
                                        requires_approach=True,
                                        id=iid)
                    self.entities.append(ent)

            for char in location.characters:
                ent = TopDownEntity(char.x, char.y,
                                    sprite=char.td_sprite,
                                    action=Function(_td_interact, char),
                                    tooltip=char.name,
                                    idle_anim=True,
                                    label=f"char_{char.id}_interact",
                                    requires_approach=True,
                                    hit_anchor=(0.5, 1.0),
                                    hit_size=(120, 160),
                                    id=char.id)
                self.entities.append(ent)
            
            # Create player entity and add to entities list
            self.player_entity = TopDownEntity(
                world.actor.x, world.actor.y,
                sprite=character.td_sprite,
                action=NullAction(),
                tooltip=character.name,
                idle_anim=False,
                is_player=True,
                requires_approach=False,
                hit_anchor=(0.5, 1.0),
                hit_size=(120, 160),
                id=getattr(character, 'id', 'player')
            )
            self.entities.append(self.player_entity)

            self.current_location = location
            self.obstacles = location.obstacles
            self.moving = False
            self.path = []

        def center_player(self):
            px, py = world.actor.x, world.actor.y
            self.player_pos = [px, py]

        def snap_camera(self):
            self.camera_offset = [
                self.player_pos[0] - self.screen_center[0],
                self.player_pos[1] - self.screen_center[1]
            ]
            
        def world_to_screen(self, wx, wy):
            return (wx - self.camera_offset[0], wy - self.camera_offset[1])

        def screen_to_world(self, sx, sy, zoom=1.0):
            rel_x = (sx - self.screen_center[0]) / zoom
            rel_y = (sy - self.screen_center[1]) / zoom
            return (rel_x + self.screen_center[0] + self.camera_offset[0], 
                    rel_y + self.screen_center[1] + self.camera_offset[1])

        def update(self, dt):
            flow_queue.process()

            target_cam_x = self.player_pos[0] - self.screen_center[0]
            target_cam_y = self.player_pos[1] - self.screen_center[1]
            
            # Skip lerp if camera was just snapped (first frame after setup)
            if self._camera_snapped:
                self.camera_offset[0] = target_cam_x
                self.camera_offset[1] = target_cam_y
                self._camera_snapped = False
            else:
                self.camera_offset[0] = self.lerp(self.camera_offset[0], target_cam_x, dt * self.camera_lerp_speed)
                self.camera_offset[1] = self.lerp(self.camera_offset[1], target_cam_y, dt * self.camera_lerp_speed)

            target_rot = self.target_rotation
            diff = (target_rot - self.player_rotation + 180) % 360 - 180
            if abs(diff) > 0.1:
                self.player_rotation = (self.player_rotation + diff * dt * self.rotation_lerp_speed) % 360

            if self.moving and self.path:
                target = self.path[0]
                dx = target[0] - self.player_pos[0]
                dy = target[1] - self.player_pos[1]
                dist = math.hypot(dx, dy)
                
                if dist < self.speed * dt:
                    self.player_pos = list(target)
                    self.path.pop(0)
                    if not self.path:
                        self.moving = False
                        self.check_interaction()
                        self.check_pending_exit()
                else:
                    move_dist = self.speed * dt
                    self.player_pos[0] += (dx / dist) * move_dist
                    self.player_pos[1] += (dy / dist) * move_dist
                    angle = math.degrees(math.atan2(dy, dx))
                    self.target_rotation = angle + 90 + 180

            world.actor.x = int(self.player_pos[0])
            world.actor.y = int(self.player_pos[1])
            
            # Sync player entity position for unified rendering
            if self.player_entity:
                self.player_entity.x = self.player_pos[0]
                self.player_entity.y = self.player_pos[1]
                self.player_entity.rotation = self.player_rotation
            
            # Keep followers near the player for snappy movement
            try:
                followers = party_manager.get_followers()
                offsets = [(-60, 40), (60, 40), (-90, 70), (90, 70)]
                for idx, c in enumerate(followers):
                    ox, oy = offsets[idx % len(offsets)]
                    c.x = int(self.player_pos[0] + ox)
                    c.y = int(self.player_pos[1] + oy)
            except Exception:
                pass

        def check_interaction(self):
            if self.interaction_callback:
                self.interaction_callback()
                self.interaction_callback = None

        def set_target(self, x, y, callback=None):
            self.interaction_callback = None
            start = (int(self.player_pos[0]), int(self.player_pos[1]))
            end = (int(x), int(y))
            self.path = self.find_path(start, end)
            if not self.path:
                renpy.notify("Path blocked")
                return
            self.moving = True
            self.target_pos = end
            self.interaction_callback = callback
            
            dx = end[0] - start[0]
            dy = end[1] - start[1]
            if dx != 0 or dy != 0:
                angle = math.degrees(math.atan2(dy, dx))
                self.target_rotation = angle + 90 + 180

        def walk_to_entity(self, x, y, callback):
            dist = 80
            dx = self.player_pos[0] - x
            dy = self.player_pos[1] - y
            mag = math.hypot(dx, dy)
            if mag > dist:
                tx = x + (dx/mag) * dist
                ty = y + (dy/mag) * dist
                self.set_target(tx, ty, callback)
            else:
                if callback: callback()

        def find_path(self, start, end):
            """A* on a coarse grid using self.cell_size; obstacles are cell tuples."""
            cell = self.cell_size
            def to_cell(pt):
                return (pt[0] // cell, pt[1] // cell)
            def to_world(c):
                return (c[0] * cell + cell // 2, c[1] * cell + cell // 2)
            start_c = to_cell(start)
            end_c = to_cell(end)

            if start_c == end_c:
                return [end]
            
            blocked = set(self.obstacles or set())
            if end_c in blocked:
                return []
            
            import heapq
            open_set = []
            heapq.heappush(open_set, (0, start_c))
            came_from = {}
            g = {start_c: 0}
            
            def heuristic(a, b):
                return abs(a[0]-b[0]) + abs(a[1]-b[1])
            
            max_iter = 5000
            iter_count = 0
            neighbors = [(1,0),(-1,0),(0,1),(0,-1)]
            
            while open_set and iter_count < max_iter:
                iter_count += 1
                _, current = heapq.heappop(open_set)
                if current == end_c:
                    # Reconstruct
                    path_cells = []
                    c = current
                    while c != start_c:
                        path_cells.append(c)
                        c = came_from[c]
                    path_cells.reverse()
                    return [to_world(c) for c in path_cells]
                
                for dx, dy in neighbors:
                    nxt = (current[0]+dx, current[1]+dy)
                    if nxt in blocked:
                        continue
                    tentative_g = g[current] + 1
                    if tentative_g < g.get(nxt, 1e9):
                        came_from[nxt] = current
                        g[nxt] = tentative_g
                        f = tentative_g + heuristic(nxt, end_c)
                        heapq.heappush(open_set, (f, nxt))
            
            return []

        def lerp(self, start, end, t):
            return start + (end - start) * t

        def walk_to_exit(self, dest_id):
            link_data = None
            current_loc = world.current_location
            for l in current_loc.entities:
                if l.get('type') == 'link' and l.get('id') == dest_id:
                    link_data = l
                    break
            if link_data:
                ex, ey = link_data['x'], link_data['y']
                self.pending_exit = dest_id
                self.set_target(ex, ey)
            else:
                renpy.notify("Exit not found!")

        def check_pending_exit(self):
            if self.pending_exit and not self.path:
                dest = self.pending_exit
                self.pending_exit = None
                current_loc = world.current_location
                spawn_pos = None
                for l in current_loc.entities:
                    if l.get('type') == 'link' and l.get('id') == dest:
                        spawn_pos = l.get('spawn')
                        break
                if world.move_to(dest):
                    if spawn_pos:
                        self.player_pos = [spawn_pos[0], spawn_pos[1]]
                        world.actor.x = spawn_pos[0]
                        world.actor.y = spawn_pos[1]
                    self.setup(world.current_location)
                    renpy.transition(Dissolve(0.5))
                else:
                    renpy.notify("Cannot move there.")


    # Instance
    td_manager = TopDownManager()

    def show_map(location):
        td_manager.setup(location)
        renpy.show_screen("top_down_map", location=location)

label _char_interaction_wrapper:
    $ char = getattr(store, '_interact_target_char', None)
    if not char:
        return
    jump char_interaction_show

label char_interaction_show:
    $ char = getattr(store, '_interact_target_char', None)
    if not char:
        return
    $ char_interaction_state = "menu"
    $ char_interaction_pending_label = None
    $ renpy.show_screen("char_interaction_menu", char, show_preview=False, show_backdrop=False)

    # show character on right
    if char.base_image:
        show expression Transform(char.base_image, xzoom=-1) as char_right at right
        with dissolve

    # move player in from left
    if character.base_image:
        show expression character.base_image as char_left at left
        with moveinleft

    jump char_interaction_loop

label char_interaction_loop:
    $ char = getattr(store, '_interact_target_char', None)
    if not char:
        jump char_interaction_end
    $ char_interaction_state = "menu"
    $ char_interaction_pending_label = None
    $ renpy.show_screen("char_interaction_menu", char, show_preview=False, show_backdrop=False)
    while True:
        $ renpy.pause(0.05)
        if not getattr(store, '_interact_target_char', None):
            $ char_interaction_state = "exit"
        if char_interaction_state == "exit":
            jump char_interaction_end
        if char_interaction_pending_label:
            $ _lbl = char_interaction_pending_label
            $ char_interaction_pending_label = None
            $ renpy.hide_screen("char_interaction_menu")
            $ renpy.with_statement(Dissolve(0.2))
            if renpy.has_label(_lbl):
                call expression _lbl from _call_npc_label_wrapper
            $ renpy.show_screen("char_interaction_menu", char, show_preview=False, show_backdrop=False)
            $ renpy.with_statement(Dissolve(0.2))
            $ char_interaction_state = "menu"

label _char_interaction_run_pending:
    $ _lbl = char_interaction_pending_label
    $ char_interaction_pending_label = None
    if not _lbl:
        return
    $ _char = getattr(store, '_interact_target_char', None)
    if not _char:
        return
    $ renpy.hide_screen("char_interaction_menu")
    $ renpy.with_statement(Dissolve(0.2))
    if renpy.has_label(_lbl):
        call expression _lbl
    $ renpy.show_screen("char_interaction_menu", _char, show_preview=False, show_backdrop=False)
    $ renpy.with_statement(Dissolve(0.2))
    return

label char_interaction_end:
    hide screen char_interaction_menu
    if character.base_image:
        show expression Transform(character.base_image, xzoom=-1) as char_left at offscreenleft with moveoutleft
    hide char_right with dissolve
    hide char_left
    $ _interact_target_char = None
    return

label _open_inventory_screen:
    call screen inventory_screen
    return

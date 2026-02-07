init -5 python:
    import math

    class FlowQueueManager(object):
        def __init__(self):
            self.queue = []
            self.active_label = None

        def queue_label(self, label_name):
            if label_name and renpy.has_label(label_name):
                self.queue.append(label_name)

        def process(self):
            if not self.active_label and self.queue:
                self.active_label = self.queue.pop(0)
                renpy.call_in_new_context(self.active_label)
                self.active_label = None

default flow_queue = FlowQueueManager()

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

    def _run_action(action):
        if action:
            renpy.run(action)

    def _td_click_entity(entity):
        if not entity or entity.is_player:
            return
        if getattr(entity, "requires_approach", False):
            td_manager.walk_to_entity(entity.x, entity.y, lambda: _run_action(entity.action))
        else:
            _run_action(entity.action)

    class TopDownEntity(object):
        def __init__(self, x, y, sprite, action=None, tooltip=None, idle_anim=False, sprite_tint=None, label=None, depth=None, is_player=False, rotation=0, requires_approach=False):
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
                    dest_loc = rpg_world.locations.get(dest_id)
                    dest_name = dest_loc.name if dest_loc else dest_id.capitalize()
                    tooltip_text = f"Go to {dest_name}"
                    
                    ent = TopDownEntity(ix, iy, 
                                    sprite="images/topdown/chars/male_base.png",
                                        action=Function(self.walk_to_exit, dest_id),
                                        tooltip=tooltip_text,
                                        sprite_tint=TintMatrix("#00ff00"),
                                        requires_approach=False)
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
                                        requires_approach=True)
                    self.entities.append(ent)

            for char in location.characters:
                ent = TopDownEntity(char.x, char.y,
                                    sprite=char.td_sprite,
                                    action=Function(_td_interact, char),
                                    tooltip=char.name,
                                    idle_anim=True,
                                    label=f"char_{char.id}_interact",
                                    requires_approach=True)
                self.entities.append(ent)
            
            # Create player entity and add to entities list
            self.player_entity = TopDownEntity(
                rpg_world.actor.x, rpg_world.actor.y,
                sprite=pc.td_sprite,
                action=NullAction(),
                tooltip=pc.name,
                idle_anim=False,
                is_player=True,
                requires_approach=False
            )
            self.entities.append(self.player_entity)

            self.current_location = location
            self.obstacles = location.obstacles
            self.moving = False
            self.path = []

        def center_player(self):
            px, py = rpg_world.actor.x, rpg_world.actor.y
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

            rpg_world.actor.x = int(self.player_pos[0])
            rpg_world.actor.y = int(self.player_pos[1])
            
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
            current_loc = rpg_world.current_location
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
                current_loc = rpg_world.current_location
                spawn_pos = None
                for l in current_loc.entities:
                    if l.get('type') == 'link' and l.get('id') == dest:
                        spawn_pos = l.get('spawn')
                        break
                if rpg_world.move_to(dest):
                    if spawn_pos:
                        self.player_pos = [spawn_pos[0], spawn_pos[1]]
                        rpg_world.actor.x = spawn_pos[0]
                        rpg_world.actor.y = spawn_pos[1]
                    self.setup(rpg_world.current_location)
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
        
    $ renpy.transition(dissolve)
    $ res = renpy.call_screen("char_interaction_menu", char)
    
    if res == "talk":
        while True:
            $ d_res = renpy.call_screen("dialogue_choice_screen", char)
            
            if d_res and renpy.has_label(d_res):
                call expression d_res from _call_npc_label_wrapper
            else:
                $ renpy.transition(dissolve)
                jump _char_interaction_wrapper
    
    elif res == "give":
        $ renpy.call_screen("give_item_screen", char)
        $ renpy.transition(dissolve)
        jump _char_interaction_wrapper
        
    $ renpy.transition(dissolve)
    return

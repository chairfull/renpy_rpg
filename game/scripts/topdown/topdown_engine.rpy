init -5 python:
    import math

    class FlowQueueManager(object):
        def __init__(self):
            self.queue = []
            self.active_label = None

        def queue_label(self, label_name):
            if label_name and renpy.has_label(label_name):
                self.queue.append(label_name)
                # If nothing else is happening, we might want to start it soon
                # but we'll let the process() loop handle it for synchronization.

        def process(self):
            # If we are already running a label in a new context, wait
            if self.active_label:
                # Ren'Py doesn't give a perfect 'is_label_finished' for new contexts
                # but we can check if we're back in the main menu/map
                # However, for this simple implementation, we'll assume 
                # call_in_new_context is blocking.
                pass

            if not self.active_label and self.queue:
                self.active_label = self.queue.pop(0)
                renpy.call_in_new_context(self.active_label)
                self.active_label = None # Reset after call finishes (blocking)

    flow_queue = FlowQueueManager()

    def _td_interact(obj):
        # Determine if it's an NPC or a raw dict object
        is_npc = hasattr(obj, 'id') and not isinstance(obj, dict)
        
        if is_npc:
            # Show the character interaction screen
            flow_queue.queue_label("_char_interaction_wrapper")
            store._interact_target_char = obj
        elif 'label' in obj:
            flow_queue.queue_label(obj['label'])
        elif obj.get('type') == 'container':
            renpy.notify(f"Interacted with container: {obj.get('name')}")
        else:
            renpy.notify(f"Interacted with {obj.get('name')}")

    class TopDownEntity(object):
        def __init__(self, x, y, sprite, action=None, tooltip=None, idle_anim=False, sprite_tint=None, label=None):
            self.x = x
            self.y = y
            self.sprite = sprite
            self.action = action
            self.tooltip = tooltip
            self.idle_anim = idle_anim
            self.sprite_tint = sprite_tint
            self.label = label

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
            self.entities = [] # Updated list of TopDownEntity objects (includes exits, chars, objects)
            
            # Character Rotation
            self.player_rotation = 0
            self.target_rotation = 0
            self.rotation_lerp_speed = 10.0
            
            # Exit Logic
            self.pending_exit = None

        def setup(self, location):
            self.entities = []
            
            # Snap camera to player immediately
            self.center_player()
            self.snap_camera()

            # Unified Entity Loading
            # Iterate through location.entities which now contains EVERYTHING (links, objects, containers)
            for item in location.entities:
                itype = item.get('type', 'object')
                ix, iy = item.get('x', 0), item.get('y', 0)
                iid = item.get('id', 'unknown')
                
                if itype == 'link':
                    # It's an exit
                    dest_id = iid
                    # Fetch destination name
                    dest_loc = rpg_world.locations.get(dest_id)
                    dest_name = dest_loc.name if dest_loc else dest_id.capitalize()
                    tooltip_text = f"Go to {dest_name}"
                    
                    ent = TopDownEntity(ix, iy, 
                                        sprite="images_topdown/chars/theo.png",
                                        action=Function(self.walk_to_exit, dest_id),
                                        tooltip=tooltip_text,
                                        sprite_tint=TintMatrix("#00ff00"))
                    print(f"DEBUG: Created Link Entity to {dest_id} at {ix},{iy}")
                    self.entities.append(ent)
                
                else:
                    ent = TopDownEntity(ix, iy,
                                        sprite=item.get('sprite', "images_topdown/chars/theo.png"),
                                        action=Function(self.walk_to_entity, ix, iy, renpy.curry(_td_interact)(item)),
                                        tooltip=item.get('name', "Entity"),
                                        idle_anim=item.get('idle_anim', True),
                                        label=item.get('label'))
                    self.entities.append(ent)

            # 2. Add Characters (NPCs) - These are runtime objects from rpg_world
            for char in location.characters:
                def _char_action(c=char):
                    renpy.show_screen("td_char_popup", char=c)
                
                ent = TopDownEntity(char.x, char.y,
                                    sprite="images_topdown/chars/theo.png",
                                    action=Function(self.walk_to_entity, char.x, char.y, renpy.curry(_td_interact)(char)),
                                    tooltip=char.name,
                                    idle_anim=True,
                                    label=f"char_{char.id}_interact")
                self.entities.append(ent)

            self.current_location = location
            self.obstacles = location.obstacles
            self.moving = False
            self.path = []

        def center_player(self):
            # Move player to center of screen or safe spot if invalid
            # We assume rpg_world.actor has the correct coordinates from previous room spawn
            px, py = rpg_world.actor.x, rpg_world.actor.y
            self.player_pos = [px, py]

        def snap_camera(self):
            """Instantly center camera on player (no lerp)"""
            self.camera_offset = [
                self.player_pos[0] - self.screen_center[0],
                self.player_pos[1] - self.screen_center[1]
            ]
            
        def world_to_screen(self, wx, wy):
            """Convert world coordinates to screen coordinates based on camera"""
            return (wx - self.camera_offset[0], wy - self.camera_offset[1])

        def screen_to_world(self, sx, sy):
            """Convert screen coordinates to world coordinates"""
            return (sx + self.camera_offset[0], sy + self.camera_offset[1])

        def update(self, dt):
            # Process any queued flows (interactions, events)
            flow_queue.process()

            # Camera Follow
            target_cam_x = self.player_pos[0] - self.screen_center[0]
            target_cam_y = self.player_pos[1] - self.screen_center[1]
            
            self.camera_offset[0] = self.lerp(self.camera_offset[0], target_cam_x, dt * self.camera_lerp_speed)
            self.camera_offset[1] = self.lerp(self.camera_offset[1], target_cam_y, dt * self.camera_lerp_speed)

            # Character Rotation
            target_rot = self.target_rotation
            
            # Normalize angles
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
                    
                    # Update Rotation
                    angle = math.degrees(math.atan2(dy, dx))
                    self.target_rotation = angle + 90 + 180 # +90 for up-facing sprite, +180 for correction

            # Update Main Character Object position constantly
            rpg_world.actor.x = int(self.player_pos[0])
            rpg_world.actor.y = int(self.player_pos[1])

        def check_interaction(self):
            if self.interaction_callback:
                self.interaction_callback()
                self.interaction_callback = None

        def set_target(self, x, y, callback=None):
            self.interaction_callback = None # interact only if successfully set new target
            start = (int(self.player_pos[0]), int(self.player_pos[1]))
            end = (int(x), int(y))
            
            # Simple direct path for now, bypassing A* for debugging unless needed
            # self.path = self.find_path(start, end)
            self.path = [end] 
            self.moving = True
            self.target_pos = end
            self.interaction_callback = callback
            
            # Update rotation target immediately
            dx = end[0] - start[0]
            dy = end[1] - start[1]
            if dx != 0 or dy != 0:
                angle = math.degrees(math.atan2(dy, dx))
                self.target_rotation = angle + 90 + 180

        def walk_to_entity(self, x, y, callback):
            """Walk near an entity then trigger callback"""
            # Offset slightly so we don't stand ON the character
            dist = 80
            dx = self.player_pos[0] - x
            dy = self.player_pos[1] - y
            mag = math.hypot(dx, dy)
            
            if mag > dist:
                tx = x + (dx/mag) * dist
                ty = y + (dy/mag) * dist
                self.set_target(tx, ty, callback)
            else:
                # Already close enough
                if callback:
                    callback()

        def find_path(self, start, end):
            # Placeholder for A*
            return [end]

        def lerp(self, start, end, t):
            return start + (end - start) * t

        def walk_to_exit(self, dest_id):
            # Find the link data to get coordinates from entity list
            link_data = None
            current_loc = rpg_world.current_location
            # Search entities for the link
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
                # We have arrived at the exit
                dest = self.pending_exit
                self.pending_exit = None
                
                # Check for spawn point in the link we just used
                current_loc = rpg_world.current_location
                spawn_pos = None
                for l in current_loc.entities:
                    if l.get('type') == 'link' and l.get('id') == dest:
                        spawn_pos = l.get('spawn')
                        break
                
                if rpg_world.move_to(dest):
                    # If spawn point defined, move player there
                    if spawn_pos:
                        self.player_pos = [spawn_pos[0], spawn_pos[1]]
                        # Also update the character object for persistence
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
    # This label is called via the FlowQueue to show character screens
    $ char = getattr(store, '_interact_target_char', None)
    if char:
        # Check if they have a specific conversation label first
        if char.label and renpy.has_label(char.label):
            call expression char.label from _call_npc_label
        else:
            # Otherwise show the generic interact screen (Talk/Give)
            call screen char_interact_screen(char)
    return

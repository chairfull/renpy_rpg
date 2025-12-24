init -20 python:
    import heapq

    class AStarNode:
        def __init__(self, x, y, parent=None, g=0, h=0):
            self.x, self.y = x, y
            self.parent = parent
            self.g = g  # Cost from start
            self.h = h  # Heuristic cost to end
            self.f = g + h  # Total cost

        def __lt__(self, other):
            return self.f < other.f

    class Pathfinder:
        @staticmethod
        def get_path(start, end, obstacles, grid_size=(1920, 1080), cell_size=40):
            # start/end are (x, y) pixel coords
            # obstacles is a set of (cx, cy) grid coords
            
            start_grid = (start[0] // cell_size, start[1] // cell_size)
            end_grid = (end[0] // cell_size, end[1] // cell_size)
            
            if end_grid in obstacles:
                return []

            open_set = []
            heapq.heappush(open_set, AStarNode(start_grid[0], start_grid[1], None, 0, Pathfinder.heuristic(start_grid, end_grid)))
            closed_set = set()
            
            while open_set:
                current = heapq.heappop(open_set)
                
                if (current.x, current.y) == end_grid:
                    path = []
                    while current:
                        path.append((current.x * cell_size + cell_size//2, current.y * cell_size + cell_size//2))
                        current = current.parent
                    return path[::-1]
                
                closed_set.add((current.x, current.y))
                
                # 8-way movement
                for dx, dy in [(0,1), (0,-1), (1,0), (-1,0), (1,1), (1,-1), (-1,1), (-1,-1)]:
                    nx, ny = current.x + dx, current.y + dy
                    
                    if nx < 0 or ny < 0 or nx >= grid_size[0]//cell_size or ny >= grid_size[1]//cell_size:
                        continue
                        
                    if (nx, ny) in obstacles or (nx, ny) in closed_set:
                        continue
                    
                    # Cost: 10 for straight, 14 for diagonal
                    move_cost = 10 if dx == 0 or dy == 0 else 14
                    g = current.g + move_cost
                    h = Pathfinder.heuristic((nx, ny), end_grid)
                    
                    neighbor = AStarNode(nx, ny, current, g, h)
                    
                    # Optimization: Check if neighbor is already in open_set with a lower G
                    in_open = False
                    for node in open_set:
                        if node.x == nx and node.y == ny and node.g <= g:
                            in_open = True
                            break
                    
                    if not in_open:
                        heapq.heappush(open_set, neighbor)
            
            return []

        @staticmethod
        def heuristic(a, b):
            # Diagonal distance
            dx = abs(a[0] - b[0])
            dy = abs(a[1] - b[1])
            return 10 * (dx + dy) + (14 - 2 * 10) * min(dx, dy)

    class TopDownManager(NoRollback):
        def __init__(self):
            self.player_pos = (960, 540)
            self.target_pos = None
            self.path = []
            self.speed = 350.0 # Slightly faster
            self.moving = False
            self.current_waypoint_idx = 0
            self.current_location = None
            
            # Interactive objects (id -> (x, y))
            self.interactives = {}
            self.obstacles = set()
            self.cell_size = 40

        def setup(self, location):
            if self.current_location != location:
                self.current_location = location
                # Only reset position if we are actually at a new location
                # (to avoid snapping during interactions)
                if not self.moving:
                    self.center_player()

            self.obstacles = location.obstacles
            self.interactives = {}
            for char in location.characters:
                self.interactives[char.name.lower()] = (char.x, char.y)
            for ent in location.entities:
                oid = getattr(ent, 'id', ent.name.lower())
                self.interactives[oid] = (ent.x, ent.y)
            
            self.moving = False
            self.path = []

        def center_player(self):
            # Move player to center of screen or safe spot
            self.player_pos = (960, 540)
            # Find closest non-obstacle cell if current is blocked
            gx, gy = int(960//self.cell_size), int(540//self.cell_size)
            if (gx, gy) in self.obstacles:
                # Simple spiral search for free cell
                for r in range(1, 10):
                    for dx, dy in [(r,0), (-r,0), (0,r), (0,-r)]:
                        nx, ny = gx+dx, gy+dy
                        if (nx, ny) not in self.obstacles:
                            self.player_pos = (nx*self.cell_size + self.cell_size//2, ny*self.cell_size + self.cell_size//2)
                            return

        def set_target(self, tx, ty):
            self.target_pos = (tx, ty)
            self.path = Pathfinder.get_path(self.player_pos, self.target_pos, self.obstacles, cell_size=self.cell_size)
            if self.path:
                self.moving = True
                self.current_waypoint_idx = 0
                renpy.restart_interaction()

        def update(self, dt):
            if not self.moving or not self.path:
                return

            dest = self.path[self.current_waypoint_idx]
            dx = dest[0] - self.player_pos[0]
            dy = dest[1] - self.player_pos[1]
            dist = (dx**2 + dy**2)**0.5
            
            move_dist = self.speed * dt
            
            if move_dist >= dist:
                self.player_pos = dest
                self.current_waypoint_idx += 1
                if self.current_waypoint_idx >= len(self.path):
                    self.moving = False
                    self.path = []
                    # Check for interaction proximity
                    self.check_interaction()
            else:
                unit_x = dx / dist
                unit_y = dy / dist
                self.player_pos = (self.player_pos[0] + unit_x * move_dist, self.player_pos[1] + unit_y * move_dist)
            
            renpy.restart_interaction()

        def check_interaction(self):
            # Check if player is near any interactive object after reaching target
            loc = rpg_world.current_location
            for obj_id, (ox, oy) in self.interactives.items():
                d = ((self.player_pos[0] - ox)**2 + (self.player_pos[1] - oy)**2)**0.5
                if d < 100: # Interaction radius
                    # Find the object in characters or current location entities
                    target_obj = None
                    for c in loc.characters:
                        if c.name.lower() == obj_id:
                            target_obj = c
                            break
                    if not target_obj:
                        for e in loc.entities:
                            if (hasattr(e,'id') and e.id == obj_id) or e.name.lower() == obj_id:
                                target_obj = e
                                break
                    
                    if target_obj:
                        renpy.call_in_new_context("_topdown_interact_helper", target_obj)
                        break

    def _topdown_interact_helper(obj):
        obj.interact()

    # Instance
    td_manager = TopDownManager()

    def td_update_func(st, at):
        td_manager.update(0.016) # Approx 60fps
        return 0.016

    def show_map(location):
        td_manager.setup(location)
        renpy.show_screen("top_down_map", location=location)

init -2000 python:
    class PathFollower(Vector3):
        def __init__(self, position=Vector3(), speed=300):
            Vector3.__init__(self, position)
            self.path = []
            self.speed = speed
            self.moving = False
        
        def set_path_target(self, target):
            start = self.xyz
            self.path = location.get_path(start, target)
            if not self.path:
                renpy.notify("Path blocked")
                return
            self.moving = True

        def update_path_following(self, dt):
            if not self.path:
                self.moving = False
                return
            target = self.path[0]
            direction = (target - self).normalized()
            distance = (target - self).length()
            step = self.speed * dt
            if step >= distance:
                self.reset(target)
                self.path.pop(0)
                self.moving = bool(self.path)
            else:
                self.move(direction * step)
                self.moving = True

    class AstarNode(Vector3):
        def __init__(self, position=Vector3(), walkable=True):
            super(AstarNode, self).__init__(position)
            self.walkable = walkable

        def __hash__(self):
            return hash((self.x, self.y, self.z))

        def __eq__(self, other):
            return (self.x, self.y, self.z) == (other.x, other.y, other.z)
    
    class Astar:
        def __init__(self, graph):
            self.nodes = set(graph.keys())
            self.graph = graph
        
        def add_node(self, node):
            if node not in self.graph:
                self.graph[node] = []

        def _add_edge(self, from_node, to_node):
            if from_node not in self.graph:
                self.graph[from_node] = []
            self.graph[from_node].append(to_node)
        
        def add_edge(self, from_node, to_node, bidirectional=True):
            self._add_edge(from_node, to_node)
            if bidirectional:
                self._add_edge(to_node, from_node)
        
        def remove_edge(self, from_node, to_node, bidirectional=True):
            if from_node in self.graph and to_node in self.graph[from_node]:
                self.graph[from_node].remove(to_node)
            if bidirectional and to_node in self.graph and from_node in self.graph[to_node]:
                self.graph[to_node].remove(from_node)
        
        def remove_node(self, node):
            if node in self.graph:
                del self.graph[node]
            for neighbors in self.graph.values():
                if node in neighbors:
                    neighbors.remove(node)
        
        def heuristic(self, a, b):
            # Manhattan distance
            return abs(a[0] - b[0]) + abs(a[1] - b[1])

        def get_neighbors(self, node):
            return self.graph.get(node, [])

        def find_path(self, start, goal):
            open_set = set([start])
            came_from = {}
            g_score = {start: 0}
            f_score = {start: self.heuristic(start, goal)}
            
            while open_set:
                current = min(open_set, key=lambda n: f_score.get(n, float('inf')))
                if current == goal:
                    path = []
                    while current in came_from:
                        path.append(current)
                        current = came_from[current]
                    path.append(start)
                    return path[::-1]
                
                open_set.remove(current)
                for neighbor in self.get_neighbors(current):
                    tentative_g_score = g_score[current] + 1
                    if tentative_g_score < g_score.get(neighbor, float('inf')):
                        came_from[neighbor] = current
                        g_score[neighbor] = tentative_g_score
                        f_score[neighbor] = tentative_g_score + self.heuristic(neighbor, goal)
                        if neighbor not in open_set:
                            open_set.add(neighbor)
            return None
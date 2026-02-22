import heapq
from .vector3 import Vector3

class Astar:
    def __init__(self):
        self.nodes = {}
        self.edges = {}

    def add_node(self, key, position=None):
        self.nodes[key] = position if position is not None else Vector3()

    def add_edge(self, a_key, b_key, bidirectional=True):
        self.edges[(a_key, b_key)] = True
        if bidirectional:
            self.edges[(b_key, a_key)] = True

    def remove_edge(self, a_key, b_key, bidirectional=True):
        self.edges.pop((a_key, b_key), None)
        if bidirectional:
            self.edges.pop((b_key, a_key), None)

    def _heuristic(self, a_key, b_key):
        a_pos = self.nodes[a_key]
        b_pos = self.nodes[b_key]
        return (a_pos - b_pos).length()

    def _cost(self, a_key, b_key):
        """Actual travel cost between two connected nodes."""
        a_pos = self.nodes[a_key]
        b_pos = self.nodes[b_key]
        return (a_pos - b_pos).length()

    def _neighbours(self, key):
        """Return all nodes reachable from the given node."""
        return [b for (a, b) in self.edges if a == key]

    def find_path(self, a_key, b_key):
        """
        Find the cheapest path between two location keys.
        Returns a list of keys from a_key to b_key, or [] if no path exists.
        """
        if a_key not in self.nodes or b_key not in self.nodes:
            return []

        # Min-heap: (f_score, g_score, current_key)
        open_heap = [(0.0, 0.0, a_key)]
        came_from = {}
        g_scores = {a_key: 0.0}

        while open_heap:
            _, g, current = heapq.heappop(open_heap)

            if current == b_key:
                # Reconstruct path
                path = []
                while current in came_from:
                    path.append(current)
                    current = came_from[current]
                path.append(a_key)
                return list(reversed(path))

            # Skip if we've already found a better path to this node
            if g > g_scores.get(current, float('inf')):
                continue

            for neighbour in self._neighbours(current):
                tentative_g = g_scores[current] + self._cost(current, neighbour)
                if tentative_g < g_scores.get(neighbour, float('inf')):
                    g_scores[neighbour] = tentative_g
                    f = tentative_g + self._heuristic(neighbour, b_key)
                    came_from[neighbour] = current
                    heapq.heappush(open_heap, (f, tentative_g, neighbour))

        return []  # No path found
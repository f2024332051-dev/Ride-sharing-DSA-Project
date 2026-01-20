"""
ShortestPath.py - Dijkstra's algorithm implementation
"""

class ShortestPath:
    """Implements Dijkstra's shortest path algorithm"""
    
    @staticmethod
    def dijkstra(city, start_node, end_node):
        """
        Find shortest path from start_node to end_node using Dijkstra's algorithm
        Returns: (distance, path) where path is list of node IDs
        """
        if start_node == end_node:
            return (0, [start_node])
        
        # Initialize distances
        distances = {}
        previous = {}
        unvisited = []
        
        for node_id in city.get_all_nodes():
            distances[node_id] = float('inf')
            previous[node_id] = None
            unvisited.append(node_id)
        
        distances[start_node] = 0
        
        # Main algorithm loop
        while unvisited:
            # Find unvisited node with minimum distance
            min_node = None
            min_dist = float('inf')
            
            for node_id in unvisited:
                if distances[node_id] < min_dist:
                    min_dist = distances[node_id]
                    min_node = node_id
            
            if min_node is None or min_node == end_node:
                break
            
            unvisited.remove(min_node)
            
            # Update distances to neighbors
            node = city.get_node(min_node)
            for edge in node.edges:
                neighbor = edge.to_node
                if neighbor in unvisited:
                    alt = distances[min_node] + edge.weight
                    if alt < distances[neighbor]:
                        distances[neighbor] = alt
                        previous[neighbor] = min_node
        
        # Reconstruct path
        if distances[end_node] == float('inf'):
            return (float('inf'), [])
        
        path = []
        current = end_node
        while current is not None:
            path.insert(0, current)
            current = previous[current]
        
        return (distances[end_node], path)

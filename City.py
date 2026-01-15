"""
City.py - Represents the city as a weighted graph with zones
Custom graph implementation without STL containers
"""

class Edge:
    """Represents an edge in the graph"""
    def __init__(self, to_node, weight):
        self.to_node = to_node
        self.weight = weight

class Node:
    """Represents a node (location) in the graph"""
    def __init__(self, node_id, zone_id, x=None, y=None):
        self.node_id = node_id
        self.zone_id = zone_id
        self.x = x  # For GUI positioning
        self.y = y  # For GUI positioning
        self.edges = []  # List of Edge objects

class City:
    """City represented as a weighted graph with zones"""
    
    def __init__(self):
        self.nodes = []  # List of Node objects
        self.zones = {}  # zone_id -> list of node_ids
        self.zone_colors = {}  # zone_id -> color
        self.node_map = {}  # node_id -> Node object
        
    def add_node(self, node_id, zone_id, x=None, y=None):
        """Add a node to the city"""
        if node_id not in self.node_map:
            node = Node(node_id, zone_id, x, y)
            self.nodes.append(node)
            self.node_map[node_id] = node
            
            if zone_id not in self.zones:
                self.zones[zone_id] = []
            self.zones[zone_id].append(node_id)
    
    def add_edge(self, from_node, to_node, weight):
        """Add a bidirectional edge between two nodes"""
        if from_node in self.node_map and to_node in self.node_map:
            # Add edge from -> to
            self.node_map[from_node].edges.append(Edge(to_node, weight))
            # Add edge to -> from (bidirectional)
            self.node_map[to_node].edges.append(Edge(from_node, weight))
    
    def get_node(self, node_id):
        """Get node by ID"""
        return self.node_map.get(node_id)
    
    def get_zone(self, node_id):
        """Get zone ID for a given node"""
        node = self.node_map.get(node_id)
        return node.zone_id if node else None
    
    def are_in_same_zone(self, node1_id, node2_id):
        """Check if two nodes are in the same zone"""
        zone1 = self.get_zone(node1_id)
        zone2 = self.get_zone(node2_id)
        return zone1 == zone2 and zone1 is not None
    
    def get_all_nodes(self):
        """Get all node IDs"""
        return list(self.node_map.keys())
    
    def get_nodes_in_zone(self, zone_id):
        """Get all node IDs in a zone"""
        return self.zones.get(zone_id, [])

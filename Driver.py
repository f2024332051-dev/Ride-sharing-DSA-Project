"""
Driver.py - Represents a driver in the system
"""

class Driver:
    """Represents a driver with location and availability"""
    
    def __init__(self, driver_id, name, current_location_node, zone_id):
        self.driver_id = driver_id
        self.name = name
        self.current_location_node = current_location_node
        self.zone_id = zone_id
        self.available = True
        self.total_trips = 0
        self.completed_trips = 0
    
    def assign_trip(self):
        """Mark driver as unavailable"""
        self.available = False
    
    def complete_trip(self, new_location_node):
        """Complete trip and update location"""
        self.available = True
        self.current_location_node = new_location_node
        self.total_trips += 1
        self.completed_trips += 1
    
    def cancel_trip(self):
        """Cancel trip and make driver available"""
        self.available = True
    
    def get_utilization(self):
        """Calculate driver utilization percentage"""
        if self.total_trips == 0:
            return 0.0
        return (self.completed_trips / self.total_trips) * 100

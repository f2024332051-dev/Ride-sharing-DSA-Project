"""
DispatchEngine.py - Handles driver assignment logic
"""

from ShortestPath import ShortestPath

class DispatchEngine:
    """Engine for assigning drivers to trips"""
    
    def __init__(self, city):
        self.city = city
    
    def find_nearest_driver(self, pickup_node, drivers):
        """
        Find the nearest available driver to pickup location
        Returns: (driver_id, distance) or (None, None) if no driver available
        """
        available_drivers = [d for d in drivers if d.available]
        
        if not available_drivers:
            return (None, None)
        
        best_driver = None
        best_distance = float('inf')
        best_in_zone = False
        
        for driver in available_drivers:
            driver_node = driver.current_location_node
            distance, _ = ShortestPath.dijkstra(self.city, driver_node, pickup_node)
            
            # Prefer drivers in the same zone
            driver_zone = self.city.get_zone(driver_node)
            pickup_zone = self.city.get_zone(pickup_node)
            in_zone = (driver_zone == pickup_zone)
            
            # If we haven't found an in-zone driver yet, or this is closer
            if (not best_in_zone and in_zone) or (best_in_zone == in_zone and distance < best_distance):
                best_driver = driver
                best_distance = distance
                best_in_zone = in_zone
        
        if best_driver:
            return (best_driver.driver_id, best_distance)
        return (None, None)
    
    def calculate_trip_distance(self, pickup_node, dropoff_node):
        """Calculate shortest distance between pickup and dropoff"""
        distance, _ = ShortestPath.dijkstra(self.city, pickup_node, dropoff_node)
        return distance

"""
Trip.py - Represents a trip with state management
"""

class TripState:
    """Trip state enumeration"""
    REQUESTED = "REQUESTED"
    ASSIGNED = "ASSIGNED"
    ONGOING = "ONGOING"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"

class Trip:
    """Represents a trip with state machine"""
    
    def __init__(self, trip_id, rider_id, pickup_node, dropoff_node, city):
        self.trip_id = trip_id
        self.rider_id = rider_id
        self.pickup_node = pickup_node
        self.dropoff_node = dropoff_node
        self.city = city
        self.state = TripState.REQUESTED
        self.driver_id = None
        self.distance = 0  # Will be calculated when assigned
        self.cost = 0  # Will be calculated when assigned
        self.base_fare = 50  # Base fare constant
        
    def assign_driver(self, driver_id, distance):
        """Assign driver and calculate cost"""
        if self.state != TripState.REQUESTED:
            return False
        
        self.driver_id = driver_id
        self.distance = distance
        
        # Calculate cost: base fare + 20% per zone crossed
        pickup_zone = self.city.get_zone(self.pickup_node)
        dropoff_zone = self.city.get_zone(self.dropoff_node)
        
        if pickup_zone != dropoff_zone:
            zones_crossed = abs(pickup_zone - dropoff_zone)
            zone_charge = self.base_fare * 0.20 * zones_crossed
            self.cost = self.base_fare + zone_charge
        else:
            self.cost = self.base_fare
        
        self.state = TripState.ASSIGNED
        return True
    
    def start_trip(self):
        """Transition to ONGOING state"""
        if self.state != TripState.ASSIGNED:
            return False
        self.state = TripState.ONGOING
        return True
    
    def complete_trip(self):
        """Transition to COMPLETED state"""
        if self.state != TripState.ONGOING:
            return False
        self.state = TripState.COMPLETED
        return True
    
    def cancel_trip(self):
        """Cancel the trip"""
        if self.state not in [TripState.REQUESTED, TripState.ASSIGNED]:
            return False
        self.state = TripState.CANCELLED
        return True
    
    def can_cancel(self):
        """Check if trip can be cancelled"""
        return self.state in [TripState.REQUESTED, TripState.ASSIGNED]
    
    def get_state(self):
        """Get current state"""
        return self.state

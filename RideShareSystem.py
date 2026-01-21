"""
RideShareSystem.py - Main system coordinator
"""

from Trip import Trip, TripState

class RideShareSystem:
    """Main system that coordinates all components"""
    
    def __init__(self, city):
        self.city = city
        self.drivers = []
        self.riders = []
        self.trips = {}  # trip_id -> Trip
        self.trip_history = []  # All trips (including cancelled/completed)
        self.next_trip_id = 1
        self.dispatch_engine = None
        self.rollback_manager = None
    
    def set_dispatch_engine(self, dispatch_engine):
        """Set the dispatch engine"""
        self.dispatch_engine = dispatch_engine
    
    def set_rollback_manager(self, rollback_manager):
        """Set the rollback manager"""
        self.rollback_manager = rollback_manager
    
    def add_driver(self, driver):
        """Add a driver to the system"""
        self.drivers.append(driver)
    
    def add_rider(self, rider):
        """Add a rider to the system"""
        self.riders.append(rider)
    
    def request_trip(self, rider_id, pickup_node, dropoff_node):
        """Request a new trip"""
        trip_id = self.next_trip_id
        self.next_trip_id += 1
        
        trip = Trip(trip_id, rider_id, pickup_node, dropoff_node, self.city)
        self.trips[trip_id] = trip
        
        # Auto-assign driver
        driver_id, driver_to_pickup_distance = self.dispatch_engine.find_nearest_driver(pickup_node, self.drivers)
        
        if driver_id:
            driver = next((d for d in self.drivers if d.driver_id == driver_id), None)
            if driver:
                # Calculate actual trip distance (pickup to dropoff)
                trip_distance = self.dispatch_engine.calculate_trip_distance(pickup_node, dropoff_node)
                
                # Record operation for rollback
                self.rollback_manager.record_operation(
                    'ASSIGN', trip_id, driver_id,
                    driver.available, driver.current_location_node
                )
                
                trip.assign_driver(driver_id, trip_distance)
                driver.assign_trip()
        
        return trip_id
    
    def start_trip(self, trip_id):
        """Start a trip (transition to ONGOING)"""
        trip = self.trips.get(trip_id)
        if not trip:
            return False
        
        if trip.start_trip():
            self.rollback_manager.record_operation('START', trip_id, trip.driver_id)
            return True
        return False
    
    def complete_trip(self, trip_id):
        """Complete a trip"""
        trip = self.trips.get(trip_id)
        if not trip:
            return False
        
        if trip.complete_trip():
            driver = next((d for d in self.drivers if d.driver_id == trip.driver_id), None)
            if driver:
                # Record operation for rollback
                prev_location = driver.current_location_node
                self.rollback_manager.record_operation(
                    'COMPLETE', trip_id, trip.driver_id,
                    driver.available, prev_location
                )
                
                driver.complete_trip(trip.dropoff_node)
            
            # Move trip to history
            self.trip_history.append(trip)
            del self.trips[trip_id]
            return True
        return False
    
    def cancel_trip(self, trip_id):
        """Cancel a trip"""
        trip = self.trips.get(trip_id)
        if not trip:
            return False
        
        if trip.cancel_trip():
            driver = None
            if trip.driver_id:
                driver = next((d for d in self.drivers if d.driver_id == trip.driver_id), None)
                if driver:
                    # Record operation for rollback
                    self.rollback_manager.record_operation(
                        'CANCEL', trip_id, trip.driver_id,
                        driver.available, driver.current_location_node
                    )
                    driver.cancel_trip()
            
            # Move trip to history
            self.trip_history.append(trip)
            del self.trips[trip_id]
            return True
        return False
    
    def get_trip(self, trip_id):
        """Get trip by ID"""
        return self.trips.get(trip_id)
    
    def get_analytics(self):
        """Get system analytics"""
        all_trips = list(self.trips.values()) + self.trip_history
        
        if not all_trips:
            return {
                'avg_distance': 0,
                'driver_utilization': {},
                'cancelled_count': 0,
                'completed_count': 0,
                'total_trips': 0
            }
        
        # Average trip distance
        total_distance = sum(t.distance for t in all_trips if t.distance > 0)
        trip_count_with_distance = len([t for t in all_trips if t.distance > 0])
        avg_distance = total_distance / trip_count_with_distance if trip_count_with_distance > 0 else 0
        
        # Driver utilization
        driver_utilization = {}
        for driver in self.drivers:
            driver_utilization[driver.driver_id] = {
                'name': driver.name,
                'utilization': driver.get_utilization(),
                'total_trips': driver.total_trips,
                'completed_trips': driver.completed_trips
            }
        
        # Cancelled vs completed
        cancelled_count = len([t for t in all_trips if t.state == TripState.CANCELLED])
        completed_count = len([t for t in all_trips if t.state == TripState.COMPLETED])
        
        return {
            'avg_distance': avg_distance,
            'driver_utilization': driver_utilization,
            'cancelled_count': cancelled_count,
            'completed_count': completed_count,
            'total_trips': len(all_trips)
        }
    
    def get_trip_history(self):
        """Get all trip history"""
        return self.trip_history + list(self.trips.values())

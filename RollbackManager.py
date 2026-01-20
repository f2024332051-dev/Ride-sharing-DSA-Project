"""
RollbackManager.py - Manages rollback operations
"""

class Operation:
    """Represents an operation that can be rolled back"""
    def __init__(self, op_type, trip_id, driver_id=None, driver_prev_state=None, driver_prev_location=None):
        self.op_type = op_type  # 'ASSIGN', 'COMPLETE', 'CANCEL', 'START'
        self.trip_id = trip_id
        self.driver_id = driver_id
        self.driver_prev_state = driver_prev_state  # Available state before operation
        self.driver_prev_location = driver_prev_location  # Location before operation

class RollbackManager:
    """Manages rollback of operations"""
    
    def __init__(self):
        self.operation_history = []  # Stack of operations
    
    def record_operation(self, op_type, trip_id, driver_id=None, driver_prev_state=None, driver_prev_location=None):
        """Record an operation for potential rollback"""
        operation = Operation(op_type, trip_id, driver_id, driver_prev_state, driver_prev_location)
        self.operation_history.append(operation)
    
    def rollback_last_k(self, k, trips, drivers):
        """
        Rollback last k operations
        Returns: True if successful, False otherwise
        """
        if k > len(self.operation_history):
            return False
        
        # Get last k operations (in reverse order)
        operations_to_rollback = self.operation_history[-k:]
        operations_to_rollback.reverse()  # Process in reverse order
        
        for op in operations_to_rollback:
            trip = trips.get(op.trip_id)
            driver = None
            if op.driver_id:
                driver = next((d for d in drivers if d.driver_id == op.driver_id), None)
            
            if op.op_type == 'ASSIGN':
                # Rollback assignment: cancel trip, restore driver
                if trip and trip.state == 'ASSIGNED':
                    trip.state = 'REQUESTED'
                    trip.driver_id = None
                if driver and op.driver_prev_state is not None:
                    driver.available = op.driver_prev_state
                    if op.driver_prev_location:
                        driver.current_location_node = op.driver_prev_location
            
            elif op.op_type == 'START':
                # Rollback start: go back to ASSIGNED
                if trip and trip.state == 'ONGOING':
                    trip.state = 'ASSIGNED'
            
            elif op.op_type == 'COMPLETE':
                # Rollback completion: go back to ONGOING, restore driver location
                if trip and trip.state == 'COMPLETED':
                    trip.state = 'ONGOING'
                if driver and op.driver_prev_location:
                    driver.current_location_node = op.driver_prev_location
                    driver.completed_trips = max(0, driver.completed_trips - 1)
                    driver.total_trips = max(0, driver.total_trips - 1)
            
            elif op.op_type == 'CANCEL':
                # Rollback cancellation: restore trip state and driver
                if trip and trip.state == 'CANCELLED':
                    # Need to determine previous state - for simplicity, assume ASSIGNED
                    trip.state = 'ASSIGNED'
                if driver and op.driver_prev_state is not None:
                    driver.available = op.driver_prev_state
        
        # Remove rolled back operations from history
        self.operation_history = self.operation_history[:-k]
        return True
    
    def get_history_size(self):
        """Get number of operations in history"""
        return len(self.operation_history)

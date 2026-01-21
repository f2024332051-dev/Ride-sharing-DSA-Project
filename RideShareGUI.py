"""
RideShareGUI.py - Tkinter GUI for Ride-Sharing System
"""

import tkinter as tk
from tkinter import ttk, messagebox
import math
import threading
import time

from City import City
from Driver import Driver
from Rider import Rider
from DispatchEngine import DispatchEngine
from RollbackManager import RollbackManager
from CancellationManager import CancellationManager
from RideShareSystem import RideShareSystem
from Trip import TripState

class TripProgressWindow:
    """Popup window showing trip progress with progress bar"""
    
    def __init__(self, parent, trip_id, system):
        self.parent = parent
        self.trip_id = trip_id
        self.system = system
        self.window = tk.Toplevel(parent)
        self.window.title(f"Trip {trip_id} Progress")
        self.window.geometry("400x200")
        self.window.resizable(False, False)
        
        # Center the window
        self.window.transient(parent)
        self.window.grab_set()
        
        self.progress_var = tk.DoubleVar()
        self.status_label = tk.Label(self.window, text="Status: REQUESTED", font=("Arial", 12, "bold"))
        self.status_label.pack(pady=10)
        
        self.progress_bar = ttk.Progressbar(self.window, variable=self.progress_var, maximum=100, length=300)
        self.progress_bar.pack(pady=20)
        
        self.details_label = tk.Label(self.window, text="", font=("Arial", 10))
        self.details_label.pack(pady=10)
        
        self.cancel_button = tk.Button(self.window, text="Cancel Trip", command=self.cancel_this_trip, bg="#F44336", fg="white")
        self.cancel_button.pack(pady=10)
        
        self.update_progress()
    
    def update_progress(self):
        """Update progress bar based on trip state"""
        if not self.window.winfo_exists():
            return
        
        trip = self.system.get_trip(self.trip_id)
        
        if not trip:
            # Trip completed or cancelled
            self.status_label.config(text="Trip Completed/Cancelled")
            self.progress_var.set(100)
            self.window.after(2000, self.window.destroy)
            return
        
        state = trip.state
        
        if state == TripState.REQUESTED:
            self.status_label.config(text="Status: REQUESTED - Waiting for driver...")
            self.progress_var.set(25)
            self.details_label.config(text="Finding nearest driver...")
        elif state == TripState.ASSIGNED:
            self.status_label.config(text="Status: ASSIGNED - Driver on the way!")
            self.progress_var.set(50)
            driver = next((d for d in self.system.drivers if d.driver_id == trip.driver_id), None)
            if driver:
                self.details_label.config(text=f"Driver: {driver.name} | Distance: {trip.distance:.1f} km | Cost: ${trip.cost:.2f}")
        elif state == TripState.ONGOING:
            self.status_label.config(text="Status: ONGOING - Trip in progress!")
            self.progress_var.set(75)
            self.details_label.config(text="Enjoy your ride!")
        elif state == TripState.COMPLETED:
            self.status_label.config(text="Status: COMPLETED")
            self.progress_var.set(100)
            self.details_label.config(text="Thank you for using our service!")
            self.window.after(2000, self.window.destroy)
            return
        elif state == TripState.CANCELLED:
            self.status_label.config(text="Status: CANCELLED")
            self.progress_var.set(0)
            self.details_label.config(text="Trip has been cancelled")
            self.window.after(2000, self.window.destroy)
            return
        
        # Continue updating
        self.window.after(500, self.update_progress)
    
    def cancel_this_trip(self):
        """Cancel the trip from the progress window"""
        success = self.parent.cancellation_manager.cancel_trip(self.parent.system, self.trip_id)
        if success:
            messagebox.showinfo("Success", f"Trip {self.trip_id} cancelled")
            self.window.destroy()
            # Update parent's displays
            self.parent.update_trips_list()
            self.parent.update_analytics()
            self.parent.draw_graph()
            # Remove from timers
            self.parent.trip_timers.pop(self.trip_id, None)
        else:
            messagebox.showerror("Error", "Cannot cancel this trip")

class RideShareGUI:
    """Main GUI class"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Ride-Sharing Dispatch & Trip Management System")
        self.root.geometry("1400x800")
        
        # Initialize system components
        self.city = self.create_sample_city()
        self.system = RideShareSystem(self.city)
        self.dispatch_engine = DispatchEngine(self.city)
        self.rollback_manager = RollbackManager()
        self.cancellation_manager = CancellationManager()
        
        self.system.set_dispatch_engine(self.dispatch_engine)
        self.system.set_rollback_manager(self.rollback_manager)
        
        # Initialize drivers and riders
        self.initialize_drivers()
        self.initialize_riders()
        
        # GUI variables
        self.selected_pickup = tk.StringVar()
        self.selected_dropoff = tk.StringVar()
        self.selected_rider = tk.StringVar()
        self.rollback_k = tk.StringVar(value="1")
        
        # Current trip progress windows
        self.progress_windows = {}
        self.trip_timers = {}
        
        # Create GUI
        self.create_gui()
        
        # Start auto state transitions
        self.start_auto_transitions()
    
    def create_sample_city(self):
        """Create a sample city with 4 zones and nodes"""
        city = City()
        
        # Zone colors
        city.zone_colors = {
            1: "#FF6B6B",  # Red
            2: "#4ECDC4",  # Teal
            3: "#45B7D1",  # Blue
            4: "#FFA07A"   # Light Salmon
        }
        
        # Zone 1: Nodes 1-4 (top-left)
        city.add_node(1, 1, 150, 150)
        city.add_node(2, 1, 250, 150)
        city.add_node(3, 1, 150, 250)
        city.add_node(4, 1, 250, 250)
        
        # Zone 2: Nodes 5-8 (top-right)
        city.add_node(5, 2, 450, 150)
        city.add_node(6, 2, 550, 150)
        city.add_node(7, 2, 450, 250)
        city.add_node(8, 2, 550, 250)
        
        # Zone 3: Nodes 9-12 (bottom-left)
        city.add_node(9, 3, 150, 450)
        city.add_node(10, 3, 250, 450)
        city.add_node(11, 3, 150, 550)
        city.add_node(12, 3, 250, 550)
        
        # Zone 4: Nodes 13-16 (bottom-right)
        city.add_node(13, 4, 450, 450)
        city.add_node(14, 4, 550, 450)
        city.add_node(15, 4, 450, 550)
        city.add_node(16, 4, 550, 550)
        
        # Add edges within zones
        # Zone 1 edges
        city.add_edge(1, 2, 10)
        city.add_edge(1, 3, 10)
        city.add_edge(2, 4, 10)
        city.add_edge(3, 4, 10)
        
        # Zone 2 edges
        city.add_edge(5, 6, 10)
        city.add_edge(5, 7, 10)
        city.add_edge(6, 8, 10)
        city.add_edge(7, 8, 10)
        
        # Zone 3 edges
        city.add_edge(9, 10, 10)
        city.add_edge(9, 11, 10)
        city.add_edge(10, 12, 10)
        city.add_edge(11, 12, 10)
        
        # Zone 4 edges
        city.add_edge(13, 14, 10)
        city.add_edge(13, 15, 10)
        city.add_edge(14, 16, 10)
        city.add_edge(15, 16, 10)
        
        # Cross-zone connections
        # Between Zone 1 and Zone 2
        city.add_edge(2, 5, 25)
        city.add_edge(4, 7, 25)
        
        # Between Zone 1 and Zone 3
        city.add_edge(3, 9, 25)
        city.add_edge(4, 10, 25)
        
        # Between Zone 2 and Zone 4
        city.add_edge(7, 13, 25)
        city.add_edge(8, 14, 25)
        
        # Between Zone 3 and Zone 4
        city.add_edge(10, 13, 25)
        city.add_edge(12, 15, 25)
        
        return city
    
    def initialize_drivers(self):
        """Initialize drivers with default locations"""
        drivers_data = [
            (1, "Driver Alice", 1, 1),
            (2, "Driver Bob", 5, 2),
            (3, "Driver Charlie", 9, 3),
            (4, "Driver Diana", 13, 4),
            (5, "Driver Eve", 2, 1)
        ]
        
        for driver_id, name, location, zone in drivers_data:
            driver = Driver(driver_id, name, location, zone)
            self.system.add_driver(driver)
    
    def initialize_riders(self):
        """Initialize riders"""
        riders_data = [
            (1, "Rider John"),
            (2, "Rider Sarah"),
            (3, "Rider Mike"),
            (4, "Rider Emma")
        ]
        
        for rider_id, name in riders_data:
            rider = Rider(rider_id, name)
            self.system.add_rider(rider)
    
    def create_gui(self):
        """Create the main GUI layout"""
        # Main container
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left side: Canvas for graph
        left_frame = tk.Frame(main_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        canvas_label = tk.Label(left_frame, text="City Map", font=("Arial", 14, "bold"))
        canvas_label.pack()
        
        self.canvas = tk.Canvas(left_frame, bg="white", width=700, height=700)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Right side: Controls and Analytics
        right_frame = tk.Frame(main_frame, width=400)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, padx=(10, 0))
        
        # Rider Interface Section
        rider_frame = tk.LabelFrame(right_frame, text="Book a Ride", font=("Arial", 12, "bold"))
        rider_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(rider_frame, text="Select Rider:").pack(anchor=tk.W, padx=5, pady=2)
        rider_combo = ttk.Combobox(rider_frame, textvariable=self.selected_rider, state="readonly")
        rider_combo['values'] = [f"{r.rider_id} - {r.name}" for r in self.system.riders]
        rider_combo.pack(fill=tk.X, padx=5, pady=2)
        
        tk.Label(rider_frame, text="Pickup Location:").pack(anchor=tk.W, padx=5, pady=2)
        pickup_combo = ttk.Combobox(rider_frame, textvariable=self.selected_pickup, state="readonly")
        pickup_combo['values'] = [f"Node {n}" for n in sorted(self.city.get_all_nodes())]
        pickup_combo.pack(fill=tk.X, padx=5, pady=2)
        
        tk.Label(rider_frame, text="Dropoff Location:").pack(anchor=tk.W, padx=5, pady=2)
        dropoff_combo = ttk.Combobox(rider_frame, textvariable=self.selected_dropoff, state="readonly")
        dropoff_combo['values'] = [f"Node {n}" for n in sorted(self.city.get_all_nodes())]
        dropoff_combo.pack(fill=tk.X, padx=5, pady=2)
        
        tk.Button(rider_frame, text="Book Ride", command=self.book_ride, bg="#4CAF50", fg="white", font=("Arial", 10, "bold")).pack(pady=10)
        
        # Active Trips Section
        trips_frame = tk.LabelFrame(right_frame, text="Active Trips", font=("Arial", 12, "bold"))
        trips_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.trips_listbox = tk.Listbox(trips_frame, height=5)
        self.trips_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        trips_buttons_frame = tk.Frame(trips_frame)
        trips_buttons_frame.pack(fill=tk.X, padx=5, pady=5)
        
        tk.Button(trips_buttons_frame, text="Cancel Trip", command=self.cancel_trip, bg="#F44336", fg="white").pack(side=tk.LEFT, padx=2)
        tk.Button(trips_buttons_frame, text="View Progress", command=self.view_trip_progress, bg="#2196F3", fg="white").pack(side=tk.LEFT, padx=2)
        
        # Rollback Section
        rollback_frame = tk.LabelFrame(right_frame, text="Rollback Operations", font=("Arial", 12, "bold"))
        rollback_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(rollback_frame, text="Rollback last K operations:").pack(anchor=tk.W, padx=5, pady=2)
        rollback_entry = tk.Entry(rollback_frame, textvariable=self.rollback_k)
        rollback_entry.pack(fill=tk.X, padx=5, pady=2)
        
        tk.Button(rollback_frame, text="Rollback", command=self.rollback_operations, bg="#FF9800", fg="white", font=("Arial", 10, "bold")).pack(pady=10)
        
        # Analytics Section
        analytics_frame = tk.LabelFrame(right_frame, text="Analytics", font=("Arial", 12, "bold"))
        analytics_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        scrollbar = tk.Scrollbar(analytics_frame)
        self.analytics_text = tk.Text(analytics_frame, height=10, wrap=tk.WORD, yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.analytics_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.analytics_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        tk.Button(analytics_frame, text="Refresh Analytics", command=self.update_analytics, bg="#9C27B0", fg="white").pack(pady=5)
        
        # Draw initial graph
        self.draw_graph()
        self.update_trips_list()
        self.update_analytics()
    
    def draw_graph(self):
        """Draw the city graph on canvas"""
        self.canvas.delete("all")
        
        scale = 0.8
        offset_x = 50
        offset_y = 50
        
        # Draw edges first
        for node in self.city.nodes:
            x1 = node.x * scale + offset_x
            y1 = node.y * scale + offset_y
            
            for edge in node.edges:
                neighbor = self.city.get_node(edge.to_node)
                if neighbor:
                    x2 = neighbor.x * scale + offset_x
                    y2 = neighbor.y * scale + offset_y
                    
                    # Draw edge
                    self.canvas.create_line(x1, y1, x2, y2, fill="gray", width=2)
                    
                    # Draw edge weight (distance)
                    mid_x = (x1 + x2) / 2
                    mid_y = (y1 + y2) / 2
                    self.canvas.create_text(mid_x, mid_y, text=str(edge.weight), fill="black", font=("Arial", 8))
        
        # Draw nodes
        for node in self.city.nodes:
            x = node.x * scale + offset_x
            y = node.y * scale + offset_y
            zone_color = self.city.zone_colors.get(node.zone_id, "#CCCCCC")
            
            # Draw zone background (larger circle)
            self.canvas.create_oval(x - 25, y - 25, x + 25, y + 25, fill=zone_color, outline="black", width=2)
            
            # Draw node number
            self.canvas.create_text(x, y, text=str(node.node_id), fill="white", font=("Arial", 12, "bold"))
        
        # Draw drivers
        for driver in self.system.drivers:
            node = self.city.get_node(driver.current_location_node)
            if node:
                x = node.x * scale + offset_x
                y = node.y * scale + offset_y
                
                # Draw driver icon (triangle)
                driver_color = "green" if driver.available else "red"
                self.canvas.create_polygon(
                    x, y - 15,
                    x - 8, y + 10,
                    x + 8, y + 10,
                    fill=driver_color, outline="black", width=2
                )
                
                # Driver name label
                self.canvas.create_text(x, y + 25, text=driver.name.split()[-1], font=("Arial", 8))
        
        # Update canvas
        self.canvas.update()
    
    def book_ride(self):
        """Book a new ride"""
        if not self.selected_rider.get():
            messagebox.showerror("Error", "Please select a rider")
            return
        
        if not self.selected_pickup.get() or not self.selected_dropoff.get():
            messagebox.showerror("Error", "Please select pickup and dropoff locations")
            return
        
        pickup_node = int(self.selected_pickup.get().split()[-1])
        dropoff_node = int(self.selected_dropoff.get().split()[-1])
        
        if pickup_node == dropoff_node:
            messagebox.showerror("Error", "Pickup and dropoff cannot be the same")
            return
        
        rider_id = int(self.selected_rider.get().split()[0])
        
        # Request trip
        trip_id = self.system.request_trip(rider_id, pickup_node, dropoff_node)
        trip = self.system.get_trip(trip_id)
        
        if trip.driver_id:
            messagebox.showinfo("Success", f"Trip {trip_id} booked!\nDriver assigned: {next((d.name for d in self.system.drivers if d.driver_id == trip.driver_id), 'Unknown')}")
            # Show progress window
            self.view_trip_progress_window(trip_id)
        else:
            messagebox.showwarning("Warning", f"Trip {trip_id} requested but no driver available")
        
        self.update_trips_list()
        self.draw_graph()
        self.update_analytics()
    
    def cancel_trip(self):
        """Cancel selected trip"""
        selection = self.trips_listbox.curselection()
        if not selection:
            messagebox.showerror("Error", "Please select a trip to cancel")
            return
        
        trip_str = self.trips_listbox.get(selection[0])
        trip_id = int(trip_str.split()[1])
        
        if self.cancellation_manager.cancel_trip(self.system, trip_id):
            messagebox.showinfo("Success", f"Trip {trip_id} cancelled")
            # Close progress window if open
            if trip_id in self.progress_windows:
                self.progress_windows[trip_id].window.destroy()
                del self.progress_windows[trip_id]
            # Remove from timers
            self.trip_timers.pop(trip_id, None)
        else:
            messagebox.showerror("Error", "Cannot cancel this trip")
        
        self.update_trips_list()
        self.draw_graph()
        self.update_analytics()
    
    def view_trip_progress(self):
        """View progress of selected trip"""
        selection = self.trips_listbox.curselection()
        if not selection:
            messagebox.showerror("Error", "Please select a trip")
            return
        
        trip_str = self.trips_listbox.get(selection[0])
        trip_id = int(trip_str.split()[1])
        
        self.view_trip_progress_window(trip_id)
    
    def view_trip_progress_window(self, trip_id):
        """Open or update progress window for a trip"""
        if trip_id not in self.progress_windows:
            self.progress_windows[trip_id] = TripProgressWindow(self.root, trip_id, self.system)
        else:
            # Window already exists, just bring to front
            self.progress_windows[trip_id].window.lift()
    
    def rollback_operations(self):
        """Rollback last k operations"""
        try:
            k = int(self.rollback_k.get())
            if k <= 0:
                messagebox.showerror("Error", "K must be positive")
                return
            
            if self.rollback_manager.rollback_last_k(k, self.system.trips, self.system.drivers):
                messagebox.showinfo("Success", f"Rolled back last {k} operations")
                # Close all progress windows
                for window in list(self.progress_windows.values()):
                    window.window.destroy()
                self.progress_windows.clear()
            else:
                messagebox.showerror("Error", f"Cannot rollback {k} operations. Only {self.rollback_manager.get_history_size()} operations in history")
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number")
        
        self.update_trips_list()
        self.draw_graph()
        self.update_analytics()
    
    def update_trips_list(self):
        """Update the active trips listbox"""
        self.trips_listbox.delete(0, tk.END)
        for trip_id, trip in self.system.trips.items():
            driver_name = "None"
            if trip.driver_id:
                driver = next((d for d in self.system.drivers if d.driver_id == trip.driver_id), None)
                if driver:
                    driver_name = driver.name
            
            trip_str = f"Trip {trip_id}: {trip.state} | Driver: {driver_name} | From: Node {trip.pickup_node} To: Node {trip.dropoff_node}"
            self.trips_listbox.insert(tk.END, trip_str)
    
    def update_analytics(self):
        """Update analytics display"""
        analytics = self.system.get_analytics()
        
        self.analytics_text.delete(1.0, tk.END)
        
        text = "=== SYSTEM ANALYTICS ===\n\n"
        text += f"Total Trips: {analytics['total_trips']}\n"
        text += f"Average Trip Distance: {analytics['avg_distance']:.2f} km\n"
        text += f"Completed Trips: {analytics['completed_count']}\n"
        text += f"Cancelled Trips: {analytics['cancelled_count']}\n\n"
        
        text += "=== DRIVER UTILIZATION ===\n"
        for driver_id, stats in analytics['driver_utilization'].items():
            text += f"\n{stats['name']}:\n"
            text += f"  Utilization: {stats['utilization']:.1f}%\n"
            text += f"  Total Trips: {stats['total_trips']}\n"
            text += f"  Completed: {stats['completed_trips']}\n"
        
        text += "\n=== TRIP HISTORY ===\n"
        history = self.system.get_trip_history()
        for trip in history[-10:]:  # Show last 10 trips
            text += f"\nTrip {trip.trip_id}: {trip.state} | Distance: {trip.distance:.1f} km | Cost: ${trip.cost:.2f}\n"
        
        self.analytics_text.insert(1.0, text)
    
    def _transition_to_ongoing(self, trip_id):
        """Helper to transition trip to ongoing"""
        self.system.start_trip(trip_id)
        if trip_id in self.progress_windows:
            self.progress_windows[trip_id].update_progress()
    
    def _transition_to_completed(self, trip_id):
        """Helper to transition trip to completed"""
        self.system.complete_trip(trip_id)
        if trip_id in self.progress_windows:
            self.progress_windows[trip_id].update_progress()
        # Close progress window after completion
        self.root.after(2000, lambda tid=trip_id: self.progress_windows.pop(tid, None) if tid in self.progress_windows else None)
    
    def start_auto_transitions(self):
        """Start automatic state transitions for trips"""
        self.trip_timers = {}  # trip_id -> (state, timestamp)
        
        def auto_transition():
            while True:
                time.sleep(1)  # Check every second
                current_time = time.time()
                
                for trip_id, trip in list(self.system.trips.items()):
                    if trip_id not in self.trip_timers:
                        # Initialize timer for this trip
                        self.trip_timers[trip_id] = (trip.state, current_time)
                    
                    state, timestamp = self.trip_timers[trip_id]
                    
                    if trip.state == TripState.ASSIGNED and state == TripState.ASSIGNED:
                        # Auto transition to ONGOING after 3 seconds
                        if current_time - timestamp >= 3:
                            self.root.after(0, lambda tid=trip_id: self._transition_to_ongoing(tid))
                            self.trip_timers[trip_id] = (TripState.ONGOING, current_time)
                    
                    elif trip.state == TripState.ONGOING and state == TripState.ONGOING:
                        # Auto transition to COMPLETED after 10 seconds
                        if current_time - timestamp >= 10:
                            self.root.after(0, lambda tid=trip_id: self._transition_to_completed(tid))
                            self.trip_timers.pop(trip_id, None)
                    
                    elif trip.state != state:
                        # State changed externally, update timer
                        self.trip_timers[trip_id] = (trip.state, current_time)
                
                # Update GUI periodically
                self.root.after(0, self.update_trips_list)
                self.root.after(0, self.draw_graph)
                self.root.after(0, self.update_analytics)
        
        # Run in separate thread
        thread = threading.Thread(target=auto_transition, daemon=True)
        thread.start()

def main():
    root = tk.Tk()
    app = RideShareGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()

# Ride-Sharing Dispatch & Trip Management System

A Python-based ride-sharing system with Tkinter GUI that simulates a ride-sharing service similar to Uber or Careem.

## Features

- **Zone-Based City Graph**: Visual representation of a city divided into 4 zones with 16 nodes (locations)
- **Driver Management**: 5 pre-defined drivers with default locations, visible on the map
- **Rider Interface**: Book rides by selecting pickup and dropoff locations
- **Trip Lifecycle**: Automatic state transitions (REQUESTED → ASSIGNED → ONGOING → COMPLETED)
- **Trip Cancellation**: Cancel trips in REQUESTED or ASSIGNED states
- **Progress Visualization**: Real-time progress bar showing trip status
- **Rollback System**: Rollback last K operations to restore system state
- **Analytics Dashboard**: 
  - Average trip distance
  - Driver utilization statistics
  - Cancelled vs completed trips
  - Trip history

## Requirements

- Python 3.6 or higher
- tkinter (usually included with Python)

## How to Run

```bash
python main.py
```

Or directly:

```bash
python RideShareGUI.py
```

## Usage

1. **Book a Ride**:
   - Select a rider from the dropdown
   - Choose pickup location (node)
   - Choose dropoff location (node)
   - Click "Book Ride"
   - A progress window will show the trip status

2. **View Trip Progress**:
   - Select a trip from the Active Trips list
   - Click "View Progress" to see detailed status

3. **Cancel a Trip**:
   - Select a trip from the Active Trips list
   - Click "Cancel Trip"

4. **Rollback Operations**:
   - Enter the number of operations to rollback (K)
   - Click "Rollback"

5. **View Analytics**:
   - Analytics are displayed automatically
   - Click "Refresh Analytics" to update

## System Architecture

### Core Components

- **City.py**: Graph representation with zones and nodes
- **Driver.py**: Driver management with location and availability
- **Rider.py**: Rider representation
- **Trip.py**: Trip state machine (REQUESTED → ASSIGNED → ONGOING → COMPLETED/CANCELLED)
- **ShortestPath.py**: Dijkstra's algorithm for shortest path calculation
- **DispatchEngine.py**: Driver assignment logic (prefers same-zone drivers)
- **RollbackManager.py**: Operation history and rollback functionality
- **RideShareSystem.py**: Main system coordinator
- **RideShareGUI.py**: Tkinter GUI implementation

### Pricing

- Base fare: $50
- Cross-zone charge: +20% per zone crossed

### Graph Structure

- 4 zones (color-coded)
- 16 nodes total (4 nodes per zone)
- Weighted edges showing distances
- Drivers shown as triangles (green = available, red = busy)

## State Transitions

Trips automatically transition through states:
- **REQUESTED**: Trip requested, finding driver (3 seconds)
- **ASSIGNED**: Driver assigned, on the way (3 seconds)
- **ONGOING**: Trip in progress (4 seconds)
- **COMPLETED**: Trip completed
- **CANCELLED**: Trip cancelled (can happen from REQUESTED or ASSIGNED)

## Notes

- Drivers move to dropoff location after completing a trip
- Cross-zone trips cost extra (20% per zone)
- System maintains complete trip history for analytics
- All operations can be rolled back

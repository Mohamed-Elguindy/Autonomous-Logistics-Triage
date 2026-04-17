from datetime import datetime, timedelta

# Flat Rate Assumptions
TRUCK_RATE_PER_MILE = 3.50  # USD
TRUCK_AVG_SPEED_MPH = 50.0
PORT_HANDLING_FEE = 500.00  # USD flat fee for rerouting

def calculate_detour_cost(distance_miles: float) -> float:
    """Calculates the financial cost of a trucking detour."""
    return round((distance_miles * TRUCK_RATE_PER_MILE) + PORT_HANDLING_FEE, 2)

def calculate_new_eta(distance_miles: float, start_time: datetime = None) -> datetime:
    """Calculates the new ETA based on trucking distance."""
    if not start_time:
        start_time = datetime.utcnow()
        
    hours_to_add = distance_miles / TRUCK_AVG_SPEED_MPH
    new_eta = start_time + timedelta(hours=hours_to_add)
    return new_eta
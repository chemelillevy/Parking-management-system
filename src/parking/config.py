"""
Configuration constants for the Parking Management System.

ASSUMPTIONS (documented for easy modification):
- Default hourly rates are in KES (Kenyan Shillings)
- Motorcycle: 50 KES per hour
- Car: 100 KES per hour
- Truck: 200 KES per hour
- Vehicles can only park in matching space types
- Time is injectable for testing purposes (clock or explicit now argument)
"""

from src.parking.enums import VehicleType


# Default hourly rates in KES (currency can be changed as needed)
HOURLY_RATES = {
    VehicleType.MOTORCYCLE: 50,
    VehicleType.CAR: 100,
    VehicleType.TRUCK: 200,
}

# Minimum parking duration in hours (for fee calculation)
MINIMUM_DURATION_HOURS = 1

"""
Enumeration classes for the Parking Management System.

Contains all enum definitions for space status, space type, vehicle type,
ticket status, and payment status.
"""

from enum import Enum


class SpaceStatus(Enum):
    """Represents the current status of a parking space."""
    AVAILABLE = "available"
    RESERVED = "reserved"
    OCCUPIED = "occupied"


class SpaceType(Enum):
    """Represents the type of parking space available."""
    MOTORCYCLE = "motorcycle"
    CAR = "car"
    TRUCK = "truck"


class VehicleType(Enum):
    """Represents the type of vehicle."""
    MOTORCYCLE = "motorcycle"
    CAR = "car"
    TRUCK = "truck"


class TicketStatus(Enum):
    """Represents the current status of a parking ticket."""
    ACTIVE = "active"
    PAID = "paid"
    CLOSED = "closed"


class PaymentStatus(Enum):
    """Represents the status of a payment transaction."""
    PENDING = "pending"
    PAID = "paid"
    FAILED = "failed"

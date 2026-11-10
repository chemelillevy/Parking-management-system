"""
Custom exception classes for the Parking Management System.

These exceptions provide clear error handling for specific business scenarios.
"""


class ParkingSystemError(Exception):
    """Base exception for all parking system errors."""
    pass


class LotFullError(ParkingSystemError):
    """Raised when no suitable parking space is available."""
    pass


class InvalidTicketError(ParkingSystemError):
    """Raised when a ticket operation is invalid (e.g., ticket not found or wrong state)."""
    pass


class PaymentError(ParkingSystemError):
    """Raised when a payment operation fails."""
    pass


class VehicleAlreadyParkedError(ParkingSystemError):
    """Raised when attempting to register a vehicle that already has an active ticket."""
    pass

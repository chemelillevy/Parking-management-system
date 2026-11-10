"""
ParkingTicket class for the Parking Management System.

Demonstrates:
- Association: Links to Vehicle, ParkingSpace, ParkingAttendant, and Payment
- Encapsulation: Private attributes with property getters
- Composition relationships (ticket uses but doesn't own these objects)
"""

from datetime import datetime
from typing import Optional, TYPE_CHECKING
from src.parking.enums import TicketStatus
from src.parking.vehicle import Vehicle
from src.parking.parking_space import ParkingSpace
from src.parking.config import MINIMUM_DURATION_HOURS
from src.parking.exceptions import InvalidTicketError

if TYPE_CHECKING:
    from src.parking.attendant import ParkingAttendant
    from src.parking.payment import Payment


class ParkingTicket:
    """
    Represents a single parking visit from entry to exit.

    One ticket = one visit. Holds references to exactly one Vehicle,
    one ParkingSpace, one ParkingAttendant, and at most one Payment.

    Attributes:
        ticket_id: Unique identifier for the ticket
        entry_time: When the vehicle entered the parking lot
        exit_time: When the vehicle exited (None until exit)
        duration: Duration of parking in hours (None until exit)
        hourly_rate: Hourly rate for this vehicle type
        fee: Total fee calculated (None until exit)
        status: Current status of the ticket
    """

    def __init__(
        self,
        ticket_id: str,
        vehicle: Vehicle,
        parking_space: ParkingSpace,
        attendant: "ParkingAttendant",
        entry_time: Optional[datetime] = None,
    ) -> None:
        """
        Initialize a parking ticket.

        Args:
            ticket_id: Unique identifier for the ticket
            vehicle: The vehicle being parked
            parking_space: The assigned parking space
            attendant: The attendant who issued the ticket
            entry_time: When the vehicle entered (defaults to now if not provided)
        """
        self._ticket_id = ticket_id
        self._vehicle = vehicle
        self._parking_space = parking_space
        self._attendant = attendant
        self._entry_time = entry_time if entry_time is not None else datetime.now()
        self._exit_time: Optional[datetime] = None
        self._duration: Optional[float] = None
        self._hourly_rate = vehicle.get_hourly_rate()
        self._fee: Optional[float] = None
        self._status = TicketStatus.ACTIVE
        self._payment: Optional["Payment"] = None

    @property
    def ticket_id(self) -> str:
        """Get the ticket ID."""
        return self._ticket_id

    @property
    def entry_time(self) -> datetime:
        """Get the entry time."""
        return self._entry_time

    @property
    def exit_time(self) -> Optional[datetime]:
        """Get the exit time (None if not exited yet)."""
        return self._exit_time

    @property
    def duration(self) -> Optional[float]:
        """Get the duration in hours (None if not exited yet)."""
        return self._duration

    @property
    def hourly_rate(self) -> int:
        """Get the hourly rate."""
        return self._hourly_rate

    @property
    def fee(self) -> Optional[float]:
        """Get the calculated fee (None if not exited yet)."""
        return self._fee

    @property
    def status(self) -> TicketStatus:
        """Get the ticket status."""
        return self._status

    @property
    def vehicle(self) -> Vehicle:
        """Get the associated vehicle."""
        return self._vehicle

    @property
    def parking_space(self) -> ParkingSpace:
        """Get the associated parking space."""
        return self._parking_space

    @property
    def attendant(self) -> "ParkingAttendant":
        """Get the attendant who issued the ticket."""
        return self._attendant

    @property
    def payment(self) -> Optional["Payment"]:
        """Get the associated payment (None if not paid yet)."""
        return self._payment

    def calculate_duration(self, exit_time: Optional[datetime] = None) -> float:
        """
        Calculate the duration of parking in hours.

        Duration is rounded up to the next full hour with a minimum of 1 hour.

        Args:
            exit_time: The exit time to use (defaults to current time if not provided)

        Returns:
            Duration in hours (rounded up, minimum 1 hour)
        """
        exit = exit_time if exit_time is not None else datetime.now()
        delta = exit - self._entry_time
        hours = delta.total_seconds() / 3600

        # Round up to next full hour with minimum of 1 hour
        billable_hours = max(MINIMUM_DURATION_HOURS, int(hours) + (1 if hours % 1 > 0 else 0))
        return float(billable_hours)

    def calculate_fee(self, exit_time: Optional[datetime] = None) -> float:
        """
        Calculate the parking fee.

        Fee = billable_hours * hourly_rate

        Args:
            exit_time: The exit time to use (defaults to current time if not provided)

        Returns:
            The calculated fee
        """
        duration = self.calculate_duration(exit_time)
        return duration * self._hourly_rate

    def set_payment(self, payment: "Payment") -> None:
        """
        Associate a payment with this ticket.

        A ticket can have at most one payment.

        Args:
            payment: The payment to associate

        Raises:
            ValueError: If a payment is already associated
        """
        if self._payment is not None:
            raise ValueError(f"Ticket {self._ticket_id} already has a payment")
        self._payment = payment

    def close_ticket(self, exit_time: Optional[datetime] = None) -> None:
        """
        Close the ticket when the vehicle exits.

        Sets exit time, finalizes duration and fee, and releases the parking space.

        Args:
            exit_time: The exit time to use (defaults to current time if not provided)

        Raises:
            InvalidTicketError: If ticket is not active
        """
        if not self.is_active():
            raise InvalidTicketError(f"Ticket {self._ticket_id} is not active (status: {self._status})")

        self._exit_time = exit_time if exit_time is not None else datetime.now()
        self._duration = self.calculate_duration(self._exit_time)
        self._fee = self.calculate_fee(self._exit_time)
        self._status = TicketStatus.CLOSED

        # Release the parking space
        self._parking_space.release()

    def is_active(self) -> bool:
        """
        Check if the ticket is currently active.

        Returns:
            True if status is ACTIVE, False otherwise
        """
        return self._status == TicketStatus.ACTIVE

    def __repr__(self) -> str:
        """Return a string representation of the ticket."""
        return (
            f"ParkingTicket(id='{self._ticket_id}', "
            f"vehicle={self._vehicle.plate_number}, "
            f"space={self._parking_space.space_id}, "
            f"status={self._status.value})"
        )

    def __str__(self) -> str:
        """Return a user-friendly string representation."""
        status_str = f" (Fee: {self._fee} KES)" if self._fee is not None else ""
        return f"Ticket {self._ticket_id} for {self._vehicle.plate_number} - {self._status.value}{status_str}"

"""
ParkingAttendant class for the Parking Management System.

Demonstrates:
- Association: Associated with ParkingTicket (1 to 0..*)
- Encapsulation: Private attributes with property getters
"""

from typing import List, Optional, TYPE_CHECKING
from src.parking.vehicle import Vehicle
from src.parking.parking_space import ParkingSpace
from src.parking.parking_lot import ParkingLot
from src.parking.exceptions import VehicleAlreadyParkedError

if TYPE_CHECKING:
    from src.parking.parking_ticket import ParkingTicket
    from src.parking.payment import Payment


class ParkingAttendant:
    """
    Represents a staff member who registers vehicles and issues tickets.

    Attributes:
        attendant_id: Unique identifier for the attendant
        name: Name of the attendant
        phone: Contact phone number
        shift: The shift the attendant works (e.g., "morning", "afternoon", "night")
    """

    def __init__(self, attendant_id: str, name: str, phone: str, shift: str) -> None:
        """
        Initialize a parking attendant.

        Args:
            attendant_id: Unique identifier for the attendant
            name: Name of the attendant
            phone: Contact phone number
            shift: The shift the attendant works
        """
        self._attendant_id = attendant_id
        self._name = name
        self._phone = phone
        self._shift = shift
        self._tickets_issued: List["ParkingTicket"] = []

    @property
    def attendant_id(self) -> str:
        """Get the attendant ID."""
        return self._attendant_id

    @property
    def name(self) -> str:
        """Get the attendant's name."""
        return self._name

    @property
    def phone(self) -> str:
        """Get the attendant's phone number."""
        return self._phone

    @property
    def shift(self) -> str:
        """Get the attendant's shift."""
        return self._shift

    @property
    def tickets_issued(self) -> List["ParkingTicket"]:
        """Get all tickets issued by this attendant."""
        return self._tickets_issued.copy()

    def register_vehicle(
        self,
        vehicle: Vehicle,
        parking_lot: ParkingLot,
        active_tickets: Optional[List["ParkingTicket"]] = None,
    ) -> None:
        """
        Register a vehicle by checking if it already has an active ticket.

        Args:
            vehicle: The vehicle to register
            parking_lot: The parking lot to check against
            active_tickets: Optional list of active tickets to check (defaults to lot's active tickets)

        Raises:
            VehicleAlreadyParkedError: If the vehicle already has an active ticket
        """
        if active_tickets is None:
            active_tickets = self._get_active_tickets_from_lot(parking_lot)

        # Check if vehicle already has an active ticket
        for ticket in active_tickets:
            if ticket.vehicle.plate_number == vehicle.plate_number and ticket.is_active():
                raise VehicleAlreadyParkedError(
                    f"Vehicle {vehicle.plate_number} already has an active ticket ({ticket.ticket_id})"
                )

    def issue_ticket(
        self,
        ticket_id: str,
        vehicle: Vehicle,
        parking_space: ParkingSpace,
        entry_time: Optional[object] = None,
    ) -> "ParkingTicket":
        """
        Issue a parking ticket for a vehicle.

        Args:
            ticket_id: Unique identifier for the ticket
            vehicle: The vehicle being parked
            parking_space: The assigned parking space
            entry_time: The entry time (defaults to now if not provided)

        Returns:
            The created ParkingTicket
        """
        from src.parking.parking_ticket import ParkingTicket

        ticket = ParkingTicket(ticket_id, vehicle, parking_space, self, entry_time)
        self._tickets_issued.append(ticket)
        return ticket

    def verify_payment(self, ticket: "ParkingTicket") -> bool:
        """
        Verify that a ticket has been paid.

        Args:
            ticket: The ticket to verify

        Returns:
            True if payment is PAID, False otherwise
        """
        if ticket.payment is None:
            return False
        return ticket.payment.is_paid()

    def _get_active_tickets_from_lot(self, parking_lot: ParkingLot) -> List["ParkingTicket"]:
        """
        Get all active tickets from the parking lot.

        This is a helper method to find active tickets when not provided.

        Args:
            parking_lot: The parking lot to query

        Returns:
            List of active tickets
        """
        # In a real implementation, the ParkingLot would maintain a list of all tickets
        # For now, we return an empty list as this will be provided by the caller
        return []

    def __repr__(self) -> str:
        """Return a string representation of the attendant."""
        return f"ParkingAttendant(id='{self._attendant_id}', name='{self._name}', shift='{self._shift}')"

    def __str__(self) -> str:
        """Return a user-friendly string representation."""
        return f"{self._name} (ID: {self._attendant_id}, Shift: {self._shift})"

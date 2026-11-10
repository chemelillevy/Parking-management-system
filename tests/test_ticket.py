"""
Tests for ParkingTicket class.
"""

import pytest
from datetime import datetime, timedelta
from src.parking.parking_ticket import ParkingTicket
from src.parking.vehicle import Car
from src.parking.parking_space import ParkingSpace
from src.parking.attendant import ParkingAttendant
from src.parking.payment import CashPayment
from src.parking.enums import SpaceType, TicketStatus
from src.parking.exceptions import InvalidTicketError


class TestParkingTicket:
    """Test cases for ParkingTicket class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.vehicle = Car("ABC123", "John Doe", "555-0100")
        self.space = ParkingSpace("A1", 1, SpaceType.CAR)
        self.attendant = ParkingAttendant("ATT001", "Alice", "555-0200", "morning")

    def test_ticket_initialization(self):
        """Test that a ticket is initialized correctly."""
        ticket = ParkingTicket("TKT001", self.vehicle, self.space, self.attendant)
        assert ticket.ticket_id == "TKT001"
        assert ticket.vehicle == self.vehicle
        assert ticket.parking_space == self.space
        assert ticket.attendant == self.attendant
        assert ticket.status == TicketStatus.ACTIVE
        assert ticket.exit_time is None
        assert ticket.duration is None
        assert ticket.fee is None

    def test_ticket_custom_entry_time(self):
        """Test ticket with custom entry time."""
        custom_time = datetime(2024, 1, 1, 10, 0, 0)
        ticket = ParkingTicket("TKT001", self.vehicle, self.space, self.attendant, custom_time)
        assert ticket.entry_time == custom_time

    def test_calculate_duration_less_than_one_hour(self):
        """Test duration calculation for less than one hour (rounds up to 1)."""
        entry_time = datetime(2024, 1, 1, 10, 0, 0)
        exit_time = datetime(2024, 1, 1, 10, 30, 0)  # 30 minutes
        ticket = ParkingTicket("TKT001", self.vehicle, self.space, self.attendant, entry_time)

        duration = ticket.calculate_duration(exit_time)
        assert duration == 1.0  # Rounds up to minimum 1 hour

    def test_calculate_duration_exact_hour(self):
        """Test duration calculation for exactly one hour."""
        entry_time = datetime(2024, 1, 1, 10, 0, 0)
        exit_time = datetime(2024, 1, 1, 11, 0, 0)  # Exactly 1 hour
        ticket = ParkingTicket("TKT001", self.vehicle, self.space, self.attendant, entry_time)

        duration = ticket.calculate_duration(exit_time)
        assert duration == 1.0

    def test_calculate_duration_one_hour_one_minute(self):
        """Test duration calculation for 1 hour 1 minute (rounds up to 2)."""
        entry_time = datetime(2024, 1, 1, 10, 0, 0)
        exit_time = datetime(2024, 1, 1, 11, 1, 0)  # 1 hour 1 minute
        ticket = ParkingTicket("TKT001", self.vehicle, self.space, self.attendant, entry_time)

        duration = ticket.calculate_duration(exit_time)
        assert duration == 2.0  # Rounds up

    def test_calculate_duration_multiple_hours(self):
        """Test duration calculation for multiple hours."""
        entry_time = datetime(2024, 1, 1, 10, 0, 0)
        exit_time = datetime(2024, 1, 1, 15, 30, 0)  # 5.5 hours
        ticket = ParkingTicket("TKT001", self.vehicle, self.space, self.attendant, entry_time)

        duration = ticket.calculate_duration(exit_time)
        assert duration == 6.0  # Rounds up from 5.5

    def test_calculate_fee(self):
        """Test fee calculation."""
        entry_time = datetime(2024, 1, 1, 10, 0, 0)
        exit_time = datetime(2024, 1, 1, 12, 30, 0)  # 2.5 hours -> 3 billable hours
        ticket = ParkingTicket("TKT001", self.vehicle, self.space, self.attendant, entry_time)

        fee = ticket.calculate_fee(exit_time)
        # Car rate is 100 KES/hour, 3 hours = 300 KES
        assert fee == 300.0

    def test_is_active_true(self):
        """Test is_active returns True for active ticket."""
        ticket = ParkingTicket("TKT001", self.vehicle, self.space, self.attendant)
        assert ticket.is_active() is True

    def test_is_active_false_after_close(self):
        """Test is_active returns False after closing ticket."""
        ticket = ParkingTicket("TKT001", self.vehicle, self.space, self.attendant)
        ticket.close_ticket()
        assert ticket.is_active() is False

    def test_set_payment(self):
        """Test setting a payment on a ticket."""
        ticket = ParkingTicket("TKT001", self.vehicle, self.space, self.attendant)
        payment = CashPayment("PAY001", 100.0, 150.0)

        ticket.set_payment(payment)
        assert ticket.payment == payment

    def test_set_payment_twice_fails(self):
        """Test that setting payment twice raises ValueError."""
        ticket = ParkingTicket("TKT001", self.vehicle, self.space, self.attendant)
        payment1 = CashPayment("PAY001", 100.0, 150.0)
        payment2 = CashPayment("PAY002", 100.0, 150.0)

        ticket.set_payment(payment1)
        with pytest.raises(ValueError):
            ticket.set_payment(payment2)

    def test_close_ticket(self):
        """Test closing a ticket."""
        entry_time = datetime(2024, 1, 1, 10, 0, 0)
        exit_time = datetime(2024, 1, 1, 12, 0, 0)
        ticket = ParkingTicket("TKT001", self.vehicle, self.space, self.attendant, entry_time)

        ticket.close_ticket(exit_time)

        assert ticket.exit_time == exit_time
        assert ticket.status == TicketStatus.CLOSED
        assert ticket.duration is not None
        assert ticket.fee is not None
        assert self.space.is_available()  # Space should be released

    def test_close_ticket_without_exit_time(self):
        """Test closing a ticket without explicit exit time (uses current time)."""
        ticket = ParkingTicket("TKT001", self.vehicle, self.space, self.attendant)
        before_close = datetime.now()

        ticket.close_ticket()

        after_close = datetime.now()
        assert before_close <= ticket.exit_time <= after_close
        assert ticket.status == TicketStatus.CLOSED

    def test_close_already_closed_ticket_fails(self):
        """Test that closing an already closed ticket raises InvalidTicketError."""
        ticket = ParkingTicket("TKT001", self.vehicle, self.space, self.attendant)
        ticket.close_ticket()

        with pytest.raises(InvalidTicketError):
            ticket.close_ticket()

    def test_close_ticket_releases_space(self):
        """Test that closing a ticket releases the parking space."""
        self.space.occupy()
        assert self.space.status != "available"

        ticket = ParkingTicket("TKT001", self.vehicle, self.space, self.attendant)
        ticket.close_ticket()

        assert self.space.is_available()

    def test_ticket_hourly_rate_from_vehicle(self):
        """Test that ticket gets hourly rate from vehicle."""
        ticket = ParkingTicket("TKT001", self.vehicle, self.space, self.attendant)
        assert ticket.hourly_rate == self.vehicle.get_hourly_rate()

    def test_ticket_repr(self):
        """Test ticket string representation."""
        ticket = ParkingTicket("TKT001", self.vehicle, self.space, self.attendant)
        repr_str = repr(ticket)
        assert "TKT001" in repr_str
        assert "ABC123" in repr_str
        assert "A1" in repr_str
        assert "active" in repr_str

    def test_ticket_str(self):
        """Test ticket user-friendly string representation."""
        ticket = ParkingTicket("TKT001", self.vehicle, self.space, self.attendant)
        str_str = str(ticket)
        assert "TKT001" in str_str
        assert "ABC123" in str_str
        assert "active" in str_str

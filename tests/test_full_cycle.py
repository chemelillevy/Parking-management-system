"""
Tests for the full parking cycle integration.
"""

import pytest
from datetime import datetime, timedelta
from src.parking.parking_lot import ParkingLot
from src.parking.parking_space import ParkingSpace
from src.parking.vehicle import Car, Motorcycle, Truck
from src.parking.attendant import ParkingAttendant
from src.parking.parking_ticket import ParkingTicket
from src.parking.payment import CashPayment, CardPayment, MobileMoneyPayment
from src.parking.enums import SpaceType, TicketStatus, PaymentStatus, SpaceStatus
from src.parking.exceptions import LotFullError, VehicleAlreadyParkedError, InvalidTicketError


class TestFullCycle:
    """Test cases for the complete parking cycle."""

    def setup_method(self):
        """Set up test fixtures."""
        self.lot = ParkingLot("LOT001", "Central Parking", "123 Main St")
        self.attendant = ParkingAttendant("ATT001", "Alice", "555-0100", "morning")
        self.active_tickets: list = []

        # Add mixed spaces
        self.lot.add_space(ParkingSpace("M1", 1, SpaceType.MOTORCYCLE))
        self.lot.add_space(ParkingSpace("M2", 1, SpaceType.MOTORCYCLE))
        self.lot.add_space(ParkingSpace("C1", 1, SpaceType.CAR))
        self.lot.add_space(ParkingSpace("C2", 1, SpaceType.CAR))
        self.lot.add_space(ParkingSpace("T1", 1, SpaceType.TRUCK))

    def test_complete_parking_cycle_car_cash(self):
        """Test complete cycle: car parks, pays with cash, exits."""
        # Create vehicle
        car = Car("ABC123", "John Doe", "555-0200")

        # Register vehicle
        self.attendant.register_vehicle(car, self.lot, self.active_tickets)

        # Assign space
        space = self.lot.assign_space(car)
        assert space.space_id == "C1" or space.space_id == "C2"

        # Issue ticket
        entry_time = datetime(2024, 1, 1, 10, 0, 0)
        ticket = self.attendant.issue_ticket("TKT001", car, space, entry_time)
        self.active_tickets.append(ticket)

        assert ticket.is_active()
        assert ticket.status == TicketStatus.ACTIVE

        # Pay with cash
        exit_time = datetime(2024, 1, 1, 12, 30, 0)  # 2.5 hours -> 3 billable hours
        fee = ticket.calculate_fee(exit_time)
        payment = CashPayment("PAY001", fee, fee + 50)  # Tender extra for change
        payment.process_payment()
        ticket.set_payment(payment)

        assert payment.is_paid()
        assert ticket.payment == payment

        # Verify payment
        assert self.attendant.verify_payment(ticket) is True

        # Close ticket (exit)
        ticket.close_ticket(exit_time)

        assert ticket.status == TicketStatus.CLOSED
        assert ticket.exit_time == exit_time
        assert ticket.fee == fee
        assert space.is_available()

    def test_complete_parking_cycle_motorcycle_card(self):
        """Test complete cycle: motorcycle parks, pays with card, exits."""
        motorcycle = Motorcycle("XYZ789", "Jane Smith", "555-0300")

        self.attendant.register_vehicle(motorcycle, self.lot, self.active_tickets)
        space = self.lot.assign_space(motorcycle)
        assert space.space_type == SpaceType.MOTORCYCLE

        entry_time = datetime(2024, 1, 1, 14, 0, 0)
        ticket = self.attendant.issue_ticket("TKT002", motorcycle, space, entry_time)
        self.active_tickets.append(ticket)

        exit_time = datetime(2024, 1, 1, 15, 15, 0)  # 1.25 hours -> 2 billable hours
        fee = ticket.calculate_fee(exit_time)
        payment = CardPayment("PAY002", fee, "1234")
        payment.process_payment()
        ticket.set_payment(payment)

        assert self.attendant.verify_payment(ticket) is True
        ticket.close_ticket(exit_time)

        assert ticket.status == TicketStatus.CLOSED
        assert space.is_available()

    def test_complete_parking_cycle_truck_mobile_money(self):
        """Test complete cycle: truck parks, pays with mobile money, exits."""
        truck = Truck("TRK456", "Bob Johnson", "555-0400")

        self.attendant.register_vehicle(truck, self.lot, self.active_tickets)
        space = self.lot.assign_space(truck)
        assert space.space_type == SpaceType.TRUCK

        entry_time = datetime(2024, 1, 1, 8, 0, 0)
        ticket = self.attendant.issue_ticket("TKT003", truck, space, entry_time)
        self.active_tickets.append(ticket)

        exit_time = datetime(2024, 1, 1, 9, 45, 0)  # 1.75 hours -> 2 billable hours
        fee = ticket.calculate_fee(exit_time)
        payment = MobileMoneyPayment("PAY003", fee, "555-0500", "TXN12345")
        payment.process_payment()
        ticket.set_payment(payment)

        assert self.attendant.verify_payment(ticket) is True
        ticket.close_ticket(exit_time)

        assert ticket.status == TicketStatus.CLOSED
        assert space.is_available()

    def test_exit_before_payment_fails(self):
        """Test that exiting before payment is detected by verify_payment."""
        car = Car("ABC123", "John Doe", "555-0200")

        self.attendant.register_vehicle(car, self.lot, self.active_tickets)
        space = self.lot.assign_space(car)
        ticket = self.attendant.issue_ticket("TKT004", car, space)
        self.active_tickets.append(ticket)

        # Verify payment check fails when no payment
        assert self.attendant.verify_payment(ticket) is False

        # The attendant should not allow exit without payment verification
        # This is enforced at the business logic level, not in close_ticket

    def test_vehicle_already_parked_rejected(self):
        """Test that a vehicle with an active ticket cannot register again."""
        car = Car("ABC123", "John Doe", "555-0200")

        self.attendant.register_vehicle(car, self.lot, self.active_tickets)
        space = self.lot.assign_space(car)
        ticket = self.attendant.issue_ticket("TKT005", car, space)
        self.active_tickets.append(ticket)

        # Try to register the same vehicle again
        with pytest.raises(VehicleAlreadyParkedError):
            self.attendant.register_vehicle(car, self.lot, self.active_tickets)

    def test_lot_full_behavior(self):
        """Test behavior when lot is full for a vehicle type."""
        # Occupy all motorcycle spaces
        space1 = self.lot.get_available_spaces(SpaceType.MOTORCYCLE)[0]
        space1.occupy()
        space2 = self.lot.get_available_spaces(SpaceType.MOTORCYCLE)[0]
        space2.occupy()

        # Try to assign space to another motorcycle
        motorcycle = Motorcycle("MOT999", "Test User", "555-9999")
        with pytest.raises(LotFullError):
            self.lot.assign_space(motorcycle)

    def test_fee_rounding_boundaries(self):
        """Test fee calculation at various time boundaries."""
        car = Car("ABC123", "John Doe", "555-0200")

        self.attendant.register_vehicle(car, self.lot, self.active_tickets)
        space = self.lot.assign_space(car)

        # Test exactly 1 hour
        entry = datetime(2024, 1, 1, 10, 0, 0)
        exit_1hr = datetime(2024, 1, 1, 11, 0, 0)
        ticket1 = self.attendant.issue_ticket("TKT006", car, space, entry)
        fee1 = ticket1.calculate_fee(exit_1hr)
        assert fee1 == 100.0  # 1 hour * 100 KES

        # Test 1 hour 1 second -> 2 hours
        exit_1hr1sec = datetime(2024, 1, 1, 11, 0, 1)
        ticket2 = self.attendant.issue_ticket("TKT007", car, space, entry)
        fee2 = ticket2.calculate_fee(exit_1hr1sec)
        assert fee2 == 200.0  # 2 hours * 100 KES

        # Test 30 minutes -> 1 hour minimum
        exit_30min = datetime(2024, 1, 1, 10, 30, 0)
        ticket3 = self.attendant.issue_ticket("TKT008", car, space, entry)
        fee3 = ticket3.calculate_fee(exit_30min)
        assert fee3 == 100.0  # 1 hour minimum * 100 KES

    def test_payment_multiplicity_0_to_1(self):
        """Test that a ticket can have at most one payment (0..1 relationship)."""
        car = Car("ABC123", "John Doe", "555-0200")

        self.attendant.register_vehicle(car, self.lot, self.active_tickets)
        space = self.lot.assign_space(car)
        ticket = self.attendant.issue_ticket("TKT009", car, space)
        self.active_tickets.append(ticket)

        # Initially no payment
        assert ticket.payment is None

        # Add one payment
        payment1 = CashPayment("PAY001", 100.0, 150.0)
        ticket.set_payment(payment1)
        assert ticket.payment == payment1

        # Try to add second payment - should fail
        payment2 = CardPayment("PAY002", 100.0, "1234")
        with pytest.raises(ValueError):
            ticket.set_payment(payment2)

    def test_multiple_vehicles_in_lot(self):
        """Test multiple vehicles parking simultaneously."""
        car1 = Car("ABC123", "John Doe", "555-0200")
        car2 = Car("DEF456", "Jane Smith", "555-0300")
        motorcycle = Motorcycle("MOT789", "Bob Wilson", "555-0400")

        # Register and park all vehicles
        for vehicle in [car1, car2, motorcycle]:
            self.attendant.register_vehicle(vehicle, self.lot, self.active_tickets)
            space = self.lot.assign_space(vehicle)
            ticket = self.attendant.issue_ticket(f"TKT_{vehicle.plate_number}", vehicle, space)
            self.active_tickets.append(ticket)

        # All should be active
        assert all(t.is_active() for t in self.active_tickets)

        # Check availability
        report = self.lot.generate_report()
        assert report["occupied"] == 3
        assert report["available"] == 2  # 5 total - 3 occupied

    def test_space_released_after_exit(self):
        """Test that space is released and becomes available after exit."""
        car = Car("ABC123", "John Doe", "555-0200")

        self.attendant.register_vehicle(car, self.lot, self.active_tickets)
        space = self.lot.assign_space(car)
        assert space.status == SpaceStatus.OCCUPIED

        ticket = self.attendant.issue_ticket("TKT010", car, space)
        self.active_tickets.append(ticket)

        # Pay and exit
        payment = CashPayment("PAY001", 100.0, 150.0)
        payment.process_payment()
        ticket.set_payment(payment)
        ticket.close_ticket()

        # Space should be available again
        assert space.is_available()

        # Should be able to assign same space to another vehicle
        car2 = Car("DEF456", "Jane Smith", "555-0300")
        self.attendant.register_vehicle(car2, self.lot, self.active_tickets)
        space2 = self.lot.assign_space(car2)
        assert space2.space_id == space.space_id

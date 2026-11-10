"""
Scripted walkthrough of the Parking Management System.

This demo creates a parking lot with 2 levels and mixed space types,
parks a car, motorcycle, and truck, shows availability reports,
processes payments with all three payment methods, exits vehicles,
and prints the final report.

Uses an injected clock to simulate elapsed time for testing.
"""

from datetime import datetime, timedelta
from src.parking.parking_lot import ParkingLot
from src.parking.parking_space import ParkingSpace
from src.parking.vehicle import Car, Motorcycle, Truck
from src.parking.attendant import ParkingAttendant
from src.parking.payment import CashPayment, CardPayment, MobileMoneyPayment
from src.parking.enums import SpaceType


def print_separator(char="=", length=60):
    """Print a separator line."""
    print(char * length)


def print_report(lot: ParkingLot):
    """Print a formatted availability report."""
    report = lot.generate_report()
    print(f"\n{'=' * 60}")
    print(f"PARKING LOT REPORT: {report['name']}")
    print(f"{'=' * 60}")
    print(f"Location: {report['location']}")
    print(f"Total Capacity: {report['total_capacity']}")
    print(f"Occupied: {report['occupied']}")
    print(f"Available: {report['available']}")
    print(f"\nPer-Level Breakdown:")
    for level, data in report['per_level_breakdown'].items():
        print(f"  Level {level}: Total={data['total']}, Occupied={data['occupied']}, Available={data['available']}")
    print(f"\nPer-Type Breakdown:")
    for space_type, data in report['per_type_breakdown'].items():
        print(f"  {space_type.capitalize()}: Total={data['total']}, Occupied={data['occupied']}, Available={data['available']}")
    print(f"{'=' * 60}\n")


def main():
    """Run the scripted demo."""
    print_separator()
    print("PARKING MANAGEMENT SYSTEM - DEMO")
    print_separator()

    # Create parking lot
    print("\n1. Creating parking lot...")
    lot = ParkingLot("LOT001", "Central Parking", "123 Main Street")
    print(f"   Created: {lot}")

    # Add spaces on 2 levels
    print("\n2. Adding parking spaces...")
    # Level 1
    lot.add_space(ParkingSpace("M1", 1, SpaceType.MOTORCYCLE))
    lot.add_space(ParkingSpace("M2", 1, SpaceType.MOTORCYCLE))
    lot.add_space(ParkingSpace("C1", 1, SpaceType.CAR))
    lot.add_space(ParkingSpace("C2", 1, SpaceType.CAR))
    lot.add_space(ParkingSpace("T1", 1, SpaceType.TRUCK))
    # Level 2
    lot.add_space(ParkingSpace("M3", 2, SpaceType.MOTORCYCLE))
    lot.add_space(ParkingSpace("C3", 2, SpaceType.CAR))
    lot.add_space(ParkingSpace("C4", 2, SpaceType.CAR))
    lot.add_space(ParkingSpace("T2", 2, SpaceType.TRUCK))

    print(f"   Added {lot.total_capacity} spaces across 2 levels")

    # Create attendant
    print("\n3. Creating parking attendant...")
    attendant = ParkingAttendant("ATT001", "Alice Johnson", "555-0100", "morning")
    print(f"   Created: {attendant}")

    # Track active tickets
    active_tickets = []

    # Injected clock for testing
    base_time = datetime(2024, 1, 1, 10, 0, 0)
    current_time = base_time

    # Park a car
    print("\n4. Parking a car...")
    car = Car("ABC123", "John Doe", "555-0200")
    print(f"   Vehicle: {car}")

    attendant.register_vehicle(car, lot, active_tickets)
    car_space = lot.assign_space(car)
    print(f"   Assigned space: {car_space}")

    current_time += timedelta(minutes=5)
    car_ticket = attendant.issue_ticket("TKT001", car, car_space, current_time)
    active_tickets.append(car_ticket)
    print(f"   Issued ticket: {car_ticket}")

    # Park a motorcycle
    print("\n5. Parking a motorcycle...")
    motorcycle = Motorcycle("XYZ789", "Jane Smith", "555-0300")
    print(f"   Vehicle: {motorcycle}")

    attendant.register_vehicle(motorcycle, lot, active_tickets)
    moto_space = lot.assign_space(motorcycle)
    print(f"   Assigned space: {moto_space}")

    current_time += timedelta(minutes=5)
    moto_ticket = attendant.issue_ticket("TKT002", motorcycle, moto_space, current_time)
    active_tickets.append(moto_ticket)
    print(f"   Issued ticket: {moto_ticket}")

    # Park a truck
    print("\n6. Parking a truck...")
    truck = Truck("TRK456", "Bob Wilson", "555-0400")
    print(f"   Vehicle: {truck}")

    attendant.register_vehicle(truck, lot, active_tickets)
    truck_space = lot.assign_space(truck)
    print(f"   Assigned space: {truck_space}")

    current_time += timedelta(minutes=5)
    truck_ticket = attendant.issue_ticket("TKT003", truck, truck_space, current_time)
    active_tickets.append(truck_ticket)
    print(f"   Issued ticket: {truck_ticket}")

    # Show availability report
    print("\n7. Current availability report...")
    print_report(lot)

    # Simulate time passing (2 hours)
    print("\n8. Simulating 2 hours of parking...")
    current_time += timedelta(hours=2)
    print(f"   Current time: {current_time}")

    # Process payments
    print("\n9. Processing payments...")

    # Car pays with cash
    print("\n   a) Car payment (CASH):")
    car_fee = car_ticket.calculate_fee(current_time)
    print(f"      Fee: {car_fee} KES")
    car_payment = CashPayment("PAY001", car_fee, car_fee + 50)
    car_payment.process_payment()
    car_ticket.set_payment(car_payment)
    print(f"      Payment: {car_payment}")
    print(f"      Change: {car_payment.change} KES")
    receipt = car_payment.generate_receipt()
    print(f"      Receipt: {receipt}")

    # Motorcycle pays with card
    print("\n   b) Motorcycle payment (CARD):")
    moto_fee = moto_ticket.calculate_fee(current_time)
    print(f"      Fee: {moto_fee} KES")
    moto_payment = CardPayment("PAY002", moto_fee, "4242")
    moto_payment.process_payment()
    moto_ticket.set_payment(moto_payment)
    print(f"      Payment: {moto_payment}")
    receipt = moto_payment.generate_receipt()
    print(f"      Receipt: {receipt}")

    # Truck pays with mobile money
    print("\n   c) Truck payment (MOBILE MONEY):")
    truck_fee = truck_ticket.calculate_fee(current_time)
    print(f"      Fee: {truck_fee} KES")
    truck_payment = MobileMoneyPayment("PAY003", truck_fee, "555-0500", "TXN12345")
    truck_payment.process_payment()
    truck_ticket.set_payment(truck_payment)
    print(f"      Payment: {truck_payment}")
    receipt = truck_payment.generate_receipt()
    print(f"      Receipt: {receipt}")

    # Verify payments
    print("\n10. Verifying payments...")
    print(f"     Car payment verified: {attendant.verify_payment(car_ticket)}")
    print(f"     Motorcycle payment verified: {attendant.verify_payment(moto_ticket)}")
    print(f"     Truck payment verified: {attendant.verify_payment(truck_ticket)}")

    # Exit vehicles
    print("\n11. Exiting vehicles...")

    print("\n   a) Car exit:")
    car_ticket.close_ticket(current_time)
    print(f"      Ticket closed: {car_ticket}")
    print(f"      Duration: {car_ticket.duration} hours")
    print(f"      Final fee: {car_ticket.fee} KES")
    print(f"      Space released: {car_space.is_available()}")

    current_time += timedelta(minutes=5)

    print("\n   b) Motorcycle exit:")
    moto_ticket.close_ticket(current_time)
    print(f"      Ticket closed: {moto_ticket}")
    print(f"      Duration: {moto_ticket.duration} hours")
    print(f"      Final fee: {moto_ticket.fee} KES")
    print(f"      Space released: {moto_space.is_available()}")

    current_time += timedelta(minutes=5)

    print("\n   c) Truck exit:")
    truck_ticket.close_ticket(current_time)
    print(f"      Ticket closed: {truck_ticket}")
    print(f"      Duration: {truck_ticket.duration} hours")
    print(f"      Final fee: {truck_ticket.fee} KES")
    print(f"      Space released: {truck_space.is_available()}")

    # Final report
    print("\n12. Final availability report...")
    print_report(lot)

    print("\n" + "=" * 60)
    print("DEMO COMPLETED SUCCESSFULLY")
    print("=" * 60)


if __name__ == "__main__":
    main()

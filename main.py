"""
Interactive CLI demo for the Parking Management System.

This provides a menu-driven interface to:
- Register a vehicle and issue a ticket
- Process payment and exit
- View availability report
- List active tickets
- Quit
"""

from datetime import datetime
from typing import List, Optional
from src.parking.parking_lot import ParkingLot
from src.parking.parking_space import ParkingSpace
from src.parking.vehicle import Car, Motorcycle, Truck
from src.parking.attendant import ParkingAttendant
from src.parking.payment import CashPayment, CardPayment, MobileMoneyPayment
from src.parking.enums import SpaceType, VehicleType
from src.parking.exceptions import LotFullError, VehicleAlreadyParkedError, InvalidTicketError


class ParkingSystemCLI:
    """Interactive CLI for the Parking Management System."""

    def __init__(self):
        """Initialize the CLI with a parking lot and attendant."""
        self.lot = ParkingLot("LOT001", "Central Parking", "123 Main Street")
        self.attendant = ParkingAttendant("ATT001", "Alice Johnson", "555-0100", "morning")
        self.active_tickets: List = []
        self._setup_lot()

    def _setup_lot(self):
        """Set up the parking lot with initial spaces."""
        # Add spaces on 2 levels
        spaces = [
            ParkingSpace("M1", 1, SpaceType.MOTORCYCLE),
            ParkingSpace("M2", 1, SpaceType.MOTORCYCLE),
            ParkingSpace("C1", 1, SpaceType.CAR),
            ParkingSpace("C2", 1, SpaceType.CAR),
            ParkingSpace("T1", 1, SpaceType.TRUCK),
            ParkingSpace("M3", 2, SpaceType.MOTORCYCLE),
            ParkingSpace("C3", 2, SpaceType.CAR),
            ParkingSpace("C4", 2, SpaceType.CAR),
            ParkingSpace("T2", 2, SpaceType.TRUCK),
        ]
        for space in spaces:
            self.lot.add_space(space)

    def print_menu(self):
        """Print the main menu."""
        print("\n" + "=" * 50)
        print("PARKING MANAGEMENT SYSTEM")
        print("=" * 50)
        print("1. Register vehicle and issue ticket")
        print("2. Process payment and exit")
        print("3. View availability report")
        print("4. List active tickets")
        print("5. Quit")
        print("=" * 50)

    def get_input(self, prompt: str) -> str:
        """Get user input with validation."""
        try:
            return input(prompt).strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting...")
            return "5"

    def register_vehicle(self):
        """Register a vehicle and issue a ticket."""
        print("\n--- Register Vehicle ---")

        # Get vehicle type
        print("\nVehicle types:")
        print("1. Motorcycle")
        print("2. Car")
        print("3. Truck")
        type_choice = self.get_input("Select vehicle type (1-3): ")

        vehicle_map = {
            "1": ("Motorcycle", Motorcycle, VehicleType.MOTORCYCLE),
            "2": ("Car", Car, VehicleType.CAR),
            "3": ("Truck", Truck, VehicleType.TRUCK),
        }

        if type_choice not in vehicle_map:
            print("Invalid choice!")
            return

        type_name, vehicle_class, _ = vehicle_map[type_choice]

        # Get vehicle details
        plate = self.get_input(f"Enter {type_name.lower()} plate number: ")
        if not plate:
            print("Plate number is required!")
            return

        owner = self.get_input("Enter owner name: ")
        if not owner:
            print("Owner name is required!")
            return

        phone = self.get_input("Enter owner phone: ")
        if not phone:
            print("Owner phone is required!")
            return

        # Create vehicle
        vehicle = vehicle_class(plate, owner, phone)

        try:
            # Register vehicle
            self.attendant.register_vehicle(vehicle, self.lot, self.active_tickets)

            # Assign space
            space = self.lot.assign_space(vehicle)
            print(f"\nAssigned space: {space}")

            # Issue ticket
            ticket_id = f"TKT{len(self.active_tickets) + 1:03d}"
            ticket = self.attendant.issue_ticket(ticket_id, vehicle, space)
            self.active_tickets.append(ticket)

            print(f"Issued ticket: {ticket}")
            print(f"Entry time: {ticket.entry_time.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"Hourly rate: {ticket.hourly_rate} KES")

        except VehicleAlreadyParkedError as e:
            print(f"\nError: {e}")
        except LotFullError as e:
            print(f"\nError: {e}")

    def process_payment_and_exit(self):
        """Process payment and exit a vehicle."""
        print("\n--- Process Payment and Exit ---")

        if not self.active_tickets:
            print("No active tickets available!")
            return

        # List active tickets
        print("\nActive tickets:")
        for i, ticket in enumerate(self.active_tickets, 1):
            if ticket.is_active():
                print(f"{i}. {ticket} - {ticket.vehicle}")

        choice = self.get_input("\nSelect ticket number (or 0 to cancel): ")

        try:
            choice_idx = int(choice) - 1
            if choice_idx < 0 or choice_idx >= len(self.active_tickets):
                print("Invalid choice!")
                return

            ticket = self.active_tickets[choice_idx]
            if not ticket.is_active():
                print("Ticket is not active!")
                return

        except ValueError:
            print("Invalid input!")
            return

        # Calculate fee
        exit_time = datetime.now()
        fee = ticket.calculate_fee(exit_time)
        print(f"\nFee: {fee} KES")

        # Get payment method
        print("\nPayment methods:")
        print("1. Cash")
        print("2. Card")
        print("3. Mobile Money")
        payment_choice = self.get_input("Select payment method (1-3): ")

        try:
            payment = None

            if payment_choice == "1":
                # Cash payment
                tendered_str = self.get_input(f"Enter amount tendered (KES): ")
                tendered = float(tendered_str)
                payment = CashPayment(f"PAY{len(self.active_tickets)}", fee, tendered)

            elif payment_choice == "2":
                # Card payment
                last_four = self.get_input("Enter card last 4 digits: ")
                if len(last_four) != 4 or not last_four.isdigit():
                    print("Invalid card number!")
                    return
                payment = CardPayment(f"PAY{len(self.active_tickets)}", fee, last_four)

            elif payment_choice == "3":
                # Mobile money payment
                phone = self.get_input("Enter phone number: ")
                if not phone:
                    print("Phone number is required!")
                    return
                ref = self.get_input("Enter transaction reference: ")
                if not ref:
                    print("Transaction reference is required!")
                    return
                payment = MobileMoneyPayment(f"PAY{len(self.active_tickets)}", fee, phone, ref)

            else:
                print("Invalid payment method!")
                return

            # Process payment
            payment.process_payment()
            ticket.set_payment(payment)

            print(f"\nPayment processed: {payment}")
            receipt = payment.generate_receipt()
            print(f"Receipt: {receipt}")

            # Verify payment
            if self.attendant.verify_payment(ticket):
                print("Payment verified successfully!")

                # Close ticket
                ticket.close_ticket(exit_time)
                print(f"\nTicket closed: {ticket}")
                print(f"Duration: {ticket.duration} hours")
                print(f"Final fee: {ticket.fee} KES")
                print(f"Exit time: {ticket.exit_time.strftime('%Y-%m-%d %H:%M:%S')}")
            else:
                print("Payment verification failed!")

        except ValueError as e:
            print(f"\nError: {e}")
        except Exception as e:
            print(f"\nError: {e}")

    def view_availability_report(self):
        """View the parking lot availability report."""
        print("\n--- Availability Report ---")
        report = self.lot.generate_report()

        print(f"\nLot: {report['name']}")
        print(f"Location: {report['location']}")
        print(f"Total Capacity: {report['total_capacity']}")
        print(f"Occupied: {report['occupied']}")
        print(f"Available: {report['available']}")

        print("\nPer-Level Breakdown:")
        for level, data in report['per_level_breakdown'].items():
            print(f"  Level {level}: Total={data['total']}, Occupied={data['occupied']}, Available={data['available']}")

        print("\nPer-Type Breakdown:")
        for space_type, data in report['per_type_breakdown'].items():
            print(f"  {space_type.capitalize()}: Total={data['total']}, Occupied={data['occupied']}, Available={data['available']}")

    def list_active_tickets(self):
        """List all active tickets."""
        print("\n--- Active Tickets ---")

        active = [t for t in self.active_tickets if t.is_active()]

        if not active:
            print("No active tickets.")
            return

        for ticket in active:
            print(f"\n{ticket}")
            print(f"  Vehicle: {ticket.vehicle}")
            print(f"  Space: {ticket.parking_space}")
            print(f"  Entry: {ticket.entry_time.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"  Hourly Rate: {ticket.hourly_rate} KES")

    def run(self):
        """Run the main CLI loop."""
        print("Welcome to the Parking Management System!")
        print(f"Lot: {self.lot.name}")
        print(f"Attendant: {self.attendant.name}")

        while True:
            self.print_menu()
            choice = self.get_input("Enter your choice (1-5): ")

            if choice == "1":
                self.register_vehicle()
            elif choice == "2":
                self.process_payment_and_exit()
            elif choice == "3":
                self.view_availability_report()
            elif choice == "4":
                self.list_active_tickets()
            elif choice == "5":
                print("\nThank you for using the Parking Management System!")
                print(f"Final capacity: {self.lot.total_capacity} spaces")
                report = self.lot.generate_report()
                print(f"Active tickets: {report['occupied']}")
                break
            else:
                print("Invalid choice! Please try again.")


def main():
    """Main entry point."""
    cli = ParkingSystemCLI()
    cli.run()


if __name__ == "__main__":
    main()

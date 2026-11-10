"""
Vehicle classes for the Parking Management System.

Demonstrates:
- Abstraction: Vehicle is an abstract base class
- Inheritance: Car, Motorcycle, Truck inherit from Vehicle
- Polymorphism: Each subclass sets its own vehicle_type and hourly rate
- Encapsulation: Private attributes with property getters
"""

from abc import ABC, abstractmethod
from typing import Dict, Any
from src.parking.enums import VehicleType
from src.parking.config import HOURLY_RATES


class Vehicle(ABC):
    """
    Abstract base class representing a vehicle in the parking system.

    Attributes:
        plate_number: Unique identifier for the vehicle
        vehicle_type: Type of vehicle (motorcycle, car, or truck)
        owner_name: Name of the vehicle owner
        owner_phone: Contact phone number of the owner
    """

    def __init__(self, plate_number: str, owner_name: str, owner_phone: str) -> None:
        """
        Initialize a vehicle.

        Args:
            plate_number: Unique plate number for the vehicle
            owner_name: Name of the vehicle owner
            owner_phone: Contact phone number of the owner
        """
        self._plate_number = plate_number
        self._vehicle_type = self._get_vehicle_type()
        self._owner_name = owner_name
        self._owner_phone = owner_phone

    @abstractmethod
    def _get_vehicle_type(self) -> VehicleType:
        """
        Return the vehicle type for this subclass.

        Each subclass must implement this to define its type.
        """
        pass

    @property
    def plate_number(self) -> str:
        """Get the vehicle's plate number."""
        return self._plate_number

    @property
    def vehicle_type(self) -> VehicleType:
        """Get the vehicle's type."""
        return self._vehicle_type

    @property
    def owner_name(self) -> str:
        """Get the owner's name."""
        return self._owner_name

    @property
    def owner_phone(self) -> str:
        """Get the owner's phone number."""
        return self._owner_phone

    def get_plate_number(self) -> str:
        """Return the vehicle's plate number."""
        return self._plate_number

    def get_vehicle_type(self) -> VehicleType:
        """Return the vehicle's type."""
        return self._vehicle_type

    def get_owner_details(self) -> Dict[str, str]:
        """
        Return the owner's details as a dictionary.

        Returns:
            Dictionary containing owner_name and owner_phone
        """
        return {
            "owner_name": self._owner_name,
            "owner_phone": self._owner_phone,
        }

    def get_hourly_rate(self) -> int:
        """
        Return the hourly rate for this vehicle type.

        Uses the configuration to get the rate based on vehicle type.
        """
        return HOURLY_RATES[self._vehicle_type]

    def __repr__(self) -> str:
        """Return a string representation of the vehicle."""
        return f"{self.__class__.__name__}(plate='{self._plate_number}', type={self._vehicle_type.value})"

    def __str__(self) -> str:
        """Return a user-friendly string representation."""
        return f"{self._vehicle_type.value.capitalize()} {self._plate_number} (Owner: {self._owner_name})"


class Car(Vehicle):
    """Represents a car vehicle type."""

    def _get_vehicle_type(self) -> VehicleType:
        """Return VehicleType.CAR."""
        return VehicleType.CAR


class Motorcycle(Vehicle):
    """Represents a motorcycle vehicle type."""

    def _get_vehicle_type(self) -> VehicleType:
        """Return VehicleType.MOTORCYCLE."""
        return VehicleType.MOTORCYCLE


class Truck(Vehicle):
    """Represents a truck vehicle type."""

    def _get_vehicle_type(self) -> VehicleType:
        """Return VehicleType.TRUCK."""
        return VehicleType.TRUCK

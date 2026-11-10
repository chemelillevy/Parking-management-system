"""
Tests for Vehicle classes.
"""

import pytest
from src.parking.vehicle import Vehicle, Car, Motorcycle, Truck
from src.parking.enums import VehicleType
from src.parking.config import HOURLY_RATES


class TestVehicle:
    """Test cases for Vehicle ABC and its subclasses."""

    def test_car_vehicle_type(self):
        """Test that Car has the correct vehicle type."""
        car = Car("ABC123", "John Doe", "555-0100")
        assert car.get_vehicle_type() == VehicleType.CAR
        assert car.vehicle_type == VehicleType.CAR

    def test_motorcycle_vehicle_type(self):
        """Test that Motorcycle has the correct vehicle type."""
        motorcycle = Motorcycle("XYZ789", "Jane Smith", "555-0200")
        assert motorcycle.get_vehicle_type() == VehicleType.MOTORCYCLE
        assert motorcycle.vehicle_type == VehicleType.MOTORCYCLE

    def test_truck_vehicle_type(self):
        """Test that Truck has the correct vehicle type."""
        truck = Truck("TRK456", "Bob Johnson", "555-0300")
        assert truck.get_vehicle_type() == VehicleType.TRUCK
        assert truck.vehicle_type == VehicleType.TRUCK

    def test_vehicle_plate_number(self):
        """Test getting plate number."""
        car = Car("ABC123", "John Doe", "555-0100")
        assert car.get_plate_number() == "ABC123"
        assert car.plate_number == "ABC123"

    def test_vehicle_owner_details(self):
        """Test getting owner details."""
        car = Car("ABC123", "John Doe", "555-0100")
        details = car.get_owner_details()
        assert details["owner_name"] == "John Doe"
        assert details["owner_phone"] == "555-0100"

    def test_vehicle_hourly_rate(self):
        """Test that each vehicle type has the correct hourly rate."""
        car = Car("ABC123", "John Doe", "555-0100")
        motorcycle = Motorcycle("XYZ789", "Jane Smith", "555-0200")
        truck = Truck("TRK456", "Bob Johnson", "555-0300")

        assert car.get_hourly_rate() == HOURLY_RATES[VehicleType.CAR]
        assert motorcycle.get_hourly_rate() == HOURLY_RATES[VehicleType.MOTORCYCLE]
        assert truck.get_hourly_rate() == HOURLY_RATES[VehicleType.TRUCK]

    def test_vehicle_cannot_be_instantiated_directly(self):
        """Test that Vehicle ABC cannot be instantiated directly."""
        with pytest.raises(TypeError):
            Vehicle("ABC123", "John Doe", "555-0100")

    def test_vehicle_repr(self):
        """Test vehicle string representation."""
        car = Car("ABC123", "John Doe", "555-0100")
        repr_str = repr(car)
        assert "Car" in repr_str
        assert "ABC123" in repr_str
        assert "car" in repr_str

    def test_vehicle_str(self):
        """Test vehicle user-friendly string representation."""
        car = Car("ABC123", "John Doe", "555-0100")
        str_str = str(car)
        assert "ABC123" in str_str
        assert "John Doe" in str_str
        assert "Car" in str_str

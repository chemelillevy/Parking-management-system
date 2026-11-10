"""
Tests for ParkingLot class.
"""

import pytest
from src.parking.parking_lot import ParkingLot
from src.parking.parking_space import ParkingSpace
from src.parking.vehicle import Car, Motorcycle, Truck
from src.parking.enums import SpaceType, SpaceStatus
from src.parking.exceptions import LotFullError


class TestParkingLot:
    """Test cases for ParkingLot class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.lot = ParkingLot("LOT001", "Central Parking", "123 Main St")

    def test_lot_initialization(self):
        """Test that a parking lot is initialized correctly."""
        assert self.lot.lot_id == "LOT001"
        assert self.lot.name == "Central Parking"
        assert self.lot.location == "123 Main St"
        assert self.lot.total_capacity == 0
        assert len(self.lot.spaces) == 0

    def test_add_space(self):
        """Test adding a parking space to the lot."""
        space = ParkingSpace("A1", 1, SpaceType.CAR)
        self.lot.add_space(space)

        assert self.lot.total_capacity == 1
        assert len(self.lot.spaces) == 1
        assert space in self.lot.spaces

    def test_add_multiple_spaces(self):
        """Test adding multiple parking spaces."""
        space1 = ParkingSpace("A1", 1, SpaceType.CAR)
        space2 = ParkingSpace("A2", 1, SpaceType.CAR)
        space3 = ParkingSpace("M1", 1, SpaceType.MOTORCYCLE)

        self.lot.add_space(space1)
        self.lot.add_space(space2)
        self.lot.add_space(space3)

        assert self.lot.total_capacity == 3
        assert len(self.lot.spaces) == 3

    def test_add_duplicate_space_id_fails(self):
        """Test that adding a space with duplicate ID raises ValueError."""
        space1 = ParkingSpace("A1", 1, SpaceType.CAR)
        space2 = ParkingSpace("A1", 2, SpaceType.CAR)  # Same ID

        self.lot.add_space(space1)
        with pytest.raises(ValueError):
            self.lot.add_space(space2)

    def test_remove_space(self):
        """Test removing a parking space."""
        space = ParkingSpace("A1", 1, SpaceType.CAR)
        self.lot.add_space(space)
        self.lot.remove_space("A1")

        assert self.lot.total_capacity == 0
        assert len(self.lot.spaces) == 0

    def test_remove_nonexistent_space_fails(self):
        """Test that removing a nonexistent space raises ValueError."""
        with pytest.raises(ValueError):
            self.lot.remove_space("A1")

    def test_remove_occupied_space_fails(self):
        """Test that removing an occupied space raises ValueError."""
        space = ParkingSpace("A1", 1, SpaceType.CAR)
        space.occupy()
        self.lot.add_space(space)

        with pytest.raises(ValueError):
            self.lot.remove_space("A1")

    def test_assign_space_success(self):
        """Test successfully assigning a space to a vehicle."""
        space = ParkingSpace("A1", 1, SpaceType.CAR)
        self.lot.add_space(space)

        car = Car("ABC123", "John Doe", "555-0100")
        assigned_space = self.lot.assign_space(car)

        assert assigned_space == space
        assert assigned_space.status == SpaceStatus.OCCUPIED

    def test_assign_space_no_available_space(self):
        """Test that assigning space when lot is full raises LotFullError."""
        space = ParkingSpace("A1", 1, SpaceType.CAR)
        space.occupy()  # Make it occupied
        self.lot.add_space(space)

        car = Car("ABC123", "John Doe", "555-0100")
        with pytest.raises(LotFullError):
            self.lot.assign_space(car)

    def test_assign_space_wrong_type(self):
        """Test that assigning space only matches vehicle type."""
        car_space = ParkingSpace("A1", 1, SpaceType.CAR)
        self.lot.add_space(car_space)

        motorcycle = Motorcycle("XYZ789", "Jane Smith", "555-0200")
        with pytest.raises(LotFullError):
            self.lot.assign_space(motorcycle)

    def test_get_available_spaces_all(self):
        """Test getting all available spaces."""
        space1 = ParkingSpace("A1", 1, SpaceType.CAR)
        space2 = ParkingSpace("A2", 1, SpaceType.CAR)
        space3 = ParkingSpace("A3", 1, SpaceType.CAR)

        self.lot.add_space(space1)
        self.lot.add_space(space2)
        self.lot.add_space(space3)

        space2.occupy()

        available = self.lot.get_available_spaces()
        assert len(available) == 2
        assert space1 in available
        assert space3 in available
        assert space2 not in available

    def test_get_available_spaces_by_type(self):
        """Test getting available spaces filtered by type."""
        car_space = ParkingSpace("A1", 1, SpaceType.CAR)
        motorcycle_space = ParkingSpace("M1", 1, SpaceType.MOTORCYCLE)

        self.lot.add_space(car_space)
        self.lot.add_space(motorcycle_space)

        car_available = self.lot.get_available_spaces(SpaceType.CAR)
        assert len(car_available) == 1
        assert car_space in car_available

        motorcycle_available = self.lot.get_available_spaces(SpaceType.MOTORCYCLE)
        assert len(motorcycle_available) == 1
        assert motorcycle_space in motorcycle_available

    def test_is_full_true(self):
        """Test is_full returns True when no spaces available."""
        space = ParkingSpace("A1", 1, SpaceType.CAR)
        space.occupy()
        self.lot.add_space(space)

        assert self.lot.is_full() is True

    def test_is_full_false(self):
        """Test is_full returns False when spaces available."""
        space = ParkingSpace("A1", 1, SpaceType.CAR)
        self.lot.add_space(space)

        assert self.lot.is_full() is False

    def test_is_full_by_type(self):
        """Test is_full with specific space type."""
        car_space = ParkingSpace("A1", 1, SpaceType.CAR)
        motorcycle_space = ParkingSpace("M1", 1, SpaceType.MOTORCYCLE)

        self.lot.add_space(car_space)
        self.lot.add_space(motorcycle_space)

        car_space.occupy()

        assert self.lot.is_full(SpaceType.CAR) is True
        assert self.lot.is_full(SpaceType.MOTORCYCLE) is False
        assert self.lot.is_full() is False  # Overall not full

    def test_generate_report(self):
        """Test generating a comprehensive report."""
        space1 = ParkingSpace("A1", 1, SpaceType.CAR)
        space2 = ParkingSpace("A2", 1, SpaceType.CAR)
        space3 = ParkingSpace("M1", 2, SpaceType.MOTORCYCLE)

        self.lot.add_space(space1)
        self.lot.add_space(space2)
        self.lot.add_space(space3)

        space2.occupy()

        report = self.lot.generate_report()

        assert report["lot_id"] == "LOT001"
        assert report["name"] == "Central Parking"
        assert report["location"] == "123 Main St"
        assert report["total_capacity"] == 3
        assert report["occupied"] == 1
        assert report["available"] == 2
        assert "per_level_breakdown" in report
        assert "per_type_breakdown" in report

    def test_report_per_level_breakdown(self):
        """Test per-level breakdown in report."""
        space1 = ParkingSpace("A1", 1, SpaceType.CAR)
        space2 = ParkingSpace("A2", 1, SpaceType.CAR)
        space3 = ParkingSpace("M1", 2, SpaceType.MOTORCYCLE)

        self.lot.add_space(space1)
        self.lot.add_space(space2)
        self.lot.add_space(space3)

        space2.occupy()

        report = self.lot.generate_report()
        level_breakdown = report["per_level_breakdown"]

        assert level_breakdown[1]["total"] == 2
        assert level_breakdown[1]["occupied"] == 1
        assert level_breakdown[1]["available"] == 1
        assert level_breakdown[2]["total"] == 1
        assert level_breakdown[2]["occupied"] == 0
        assert level_breakdown[2]["available"] == 1

    def test_report_per_type_breakdown(self):
        """Test per-type breakdown in report."""
        space1 = ParkingSpace("A1", 1, SpaceType.CAR)
        space2 = ParkingSpace("A2", 1, SpaceType.CAR)
        space3 = ParkingSpace("M1", 1, SpaceType.MOTORCYCLE)

        self.lot.add_space(space1)
        self.lot.add_space(space2)
        self.lot.add_space(space3)

        space2.occupy()

        report = self.lot.generate_report()
        type_breakdown = report["per_type_breakdown"]

        assert type_breakdown["car"]["total"] == 2
        assert type_breakdown["car"]["occupied"] == 1
        assert type_breakdown["car"]["available"] == 1
        assert type_breakdown["motorcycle"]["total"] == 1
        assert type_breakdown["motorcycle"]["occupied"] == 0
        assert type_breakdown["motorcycle"]["available"] == 1

    def test_composition_spaces_belong_to_lot(self):
        """Test that spaces are composed by the lot (they belong to it)."""
        space = ParkingSpace("A1", 1, SpaceType.CAR)
        self.lot.add_space(space)

        # Space is in the lot's list
        assert space in self.lot.spaces

        # Creating a new lot and adding the same space should fail
        lot2 = ParkingLot("LOT002", "Other Parking", "456 Oak St")
        with pytest.raises(ValueError, match="already belongs to a lot"):
            lot2.add_space(space)

    def test_lot_repr(self):
        """Test lot string representation."""
        repr_str = repr(self.lot)
        assert "LOT001" in repr_str
        assert "Central Parking" in repr_str
        assert "0" in repr_str  # capacity

    def test_lot_str(self):
        """Test lot user-friendly string representation."""
        str_str = str(self.lot)
        assert "Central Parking" in str_str
        assert "123 Main St" in str_str
        assert "0 spaces" in str_str

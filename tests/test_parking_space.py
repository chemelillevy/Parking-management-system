"""
Tests for ParkingSpace class.
"""

import pytest
from src.parking.parking_space import ParkingSpace
from src.parking.enums import SpaceStatus, SpaceType


class TestParkingSpace:
    """Test cases for ParkingSpace class."""

    def test_parking_space_initialization(self):
        """Test that a parking space is initialized correctly."""
        space = ParkingSpace("A1", 1, SpaceType.CAR)
        assert space.space_id == "A1"
        assert space.level_number == 1
        assert space.space_type == SpaceType.CAR
        assert space.status == SpaceStatus.AVAILABLE

    def test_is_available_when_available(self):
        """Test is_available returns True when space is available."""
        space = ParkingSpace("A1", 1, SpaceType.CAR)
        assert space.is_available() is True

    def test_is_available_when_occupied(self):
        """Test is_available returns False when space is occupied."""
        space = ParkingSpace("A1", 1, SpaceType.CAR)
        space.occupy()
        assert space.is_available() is False

    def test_reserve_available_space(self):
        """Test reserving an available space."""
        space = ParkingSpace("A1", 1, SpaceType.CAR)
        space.reserve()
        assert space.status == SpaceStatus.RESERVED

    def test_reserve_occupied_space_fails(self):
        """Test that reserving an occupied space raises ValueError."""
        space = ParkingSpace("A1", 1, SpaceType.CAR)
        space.occupy()
        with pytest.raises(ValueError):
            space.reserve()

    def test_occupy_available_space(self):
        """Test occupying an available space."""
        space = ParkingSpace("A1", 1, SpaceType.CAR)
        space.occupy()
        assert space.status == SpaceStatus.OCCUPIED

    def test_occupy_reserved_space(self):
        """Test occupying a reserved space."""
        space = ParkingSpace("A1", 1, SpaceType.CAR)
        space.reserve()
        space.occupy()
        assert space.status == SpaceStatus.OCCUPIED

    def test_occupy_occupied_space_fails(self):
        """Test that occupying an already occupied space raises ValueError."""
        space = ParkingSpace("A1", 1, SpaceType.CAR)
        space.occupy()
        with pytest.raises(ValueError):
            space.occupy()

    def test_release_occupied_space(self):
        """Test releasing an occupied space makes it available."""
        space = ParkingSpace("A1", 1, SpaceType.CAR)
        space.occupy()
        space.release()
        assert space.status == SpaceStatus.AVAILABLE

    def test_release_reserved_space(self):
        """Test releasing a reserved space makes it available."""
        space = ParkingSpace("A1", 1, SpaceType.CAR)
        space.reserve()
        space.release()
        assert space.status == SpaceStatus.AVAILABLE

    def test_space_types(self):
        """Test different space types."""
        motorcycle_space = ParkingSpace("M1", 1, SpaceType.MOTORCYCLE)
        car_space = ParkingSpace("C1", 1, SpaceType.CAR)
        truck_space = ParkingSpace("T1", 1, SpaceType.TRUCK)

        assert motorcycle_space.space_type == SpaceType.MOTORCYCLE
        assert car_space.space_type == SpaceType.CAR
        assert truck_space.space_type == SpaceType.TRUCK

    def test_parking_space_repr(self):
        """Test parking space string representation."""
        space = ParkingSpace("A1", 1, SpaceType.CAR)
        repr_str = repr(space)
        assert "A1" in repr_str
        assert "1" in repr_str
        assert "car" in repr_str
        assert "available" in repr_str

    def test_parking_space_str(self):
        """Test parking space user-friendly string representation."""
        space = ParkingSpace("A1", 1, SpaceType.CAR)
        str_str = str(space)
        assert "A1" in str_str
        assert "Level 1" in str_str
        assert "car" in str_str
        assert "available" in str_str

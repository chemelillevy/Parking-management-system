"""
ParkingSpace class for the Parking Management System.

Demonstrates:
- Encapsulation: Private attributes with property getters
- Association: Associated with ParkingTicket (1 to 0..*)
- Composition: Part of ParkingLot (1 to 1..*)
"""

from typing import Optional
from src.parking.enums import SpaceStatus, SpaceType


class ParkingSpace:
    """
    Represents a single parking bay in the facility.

    Attributes:
        space_id: Unique identifier for the parking space
        level_number: The floor/level where the space is located
        space_type: Type of vehicles that can park here (motorcycle, car, truck)
        status: Current availability status of the space
    """

    def __init__(self, space_id: str, level_number: int, space_type: SpaceType) -> None:
        """
        Initialize a parking space.

        Args:
            space_id: Unique identifier for the space
            level_number: Floor/level number where the space is located
            space_type: Type of vehicles that can use this space
        """
        self._space_id = space_id
        self._level_number = level_number
        self._space_type = space_type
        self._status = SpaceStatus.AVAILABLE
        self._lot: Optional[object] = None  # Track which lot owns this space

    @property
    def space_id(self) -> str:
        """Get the space ID."""
        return self._space_id

    @property
    def level_number(self) -> int:
        """Get the level number."""
        return self._level_number

    @property
    def space_type(self) -> SpaceType:
        """Get the space type."""
        return self._space_type

    @property
    def status(self) -> SpaceStatus:
        """Get the current status."""
        return self._status

    def set_lot(self, lot: object) -> None:
        """
        Set the lot that owns this space (for composition enforcement).

        Args:
            lot: The parking lot that owns this space

        Raises:
            ValueError: If space already belongs to a different lot
        """
        if self._lot is not None and self._lot is not lot:
            raise ValueError(f"Space {self._space_id} already belongs to a lot")
        self._lot = lot

    def is_available(self) -> bool:
        """
        Check if the space is currently available.

        Returns:
            True if status is AVAILABLE, False otherwise
        """
        return self._status == SpaceStatus.AVAILABLE

    def reserve(self) -> None:
        """
        Mark the space as reserved.

        Raises:
            ValueError: If space is not available
        """
        if not self.is_available():
            raise ValueError(f"Space {self._space_id} is not available for reservation")
        self._status = SpaceStatus.RESERVED

    def occupy(self) -> None:
        """
        Mark the space as occupied.

        Raises:
            ValueError: If space is not available or reserved
        """
        if self._status not in (SpaceStatus.AVAILABLE, SpaceStatus.RESERVED):
            raise ValueError(f"Space {self._space_id} cannot be occupied (current status: {self._status})")
        self._status = SpaceStatus.OCCUPIED

    def release(self) -> None:
        """
        Release the space back to available status.

        Can be called from RESERVED or OCCUPIED status.
        """
        self._status = SpaceStatus.AVAILABLE

    def __repr__(self) -> str:
        """Return a string representation of the parking space."""
        return f"ParkingSpace(id='{self._space_id}', level={self._level_number}, type={self._space_type.value}, status={self._status.value})"

    def __str__(self) -> str:
        """Return a user-friendly string representation."""
        return f"Space {self._space_id} (Level {self._level_number}, {self._space_type.value}, {self._status.value})"

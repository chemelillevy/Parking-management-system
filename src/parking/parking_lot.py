"""
ParkingLot class for the Parking Management System.

Demonstrates:
- Composition: Owns ParkingSpace objects (1 to 1..*)
- Encapsulation: Private attributes with property getters
- Association: Associated with ParkingTicket through spaces
"""

from typing import List, Dict, Any, Optional, TYPE_CHECKING
from src.parking.parking_space import ParkingSpace
from src.parking.vehicle import Vehicle
from src.parking.enums import SpaceType, SpaceStatus
from src.parking.exceptions import LotFullError

if TYPE_CHECKING:
    from src.parking.enums import VehicleType


class ParkingLot:
    """
    Represents the entire parking facility.

    The lot owns and manages its parking spaces. It can assign spaces,
    check availability, and generate reports.

    Attributes:
        lot_id: Unique identifier for the parking lot
        name: Name of the parking facility
        location: Location/address of the facility
        total_capacity: Total number of parking spaces
    """

    def __init__(self, lot_id: str, name: str, location: str) -> None:
        """
        Initialize a parking lot.

        Args:
            lot_id: Unique identifier for the lot
            name: Name of the parking facility
            location: Location/address of the facility
        """
        self._lot_id = lot_id
        self._name = name
        self._location = location
        self._spaces: List[ParkingSpace] = []
        self._total_capacity = 0

    @property
    def lot_id(self) -> str:
        """Get the lot ID."""
        return self._lot_id

    @property
    def name(self) -> str:
        """Get the lot name."""
        return self._name

    @property
    def location(self) -> str:
        """Get the lot location."""
        return self._location

    @property
    def total_capacity(self) -> int:
        """Get the total capacity (number of spaces)."""
        return self._total_capacity

    @property
    def spaces(self) -> List[ParkingSpace]:
        """Get all parking spaces (copy to prevent external modification)."""
        return self._spaces.copy()

    def add_space(self, space: ParkingSpace) -> None:
        """
        Add a parking space to the lot.

        Args:
            space: The parking space to add

        Raises:
            ValueError: If a space with the same ID already exists
        """
        # Check for duplicate space ID
        for existing_space in self._spaces:
            if existing_space.space_id == space.space_id:
                raise ValueError(f"Space with ID '{space.space_id}' already exists in the lot")

        # Set the lot as the owner (composition)
        space.set_lot(self)

        self._spaces.append(space)
        self._total_capacity += 1

    def remove_space(self, space_id: str) -> None:
        """
        Remove a parking space from the lot.

        Args:
            space_id: The ID of the space to remove

        Raises:
            ValueError: If the space is not found or is occupied
        """
        space = self._find_space(space_id)
        if space is None:
            raise ValueError(f"Space with ID '{space_id}' not found")

        if space.status == SpaceStatus.OCCUPIED:
            raise ValueError(f"Cannot remove occupied space '{space_id}'")

        self._spaces.remove(space)
        self._total_capacity -= 1

    def assign_space(self, vehicle: Vehicle) -> ParkingSpace:
        """
        Assign an available parking space to a vehicle.

        Finds an available space that matches the vehicle type,
        marks it as occupied, and returns it.

        Args:
            vehicle: The vehicle needing a space

        Returns:
            The assigned ParkingSpace

        Raises:
            LotFullError: If no suitable space is available
        """
        # Find available space matching vehicle type
        available_space = self._find_available_space(vehicle.vehicle_type)

        if available_space is None:
            raise LotFullError(
                f"No available {vehicle.vehicle_type.value} space for vehicle {vehicle.plate_number}"
            )

        # Occupy the space
        available_space.occupy()
        return available_space

    def get_available_spaces(self, space_type: Optional[SpaceType] = None) -> List[ParkingSpace]:
        """
        Get all available parking spaces.

        Args:
            space_type: Optional filter by space type (returns all types if None)

        Returns:
            List of available parking spaces
        """
        if space_type is None:
            return [space for space in self._spaces if space.is_available()]
        return [space for space in self._spaces if space.is_available() and space.space_type == space_type]

    def is_full(self, space_type: Optional[SpaceType] = None) -> bool:
        """
        Check if the lot is full.

        Args:
            space_type: Optional check only for a specific space type

        Returns:
            True if no spaces are available (for the type if specified), False otherwise
        """
        available = self.get_available_spaces(space_type)
        return len(available) == 0

    def generate_report(self) -> Dict[str, Any]:
        """
        Generate a comprehensive availability report.

        Returns:
            Dictionary containing:
            - total_capacity: Total number of spaces
            - occupied: Number of occupied spaces
            - available: Number of available spaces
            - per_level_breakdown: Breakdown by level
            - per_type_breakdown: Breakdown by space type
        """
        occupied_count = sum(1 for space in self._spaces if space.status == SpaceStatus.OCCUPIED)
        available_count = sum(1 for space in self._spaces if space.is_available())

        # Per-level breakdown
        level_breakdown: Dict[int, Dict[str, int]] = {}
        for space in self._spaces:
            level = space.level_number
            if level not in level_breakdown:
                level_breakdown[level] = {"total": 0, "occupied": 0, "available": 0}
            level_breakdown[level]["total"] += 1
            if space.status == SpaceStatus.OCCUPIED:
                level_breakdown[level]["occupied"] += 1
            elif space.is_available():
                level_breakdown[level]["available"] += 1

        # Per-type breakdown
        type_breakdown: Dict[str, Dict[str, int]] = {}
        for space in self._spaces:
            space_type = space.space_type.value
            if space_type not in type_breakdown:
                type_breakdown[space_type] = {"total": 0, "occupied": 0, "available": 0}
            type_breakdown[space_type]["total"] += 1
            if space.status == SpaceStatus.OCCUPIED:
                type_breakdown[space_type]["occupied"] += 1
            elif space.is_available():
                type_breakdown[space_type]["available"] += 1

        return {
            "lot_id": self._lot_id,
            "name": self._name,
            "location": self._location,
            "total_capacity": self._total_capacity,
            "occupied": occupied_count,
            "available": available_count,
            "per_level_breakdown": level_breakdown,
            "per_type_breakdown": type_breakdown,
        }

    def _find_space(self, space_id: str) -> Optional[ParkingSpace]:
        """
        Find a parking space by ID.

        Args:
            space_id: The ID of the space to find

        Returns:
            The ParkingSpace if found, None otherwise
        """
        for space in self._spaces:
            if space.space_id == space_id:
                return space
        return None

    def _find_available_space(self, vehicle_type: object) -> Optional[ParkingSpace]:
        """
        Find an available space matching the vehicle type.

        Args:
            vehicle_type: The type of vehicle needing a space (VehicleType enum)

        Returns:
            The first available ParkingSpace matching the type, None if not found
        """
        for space in self._spaces:
            # Compare by value since VehicleType and SpaceType are different enums
            if space.space_type.value == vehicle_type.value and space.is_available():
                return space
        return None

    def __repr__(self) -> str:
        """Return a string representation of the parking lot."""
        return f"ParkingLot(id='{self._lot_id}', name='{self._name}', capacity={self._total_capacity})"

    def __str__(self) -> str:
        """Return a user-friendly string representation."""
        return f"{self._name} ({self._location}) - {self._total_capacity} spaces"

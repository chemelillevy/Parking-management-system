"""
Authentication and User Management System.

Handles user registration, login, and session management with secure password hashing.
"""

import hashlib
import json
import os
from typing import Optional, Dict, List
from datetime import datetime
from dataclasses import dataclass, asdict


@dataclass
class User:
    """Represents a user in the system."""
    user_id: str
    username: str
    email: str
    full_name: str
    phone: str
    role: str  # "admin", "attendant", "staff"
    password_hash: str
    created_at: str
    is_active: bool = True


class AuthenticationSystem:
    """Handles user authentication and management."""

    def __init__(self, users_file: str = "users.json"):
        """
        Initialize the authentication system.

        Args:
            users_file: Path to the JSON file storing user data
        """
        self.users_file = users_file
        self.current_user: Optional[User] = None
        self._load_users()

    def _load_users(self) -> None:
        """Load users from the JSON file."""
        if os.path.exists(self.users_file):
            try:
                with open(self.users_file, 'r') as f:
                    users_data = json.load(f)
                    self.users: Dict[str, User] = {
                        user_id: User(**user_data)
                        for user_id, user_data in users_data.items()
                    }
            except (json.JSONDecodeError, KeyError):
                self.users = {}
        else:
            self.users = {}

    def _save_users(self) -> None:
        """Save users to the JSON file."""
        users_data = {
            user_id: asdict(user)
            for user_id, user in self.users.items()
        }
        with open(self.users_file, 'w') as f:
            json.dump(users_data, f, indent=2)

    def _hash_password(self, password: str) -> str:
        """
        Hash a password using SHA-256.

        Args:
            password: Plain text password

        Returns:
            Hashed password
        """
        return hashlib.sha256(password.encode()).hexdigest()

    def register_user(
        self,
        username: str,
        password: str,
        email: str,
        full_name: str,
        phone: str,
        role: str = "attendant"
    ) -> tuple[bool, str]:
        """
        Register a new user.

        Args:
            username: Unique username
            password: Plain text password (will be hashed)
            email: User's email
            full_name: User's full name
            phone: User's phone number
            role: User's role (admin, attendant, staff)

        Returns:
            Tuple of (success, message)
        """
        # Validate username uniqueness
        if any(user.username == username for user in self.users.values()):
            return False, "Username already exists"

        # Validate email uniqueness
        if any(user.email == email for user in self.users.values()):
            return False, "Email already registered"

        # Validate password strength
        if len(password) < 6:
            return False, "Password must be at least 6 characters"

        # Create user
        user_id = f"USR{len(self.users) + 1:04d}"
        password_hash = self._hash_password(password)
        created_at = datetime.now().isoformat()

        user = User(
            user_id=user_id,
            username=username,
            email=email,
            full_name=full_name,
            phone=phone,
            role=role,
            password_hash=password_hash,
            created_at=created_at
        )

        self.users[user_id] = user
        self._save_users()

        return True, "Registration successful"

    def login(self, username: str, password: str) -> tuple[bool, str]:
        """
        Authenticate a user.

        Args:
            username: Username
            password: Plain text password

        Returns:
            Tuple of (success, message)
        """
        # Find user by username
        user = next((u for u in self.users.values() if u.username == username), None)

        if not user:
            return False, "Invalid username or password"

        if not user.is_active:
            return False, "Account is deactivated"

        # Verify password
        password_hash = self._hash_password(password)
        if password_hash != user.password_hash:
            return False, "Invalid username or password"

        # Set current user
        self.current_user = user

        return True, f"Welcome back, {user.full_name}!"

    def logout(self) -> None:
        """Log out the current user."""
        self.current_user = None

    def is_logged_in(self) -> bool:
        """Check if a user is logged in."""
        return self.current_user is not None

    def get_current_user(self) -> Optional[User]:
        """Get the currently logged-in user."""
        return self.current_user

    def get_all_users(self) -> List[User]:
        """Get all users (for admin)."""
        return list(self.users.values())

    def deactivate_user(self, user_id: str) -> tuple[bool, str]:
        """
        Deactivate a user account.

        Args:
            user_id: ID of the user to deactivate

        Returns:
            Tuple of (success, message)
        """
        if user_id not in self.users:
            return False, "User not found"

        if self.users[user_id].user_id == self.current_user.user_id:
            return False, "Cannot deactivate your own account"

        self.users[user_id].is_active = False
        self._save_users()

        return True, "User deactivated successfully"

    def activate_user(self, user_id: str) -> tuple[bool, str]:
        """
        Activate a user account.

        Args:
            user_id: ID of the user to activate

        Returns:
            Tuple of (success, message)
        """
        if user_id not in self.users:
            return False, "User not found"

        self.users[user_id].is_active = True
        self._save_users()

        return True, "User activated successfully"

    def create_default_admin(self) -> None:
        """Create a default admin account if no users exist."""
        if not self.users:
            self.register_user(
                username="admin",
                password="admin123",
                email="admin@parking.com",
                full_name="System Administrator",
                phone="555-0000",
                role="admin"
            )

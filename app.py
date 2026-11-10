"""
Main entry point for the Parking Management System with authentication.

This is the file to run to start the application with secure login.
"""

from src.parking.auth import AuthenticationSystem
from login_gui import LoginWindow
from gui import ParkingSystemGUI


def main():
    """Main entry point with authentication."""
    # Initialize authentication system
    auth_system = AuthenticationSystem()

    # Create default admin if no users exist
    auth_system.create_default_admin()

    # Show login window
    def on_login_success():
        """Callback when login succeeds - show main GUI."""
        app = ParkingSystemGUI(auth_system)
        app.run()

    # Start with login window
    login_window = LoginWindow(auth_system, on_login_success)
    login_window.run()


if __name__ == "__main__":
    main()

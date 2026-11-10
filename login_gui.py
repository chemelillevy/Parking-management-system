"""
Login and Registration GUI for Parking Management System.

Provides secure login and registration screens with QuickBooks styling.
"""

import customtkinter as ctk
from tkinter import messagebox
from src.parking.auth import AuthenticationSystem, User

# QuickBooks Color Palette
QB_GREEN = "#2CA58D"
QB_DARK_GREEN = "#1E7A6A"
QB_LIGHT_GREEN = "#E8F5F0"
QB_WHITE = "#FFFFFF"
QB_LIGHT_GRAY = "#F5F7FA"
QB_MEDIUM_GRAY = "#E0E6ED"
QB_DARK_GRAY = "#374151"
QB_TEXT = "#1F2937"
QB_BORDER = "#D1D5DB"


class LoginWindow:
    """Login window for the Parking Management System."""

    def __init__(self, auth_system: AuthenticationSystem, on_login_success):
        """
        Initialize the login window.

        Args:
            auth_system: Authentication system instance
            on_login_success: Callback function when login succeeds
        """
        self.auth_system = auth_system
        self.on_login_success = on_login_success

        # Configure appearance
        ctk.set_appearance_mode("Light")

        # Create login window
        self.root = ctk.CTk()
        self.root.geometry("500x600")
        self.root.title("Parking Management System - Login")
        self.root.resizable(False, False)

        self._create_login_ui()

    def _create_login_ui(self):
        """Create the login UI."""
        # Main container
        container = ctk.CTkFrame(self.root, fg_color=QB_LIGHT_GRAY)
        container.pack(fill="both", expand=True)

        # White card
        card = ctk.CTkFrame(container, fg_color=QB_WHITE, corner_radius=20)
        card.pack(fill="both", expand=True, padx=40, pady=40)

        # Logo
        logo_frame = ctk.CTkFrame(card, fg_color="transparent")
        logo_frame.pack(pady=(40, 20))

        logo_box = ctk.CTkFrame(logo_frame, width=80, height=80, fg_color=QB_GREEN, corner_radius=16)
        logo_box.pack()
        logo_box.pack_propagate(False)

        logo_text = ctk.CTkLabel(
            logo_box,
            text="PM",
            font=ctk.CTkFont(size=32, weight="bold"),
            text_color="white"
        )
        logo_text.place(relx=0.5, rely=0.5, anchor="center")

        # Title
        ctk.CTkLabel(
            card,
            text="Parking Management",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=QB_TEXT
        ).pack(pady=(10, 5))

        ctk.CTkLabel(
            card,
            text="Sign in to your account",
            font=ctk.CTkFont(size=14),
            text_color="#6B7280"
        ).pack(pady=(0, 30))

        # Username
        ctk.CTkLabel(card, text="Username", font=ctk.CTkFont(size=13, weight="bold"), text_color=QB_TEXT, anchor="w").pack(fill="x", padx=50, pady=(0, 8))
        self.username_entry = ctk.CTkEntry(card, height=45, placeholder_text="Enter your username", corner_radius=8, border_width=2, border_color=QB_BORDER)
        self.username_entry.pack(fill="x", padx=50, pady=(0, 20))

        # Password
        ctk.CTkLabel(card, text="Password", font=ctk.CTkFont(size=13, weight="bold"), text_color=QB_TEXT, anchor="w").pack(fill="x", padx=50, pady=(0, 8))
        self.password_entry = ctk.CTkEntry(card, height=45, placeholder_text="Enter your password", show="*", corner_radius=8, border_width=2, border_color=QB_BORDER)
        self.password_entry.pack(fill="x", padx=50, pady=(0, 30))

        # Login button
        login_btn = ctk.CTkButton(
            card,
            text="Sign In",
            height=50,
            fg_color=QB_GREEN,
            hover_color=QB_DARK_GREEN,
            font=ctk.CTkFont(size=16, weight="bold"),
            corner_radius=8,
            command=self._handle_login
        )
        login_btn.pack(fill="x", padx=50, pady=(0, 15))

        # Register link
        register_label = ctk.CTkLabel(
            card,
            text="Don't have an account? ",
            font=ctk.CTkFont(size=13),
            text_color="#6B7280"
        )
        register_label.pack(pady=(0, 0))

        register_btn = ctk.CTkButton(
            card,
            text="Register",
            fg_color=QB_LIGHT_GRAY,
            text_color=QB_GREEN,
            hover_color=QB_MEDIUM_GRAY,
            font=ctk.CTkFont(size=13, weight="bold"),
            width=80,
            command=self._show_register
        )
        register_btn.pack(pady=(0, 40))

        # Bind Enter key
        self.root.bind("<Return>", lambda e: self._handle_login())

    def _handle_login(self):
        """Handle login attempt."""
        username = self.username_entry.get()
        password = self.password_entry.get()

        if not username or not password:
            messagebox.showerror("Error", "Please enter both username and password")
            return

        success, message = self.auth_system.login(username, password)

        if success:
            self.root.destroy()
            self.on_login_success()
        else:
            messagebox.showerror("Login Failed", message)

    def _show_register(self):
        """Show the registration window."""
        self.root.destroy()
        RegisterWindow(self.auth_system, self._back_to_login).run()

    def _back_to_login(self):
        """Return to login window."""
        LoginWindow(self.auth_system, self.on_login_success).run()

    def run(self):
        """Run the login window."""
        self.root.mainloop()


class RegisterWindow:
    """Registration window for the Parking Management System."""

    def __init__(self, auth_system: AuthenticationSystem, on_back):
        """
        Initialize the registration window.

        Args:
            auth_system: Authentication system instance
            on_back: Callback function to return to login
        """
        self.auth_system = auth_system
        self.on_back = on_back

        # Configure appearance
        ctk.set_appearance_mode("Light")

        # Create registration window
        self.root = ctk.CTk()
        self.root.geometry("500x700")
        self.root.title("Parking Management System - Register")
        self.root.resizable(False, False)

        self._create_register_ui()

    def _create_register_ui(self):
        """Create the registration UI."""
        # Main container
        container = ctk.CTkFrame(self.root, fg_color=QB_LIGHT_GRAY)
        container.pack(fill="both", expand=True)

        # White card
        card = ctk.CTkFrame(container, fg_color=QB_WHITE, corner_radius=20)
        card.pack(fill="both", expand=True, padx=40, pady=40)

        # Logo
        logo_frame = ctk.CTkFrame(card, fg_color="transparent")
        logo_frame.pack(pady=(30, 20))

        logo_box = ctk.CTkFrame(logo_frame, width=60, height=60, fg_color=QB_GREEN, corner_radius=12)
        logo_box.pack()
        logo_box.pack_propagate(False)

        logo_text = ctk.CTkLabel(
            logo_box,
            text="PM",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color="white"
        )
        logo_text.place(relx=0.5, rely=0.5, anchor="center")

        # Title
        ctk.CTkLabel(
            card,
            text="Create Account",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=QB_TEXT
        ).pack(pady=(10, 5))

        ctk.CTkLabel(
            card,
            text="Fill in your details to register",
            font=ctk.CTkFont(size=14),
            text_color="#6B7280"
        ).pack(pady=(0, 25))

        # Form fields
        fields = [
            ("Full Name", "full_name", "Enter your full name"),
            ("Username", "username", "Choose a username"),
            ("Email", "email", "Enter your email"),
            ("Phone", "phone", "Enter your phone number"),
            ("Password", "password", "Create a password (min 6 chars)"),
            ("Confirm Password", "confirm_password", "Confirm your password"),
        ]

        self.entries = {}
        for label, key, placeholder in fields:
            ctk.CTkLabel(card, text=label, font=ctk.CTkFont(size=13, weight="bold"), text_color=QB_TEXT, anchor="w").pack(fill="x", padx=50, pady=(0, 8))
            entry = ctk.CTkEntry(card, height=45, placeholder_text=placeholder, corner_radius=8, border_width=2, border_color=QB_BORDER)
            if "password" in key:
                entry.configure(show="*")
            entry.pack(fill="x", padx=50, pady=(0, 15))
            self.entries[key] = entry

        # Role selection
        ctk.CTkLabel(card, text="Role", font=ctk.CTkFont(size=13, weight="bold"), text_color=QB_TEXT, anchor="w").pack(fill="x", padx=50, pady=(0, 8))
        self.role_var = ctk.StringVar(value="attendant")
        role_frame = ctk.CTkFrame(card, fg_color=QB_LIGHT_GRAY, corner_radius=8)
        role_frame.pack(fill="x", padx=50, pady=(0, 25))

        for role in ["attendant", "staff"]:
            ctk.CTkRadioButton(role_frame, text=role.capitalize(), variable=self.role_var, value=role, font=ctk.CTkFont(size=14)).pack(side="left", padx=20, pady=10)

        # Register button
        register_btn = ctk.CTkButton(
            card,
            text="Create Account",
            height=50,
            fg_color=QB_GREEN,
            hover_color=QB_DARK_GREEN,
            font=ctk.CTkFont(size=16, weight="bold"),
            corner_radius=8,
            command=self._handle_register
        )
        register_btn.pack(fill="x", padx=50, pady=(0, 15))

        # Back link
        back_label = ctk.CTkLabel(
            card,
            text="Already have an account? ",
            font=ctk.CTkFont(size=13),
            text_color="#6B7280"
        )
        back_label.pack(pady=(0, 0))

        back_btn = ctk.CTkButton(
            card,
            text="Sign In",
            fg_color=QB_LIGHT_GRAY,
            text_color=QB_GREEN,
            hover_color=QB_MEDIUM_GRAY,
            font=ctk.CTkFont(size=13, weight="bold"),
            width=60,
            command=self._handle_back
        )
        back_btn.pack(pady=(0, 30))

    def _handle_register(self):
        """Handle registration attempt."""
        full_name = self.entries["full_name"].get()
        username = self.entries["username"].get()
        email = self.entries["email"].get()
        phone = self.entries["phone"].get()
        password = self.entries["password"].get()
        confirm_password = self.entries["confirm_password"].get()
        role = self.role_var.get()

        # Validation
        if not all([full_name, username, email, phone, password, confirm_password]):
            messagebox.showerror("Error", "Please fill in all fields")
            return

        if password != confirm_password:
            messagebox.showerror("Error", "Passwords do not match")
            return

        if len(password) < 6:
            messagebox.showerror("Error", "Password must be at least 6 characters")
            return

        # Register
        success, message = self.auth_system.register_user(
            username=username,
            password=password,
            email=email,
            full_name=full_name,
            phone=phone,
            role=role
        )

        if success:
            messagebox.showinfo("Success", message + "\n\nPlease sign in with your new account.")
            self._handle_back()
        else:
            messagebox.showerror("Registration Failed", message)

    def _handle_back(self):
        """Return to login window."""
        self.root.destroy()
        self.on_back()

    def run(self):
        """Run the registration window."""
        self.root.mainloop()

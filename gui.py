"""
Parking Management System - QuickBooks-Style GUI

A professional graphical user interface using CustomTkinter that mimics
the clean, modern design of QuickBooks accounting software.

QuickBooks Design Language:
- Primary Green: #2CA01C
- Dark Green: #237804
- Light Green: #E9F5E9
- White: #FFFFFF
- Light Gray: #F7F8F9
- Medium Gray: #E5E7EB
- Dark Gray: #374151
- Text: #1F2937
- Border: #D1D5DB
"""

import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime
from typing import List, Optional
from src.parking.parking_lot import ParkingLot
from src.parking.parking_space import ParkingSpace
from src.parking.vehicle import Car, Motorcycle, Truck
from src.parking.attendant import ParkingAttendant
from src.parking.parking_ticket import ParkingTicket
from src.parking.payment import CashPayment, CardPayment, MobileMoneyPayment
from src.parking.enums import SpaceType, TicketStatus
from src.parking.exceptions import LotFullError, VehicleAlreadyParkedError
from src.parking.auth import AuthenticationSystem

# QuickBooks Color Palette
QB_GREEN = "#2CA01C"
QB_DARK_GREEN = "#237804"
QB_LIGHT_GREEN = "#E9F5E9"
QB_WHITE = "#FFFFFF"
QB_LIGHT_GRAY = "#F7F8F9"
QB_MEDIUM_GRAY = "#E5E7EB"
QB_DARK_GRAY = "#374151"
QB_TEXT = "#1F2937"
QB_BORDER = "#D1D5DB"
QB_SUCCESS = "#10B981"
QB_WARNING = "#F59E0B"
QB_DANGER = "#EF4444"


class ParkingSystemGUI:
    """Main GUI application for the Parking Management System."""

    def __init__(self, auth_system: AuthenticationSystem):
        """
        Initialize the GUI application.

        Args:
            auth_system: Authentication system instance with logged-in user
        """
        # Configure appearance - QuickBooks Light Mode
        ctk.set_appearance_mode("Light")

        # Create main window
        self.root = ctk.CTk()
        self.root.geometry("1400x800")
        self.root.title("Parking Management System")
        self.root.minsize(1200, 700)

        # Store auth system
        self.auth_system = auth_system

        # Initialize parking system
        self.lot = ParkingLot("LOT001", "Central Parking", "123 Main Street")
        self.attendant = ParkingAttendant("ATT001", auth_system.get_current_user().full_name, auth_system.get_current_user().phone, "morning")
        self.active_tickets: List = []
        self._setup_lot()

        # Create UI
        self._create_sidebar()
        self._create_main_content()

        # Start with dashboard
        self.show_dashboard()

    def _setup_lot(self):
        """Set up the parking lot with initial spaces."""
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

    def _create_sidebar(self):
        """Create the sidebar navigation with QuickBooks styling."""
        self.sidebar = ctk.CTkFrame(self.root, width=280, corner_radius=0, fg_color=QB_WHITE, border_width=1, border_color=QB_BORDER)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        # Logo/Title - QuickBooks style
        logo_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        logo_frame.pack(pady=30, padx=20, fill="x")

        # QuickBooks-style logo
        logo_box = ctk.CTkFrame(logo_frame, width=60, height=60, fg_color=QB_GREEN, corner_radius=12)
        logo_box.pack(anchor="w")
        logo_box.pack_propagate(False)

        logo_text = ctk.CTkLabel(
            logo_box,
            text="PM",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color="white"
        )
        logo_text.place(relx=0.5, rely=0.5, anchor="center")

        title_label = ctk.CTkLabel(
            logo_frame,
            text="Parking\nManagement",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=QB_TEXT,
            anchor="w"
        )
        title_label.pack(anchor="w", pady=(15, 0))

        # Navigation buttons - QuickBooks style
        self.nav_buttons = []
        nav_items = [
            ("Dashboard", self.show_dashboard),
            ("Register Vehicle", self.show_register_vehicle),
            ("Manage Parking", self.show_manage_parking),
            ("Process Payment", self.show_process_payment),
            ("Reports", self.show_reports),
        ]

        nav_label = ctk.CTkLabel(
            self.sidebar,
            text="MENU",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="#9CA3AF",
            anchor="w"
        )
        nav_label.pack(pady=(30, 10), padx=20, fill="x")

        for i, (text, command) in enumerate(nav_items):
            btn = ctk.CTkButton(
                self.sidebar,
                text=text,
                font=ctk.CTkFont(size=14),
                height=45,
                fg_color="transparent",
                text_color=QB_DARK_GRAY,
                hover_color=QB_LIGHT_GREEN,
                anchor="w",
                command=lambda cmd=command, idx=i: self._navigate_to(cmd, idx)
            )
            btn.pack(pady=2, padx=15, fill="x")
            self.nav_buttons.append(btn)

        # Bottom section
        ctk.CTkFrame(self.sidebar, height=1, fg_color=QB_BORDER).pack(fill="x", pady=30, padx=20)

        user_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        user_frame.pack(side="bottom", pady=20, padx=20, fill="x")

        user_avatar = ctk.CTkFrame(user_frame, width=40, height=40, fg_color=QB_GREEN, corner_radius=20)
        user_avatar.pack(side="left")
        user_avatar.pack_propagate(False)

        current_user = self.auth_system.get_current_user()
        user_initials = "".join(w[0] for w in (current_user.full_name if current_user else "Guest").split()[:2]).upper() or "G"
        user_initial = ctk.CTkLabel(
            user_avatar,
            text=user_initials,
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="white"
        )
        user_initial.place(relx=0.5, rely=0.5, anchor="center")

        user_info = ctk.CTkFrame(user_frame, fg_color="transparent")
        user_info.pack(side="left", padx=12, fill="x", expand=True)

        ctk.CTkLabel(
            user_info,
            text=current_user.full_name if current_user else "Guest",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=QB_TEXT,
            anchor="w"
        ).pack(anchor="w")

        ctk.CTkLabel(
            user_info,
            text=current_user.role.capitalize() if current_user else "Guest",
            font=ctk.CTkFont(size=11),
            text_color="#6B7280",
            anchor="w"
        ).pack(anchor="w")

        # Logout button
        logout_btn = ctk.CTkButton(
            self.sidebar,
            text="Logout",
            font=ctk.CTkFont(size=13),
            height=40,
            fg_color="transparent",
            text_color="#DC2626",
            hover_color="#FEE2E2",
            command=self._handle_logout
        )
        logout_btn.pack(side="bottom", pady=10, padx=15, fill="x")

        # Exit button
        exit_btn = ctk.CTkButton(
            self.sidebar,
            text="Exit App",
            font=ctk.CTkFont(size=13),
            height=40,
            fg_color="transparent",
            text_color="#9CA3AF",
            hover_color=QB_LIGHT_GRAY,
            command=self.root.quit
        )
        exit_btn.pack(side="bottom", pady=(0, 10), padx=15, fill="x")

    def _navigate_to(self, command, index):
        """Navigate to a page and update button states."""
        # Reset all buttons
        for btn in self.nav_buttons:
            btn.configure(fg_color="transparent", text_color=QB_DARK_GRAY, hover_color=QB_LIGHT_GREEN)

        # Highlight selected button with QuickBooks green
        self.nav_buttons[index].configure(fg_color=QB_GREEN, text_color="white", hover_color=QB_DARK_GREEN)

        # Execute command
        command()

    def _create_main_content(self):
        """Create the main content area."""
        self.main_content = ctk.CTkFrame(self.root, corner_radius=0, fg_color=QB_LIGHT_GRAY)
        self.main_content.pack(side="right", fill="both", expand=True)

    def _clear_main_content(self):
        """Clear the main content area."""
        for widget in self.main_content.winfo_children():
            widget.destroy()

    def _create_header(self, title: str, subtitle: str = ""):
        """Create a QuickBooks-style header."""
        header_frame = ctk.CTkFrame(self.main_content, height=80, fg_color=QB_WHITE)
        header_frame.pack(fill="x", padx=0, pady=0)
        header_frame.pack_propagate(False)

        # Header content
        content_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=30, pady=20)

        title_label = ctk.CTkLabel(
            content_frame,
            text=title,
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color=QB_TEXT,
            anchor="w"
        )
        title_label.pack(side="left", anchor="w")

        if subtitle:
            subtitle_label = ctk.CTkLabel(
                content_frame,
                text=subtitle,
                font=ctk.CTkFont(size=14),
                text_color="#6B7280",
                anchor="w"
            )
            subtitle_label.pack(side="left", anchor="w", padx=(15, 0))

        # Date/time
        time_label = ctk.CTkLabel(
            content_frame,
            text=datetime.now().strftime("%B %d, %Y • %H:%M"),
            font=ctk.CTkFont(size=13),
            text_color="#6B7280"
        )
        time_label.pack(side="right")

    def show_dashboard(self):
        """Show the dashboard with statistics."""
        self._clear_main_content()
        self._create_header("Dashboard", "Overview of parking operations")

        # Statistics cards
        stats_frame = ctk.CTkFrame(self.main_content, fg_color="transparent")
        stats_frame.pack(fill="x", padx=30, pady=20)

        report = self.lot.generate_report()

        # Create stat cards with QuickBooks styling
        stats = [
            ("Total Capacity", str(report["total_capacity"]), QB_GREEN, "🅿️"),
            ("Occupied", str(report["occupied"]), QB_WARNING, "🚗"),
            ("Available", str(report["available"]), QB_SUCCESS, "✓"),
            ("Active Tickets", str(len([t for t in self.active_tickets if t.is_active()])), QB_DANGER, "🎫"),
        ]

        for i, (label, value, color, icon) in enumerate(stats):
            card = ctk.CTkFrame(stats_frame, fg_color=QB_WHITE, corner_radius=12, border_width=1, border_color=QB_BORDER)
            card.grid(row=0, column=i, padx=10, pady=10, sticky="nsew")
            stats_frame.grid_columnconfigure(i, weight=1)

            # Card content
            card_content = ctk.CTkFrame(card, fg_color="transparent")
            card_content.pack(fill="both", expand=True, padx=20, pady=20)

            # Icon and label row
            top_row = ctk.CTkFrame(card_content, fg_color="transparent")
            top_row.pack(fill="x")

            ctk.CTkLabel(top_row, text=icon, font=ctk.CTkFont(size=24)).pack(side="left")
            ctk.CTkLabel(top_row, text=label, font=ctk.CTkFont(size=13, weight="bold"), text_color="#6B7280").pack(side="right")

            # Value
            ctk.CTkLabel(
                card_content,
                text=value,
                font=ctk.CTkFont(size=36, weight="bold"),
                text_color=color
            ).pack(pady=(10, 0))

        # Quick actions
        actions_frame = ctk.CTkFrame(self.main_content, fg_color=QB_WHITE, corner_radius=12)
        actions_frame.pack(fill="x", padx=30, pady=10)

        actions_header = ctk.CTkFrame(actions_frame, fg_color="transparent")
        actions_header.pack(fill="x", padx=25, pady=(20, 15))

        ctk.CTkLabel(actions_header, text="Quick Actions", font=ctk.CTkFont(size=18, weight="bold"), text_color=QB_TEXT).pack(side="left")

        action_buttons_frame = ctk.CTkFrame(actions_frame, fg_color="transparent")
        action_buttons_frame.pack(fill="x", padx=25, pady=(0, 20))

        actions = [
            ("Register Vehicle", self.show_register_vehicle, QB_GREEN),
            ("View Spaces", self.show_manage_parking, QB_DARK_GRAY),
            ("Process Payment", self.show_process_payment, QB_SUCCESS),
            ("View Reports", self.show_reports, QB_DARK_GRAY),
        ]

        for text, command, color in actions:
            btn = ctk.CTkButton(
                action_buttons_frame,
                text=text,
                command=command,
                height=45,
                fg_color=color,
                hover_color=self._darken_color(color),
                font=ctk.CTkFont(size=14, weight="bold")
            )
            btn.pack(side="left", padx=8, expand=True, fill="x")

        # Recent activity
        activity_frame = ctk.CTkFrame(self.main_content, fg_color=QB_WHITE, corner_radius=12)
        activity_frame.pack(fill="both", expand=True, padx=30, pady=(10, 30))

        activity_header = ctk.CTkFrame(activity_frame, fg_color="transparent")
        activity_header.pack(fill="x", padx=25, pady=(20, 15))

        ctk.CTkLabel(activity_header, text="Recent Activity", font=ctk.CTkFont(size=18, weight="bold"), text_color=QB_TEXT).pack(side="left")

        # Activity list
        activity_scroll = ctk.CTkScrollableFrame(activity_frame, fg_color="transparent")
        activity_scroll.pack(fill="both", expand=True, padx=25, pady=(0, 20))

        if self.active_tickets:
            for ticket in self.active_tickets[-10:]:
                status_color = QB_SUCCESS if ticket.status == TicketStatus.CLOSED else QB_WARNING
                status_text = "Completed" if ticket.status == TicketStatus.CLOSED else "Active"

                activity_item = ctk.CTkFrame(activity_scroll, fg_color=QB_LIGHT_GRAY, corner_radius=8)
                activity_item.pack(fill="x", pady=8)

                # Vehicle info
                info_frame = ctk.CTkFrame(activity_item, fg_color="transparent")
                info_frame.pack(side="left", padx=15, pady=12)

                ctk.CTkLabel(
                    info_frame,
                    text=f"{ticket.vehicle.plate_number}",
                    font=ctk.CTkFont(size=14, weight="bold"),
                    text_color=QB_TEXT
                ).pack(anchor="w")

                ctk.CTkLabel(
                    info_frame,
                    text=f"{ticket.vehicle.vehicle_type.value} • Space {ticket.parking_space.space_id}",
                    font=ctk.CTkFont(size=12),
                    text_color="#6B7280"
                ).pack(anchor="w", pady=(2, 0))

                # Status badge
                status_badge = ctk.CTkLabel(
                    activity_item,
                    text=status_text,
                    fg_color=status_color,
                    corner_radius=6,
                    width=80,
                    height=28,
                    font=ctk.CTkFont(size=11, weight="bold"),
                    text_color="white"
                )
                status_badge.pack(side="right", padx=15, pady=12)
        else:
            ctk.CTkLabel(activity_scroll, text="No recent activity", text_color="#9CA3AF", font=ctk.CTkFont(size=14)).pack(pady=40)

        # Highlight dashboard button
        self.nav_buttons[0].configure(fg_color=QB_GREEN, text_color="white", hover_color=QB_DARK_GREEN)

    def _darken_color(self, hex_color: str, factor: float = 0.8) -> str:
        """Darken a hex color by a factor."""
        hex_color = hex_color.lstrip('#')
        rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        rgb = tuple(int(c * factor) for c in rgb)
        return f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"

    def show_register_vehicle(self):
        """Show vehicle registration form."""
        self._clear_main_content()
        self._create_header("Register Vehicle", "Register a new vehicle and assign parking space")

        form_frame = ctk.CTkFrame(self.main_content, fg_color=QB_WHITE, corner_radius=12)
        form_frame.pack(fill="both", expand=True, padx=30, pady=20)

        form_content = ctk.CTkFrame(form_frame, fg_color="transparent")
        form_content.pack(fill="both", expand=True, padx=40, pady=40)

        # Vehicle type selection
        ctk.CTkLabel(form_content, text="Vehicle Type", font=ctk.CTkFont(size=14, weight="bold"), text_color=QB_TEXT).pack(anchor="w", pady=(0, 10))
        self.vehicle_type_var = ctk.StringVar(value="Car")
        type_frame = ctk.CTkFrame(form_content, fg_color=QB_LIGHT_GRAY, corner_radius=8)
        type_frame.pack(fill="x", pady=(0, 25))

        for vtype in ["Car", "Motorcycle", "Truck"]:
            ctk.CTkRadioButton(type_frame, text=vtype, variable=self.vehicle_type_var, value=vtype, font=ctk.CTkFont(size=14)).pack(side="left", padx=20, pady=10)

        # Input fields
        fields = [
            ("Plate Number", "plate_entry", "Enter license plate"),
            ("Owner Name", "owner_entry", "Enter owner's full name"),
            ("Owner Phone", "phone_entry", "Enter phone number"),
        ]

        self.entries = {}
        for label, key, placeholder in fields:
            ctk.CTkLabel(form_content, text=label, font=ctk.CTkFont(size=14, weight="bold"), text_color=QB_TEXT).pack(anchor="w", pady=(0, 8))
            entry = ctk.CTkEntry(form_content, height=45, placeholder_text=placeholder, corner_radius=8, border_width=2, border_color=QB_BORDER)
            entry.pack(fill="x", pady=(0, 20))
            self.entries[key] = entry

        # Register button
        register_btn = ctk.CTkButton(
            form_content,
            text="Register & Assign Space",
            height=50,
            fg_color=QB_GREEN,
            hover_color=QB_DARK_GREEN,
            font=ctk.CTkFont(size=16, weight="bold"),
            corner_radius=8,
            command=self._register_vehicle
        )
        register_btn.pack(fill="x", pady=(10, 15))

        # Clear button
        clear_btn = ctk.CTkButton(
            form_content,
            text="Clear Form",
            height=45,
            fg_color="transparent",
            border_width=2,
            border_color=QB_BORDER,
            text_color=QB_TEXT,
            hover_color=QB_LIGHT_GRAY,
            font=ctk.CTkFont(size=14),
            corner_radius=8,
            command=self._clear_register_form
        )
        clear_btn.pack(fill="x")

    def _clear_register_form(self):
        """Clear the registration form."""
        for entry in self.entries.values():
            entry.delete(0, "end")

    def _register_vehicle(self):
        """Register a vehicle and assign a space."""
        vtype = self.vehicle_type_var.get()
        plate = self.entries["plate_entry"].get()
        owner = self.entries["owner_entry"].get()
        phone = self.entries["phone_entry"].get()

        if not all([plate, owner, phone]):
            messagebox.showerror("Error", "Please fill in all fields")
            return

        try:
            vehicle_classes = {"Car": Car, "Motorcycle": Motorcycle, "Truck": Truck}
            vehicle = vehicle_classes[vtype](plate, owner, phone)
            self.attendant.register_vehicle(vehicle, self.lot, self.active_tickets)
            space = self.lot.assign_space(vehicle)
            ticket_id = f"TKT{len(self.active_tickets) + 1:03d}"
            ticket = self.attendant.issue_ticket(ticket_id, vehicle, space)
            self.active_tickets.append(ticket)

            messagebox.showinfo(
                "Success",
                f"Vehicle registered successfully!\n\n"
                f"Plate: {plate}\n"
                f"Space: {space.space_id}\n"
                f"Ticket: {ticket_id}\n"
                f"Entry Time: {ticket.entry_time.strftime('%Y-%m-%d %H:%M:%S')}"
            )
            self._clear_register_form()

        except VehicleAlreadyParkedError as e:
            messagebox.showerror("Error", str(e))
        except LotFullError as e:
            messagebox.showerror("Error", str(e))

    def show_manage_parking(self):
        """Show parking management view."""
        self._clear_main_content()
        self._create_header("Manage Parking", "View and manage parking spaces and active tickets")

        # Tabs
        tabview = ctk.CTkTabview(self.main_content, fg_color="transparent", segmented_button_fg_color=QB_LIGHT_GRAY, segmented_button_selected_color=QB_GREEN, segmented_button_selected_hover_color=QB_DARK_GREEN)
        tabview.pack(fill="both", expand=True, padx=30, pady=20)

        tabview.add("Available Spaces")
        tabview.add("Active Tickets")
        tabview.add("All Spaces")

        available_tab = tabview.tab("Available Spaces")
        self._create_spaces_table(available_tab, available_only=True)

        tickets_tab = tabview.tab("Active Tickets")
        self._create_tickets_table(tickets_tab)

        all_spaces_tab = tabview.tab("All Spaces")
        self._create_spaces_table(all_spaces_tab, available_only=False)

    def _create_spaces_table(self, parent, available_only: bool):
        """Create a table showing parking spaces."""
        spaces = self.lot.get_available_spaces() if available_only else self.lot.spaces

        table_frame = ctk.CTkFrame(parent, fg_color=QB_WHITE, corner_radius=12)
        table_frame.pack(fill="both", expand=True, padx=20, pady=20)

        if not spaces:
            ctk.CTkLabel(table_frame, text="No spaces to display", text_color="#9CA3AF", font=ctk.CTkFont(size=14)).pack(pady=40)
            return

        # Scrollable frame
        scroll_frame = ctk.CTkScrollableFrame(table_frame, fg_color="transparent")
        scroll_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Header
        header_frame = ctk.CTkFrame(scroll_frame, height=50, fg_color=QB_LIGHT_GRAY, corner_radius=8)
        header_frame.pack(fill="x", pady=(0, 10))
        header_frame.pack_propagate(False)

        # Use grid for better alignment
        headers = ["Space ID", "Level", "Type", "Status"]
        header_widths = [120, 80, 120, 100]

        for i, (header, width) in enumerate(zip(headers, header_widths)):
            header_label = ctk.CTkLabel(
                header_frame,
                text=header,
                font=ctk.CTkFont(size=13, weight="bold"),
                text_color=QB_TEXT,
                width=width
            )
            header_label.pack(side="left", padx=0)

        # Rows
        for space in spaces:
            row_frame = ctk.CTkFrame(scroll_frame, height=50, fg_color="transparent")
            row_frame.pack(fill="x", pady=5)
            row_frame.pack_propagate(False)

            # Space ID
            ctk.CTkLabel(
                row_frame,
                text=space.space_id,
                font=ctk.CTkFont(size=13),
                width=header_widths[0]
            ).pack(side="left", padx=0)

            # Level
            ctk.CTkLabel(
                row_frame,
                text=str(space.level_number),
                font=ctk.CTkFont(size=13),
                width=header_widths[1]
            ).pack(side="left", padx=0)

            # Type
            ctk.CTkLabel(
                row_frame,
                text=space.space_type.value.capitalize(),
                font=ctk.CTkFont(size=13),
                width=header_widths[2]
            ).pack(side="left", padx=0)

            # Status badge - fixed position
            status_color = QB_SUCCESS if space.is_available() else QB_DANGER
            status_badge = ctk.CTkLabel(
                row_frame,
                text=space.status.value.capitalize(),
                fg_color=status_color,
                corner_radius=6,
                width=header_widths[3],
                height=30,
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color="white"
            )
            status_badge.pack(side="left", padx=0)

    def _create_tickets_table(self, parent):
        """Create a table showing active tickets."""
        active = [t for t in self.active_tickets if t.is_active()]

        table_frame = ctk.CTkFrame(parent, fg_color=QB_WHITE, corner_radius=12)
        table_frame.pack(fill="both", expand=True, padx=20, pady=20)

        if not active:
            ctk.CTkLabel(table_frame, text="No active tickets", text_color="#9CA3AF", font=ctk.CTkFont(size=14)).pack(pady=40)
            return

        # Scrollable frame
        scroll_frame = ctk.CTkScrollableFrame(table_frame, fg_color="transparent")
        scroll_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Header
        header_frame = ctk.CTkFrame(scroll_frame, height=50, fg_color=QB_LIGHT_GRAY, corner_radius=8)
        header_frame.pack(fill="x", pady=(0, 10))
        header_frame.pack_propagate(False)

        # Use grid for better alignment
        headers = ["Ticket", "Plate", "Type", "Space", "Entry Time"]
        header_widths = [100, 120, 120, 100, 80]

        for i, (header, width) in enumerate(zip(headers, header_widths)):
            header_label = ctk.CTkLabel(
                header_frame,
                text=header,
                font=ctk.CTkFont(size=13, weight="bold"),
                text_color=QB_TEXT,
                width=width
            )
            header_label.pack(side="left", padx=0)

        # Rows
        for ticket in active:
            row_frame = ctk.CTkFrame(scroll_frame, height=50, fg_color="transparent")
            row_frame.pack(fill="x", pady=5)
            row_frame.pack_propagate(False)

            # Ticket ID
            ctk.CTkLabel(
                row_frame,
                text=ticket.ticket_id,
                font=ctk.CTkFont(size=13),
                width=header_widths[0]
            ).pack(side="left", padx=0)

            # Plate
            ctk.CTkLabel(
                row_frame,
                text=ticket.vehicle.plate_number,
                font=ctk.CTkFont(size=13),
                width=header_widths[1]
            ).pack(side="left", padx=0)

            # Type
            ctk.CTkLabel(
                row_frame,
                text=ticket.vehicle.vehicle_type.value.capitalize(),
                font=ctk.CTkFont(size=13),
                width=header_widths[2]
            ).pack(side="left", padx=0)

            # Space
            ctk.CTkLabel(
                row_frame,
                text=ticket.parking_space.space_id,
                font=ctk.CTkFont(size=13),
                width=header_widths[3]
            ).pack(side="left", padx=0)

            # Entry Time
            ctk.CTkLabel(
                row_frame,
                text=ticket.entry_time.strftime("%H:%M"),
                font=ctk.CTkFont(size=13),
                width=header_widths[4]
            ).pack(side="left", padx=0)

    def show_process_payment(self):
        """Show payment processing form."""
        self._clear_main_content()
        self._create_header("Process Payment", "Calculate fees and process vehicle exit")

        form_frame = ctk.CTkFrame(self.main_content, fg_color=QB_WHITE, corner_radius=12)
        form_frame.pack(fill="both", expand=True, padx=30, pady=20)

        form_content = ctk.CTkFrame(form_frame, fg_color="transparent")
        form_content.pack(fill="both", expand=True, padx=40, pady=40)

        # Select ticket
        ctk.CTkLabel(form_content, text="Select Active Ticket", font=ctk.CTkFont(size=14, weight="bold"), text_color=QB_TEXT).pack(anchor="w", pady=(0, 10))

        active_tickets = [t for t in self.active_tickets if t.is_active()]
        if not active_tickets:
            ctk.CTkLabel(form_content, text="No active tickets to process", text_color="#9CA3AF", font=ctk.CTkFont(size=16)).pack(pady=40)
            return

        ticket_options = [f"{t.ticket_id} - {t.vehicle.plate_number} ({t.vehicle.vehicle_type.value})" for t in active_tickets]
        self.ticket_selector = ctk.CTkOptionMenu(form_content, values=ticket_options, height=45, corner_radius=8, fg_color=QB_LIGHT_GRAY)
        self.ticket_selector.pack(fill="x", pady=(0, 20))

        # Calculate fee
        calculate_btn = ctk.CTkButton(
            form_content,
            text="Calculate Fee",
            height=45,
            fg_color=QB_DARK_GRAY,
            hover_color=QB_DARK_GRAY,
            font=ctk.CTkFont(size=14, weight="bold"),
            corner_radius=8,
            command=self._calculate_fee
        )
        calculate_btn.pack(fill="x", pady=(0, 15))

        self.fee_label = ctk.CTkLabel(form_content, text="", font=ctk.CTkFont(size=32, weight="bold"), text_color=QB_GREEN)
        self.fee_label.pack(pady=(0, 25))

        # Payment method
        ctk.CTkLabel(form_content, text="Payment Method", font=ctk.CTkFont(size=14, weight="bold"), text_color=QB_TEXT).pack(anchor="w", pady=(0, 10))
        self.payment_method_var = ctk.StringVar(value="Cash")
        method_frame = ctk.CTkFrame(form_content, fg_color=QB_LIGHT_GRAY, corner_radius=8)
        method_frame.pack(fill="x", pady=(0, 25))

        for method in ["Cash", "Card", "Mobile Money"]:
            ctk.CTkRadioButton(method_frame, text=method, variable=self.payment_method_var, value=method, font=ctk.CTkFont(size=14)).pack(side="left", padx=20, pady=10)

        # Payment details entry
        self.payment_details_entry = ctk.CTkEntry(form_content, placeholder_text="Enter amount tendered (e.g., 150)", height=45, corner_radius=8, border_width=2, border_color=QB_BORDER)
        self.payment_details_entry.pack(fill="x", pady=(0, 20))

        # Process button
        process_btn = ctk.CTkButton(
            form_content,
            text="Process Payment & Exit",
            height=50,
            fg_color=QB_GREEN,
            hover_color=QB_DARK_GREEN,
            font=ctk.CTkFont(size=16, weight="bold"),
            corner_radius=8,
            command=self._process_payment
        )
        process_btn.pack(fill="x", pady=(10, 15))

        self.selected_ticket = None
        self.current_fee = 0

        # Update placeholder when payment method changes
        self.payment_method_var.trace_add("write", self._update_payment_placeholder)

    def _update_payment_placeholder(self, *args):
        """Update the payment entry placeholder based on payment method."""
        method = self.payment_method_var.get()
        placeholders = {
            "Cash": "Enter amount tendered (e.g., 150)",
            "Card": "Enter card last 4 digits (e.g., 1234)",
            "Mobile Money": "Enter phone number (e.g., 555-0100)"
        }
        self.payment_details_entry.configure(placeholder_text=placeholders.get(method, ""))

    def _calculate_fee(self):
        """Calculate the fee for the selected ticket."""
        active_tickets = [t for t in self.active_tickets if t.is_active()]
        selection = self.ticket_selector.get()
        if selection:
            ticket_options = [f"{t.ticket_id} - {t.vehicle.plate_number} ({t.vehicle.vehicle_type.value})" for t in active_tickets]
            idx = ticket_options.index(selection)
            self.selected_ticket = active_tickets[idx]
            self.current_fee = self.selected_ticket.calculate_fee()
            self.fee_label.configure(text=f"{self.current_fee} KES")

    def _process_payment(self):
        """Process payment and exit vehicle."""
        if not self.selected_ticket:
            messagebox.showerror("Error", "Please select a ticket and calculate the fee first")
            return

        if self.current_fee == 0:
            messagebox.showerror("Error", "Please calculate the fee first")
            return

        method = self.payment_method_var.get()
        details = self.payment_details_entry.get()

        try:
            if method == "Cash":
                if not details:
                    messagebox.showerror("Error", "Please enter the amount tendered")
                    return
                amount_tendered = float(details)
                if amount_tendered < self.current_fee:
                    messagebox.showerror("Error", f"Insufficient amount. Minimum required: {self.current_fee} KES")
                    return
                payment = CashPayment(f"PAY{len(self.active_tickets)}", self.current_fee, amount_tendered)
            elif method == "Card":
                last_four = details if details else "1234"
                if len(last_four) != 4 or not last_four.isdigit():
                    messagebox.showerror("Error", "Please enter valid 4-digit card number")
                    return
                payment = CardPayment(f"PAY{len(self.active_tickets)}", self.current_fee, last_four)
            else:
                phone = details if details else "555-0100"
                if not phone:
                    messagebox.showerror("Error", "Please enter phone number")
                    return
                payment = MobileMoneyPayment(f"PAY{len(self.active_tickets)}", self.current_fee, phone, "TXNREF")

            payment.process_payment()
            self.selected_ticket.set_payment(payment)

            if self.attendant.verify_payment(self.selected_ticket):
                self.selected_ticket.close_ticket()
                change_info = f"\nChange: {payment.change} KES" if method == "Cash" else ""

                messagebox.showinfo(
                    "Success",
                    f"Payment processed successfully!\n\n"
                    f"Amount: {self.current_fee} KES\n"
                    f"Method: {method}{change_info}\n"
                    f"Duration: {self.selected_ticket.duration} hours\n"
                    f"Space Released: {self.selected_ticket.parking_space.space_id}"
                )

                self.payment_details_entry.delete(0, "end")
                self.fee_label.configure(text="")
                self.selected_ticket = None
                self.current_fee = 0
            else:
                messagebox.showerror("Error", "Payment verification failed")

        except ValueError as e:
            messagebox.showerror("Error", f"Invalid input: {str(e)}")

    def show_reports(self):
        """Show reports."""
        self._clear_main_content()
        self._create_header("Reports", "Detailed parking statistics and breakdowns")

        report_frame = ctk.CTkFrame(self.main_content, fg_color=QB_WHITE, corner_radius=12)
        report_frame.pack(fill="both", expand=True, padx=30, pady=20)

        data = self.lot.generate_report()

        # Summary cards
        summary_frame = ctk.CTkFrame(report_frame, fg_color="transparent")
        summary_frame.pack(fill="x", padx=30, pady=30)

        summaries = [
            ("Total Capacity", data["total_capacity"], QB_GREEN),
            ("Occupied", data["occupied"], QB_WARNING),
            ("Available", data["available"], QB_SUCCESS),
        ]

        for label, value, color in summaries:
            card = ctk.CTkFrame(summary_frame, fg_color=QB_LIGHT_GRAY, corner_radius=12)
            card.pack(side="left", padx=10, expand=True, fill="x")
            ctk.CTkLabel(card, text=label, font=ctk.CTkFont(size=13), text_color="#6B7280").pack(pady=(15, 5))
            ctk.CTkLabel(card, text=str(value), font=ctk.CTkFont(size=28, weight="bold"), text_color=color).pack(pady=(0, 15))

        # Per-level breakdown
        level_frame = ctk.CTkFrame(report_frame, fg_color="transparent")
        level_frame.pack(fill="both", expand=True, padx=30, pady=(0, 20))

        ctk.CTkLabel(level_frame, text="Per-Level Breakdown", font=ctk.CTkFont(size=18, weight="bold"), text_color=QB_TEXT).pack(anchor="w", pady=(20, 15))

        level_scroll = ctk.CTkScrollableFrame(level_frame, fg_color="transparent")
        level_scroll.pack(fill="both", expand=True, padx=30, pady=(0, 20))

        for level, info in data["per_level_breakdown"].items():
            level_card = ctk.CTkFrame(level_scroll, fg_color=QB_LIGHT_GRAY, corner_radius=8)
            level_card.pack(fill="x", pady=8)

            ctk.CTkLabel(level_card, text=f"Level {level}", font=ctk.CTkFont(size=14, weight="bold"), text_color=QB_TEXT).pack(side="left", padx=15, pady=12)
            ctk.CTkLabel(level_card, text=f"Total: {info['total']}", font=ctk.CTkFont(size=13)).pack(side="left", padx=15)
            ctk.CTkLabel(level_card, text=f"Occupied: {info['occupied']}", font=ctk.CTkFont(size=13), text_color=QB_DANGER).pack(side="left", padx=15)
            ctk.CTkLabel(level_card, text=f"Available: {info['available']}", font=ctk.CTkFont(size=13), text_color=QB_SUCCESS).pack(side="left", padx=15)

        # Per-type breakdown
        type_frame = ctk.CTkFrame(report_frame, fg_color="transparent")
        type_frame.pack(fill="both", expand=True, padx=30, pady=(0, 30))

        ctk.CTkLabel(type_frame, text="Per-Type Breakdown", font=ctk.CTkFont(size=18, weight="bold"), text_color=QB_TEXT).pack(anchor="w", pady=(20, 15))

        type_scroll = ctk.CTkScrollableFrame(type_frame, fg_color="transparent")
        type_scroll.pack(fill="both", expand=True, padx=30, pady=(0, 20))

        for space_type, info in data["per_type_breakdown"].items():
            type_card = ctk.CTkFrame(type_scroll, fg_color=QB_LIGHT_GRAY, corner_radius=8)
            type_card.pack(fill="x", pady=8)

            ctk.CTkLabel(type_card, text=space_type.capitalize(), font=ctk.CTkFont(size=14, weight="bold"), text_color=QB_TEXT).pack(side="left", padx=15, pady=12)
            ctk.CTkLabel(type_card, text=f"Total: {info['total']}", font=ctk.CTkFont(size=13)).pack(side="left", padx=15)
            ctk.CTkLabel(type_card, text=f"Occupied: {info['occupied']}", font=ctk.CTkFont(size=13), text_color=QB_DANGER).pack(side="left", padx=15)
            ctk.CTkLabel(type_card, text=f"Available: {info['available']}", font=ctk.CTkFont(size=13), text_color=QB_SUCCESS).pack(side="left", padx=15)

    def _handle_logout(self):
        """Handle user logout."""
        if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
            self.auth_system.logout()
            self.root.destroy()
            # Return to login screen
            from login_gui import LoginWindow
            LoginWindow(self.auth_system, lambda: self.__class__(self.auth_system).run()).run()

    def run(self):
        """Run the GUI application."""
        self.root.mainloop()


def main():
    """Main entry point."""
    app = ParkingSystemGUI()
    app.run()


if __name__ == "__main__":
    main()

import tkinter as tk
from tkinter import messagebox
import ttkbootstrap as ttkb

from validation import (
    SERIAL_PLACEHOLDER,
    VIN_PLACEHOLDER,
    AXLE_PLACEHOLDER,
    GVW_PLACEHOLDER,
    REGISTRATION_PLACEHOLDER,
    is_serial_valid,
    validate_serial_entry,
    is_vin_valid,
    validate_vin_entry,
    is_registration_valid,
    validate_registration_entry,
    is_integer_in_range,
    validate_numeric_range_entry,
)
from logger import write_log

FIELD_ROWS = [
    ("Tag ID Storage", "tag_id"),
    ("Serial Number Storage", "serial"),
    ("TA Certification Storage", "cert"),
    ("GVW/GCW Storage", "gvw"),
    ("VIN Storage", "vin"),
    ("Registration No.", "registration"),
    ("Axle Count Storage", "axle"),
    ("Insurance Information", "insurance"),
]

READ_COMMANDS = {
    "tag_id": "24110100E1F023",        # Read Tag EPC (0x00) -> Hex As-Is
    "serial": "24110101F1D123",        # Serial Reader Number (0x01) -> Alphanumeric
    "vin": "24110102C1B223",           # Trailer VIN (0x02) -> Alphanumeric
    "axle": "24110103D19323",          # Axle Count (0x03) -> Numerical
    "registration": "24110104A17423",  # Registration Number (0x04) -> Alphanumeric
    "gvw": "24110105B15523",           # Trailer Gross Weight (0x05) -> Decimal
    "cert": "24110106813623",          # Meta Data / TA Cert (0x06) -> Hex As-Is
}

PLACEHOLDERS = {
    "serial": SERIAL_PLACEHOLDER,
    "vin": VIN_PLACEHOLDER,
    "axle": AXLE_PLACEHOLDER,
    "gvw": GVW_PLACEHOLDER,
    "registration": REGISTRATION_PLACEHOLDER,
}

PLACEHOLDER_COLOR = "#d0d0d1"
NORMAL_COLOR = "#f8fafc"


class TagFormFrame:
    """Component managing the Tag Data form grid, validation, and individual Read/Write buttons."""

    def __init__(self, parent_frame, root, reader, log_console_getter, reset_reader_status_cb=None):
        self.root = root
        self.reader = reader
        self.get_log_console = log_console_getter
        self.reset_reader_status_cb = reset_reader_status_cb

        self.field_vars = {}
        self.entry_widgets = {}

        self.form_container = tk.LabelFrame(
            parent_frame,
            text="Tag Data",
            padx=20,
            pady=20,
            bg="#1f2937",
            fg="#f8fafc",
            font=("Segoe UI", 12, "bold"),
        )
        self.form_container.pack(side="left", fill="y", padx=(0, 10), pady=(0, 8))
        self.form_container.configure(width=650)
        self.form_container.pack_propagate(False)

        self.form_grid = ttkb.Frame(self.form_container)
        self.form_grid.pack(anchor="nw", padx=5, pady=5)

        self._build_fields()
        self._build_action_buttons()

    def _build_fields(self):
        for row_index, (label_text, var_name) in enumerate(FIELD_ROWS):
            ttkb.Label(self.form_grid, text=label_text, style="Field.TLabel").grid(
                row=row_index * 2, column=0, columnspan=3, sticky="w", pady=(0, 2)
            )

            var = tk.StringVar()
            self.field_vars[var_name] = var
            entry_options = {
                "textvariable": var,
                "width": 34,
                "bootstyle": "info",
                "state": "normal",
            }

            if var_name == "serial":
                entry_options["validate"] = "key"
                entry_options["validatecommand"] = (
                    self.root.register(validate_serial_entry),
                    "%P",
                )
                entry = ttkb.Entry(self.form_grid, **entry_options)
            elif var_name == "vin":
                entry_options["validate"] = "key"
                entry_options["validatecommand"] = (
                    self.root.register(validate_vin_entry),
                    "%P",
                )
                entry = ttkb.Entry(self.form_grid, **entry_options)
            elif var_name == "registration":
                entry_options["validate"] = "key"
                entry_options["validatecommand"] = (
                    self.root.register(validate_registration_entry),
                    "%P",
                )
                entry = ttkb.Entry(self.form_grid, **entry_options)
            elif var_name == "axle":
                entry_options["validate"] = "key"
                entry_options["validatecommand"] = (
                    self.root.register(validate_numeric_range_entry),
                    "%P",
                    5,
                )
                entry = ttkb.Entry(self.form_grid, **entry_options)
            elif var_name == "gvw":
                entry_options["validate"] = "key"
                entry_options["validatecommand"] = (
                    self.root.register(validate_numeric_range_entry),
                    "%P",
                    10,
                )
                entry = ttkb.Entry(self.form_grid, **entry_options)
            else:
                entry = ttkb.Entry(self.form_grid, **entry_options)

            entry.grid(row=row_index * 2 + 1, column=0, sticky="w", pady=(0, 8))
            self.entry_widgets[var_name] = entry

            if var_name in PLACEHOLDERS:
                ph = PLACEHOLDERS[var_name]
                var.set(ph)
                entry.configure(foreground=PLACEHOLDER_COLOR)
                entry.bind("<FocusIn>", lambda e, name=var_name: self._clear_placeholder(e, name))
                entry.bind("<FocusOut>", lambda e, name=var_name: self._restore_placeholder(e, name))

            # Read button alongside field
            ttkb.Button(
                self.form_grid,
                text="Read",
                command=lambda name=var_name: self.read_field(name),
                bootstyle="info",
                width=7,
            ).grid(
                row=row_index * 2 + 1,
                column=1,
                sticky="w",
                padx=(6, 2),
                pady=(0, 8),
            )

            # Write button alongside field
            ttkb.Button(
                self.form_grid,
                text="Write",
                command=lambda name=var_name: self.write_field(name),
                bootstyle="success",
                width=7,
            ).grid(
                row=row_index * 2 + 1,
                column=2,
                sticky="w",
                padx=(2, 0),
                pady=(0, 8),
            )

    def _build_action_buttons(self):
        button_frame = ttkb.Frame(self.form_container)
        button_frame.pack(fill="x", pady=(5, 0))

        button_center = ttkb.Frame(button_frame)
        button_center.pack(anchor="center")

        # Renamed from Write Tag (All) to Read All
        ttkb.Button(
            button_center,
            text="Read All",
            command=self.read_all_fields,
            bootstyle="info",
            width=16,
        ).pack(side="left", padx=(0, 12))

        ttkb.Button(
            button_center,
            text="Clear Form",
            command=self.clear_fields,
            bootstyle="warning",
            width=16,
        ).pack(side="left")

    def _clear_placeholder(self, event, var_name: str):
        ph = PLACEHOLDERS.get(var_name, "")
        if self.field_vars[var_name].get() == ph:
            self.field_vars[var_name].set("")
            event.widget.configure(foreground=NORMAL_COLOR)

    def _restore_placeholder(self, event, var_name: str):
        ph = PLACEHOLDERS.get(var_name, "")
        if self.field_vars[var_name].get().strip() == "":
            self.field_vars[var_name].set(ph)
            event.widget.configure(foreground=PLACEHOLDER_COLOR)

    def get_field_value(self, field_name: str) -> str:
        val = self.field_vars[field_name].get().strip()
        if field_name in PLACEHOLDERS and val == PLACEHOLDERS[field_name]:
            return ""
        return val

    def set_field_value(self, field_name: str, value: str):
        if field_name in self.field_vars:
            self.field_vars[field_name].set(value)
            widget = self.entry_widgets.get(field_name)
            if widget:
                widget.configure(foreground=NORMAL_COLOR)

    def read_field(self, field_name: str):
        log_console = self.get_log_console()

        if field_name in READ_COMMANDS:
            cmd_hex = READ_COMMANDS[field_name]
            cmd_bytes = bytes.fromhex(cmd_hex)
            if self.reader.is_connected():
                self.reader.write_bytes(cmd_bytes)
                write_log(f"UART TX (hex): {cmd_hex.upper()}", log_console)
                write_log(f"Read command sent for {field_name.replace('_', ' ').title()}", log_console)
            else:
                write_log(f"Read command failed for {field_name}: reader not connected", log_console)
                messagebox.showwarning("Read Field", "Connect the reader before reading.")
        else:
            value = self.get_field_value(field_name)
            if value:
                write_log(f"Read field '{field_name}' : {value}", log_console)
                messagebox.showinfo("Read Field", f"{field_name.replace('_', ' ').title()} loaded.")
            else:
                write_log(f"Read field '{field_name}' is empty", log_console)
                messagebox.showwarning("Read Field", "This field is empty.")

    def read_all_fields(self):
        """Sequentially transmit Read commands for all fields spaced 200ms apart."""
        log_console = self.get_log_console()

        if not self.reader.is_connected():
            write_log("Read All failed: reader not connected", log_console)
            messagebox.showwarning("Read All", "Connect the reader before reading fields.")
            return

        write_log("Starting Read All fields sequence...", log_console)
        commands = list(READ_COMMANDS.items())
        interval_ms = 200  # 200ms delay between command transmissions

        def _send_next(index=0):
            if index >= len(commands):
                write_log("Read All sequence completed dispatching.", log_console)
                return

            field_name, cmd_hex = commands[index]
            if self.reader.is_connected():
                cmd_bytes = bytes.fromhex(cmd_hex)
                self.reader.write_bytes(cmd_bytes)
                write_log(
                    f"UART TX (hex): {cmd_hex.upper()} [{field_name.replace('_', ' ').title()}]",
                    log_console,
                )

            # Schedule next field request after interval_ms
            self.root.after(interval_ms, lambda: _send_next(index + 1))

        _send_next(0)

    def write_field(self, field_name: str):
        log_console = self.get_log_console()
        val = self.get_field_value(field_name)

        if field_name == "vin":
            if not val:
                write_log("Write VIN failed: VIN box is empty", log_console)
                messagebox.showwarning("Write Field", "Please enter a VIN before writing.")
                return
            if not is_vin_valid(val):
                write_log(
                    "Write VIN failed: VIN must be exactly 17 alphanumeric characters",
                    log_console,
                )
                messagebox.showerror(
                    "Validation Error",
                    "VIN must be exactly 17 alphanumeric characters.",
                )
                return

            # Convert 17 ASCII characters to hex bytes (padded with 0x00 if needed)
            vin_ascii_bytes = val.encode("ascii").ljust(17, b"\x00")
            header_bytes = bytes.fromhex("24120102")  # Start $ (24), Write Cmd (12), Param ID (01 02)
            footer_bytes = bytes.fromhex("C1B223")    # Checksum (C1 B2), End # (23)

            full_frame = header_bytes + vin_ascii_bytes + footer_bytes
            frame_hex = full_frame.hex().upper()

            if self.reader.is_connected():
                self.reader.write_bytes(full_frame)
                write_log(f"UART TX (hex): {frame_hex}", log_console)
                write_log(f"Write VIN command sent for: {val}", log_console)
                messagebox.showinfo("Write VIN", f"VIN write frame transmitted:\n{frame_hex}")
            else:
                write_log("Write VIN command failed: reader not connected", log_console)
                messagebox.showwarning("Write Field", "Connect the reader before writing VIN.")

        else:
            if val:
                write_log(f"Write request submitted for '{field_name}' : {val}", log_console)
                messagebox.showinfo("Write Field", f"Write data for {field_name.replace('_', ' ').title()} prepared.")
            else:
                write_log(f"Write field '{field_name}' is empty", log_console)
                messagebox.showwarning("Write Field", "Please enter data before writing.")

    def clear_fields(self):
        for name, var in self.field_vars.items():
            var.set("")
            if name in PLACEHOLDERS:
                ph = PLACEHOLDERS[name]
                var.set(ph)
                widget = self.entry_widgets.get(name)
                if widget:
                    widget.configure(foreground=PLACEHOLDER_COLOR)

        if callable(self.reset_reader_status_cb):
            self.reset_reader_status_cb()

        write_log("Form cleared", self.get_log_console())

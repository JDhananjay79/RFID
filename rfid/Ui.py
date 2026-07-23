import os
import tkinter as tk
from tkinter import messagebox, filedialog
import ttkbootstrap as ttkb
from pathlib import Path
from PIL import Image, ImageTk
from serial.tools import list_ports
from config import PORT, BAUDRATE, LOG_DEFAULT_PATH
from logger import write_log
from rfid.event_logger import LogConsole
from rfid.serial_port import SerialReader

logging_enabled = False
reader = SerialReader(PORT, BAUDRATE)

root = ttkb.Window(themename="darkly")
root.geometry("2000x900")
root.minsize(1300, 900)
root.title("RFID Communicator")

style = ttkb.Style(theme="darkly")
style.configure("Card.TFrame", background="#223446")
style.configure("Title.TLabel", font=("Segoe UI", 22, "bold"), foreground="#F8FAFC")
style.configure("Section.TLabel", font=("Segoe UI", 11, "bold"), foreground="#E2E8F0")
style.configure("Field.TLabel", font=("Segoe UI", 10), foreground="#E2E8F0")
style.configure("Caption.TLabel", font=("Segoe UI", 9), foreground="#94a3b8")
style.configure("Status.TLabel", font=("Segoe UI", 10, "bold"), foreground="#A5B4FC")
style.configure("Value.TLabel", font=("Segoe UI", 10), foreground="#E2E8F0")
style.configure("Card.TFrame", background="#1f2937")

main_frame = ttkb.Frame(root)
main_frame.pack(fill="both", expand=True)

BASE_DIR = Path(__file__).resolve().parent
icon_path = BASE_DIR.parent / "assets" / "Acc_logo.ico"
if icon_path.exists():
    try:
        root.iconbitmap(str(icon_path))
    except Exception:
        pass

header_frame = ttkb.Frame(main_frame)
header_frame.pack(fill="x", pady=(0, 15), padx=15)

logo_path = BASE_DIR.parent / "assets" / "Acc_logo.png"
photo = None
if logo_path.exists():
    image = Image.open(logo_path)
    image = image.resize((120, 80))
    photo = ImageTk.PhotoImage(image)

if photo:
    logo_label = ttkb.Label(header_frame, image=photo, bootstyle="light")
    logo_label.image = photo
    logo_label.pack(side="left", padx=(0, 20), pady=(10, 10))

header_text = ttkb.Label(header_frame, text="Event-Based Parameter Reader & Writer", style="Title.TLabel")
header_text.pack(side="left", pady=10)

version_label = ttkb.Label(
    header_frame,
    text="Version: 1.0.0",
    style="Field.TLabel",
)
version_label.pack(side="right", pady=10)

content_frame = ttkb.Frame(main_frame)
content_frame.pack(fill="both", expand=True, padx=15, pady=(0, 15))

# Tag Data section
form_container = tk.LabelFrame(
    content_frame,
    text="Tag Data",
    padx=20,
    pady=20,
    bg="#1f2937",
    fg="#f8fafc",
    font=("Segoe UI", 12, "bold"),
)
form_container.pack(side="left", fill="y", padx=(0, 10), pady=(0, 8))
form_container.configure(width=620)
form_container.pack_propagate(False)

form_grid = ttkb.Frame(form_container)
form_grid.pack(anchor="nw", padx=10, pady=10)

def detect_com_ports():
    try:
        ports = [port.device for port in list_ports.comports()]
        return sorted(ports)
    except Exception:
        return []


serial_placeholder = "(Alphanumeric: Max 16 characters)"
serial_placeholder_color = "#d0d0d1"
serial_normal_color = "#f8fafc"


def is_serial_valid(value: str) -> bool:
    return len(value) == 16 and value.isalnum()


def validate_serial_entry(new_value: str) -> bool:
    if new_value == "" or new_value == serial_placeholder:
        return True
    return len(new_value) <= 16 and new_value.isalnum()


def clear_serial_placeholder(event):
    current = field_vars["serial"].get()
    if current == serial_placeholder:
        field_vars["serial"].set("")
        event.widget.configure(foreground=serial_normal_color)


def restore_serial_placeholder(event):
    current = field_vars["serial"].get().strip()
    if current == "":
        field_vars["serial"].set(serial_placeholder)
        event.widget.configure(foreground=serial_placeholder_color)


def is_vin_valid(value: str) -> bool:
    return len(value) == 17 and value.isalnum()


def validate_vin_entry(new_value: str) -> bool:
    if new_value == "":
        return True
    return len(new_value) <= 17 and new_value.isalnum()


def is_registration_valid(value: str) -> bool:
    return len(value) == 12 and value.isalnum()


def validate_registration_entry(new_value: str) -> bool:
    if new_value == "":
        return True
    return len(new_value) <= 12 and new_value.isalnum()


def is_integer_in_range(value: str, min_value: int, max_value: int) -> bool:
    if not value.isdigit():
        return False
    try:
        numeric = int(value)
    except ValueError:
        return False
    return min_value <= numeric <= max_value


def validate_numeric_range_entry(new_value: str, max_digits: int) -> bool:
    if new_value == "":
        return True
    return len(new_value) <= max_digits and new_value.isdigit()


field_vars = {}
serial_entry_widget = None
field_rows = [
    ("Tag ID Storage", "tag_id"),
    ("Serial Number Storage", "serial"),
    ("TA Certification Storage", "cert"),
    ("GVW/GCW Storage", "gvw"),
    ("VIN Storage", "vin"),
    ("Registration No.", "registration"),
    ("Axle Count Storage", "axle"),
    ("Insurance Information", "insurance"),
]

for row_index, (label_text, var_name) in enumerate(field_rows):
    ttkb.Label(form_grid, text=label_text, style="Field.TLabel").grid(
        row=row_index * 2, column=0, columnspan=2, sticky="w", pady=(0, 4)
    )

    field_vars[var_name] = tk.StringVar()
    entry_state = "normal"
    entry_options = {
        "textvariable": field_vars[var_name],
        "width": 38,
        "bootstyle": "info",
        "state": entry_state,
    }
    if var_name == "serial":
        entry_options["validate"] = "key"
        entry_options["validatecommand"] = (root.register(validate_serial_entry), "%P")
        serial_entry_widget = ttkb.Entry(form_grid, **entry_options)
        serial_entry_widget.grid(row=row_index * 2 + 1, column=0, sticky="w", pady=(0, 10))
        serial_entry_widget.bind("<FocusIn>", clear_serial_placeholder)
        serial_entry_widget.bind("<FocusOut>", restore_serial_placeholder)
        field_vars["serial"].set(serial_placeholder)
        serial_entry_widget.configure(foreground=serial_placeholder_color)
    elif var_name == "vin":
        entry_options["validate"] = "key"
        entry_options["validatecommand"] = (root.register(validate_vin_entry), "%P")
        ttkb.Entry(form_grid, **entry_options).grid(row=row_index * 2 + 1, column=0, sticky="w", pady=(0, 10))
    elif var_name == "registration":
        entry_options["validate"] = "key"
        entry_options["validatecommand"] = (root.register(validate_registration_entry), "%P")
        ttkb.Entry(form_grid, **entry_options).grid(row=row_index * 2 + 1, column=0, sticky="w", pady=(0, 10))
    elif var_name == "axle":
        entry_options["validate"] = "key"
        entry_options["validatecommand"] = (root.register(validate_numeric_range_entry), "%P", 5)
        ttkb.Entry(form_grid, **entry_options).grid(row=row_index * 2 + 1, column=0, sticky="w", pady=(0, 10))
    elif var_name == "gvw":
        entry_options["validate"] = "key"
        entry_options["validatecommand"] = (root.register(validate_numeric_range_entry), "%P", 10)
        ttkb.Entry(form_grid, **entry_options).grid(row=row_index * 2 + 1, column=0, sticky="w", pady=(0, 10))
    else:
        ttkb.Entry(form_grid, **entry_options).grid(row=row_index * 2 + 1, column=0, sticky="w", pady=(0, 10))
    ttkb.Button(
        form_grid,
        text="Read",
        command=lambda name=var_name: read_field(name),
        bootstyle="info",
        width=10,
    ).grid(row=row_index * 2 + 1, column=1, sticky="w", padx=(10, 0), pady=(0, 10),)

button_frame = ttkb.Frame(form_container)
button_frame.pack(fill="x", pady=(1, 0))

button_center = ttkb.Frame(button_frame)
button_center.pack(anchor="center")
def get_field_value(field_name: str) -> str:
    value = field_vars[field_name].get().strip()
    if field_name == "serial" and value == serial_placeholder:
        return ""
    return value


def read_field(field_name):
    value = get_field_value(field_name)
    if value:
        write_log(f"Read field '{field_name}' : {value}", log_console)
        messagebox.showinfo("Read Field", f"{field_name.replace('_', ' ').title()} loaded.")
    else:
        write_log(f"Read field '{field_name}' is empty", log_console)
        messagebox.showwarning("Read Field", "This field is empty.")


def write_tag():
    serial_value = field_vars["serial"].get().strip()
    if serial_value and not is_serial_valid(serial_value):
        write_log(
            "Write Tag failed: Serial Number Storage must be exactly 16 alphanumeric characters",
            log_console,
        )
        messagebox.showerror(
            "Validation Error",
            "Serial Number Storage must be exactly 16 alphanumeric characters.",
        )
        return

    vin_value = field_vars["vin"].get().strip()
    if vin_value and not is_vin_valid(vin_value):
        write_log(
            "Write Tag failed: VIN Storage must be exactly 17 alphanumeric characters",
            log_console,
        )
        messagebox.showerror(
            "Validation Error",
            "VIN Storage must be exactly 17 alphanumeric characters.",
        )
        return

    registration_value = field_vars["registration"].get().strip()
    if registration_value and not is_registration_valid(registration_value):
        write_log(
            "Write Tag failed: Registration No. must be exactly 12 alphanumeric characters",
            log_console,
        )
        messagebox.showerror(
            "Validation Error",
            "Registration No. must be exactly 12 alphanumeric characters.",
        )
        return

    axle_value = field_vars["axle"].get().strip()
    if axle_value:
        if not axle_value.isdigit():
            write_log(
                "Write Tag failed: Axle Count Storage must contain only numeric digits",
                log_console,
            )
            messagebox.showerror(
                "Validation Error",
                "Axle Count Storage must contain only numeric digits.",
            )
            return
        if not is_integer_in_range(axle_value, 0, 65535):
            write_log(
                "Write Tag failed: Axle Count Storage must be between 0 and 65535",
                log_console,
            )
            messagebox.showerror(
                "Validation Error",
                "Axle Count Storage must be a number between 0 and 65535.",
            )
            return

    gvw_value = field_vars["gvw"].get().strip()
    if gvw_value:
        if not gvw_value.isdigit():
            write_log(
                "Write Tag failed: GVW/GCW Storage must contain only numeric digits",
                log_console,
            )
            messagebox.showerror(
                "Validation Error",
                "GVW/GCW Storage must contain only numeric digits.",
            )
            return
        if not is_integer_in_range(gvw_value, 0, 4294967295):
            write_log(
                "Write Tag failed: GVW/GCW Storage must be between 0 and 4294967295",
                log_console,
            )
            messagebox.showerror(
                "Validation Error",
                "GVW/GCW Storage must be a number between 0 and 4294967295.",
            )
            return

    values = [field_vars[name].get().strip() for _, name in field_rows]
    if any(values):
        write_log("Write Tag request submitted", log_console)
        messagebox.showinfo("Write Tag", "Tag data is ready to write.")
    else:
        write_log("Write Tag failed: no tag fields entered", log_console)
        messagebox.showwarning("Write Tag", "Enter at least one field before writing.")


def clear_fields():
    for var in field_vars.values():
        var.set("")
    reader_status.set("Idle")
    tag_present.set("No")
    write_log("Form cleared", log_console)

write_button = ttkb.Button(
    button_center,
    text="Write Tag",
    command=write_tag,
    bootstyle="success",
    width=16,
)
write_button.pack(side="left", padx=(0, 12))

clear_button = ttkb.Button(
    button_center,
    text="Clear",
    command=clear_fields,
    bootstyle="warning",
    width=16,
)
clear_button.pack(side="left")

# Right side panel
right_panel = ttkb.Frame(content_frame)
right_panel.pack(side="right", fill="both", expand=True)

# Top row for Communication, Reader, and Read Existing Tag
top_row = ttkb.Frame(right_panel)
top_row.pack(fill="x", pady=(0, 12))

# Communication section
communication_frame = tk.LabelFrame(
    top_row,
    text="Communication",
    padx=18,
    pady=18,
    bg="#1f2937",
    fg="#f8fafc",
    font=("Segoe UI", 11, "bold"),
)
communication_frame.pack(side="left", fill="y", expand=False, padx=(0, 10), pady=(0, 4))
communication_frame.configure(width=400)
communication_frame.columnconfigure(1, weight=1)
communication_frame.columnconfigure(3, weight=1)

medium_var = tk.StringVar(value="UART")
port_var = tk.StringVar(value=PORT)
baud_var = tk.StringVar(value=str(BAUDRATE))
status_var = tk.StringVar(value="Disconnected")

available_ports = detect_com_ports()
if not available_ports:
    available_ports = ["COM1", "COM2", "COM3", "COM4", "COM5"]

default_port = PORT if PORT in available_ports else (available_ports[0] if available_ports else PORT)
port_var = tk.StringVar(value=default_port)
available_baud_rates = ["9600", "19200", "38400", "57600", "115200"]

port_combobox = None
for label_text, variable, values in [
    ("Medium", medium_var, ["UART", "PCAN"]),
    ("COM Port", port_var, available_ports),
    ("Baud Rate", baud_var, available_baud_rates),
]:
    if label_text == "Medium":
        row = 0
        col = 0
    elif label_text == "COM Port":
        row = 0
        col = 2
    else:
        row = 1
        col = 0

    ttkb.Label(communication_frame, text=label_text, style="Field.TLabel").grid(
        row=row, column=col, sticky="w", pady=(0, 10)
    )
    combobox = ttkb.Combobox(
        communication_frame,
        textvariable=variable,
        values=values,
        state="readonly",
        bootstyle="info",
        width=18,
    )
    if label_text == "Medium":
        grid_padx = (12, 24)
    elif label_text == "COM Port":
        grid_padx = (12, 0)
    else:
        grid_padx = (12, 0)
    if label_text == "Baud Rate":
        grid_pady = (0, 16)
    else:
        grid_pady = (0, 10)
    combobox.grid(row=row, column=col + 1, sticky="w", padx=grid_padx, pady=grid_pady)
    if label_text == "COM Port":
        port_combobox = combobox

if port_combobox is not None:
    port_combobox.configure(values=available_ports)

button_frame_comm = ttkb.Frame(communication_frame)
button_frame_comm.grid(row=2, column=0, columnspan=3, pady=(16, 0), sticky="ew")
button_frame_comm.columnconfigure(0, weight=1)
button_frame_comm.columnconfigure(1, weight=1)
button_frame_comm.columnconfigure(2, weight=1)

connect_button = ttkb.Button(
    button_frame_comm,
    text="Connect",
    command=lambda: connect_reader(),
    bootstyle="success",
)
connect_button.grid(row=0, column=0, sticky="ew", padx=(0, 14))

disconnect_button = ttkb.Button(
    button_frame_comm,
    text="Disconnect",
    command=lambda: disconnect_reader(),
    bootstyle="danger",
    state="disabled",
)
disconnect_button.grid(row=0, column=1, sticky="ew", padx=(14, 14))

status_frame = ttkb.Frame(button_frame_comm)
status_frame.grid(row=0, column=2, sticky="w", padx=(14, 0))
status_label = ttkb.Label(
    status_frame,
    text="Status:",
    style="Field.TLabel",
)
status_label.pack(side="left", padx=(0, 4))
status_value = ttkb.Label(
    status_frame,
    textvariable=status_var,
    style="Value.TLabel",
)
status_value.pack(side="left")

# Reader section
reader_frame = tk.LabelFrame(
    top_row,
    text="Reader",
    padx=18,
    pady=18,
    bg="#1f2937",
    fg="#f8fafc",
    font=("Segoe UI", 11, "bold"),
)
reader_frame.pack(side="left", fill="y", padx=(0, 10), expand=False)
reader_frame.configure(width=260)
reader_frame.columnconfigure(1, weight=1)
reader_frame.columnconfigure(3, weight=1)

reader_status = tk.StringVar(value="Idle")
tag_present = tk.StringVar(value="No")

status_title = ttkb.Label(reader_frame, text="Status:", style="Field.TLabel")
status_title.grid(row=0, column=0, sticky="w", pady=(0, 10))
status_value = ttkb.Label(reader_frame, textvariable=reader_status, style="Value.TLabel")
status_value.grid(row=0, column=1, sticky="w", padx=(10, 36), pady=(0, 10))

present_title = ttkb.Label(reader_frame, text="Tag Present:", style="Field.TLabel")
present_title.grid(row=0, column=2, sticky="w", pady=(0, 10))
present_value = ttkb.Label(reader_frame, textvariable=tag_present, style="Value.TLabel")
present_value.grid(row=0, column=3, sticky="w", padx=(10, 0), pady=(0, 10))

reader_button_frame = ttkb.Frame(reader_frame)
reader_button_frame.grid(row=1, column=0, columnspan=4, pady=(16, 0), sticky="ew")
reader_button_frame.columnconfigure(0, weight=1)
reader_button_frame.columnconfigure(1, weight=1)

start_scan_button = ttkb.Button(
    reader_button_frame,
    text="Start Scan",
    command=lambda: start_scan(),
    bootstyle="info",
    state="disabled",
)
start_scan_button.grid(row=0, column=0, sticky="ew", padx=(0, 14))

stop_scan_button = ttkb.Button(
    reader_button_frame,
    text="Stop Scan",
    command=lambda: stop_scan(),
    bootstyle="secondary",
    state="disabled",
)
stop_scan_button.grid(row=0, column=1, sticky="ew", padx=(14, 0))

# Activity log section
log_frame = tk.LabelFrame(
    right_panel,
    text="Activity Log",
    padx=10,
    pady=10,
    bg="#1f2937",
    fg="#f8fafc",
    font=("Segoe UI", 11, "bold"),
)
log_frame.pack(fill="both", expand=True, pady=(0, 8))
log_frame.pack_propagate(False)

controls_subframe = ttkb.Frame(log_frame)
controls_subframe.pack(fill="x", pady=(0, 8))

auto_save_var = tk.BooleanVar(value=False)
log_path_var = tk.StringVar(value=LOG_DEFAULT_PATH)

def browse_log_path():
    path = filedialog.asksaveasfilename(
        parent=root,
        title="Select log file",
        defaultextension=".log",
        filetypes=[("Log files", "*.log"), ("All files", "*")],
    )
    if path:
        log_path_var.set(path)
        log_console.set_file_path(path)


def toggle_auto_save():
    enabled = bool(auto_save_var.get())
    log_console.enable_auto_save(enabled)
    write_log(f"Auto-save {'enabled' if enabled else 'disabled'}", log_console)


auto_save_cb = ttkb.Checkbutton(
    controls_subframe,
    text="Auto Save Logs",
    variable=auto_save_var,
    command=toggle_auto_save,
    bootstyle="info",
)
auto_save_cb.pack(side="left", padx=(0, 8))

log_path_entry = ttkb.Entry(
    controls_subframe,
    textvariable=log_path_var,
    width=80,
    bootstyle="info",
)
log_path_entry.pack(side="left", expand=True, padx=(0, 8))

browse_btn = ttkb.Button(
    controls_subframe,
    text="Browse",
    command=browse_log_path,
    bootstyle="secondary",
)
browse_btn.pack(side="left")

clear_log_btn = ttkb.Button(
    controls_subframe,
    text="Clear Log",
    command=lambda: clear_log_console(),
    bootstyle="secondary",
)
clear_log_btn.pack(side="left", padx=(8, 0))

log_console = LogConsole(log_frame)
log_console.set_file_path(log_path_var.get())
log_console.pack(fill="both", expand=True)

write_log("RFID Communicator started", log_console)

def _set_connection_state(connected: bool):
    if connected:
        status_var.set("Connected")
        connect_button.configure(state="disabled")
        disconnect_button.configure(state="normal")
        start_scan_button.configure(state="normal")
        stop_scan_button.configure(state="normal")
    else:
        status_var.set("Disconnected")
        reader_status.set("Idle")
        tag_present.set("No")
        connect_button.configure(state="normal")
        disconnect_button.configure(state="disabled")
        start_scan_button.configure(state="disabled")
        stop_scan_button.configure(state="disabled")


def clear_log_console():
    log_console.clear()


def populate_com_ports():
    ports = detect_com_ports()
    if not ports:
        ports = ["COM1", "COM2", "COM3", "COM4", "COM5"]
    port_combobox.configure(values=ports)
    if port_var.get() not in ports:
        port_var.set(ports[0])

populate_com_ports()


def connect_reader():
    if reader.is_connected():
        write_log("Reader already connected", log_console)
        return

    selected_port = "COM3"
    port_var.set(selected_port)
    port_combobox.configure(values=[selected_port])
    success = reader.connect(
        port=selected_port,
        baudrate=int(baud_var.get()),
    )
    if success:
        _set_connection_state(True)
        write_log(f"Connected to {selected_port} @ {baud_var.get()}", log_console)
        port_var.set(selected_port)
    else:
        _set_connection_state(False)
        write_log("Failed to connect", log_console)


def disconnect_reader():
    reader.disconnect()
    _set_connection_state(False)
    write_log("Disconnected from reader", log_console)


def start_scan():
    if not reader.is_connected():
        messagebox.showwarning("Start Scan", "Connect the reader before scanning.")
        return
    reader_status.set("Scanning")
    if reader.write_line("SCAN\n"):
        write_log("Start scan command sent", log_console)
    else:
        write_log("Failed to send scan command", log_console)


def stop_scan():
    if not reader.is_connected():
        return
    reader_status.set("Idle")
    write_log("Stop scan", log_console)


def update_gui():
    while True:
        data = reader.get_data()
        if data is None:
            break
        write_log(f"UART RX : {data}", log_console)
        if data.startswith("TAG:"):
            tag = data.replace("TAG:", "").strip()
            field_vars["tag_id"].set(tag)
            tag_present.set("Yes")
            reader_status.set("Tag detected")
            write_log(f"Tag detected: {tag}", log_console)
    root.after(100, update_gui)


def on_close():
    try:
        reader.stop()
    except Exception:
        pass
    try:
        root.destroy()
    except Exception:
        pass


def toggle_logging(event=None):
    global logging_enabled
    logging_enabled = not logging_enabled
    write_log("Logging Started" if logging_enabled else "Logging Stopped", log_console)

root.bind("<space>", toggle_logging)
root.after(100, update_gui)
root.protocol("WM_DELETE_WINDOW", on_close)

if __name__ == "__main__":
    root.mainloop()

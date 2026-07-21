import os
import tkinter as tk
from tkinter import messagebox, filedialog
import ttkbootstrap as ttkb
from pathlib import Path
from PIL import Image, ImageTk
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

header_text = ttkb.Label(header_frame, text="RFID Tag Writer", style="Title.TLabel")
header_text.pack(side="left", pady=10)

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
form_container.configure(width=420)
form_container.pack_propagate(False)

form_grid = ttkb.Frame(form_container)
form_grid.pack(anchor="nw", padx=10, pady=10)

field_vars = {}
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
        row=row_index * 2, column=0, sticky="w", pady=(0, 4)
    )
    field_vars[var_name] = tk.StringVar()
    ttkb.Entry(
        form_grid,
        textvariable=field_vars[var_name],
        width=33,
        bootstyle="info",
    ).grid(row=row_index * 2 + 1, column=0, sticky="w", pady=(0, 10))

button_frame = ttkb.Frame(form_container)
button_frame.pack(fill="x", pady=(10, 0))

existing_tag_var = tk.StringVar()

def write_tag():
    values = [field_vars[name].get().strip() for _, name in field_rows]
    if all(values):
        write_log("Write Tag request submitted", log_console)
        messagebox.showinfo("Write Tag", "Tag data is ready to write.")
    else:
        messagebox.showwarning("Write Tag", "Fill all tag fields before writing.")


def clear_fields():
    for var in field_vars.values():
        var.set("")
    existing_tag_var.set("")
    reader_status.set("Idle")
    tag_present.set("No")
    write_log("Form cleared", log_console)

read_button = ttkb.Button(
    button_frame,
    text="Read Tag",
    command=lambda: read_existing_tag(),
    bootstyle="secondary",
)
read_button.pack(side="left", expand=True, fill="x", padx=(0, 8))

write_button = ttkb.Button(
    button_frame,
    text="Write Tag",
    command=write_tag,
    bootstyle="success",
)
write_button.pack(side="left", expand=True, fill="x", padx=(0, 8))

clear_button = ttkb.Button(
    button_frame,
    text="Clear",
    command=clear_fields,
    bootstyle="warning",
)
clear_button.pack(side="left", expand=True, fill="x")

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
    padx=16,
    pady=16,
    bg="#1f2937",
    fg="#f8fafc",
    font=("Segoe UI", 11, "bold"),
)
communication_frame.pack(side="left", fill="both", expand=True, padx=(0, 8))

medium_var = tk.StringVar(value="UART")
port_var = tk.StringVar(value=PORT)
baud_var = tk.StringVar(value=str(BAUDRATE))
status_var = tk.StringVar(value="Disconnected")

available_ports = ["COM1", "COM2", "COM3", "COM4", "COM5"]
available_baud_rates = ["9600", "19200", "38400", "57600", "115200"]

for row_index, (label_text, variable, values) in enumerate([
    ("Medium", medium_var, ["UART", "PCAN"]),
    ("COM Port", port_var, available_ports),
    ("Baud Rate", baud_var, available_baud_rates),
]):
    ttkb.Label(communication_frame, text=label_text, style="Field.TLabel").grid(
        row=row_index, column=0, sticky="w", pady=(0, 6)
    )
    ttkb.Combobox(
        communication_frame,
        textvariable=variable,
        values=values,
        state="readonly",
        bootstyle="info",
        width=20,
    ).grid(row=row_index, column=1, sticky="w", padx=(10, 0), pady=(0, 6))

status_label = ttkb.Label(
    communication_frame,
    text="Status:",
    style="Field.TLabel",
)
status_label.grid(row=3, column=0, sticky="w", pady=(8, 0))
status_value = ttkb.Label(
    communication_frame,
    textvariable=status_var,
    style="Value.TLabel",
)
status_value.grid(row=3, column=1, sticky="w", padx=(10, 0), pady=(8, 0))

button_frame_comm = ttkb.Frame(communication_frame)
button_frame_comm.grid(row=4, column=0, columnspan=2, pady=(12, 0), sticky="ew")
button_frame_comm.columnconfigure(0, weight=1)
button_frame_comm.columnconfigure(1, weight=1)

connect_button = ttkb.Button(
    button_frame_comm,
    text="Connect",
    command=lambda: connect_reader(),
    bootstyle="success",
)
connect_button.grid(row=0, column=0, sticky="ew", padx=(0, 6))

disconnect_button = ttkb.Button(
    button_frame_comm,
    text="Disconnect",
    command=lambda: disconnect_reader(),
    bootstyle="danger",
    state="disabled",
)
disconnect_button.grid(row=0, column=1, sticky="ew", padx=(6, 0))

# Reader section
reader_frame = tk.LabelFrame(
    top_row,
    text="Reader",
    padx=16,
    pady=16,
    bg="#1f2937",
    fg="#f8fafc",
    font=("Segoe UI", 11, "bold"),
)
reader_frame.pack(side="left", fill="both", expand=True, padx=(0, 8))

reader_status = tk.StringVar(value="Idle")
tag_present = tk.StringVar(value="No")

status_title = ttkb.Label(reader_frame, text="Status:", style="Field.TLabel")
status_title.grid(row=0, column=0, sticky="w", pady=(0, 6))
status_value = ttkb.Label(reader_frame, textvariable=reader_status, style="Value.TLabel")
status_value.grid(row=0, column=1, sticky="w", padx=(10, 0), pady=(0, 6))

present_title = ttkb.Label(reader_frame, text="Tag Present:", style="Field.TLabel")
present_title.grid(row=1, column=0, sticky="w", pady=(0, 6))
present_value = ttkb.Label(reader_frame, textvariable=tag_present, style="Value.TLabel")
present_value.grid(row=1, column=1, sticky="w", padx=(10, 0), pady=(0, 6))

reader_button_frame = ttkb.Frame(reader_frame)
reader_button_frame.grid(row=2, column=0, columnspan=2, pady=(12, 0), sticky="ew")
reader_button_frame.columnconfigure(0, weight=1)
reader_button_frame.columnconfigure(1, weight=1)

start_scan_button = ttkb.Button(
    reader_button_frame,
    text="Start Scan",
    command=lambda: start_scan(),
    bootstyle="info",
    state="disabled",
)
start_scan_button.grid(row=0, column=0, sticky="ew", padx=(0, 6))

stop_scan_button = ttkb.Button(
    reader_button_frame,
    text="Stop Scan",
    command=lambda: stop_scan(),
    bootstyle="secondary",
    state="disabled",
)
stop_scan_button.grid(row=0, column=1, sticky="ew", padx=(6, 0))

# Read Existing Tag section
existing_tag_frame = tk.LabelFrame(
    top_row,
    text="Read Existing Tag",
    padx=16,
    pady=16,
    bg="#1f2937",
    fg="#f8fafc",
    font=("Segoe UI", 11, "bold"),
)
existing_tag_frame.pack(side="left", fill="both", expand=True)

existing_tag_var = tk.StringVar()

ttkb.Label(existing_tag_frame, text="Tag ID", style="Field.TLabel").grid(
    row=0, column=0, sticky="w", pady=(0, 6)
)

ttkb.Entry(
    existing_tag_frame,
    textvariable=existing_tag_var,
    width=40,
    bootstyle="info",
).grid(row=1, column=0, sticky="ew", pady=(0, 10))

read_existing_button = ttkb.Button(
    existing_tag_frame,
    text="Read",
    command=lambda: read_existing_tag(),
    bootstyle="primary",
)
read_existing_button.grid(row=1, column=1, sticky="ew", padx=(10, 0), pady=(0, 10))

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
    width=38,
    bootstyle="info",
)
log_path_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))

browse_btn = ttkb.Button(
    controls_subframe,
    text="Browse",
    command=browse_log_path,
    bootstyle="secondary",
)
browse_btn.pack(side="left")

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


def connect_reader():
    if reader.is_connected():
        write_log("Reader already connected", log_console)
        return
    success = reader.connect(
        port=port_var.get(),
        baudrate=int(baud_var.get()),
    )
    if success:
        _set_connection_state(True)
        write_log(f"Connected to {port_var.get()} @ {baud_var.get()}", log_console)
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
    write_log("Start scan", log_console)


def stop_scan():
    if not reader.is_connected():
        return
    reader_status.set("Idle")
    write_log("Stop scan", log_console)


def read_existing_tag():
    existing_id = existing_tag_var.get().strip()
    if existing_id:
        write_log(f"Read existing tag ID: {existing_id}", log_console)
        messagebox.showinfo("Read Existing Tag", "Existing tag ID loaded.")
        return
    tag_id_value = field_vars["tag_id"].get().strip()
    if tag_id_value:
        existing_tag_var.set(tag_id_value)
        write_log("Existing tag loaded from detected tag", log_console)
        return
    messagebox.showinfo("Read Existing Tag", "No tag ID available to read.")


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
